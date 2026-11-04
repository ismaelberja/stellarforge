"""Version 0.9: per-epoch, per-OID provisional Gaia/ZTF astrometric evidence.

Not a full astrometric solution: no covariance, parallax, perspective, WCS,
blending, or independent image inspection. Never asserts an identity match.
"""
from __future__ import annotations

from collections import defaultdict
import math
import statistics

from .association import mjd_to_approximate_julian_year, propagate_gaia_position
from .coordinates import angular_separation_arcsec, validate_icrs
from .ztf_photometry import PhotometricPoint


def _quantile(values: list[float], q: float) -> float:
    if not values or not 0 <= q <= 1:
        raise ValueError("Cannot quantify empty vector or invalid percentile")
    v = sorted(values)
    idx = (len(v) - 1) * q
    lo, hi = math.floor(idx), math.ceil(idx)
    return v[lo] * (hi - idx) + v[hi] * (idx - lo)


def per_epoch_association_evidence(
    points: list[PhotometricPoint], *, gaia_id: str, ra_deg: float, dec_deg: float,
    pmra_star_mas_yr: float | None, pmdec_mas_yr: float | None,
    position_reference: str = "Gaia", radius_arcsec: float = 2.0,
    min_positioned_epochs: int = 3,
) -> dict:
    """Score each usable MJD ZTF coordinate against Gaia at that *row's epoch*.

    Every combination of OID and band has a separate report. A candidate inside
    the cone is merely a possible positional match; never a confirmed crossmatch.
    Curves without MJD/positions are preserved as unassessable, not discarded.
    """
    if not isinstance(gaia_id, str) or not gaia_id.isdigit() or not (0 < len(gaia_id) <= 19):
        raise ValueError("Expected exact Gaia DR3 identifier string")
    validate_icrs(ra_deg, dec_deg)
    if not math.isfinite(radius_arcsec) or not 0 < radius_arcsec <= 30:
        raise ValueError("Invalid search radius")
    if not isinstance(min_positioned_epochs, int) or min_positioned_epochs < 1:
        raise ValueError("Invalid minimum epoch count")
    motion = (position_reference == "Gaia" and pmra_star_mas_yr is not None
              and pmdec_mas_yr is not None)
    if motion and not (math.isfinite(pmra_star_mas_yr) and math.isfinite(pmdec_mas_yr)):
        raise ValueError("Invalid proper motion")
    grouped = defaultdict(list)
    for p in points:
        if p.band not in ("g", "r", "i") or not p.oid.isdigit() or not p.oid:
            raise ValueError("Invalid curve identifiers")
        grouped[(p.oid, p.band, p.time_scale)].append(p)
    curves = []
    for (oid, band, scale), obs in sorted(grouped.items()):
        catalog_separations = []
        epoch_separations = []
        epochs = []
        for p in obs:
            if scale != "MJD" or p.ra_deg is None or p.dec_deg is None:
                continue
            epoch = mjd_to_approximate_julian_year(p.time_value)
            reference_sep = angular_separation_arcsec(ra_deg, dec_deg, p.ra_deg, p.dec_deg)
            catalog_separations.append(reference_sep)
            epochs.append(epoch)
            if motion:
                r, d = propagate_gaia_position(ra_deg, dec_deg, pmra_star_mas_yr,
                                               pmdec_mas_yr, epoch)
                epoch_separations.append(angular_separation_arcsec(r, d, p.ra_deg, p.dec_deg))
        distances = epoch_separations if motion else catalog_separations
        if not distances or len(distances) < min_positioned_epochs:
            status = "insufficient_epoch_positions"
        elif not motion:
            status = "no_reliable_Gaia_epoch_propagation"
        elif all(d > radius_arcsec for d in distances):
            status = "outside_radius_all_epochs"
        elif sum(d <= radius_arcsec for d in distances) < len(distances):
            status = "mixed_inside_outside_radius"
        else:
            status = "provisional_inside_radius_all_epochs"
        curves.append({
            "oid": oid, "band": band, "time_scale": scale,
            "n_qc_accepted_epochs": len(obs), "n_positioned_mjd_epochs": len(distances),
            "status": status,
            "median_epoch_julian_year": round(statistics.median(epochs), 6) if epochs else None,
            "median_separation_from_catalog_arcsec": round(statistics.median(catalog_separations), 6)
                if catalog_separations else None,
            "median_epoch_corrected_separation_arcsec": round(statistics.median(epoch_separations), 6)
                if epoch_separations else None,
            "p95_epoch_corrected_separation_arcsec": round(_quantile(epoch_separations, .95), 6)
                if epoch_separations else None,
            "fraction_epochs_inside_radius": round(sum(d <= radius_arcsec for d in distances) / len(distances), 6)
                if distances else None,
            "actual_image_and_blending_review_performed": False,
        })
    provisional = [c for c in curves if c["status"] == "provisional_inside_radius_all_epochs"]
    band_counts = {band: sum(x["band"] == band for x in provisional) for band in ("g", "r", "i")}
    if not curves:
        global_status = "no_good_photometry"
    elif not motion:
        global_status = "missing_Gaia_epoch_propagation"
    elif any(v > 1 for v in band_counts.values()):
        global_status = "ambiguous_multiple_oids_same_band"
    elif provisional:
        global_status = "possible_counterparts_require_independent_review"
    elif any(c["status"] == "mixed_inside_outside_radius" for c in curves):
        global_status = "variable_angular_separation_requires_review"
    elif all(c["status"] == "outside_radius_all_epochs" for c in curves):
        global_status = "all_positioned_curves_outside_radius"
    else:
        global_status = "no_sufficient_epoch_positions"
    return {
        "method": "v0.9_Gaia_TangentPlane_Approximation_Per_ZTF_MJD_Epoch",
        "gaia_dr3_source_id": gaia_id,
        "catalog_ra_deg": ra_deg, "catalog_dec_deg": dec_deg,
        "catalog_reference": position_reference, "radius_arcsec": radius_arcsec,
        "status": global_status,
        "n_curves": len(curves), "n_provisionally_in_radius": len(provisional),
        "ambiguous_bands": [band for band, n in band_counts.items() if n > 1],
        "curves": curves,
        "astrometric_identity_confirmed": False,
        "limitations": [
            "Gaia DR3 positions are propagated with 2D proper motion only, not full covariance/parallax.",
            "Survey positions from photometric rows may not be independent centroid measurements.",
            "No ZTF images, PSF fitting, blends, morphology or Gaia neighbor query are analyzed.",
            "The HJD/HMJD conventions are not converted to MJD for this astrometric screen.",
            "A cone match never establishes unique physical source identity.",
        ],
    }