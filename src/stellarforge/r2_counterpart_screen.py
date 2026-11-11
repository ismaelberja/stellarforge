"""R2 companion to the exact Gaia-ID audit: real *positional* source screening.

Per predeclared technical Taurus target: one Gaia DR3 15-arcsec cone and
one official IRSA ZTF 2-arcsec positional-lightcurve query. Only bounded,
derived and defensively qualified aggregates are public. Neither two
positionally close sources nor sparse Gaia neighbours establish a
physical Gaia--ZTF association, a single star, or astrophysical variability.

No ZTF original science FITS/masks/PSFcat are downloaded in this R2 step.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import math
import statistics
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .association import mjd_to_approximate_julian_year, propagate_gaia_position
from .coordinates import angular_separation_arcsec, validate_icrs
from .v14_field_review import (
    MAX_GAIA_ROWS, audit_neighbours, fetch_gaia_csv, make_gaia_adql,
    parse_gaia_csv,
)
from .ztf_photometry import inspect_ztf_bytes

IRSA_URL = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
GAIA_RADIUS_ARCSEC = 15.0
ZTF_RADIUS_ARCSEC = 2.0
ZTF_RESPONSE_BYTES_MAX = 4_000_000
ZTF_MAX_CURVES_PER_TARGET = 30
FAILED_NETWORK = (HTTPError, URLError, TimeoutError, OSError, ValueError,
                  UnicodeError)


def ztf_positional_url(ra: float, dec: float, *,
                       radius_arcsec: float = ZTF_RADIUS_ARCSEC) -> str:
    """Official IRSA API query for all objects in a tiny fixed circle.

    NOBS_MIN=5 controls transferred photometry size; NOT a scientific
    source-validation rule. No source-ID lookup or candidate post-selection.
    """
    validate_icrs(ra, dec)
    if not math.isfinite(radius_arcsec) or not 0 < radius_arcsec <= 2.0:
        raise ValueError("R2 positional-query radius must be in (0,2] arcsec")
    params = urlencode({
        "POS": f"CIRCLE {ra:.9f} {dec:.9f} {radius_arcsec / 3600:.10f}",
        "NOBS_MIN": "5", "FORMAT": "csv",
    })
    return f"{IRSA_URL}?{params}"


def fetch_ztf_positional(ra: float, dec: float, *,
                         radius_arcsec: float = ZTF_RADIUS_ARCSEC,
                         timeout_sec: float = 15.0, opener=urlopen) -> bytes:
    if not math.isfinite(timeout_sec) or not 5 <= timeout_sec <= 45:
        raise ValueError("R2 IRSA timeout must be in [5,45] seconds")
    url = ztf_positional_url(ra, dec, radius_arcsec=radius_arcsec)
    request = Request(
        url, headers={"User-Agent": "StellarForge/2.0 Taurus R2 research source review",
                      "Accept": "text/csv,text/plain"},
        method="GET")
    with opener(request, timeout=timeout_sec) as response:
        payload = response.read(ZTF_RESPONSE_BYTES_MAX + 1)
    if not payload or len(payload) > ZTF_RESPONSE_BYTES_MAX:
        raise ValueError("ZTF positional query empty or larger than bounded limit")
    if payload.lstrip().startswith((b"<", b"{")):
        raise ValueError("ZTF IRSA returned HTML/XML/JSON instead of photometry CSV")
    return payload


def screen_ztf_angular_oids(payload: bytes, gaia_target: dict | None) -> dict:
    """Review distinct OID/band MJD groups using Gaia PM, not a physical match.

    Original ZTF ra/dec (or objra/objdec) are survey-reported position
    proxies; this is not independent imaging/WCS astrometry. Annual
    parallax, survey centroid error, blending and non-linear motions
    remain outside this method. An empty/invalid query is not a
    photometric nondetection.
    """
    audit, points = inspect_ztf_bytes(payload, min_good_epochs=1)
    by_group = defaultdict(list)
    for point in points:
        by_group[(point.oid, point.band, point.time_scale)].append(point)
    if len(by_group) > ZTF_MAX_CURVES_PER_TARGET:
        raise ValueError("ZTF cone yielded too many candidate OID/band groups")
    candidates = []
    for (oid, band, scale), obs in sorted(by_group.items()):
        times = [p.time_value for p in obs]
        row = {
            "ztf_oid": oid, "ztf_band": band, "original_time_type": scale,
            "n_ztf_quality_accepted_epochs": len(obs),
            "position_screen": "NOT_EVALUATED",
            "separation_gaia_vs_survey_catalogue_median_arcsec": None,
            "provisional_position_within_2arcsec": False,
            "physical_source_identity_confirmed": False,
        }
        if scale != "MJD" or gaia_target is None:
            row["position_screen"] = (
                "NON_MJD_TIME_SYSTEM_NOT_CONVERTED" if scale != "MJD"
                else "GAIA_TARGET_NOT_RETRIEVED")
        elif gaia_target.get("pmra") is None or gaia_target.get("pmdec") is None:
            row["position_screen"] = "GAIA_PROPER_MOTION_MISSING"
        elif any(p.ra_deg is None or p.dec_deg is None for p in obs):
            row["position_screen"] = "ZTF_OBJECT_POSITION_MISSING"
        else:
            separations = []
            for p in obs:
                epoch = mjd_to_approximate_julian_year(p.time_value)
                ra, dec = propagate_gaia_position(
                    gaia_target["ra"], gaia_target["dec"],
                    gaia_target["pmra"], gaia_target["pmdec"],
                    epoch)
                separations.append(angular_separation_arcsec(
                    ra, dec, p.ra_deg, p.dec_deg))
            median = statistics.median(separations)
            row["separation_gaia_vs_survey_catalogue_median_arcsec"] = round(median, 5)
            row["ztf_median_mjd"] = round(statistics.median(times), 6)
            row["position_screen"] = ("WITHIN_PROVISIONAL_2_ARCSEC_RADIUS"
                                     if median <= ZTF_RADIUS_ARCSEC
                                     else "OUTSIDE_PROVISIONAL_2_ARCSEC_RADIUS")
            row["provisional_position_within_2arcsec"] = median <= ZTF_RADIUS_ARCSEC
        candidates.append(row)
    by_band = defaultdict(set)
    for item in candidates:
        if item["provisional_position_within_2arcsec"]:
            by_band[item["ztf_band"]].add(item["ztf_oid"])
    ambiguous_bands = sorted(
        band for band, oids in by_band.items() if len(oids) > 1)
    for c in candidates:
        if c["ztf_band"] in ambiguous_bands and c["provisional_position_within_2arcsec"]:
            c["position_screen"] = "AMBIGUOUS_MULTIPLE_ZTF_OIDS_SAME_BAND"
    return {
        "source": "Official IRSA ZTF positional source/photometry query",
        "raw_sha256_no_csv_committed": hashlib.sha256(payload).hexdigest(),
        "raw_rows": audit["raw_rows"],
        "n_quality_accepted_photometric_rows": audit["kept_rows"],
        "n_candidate_oid_band_time_groups": len(candidates),
        "n_oid_band_groups_inside_provisional_2arcsec": sum(
            x["provisional_position_within_2arcsec"] for x in candidates),
        "ambiguous_same_band_ztf_oid_bands": ambiguous_bands,
        "n_unique_ztf_oids_returned": len({c["ztf_oid"] for c in candidates}),
        "candidates": candidates,
        "n_gaia_ztf_physical_matches_confirmed": 0,
        "no_ztf_science_fits_review_completed": True,
        "data_scope": "REAL_IRSA_CATALOGUE_PHOTOMETRY_NOT_PHYSICAL_IDENTITY",
        "original_ztf_image_deblending_review": "NOT_PERFORMED",
    }


def assess_r2_target(seed: dict, *, gaia_fetch=fetch_gaia_csv,
                     ztf_fetch=fetch_ztf_positional,
                     timeout_sec: float = 15.0) -> dict:
    """An honest row even when Gaia or IRSA is temporarily unavailable."""
    sid = str(seed["gaia"]).strip()
    ra, dec = float(seed["ra"]), float(seed["dec"])
    validate_icrs(ra, dec)
    if not sid.isascii() or not sid.isdigit():
        raise ValueError("Gaia exact ID invalid")
    result = {
        "gaia_dr3_source_id": sid,
        "technical_seed_group": seed["group"],
        "gaia_catalogue_neighbours_status": "NOT_CHECKED",
        "gaia_cone_raw_sha256": None,
        "gaia_neighbours_within_2arcsec": None,
        "gaia_neighbours_within_5arcsec": None,
        "gaia_cone_max200_truncated": None,
        "gaia_target_ruwe": None,
        "ztf_positional_query_status": "NOT_CHECKED",
        "ztf_query_url_sha256": hashlib.sha256(
            ztf_positional_url(ra, dec).encode()).hexdigest(),
        "ztf_raw_sha256": None,
        "ztf_original_rows": None,
        "ztf_oid_band_groups": None,
        "ztf_oid_band_groups_near_gaia": None,
        "ztf_ambiguous_bands": [],
        "ztf_candidate_oids_per_band": [],
        "gaia_ztf_physical_identity_status": "PENDING_INDEPENDENT_ORIGINAL_FITS_AND_CROSSMATCH",
        "full_r2_identity_completed": False,
        "new_variable_star_confirmed": False,
    }
    gaia_target = None
    try:
        raw = gaia_fetch(ra, dec, radius_arcsec=GAIA_RADIUS_ARCSEC,
                         timeout_sec=timeout_sec)
        result["gaia_cone_raw_sha256"] = hashlib.sha256(raw).hexdigest()
        rows = parse_gaia_csv(raw)
        check = audit_neighbours(
            rows, target_id=sid, ra_deg=ra, dec_deg=dec,
            epoch_jyear=2021.0, cone_arcsec=GAIA_RADIUS_ARCSEC)
        result["gaia_catalogue_neighbours_status"] = check["status"]
        result["gaia_cone_max200_truncated"] = check["truncated_by_max_rows"]
        result["gaia_neighbours_within_2arcsec"] = check.get(
            "n_other_gaia_sources_within_2_arcsec")
        result["gaia_neighbours_within_5arcsec"] = check.get(
            "n_other_gaia_sources_within_5_arcsec")
        result["gaia_target_ruwe"] = check.get("target_gaia_ruwe")
        gaia_target = next((r for r in rows if r["source_id"] == sid), None)
        if result["gaia_cone_max200_truncated"]:
            gaia_target = None
    except FAILED_NETWORK:
        result["gaia_catalogue_neighbours_status"] = "GAIA_QUERY_OR_PARSE_UNAVAILABLE"
    try:
        raw = ztf_fetch(ra, dec, radius_arcsec=ZTF_RADIUS_ARCSEC,
                        timeout_sec=timeout_sec)
        detail = screen_ztf_angular_oids(raw, gaia_target)
        result["ztf_positional_query_status"] = "ORIGINAL_IRSA_RESPONSE_INSPECTED"
        result["ztf_raw_sha256"] = detail["raw_sha256_no_csv_committed"]
        result["ztf_original_rows"] = detail["raw_rows"]
        result["ztf_oid_band_groups"] = detail["n_candidate_oid_band_time_groups"]
        result["ztf_oid_band_groups_near_gaia"] = (
            detail["n_oid_band_groups_inside_provisional_2arcsec"])
        result["ztf_ambiguous_bands"] = detail["ambiguous_same_band_ztf_oid_bands"]
        result["ztf_candidate_oids_per_band"] = detail["candidates"]
    except FAILED_NETWORK:
        result["ztf_positional_query_status"] = "IRSA_QUERY_OR_PARSE_UNAVAILABLE"
    return result


def summarise_r2_screen(rows: list[dict], *, seed_sha256: str) -> dict:
    if not isinstance(rows, list) or len(rows) != 24:
        raise ValueError("R2 screening report requires all frozen 24 candidates")
    ids = [r["gaia_dr3_source_id"] for r in rows]
    if len(set(ids)) != 24:
        raise ValueError("R2 report contains duplicate candidates")
    n_gaia = sum(
        r["gaia_catalogue_neighbours_status"] ==
        "GAIA_NEIGHBOUR_SCREEN_NOT_IMAGE_VALIDATION" for r in rows)
    n_ztf = sum(r["ztf_positional_query_status"] ==
                "ORIGINAL_IRSA_RESPONSE_INSPECTED" for r in rows)
    return {
        "phase": "R2_GAIA_NEIGHBOURS_AND_ZTF_POSITIONAL_OIDS_NOT_PHYSICAL_IDENTITY",
        "original_r1_seed_sha256": seed_sha256,
        "n_frozen_technical_candidates": 24,
        "n_gaia_cones_with_complete_catalogue_screen": n_gaia,
        "n_ztf_cones_with_parsed_real_irsa_data": n_ztf,
        "n_gaia_catalogue_cones_failed_or_truncated": 24 - n_gaia,
        "n_ztf_irsa_cones_failed_or_unparseable": 24 - n_ztf,
        "n_sources_with_gaia_neighbours_within_2arcsec": sum(
            r["gaia_neighbours_within_2arcsec"] is not None
            and r["gaia_neighbours_within_2arcsec"] > 0 for r in rows),
        "n_sources_with_multiple_ztf_oids_in_a_band": sum(
            bool(r["ztf_ambiguous_bands"]) for r in rows),
        "n_sources_with_provisional_ztf_oid_groups": sum(
            (r["ztf_oid_band_groups_near_gaia"] or 0) > 0 for r in rows),
        "n_independently_authenticated_gaia_ztf_physical_identities": 0,
        "n_confirmed_variable_stars": 0,
        "original_ztf_science_pixel_mask_and_psfcat_independent_review_completed": False,
        "scientifically_vetted_24_source_YSO_sample": False,
        "full_R2_complete": False,
        "individual_targets": rows,
        "limitations": [
            "A 15-arcsec Gaia DR3 cone is not complete for faint/unresolved optical neighbours.",
            "A 2-arcsec ZTF light-curve API positional query is not a Gaia--ZTF physical source crossmatch.",
            "Approximate proper motion at each original MJD omits annual parallax and Gaia/ZTF covariance/systematics.",
            "ZTF OID sky positions are inherited from survey processing; external image/mask and catalogue verification remains mandatory.",
            "All query/parse failures stay labelled unavailable and are not used as negative stellar photometric results.",
            "The frozen pre-existing 24-target subset is not a representative Taurus young-star population.",
        ],
    }
