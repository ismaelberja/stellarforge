"""Conservative same-image radial-profile controls for public ZTF FITS cutouts.

NOT a PSF calibration, deblending, new source discovery, or validated Gaia/ZTF
identification. Multiple potentially stellar image peaks may be instrumental
artifacts or galaxies: the comparison is an engineering diagnostic only.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import io
import math
import statistics
from urllib.error import HTTPError, URLError

from .association import mjd_to_approximate_julian_year, propagate_gaia_position
from .v14_field_review import ztf_reference_cutout_url, ztf_science_cutout_url
from .v15_image_pixels import fetch_fits_cutout, inspect_fits_cutout
from .v16_psf_repeatability import fit_local_gaussian_proxy, PSF_OK

RADIAL_BINS_PIXELS = ((0, 1.25), (1.25, 2.25), (2.25, 3.25),
                      (3.25, 4.25), (4.25, 5.25), (5.25, 6.25))
MAX_CONTROL_CANDIDATES = 10


def _read_image(raw: bytes):
    import numpy as np
    from astropy.io import fits
    from astropy.wcs import WCS
    with fits.open(io.BytesIO(raw), memmap=False) as hdul:
        images = [h for h in hdul
                  if getattr(h, "data", None) is not None
                  and getattr(h.data, "ndim", None) == 2]
        if len(images) != 1:
            raise ValueError("Expected exactly one two-dimensional FITS image")
        img = np.asarray(images[0].data, dtype=float).copy()
        wcs = WCS(images[0].header.copy())
    return img, wcs


def _local_radial_proxy(image, cx: float, cy: float):
    """Background-subtracted radial fractions; no PSF/crowding calibration."""
    import numpy as np
    ny, nx = image.shape
    if not (15 <= cx < nx - 15 and 15 <= cy < ny - 15):
        return None
    xmin = max(0, int(cx) - 16)
    xmax = min(nx, int(cx) + 17)
    ymin = max(0, int(cy) - 16)
    ymax = min(ny, int(cy) + 17)
    cut = image[ymin:ymax, xmin:xmax]
    yy, xx = np.indices(cut.shape)
    rr = np.hypot(xx+xmin-cx, yy+ymin-cy)
    good = np.isfinite(cut)
    annulus = good & (rr >= 9) & (rr < 13)
    if annulus.sum() < 50:
        return None
    bg = float(np.median(cut[annulus]))
    noise = float(1.4826 * np.median(np.abs(cut[annulus]-bg)))
    if not math.isfinite(noise) or noise <= 1e-9:
        return None
    corrected = cut-bg
    aperture = good & (rr < 6.25)
    if aperture.sum() < 90:
        return None
    total = float(np.sum(corrected[aperture]))
    core = corrected[good & (rr < 1.5)]
    if total <= 0 or core.size < 3 or float(np.max(core)) < 8*noise:
        return None
    fractions = []
    for low, high in RADIAL_BINS_PIXELS:
        mask = good & (rr >= low) & (rr < high)
        if mask.sum() < 2:
            return None
        fractions.append(float(np.sum(corrected[mask])/total))
    if not all(math.isfinite(x) for x in fractions):
        return None
    # A negatively offset bowl or strong sky contamination makes this proxy
    # uninterpretable even if a local maximum is present.
    if min(fractions) < -.15 or sum(fractions) > 1.2:
        return None
    return {
        "normalized_ring_fractions": fractions,
        "local_background_median": round(bg, 5),
        "local_mad_noise_proxy": round(noise, 5),
        "central_peak_snr_proxy": round(float(np.max(core))/noise, 3),
    }


def inspect_image_with_same_field_controls(
    raw: bytes, *, expected_ra_deg: float, expected_dec_deg: float,
    image_kind: str = "science",
) -> dict:
    """Measure an *unverified* target and separated same-image comparison peaks.

    A control is an image peak > 13 px from the target, > 15 px from edges,
    isolated by at least 9 px from another candidate peak and with a usable
    radial noise/flux profile. No stellar classifier or empirical calibrated
    PSF is assumed; no association/classification flags are set true.
    """
    import numpy as np
    from scipy.ndimage import gaussian_filter, maximum_filter

    if image_kind not in ("science", "reference_coadd"):
        raise ValueError("Unsupported FITS image kind")
    upstream = inspect_fits_cutout(
        raw, expected_ra_deg=expected_ra_deg, expected_dec_deg=expected_dec_deg)
    if upstream["status"] != "PIXEL_WCS_PROVISIONAL_SCREEN_COMPLETED":
        return {
            "status": "V15_IMAGE_GATE_INCOMPLETE",
            "image_gate_status": upstream["status"],
            "field_psf_calibrated": False,
            "deblending_verified": False,
            "gaia_ztf_identity_confirmed": False,
        }

    img, wcs = _read_image(raw)
    if img.shape[0] < 45 or img.shape[1] < 45:
        return {
            "status": "INSUFFICIENT_FIELD_FOR_CONTROLS",
            "field_psf_calibrated": False, "deblending_verified": False,
            "gaia_ztf_identity_confirmed": False,
        }
    tx, ty = map(float, wcs.world_to_pixel_values(
        expected_ra_deg, expected_dec_deg))
    fitted = fit_local_gaussian_proxy(
        raw, expected_ra_deg=expected_ra_deg,
        expected_dec_deg=expected_dec_deg, image_kind=image_kind)
    target = _local_radial_proxy(img, tx, ty)
    if target is None:
        return {
            "status": "TARGET_RADIAL_PROXY_UNUSABLE",
            "single_gaussian_fit": fitted,
            "field_psf_calibrated": False, "deblending_verified": False,
            "gaia_ztf_identity_confirmed": False,
        }
    finite = np.isfinite(img)
    med = float(np.nanmedian(img))
    noise_global = float(1.4826*np.nanmedian(np.abs(img[finite]-med)))
    if not math.isfinite(noise_global) or noise_global <= 1e-9:
        raise ValueError("Global image noise proxy not defined")
    smooth = gaussian_filter(np.where(finite,img,med), sigma=1.2)
    threshold = med + 8*noise_global
    selected = (smooth == maximum_filter(smooth, size=7)) & (smooth > threshold)
    border = 16
    selected[:border,:] = False
    selected[-border:,:] = False
    selected[:,:border] = False
    selected[:,-border:] = False
    yy, xx = np.nonzero(selected)
    heights = [float(smooth[y,x]) for y,x in zip(yy,xx)]
    candidates = sorted(zip(xx, yy, heights), key=lambda row: -row[2])
    filtered = []
    for x,y,height in candidates:
        if math.hypot(x-tx,y-ty) < 13.0:
            continue
        if any(math.hypot(x-u,y-v)<9 for u,v,_ in filtered):
            continue
        filtered.append((int(x),int(y),height))
        if len(filtered)>=MAX_CONTROL_CANDIDATES:
            break
    controls = []
    for x,y,height in filtered:
        profile = _local_radial_proxy(img,float(x),float(y))
        if profile is not None:
            controls.append(profile)
    n_controls = len(controls)
    result = {
        "status": "SAME_IMAGE_RADIAL_SHAPE_COMPARISON_PROVISIONAL"
                  if n_controls>=2 else "INSUFFICIENT_UNVERIFIED_FIELD_CONTROLS",
        "fits_sha256": hashlib.sha256(raw).hexdigest(),
        "kind": image_kind,
        "field_width_pixels": int(img.shape[1]),
        "field_height_pixels": int(img.shape[0]),
        "target_single_gaussian_fit": fitted,
        "target_ring_fractions": [round(x, 5)
                                  for x in target["normalized_ring_fractions"]],
        "n_candidate_image_peaks_outside_target": len(filtered),
        "n_usable_unclassified_controls": n_controls,
        "control_peaks_not_classified_as_stars": True,
        "wcs_independently_recalibrated": False,
        "instrumental_PSF_calibrated": False,
        "field_psf_calibrated": False,
        "deblending_verified": False,
        "gaia_ztf_identity_confirmed": False,
        "astro_companion_confirmed": False,
    }
    if n_controls >= 2:
        matrix=np.array([r["normalized_ring_fractions"] for r in controls])
        control_med=np.median(matrix,axis=0)
        diff=np.array(target["normalized_ring_fractions"])-control_med
        result.update({
            "control_median_ring_fractions": [
                round(float(x), 5) for x in control_med],
            "target_minus_control_median_ring_fractions": [
                round(float(x), 5) for x in diff],
            "max_abs_ring_fraction_deviation": round(
                float(np.max(np.abs(diff))), 5),
            "descriptive_shape_review_flag": bool(
                np.max(np.abs(diff)) > .12),
            "shape_review_flag_is_not_a_binary_detection": True,
        })
    return result


def stratified_ztf_image_candidates(
    raw_csv: bytes, *, ra_deg: float, dec_deg: float,
    pmra_mas_yr: float, pmdec_mas_yr: float,
    science_per_oid: int = 6, cutout_arcsec: float = 90.0,
) -> list[dict]:
    """Up to 6 uniformly distributed original epochs per OID + 1 ref URL.

    Quality flag filtering retains the project's existing bit-32768 veto.
    The resulting selection is a *transport opportunity*, not scientifically
    representative epoch sampling or a new photometric measurement.
    """
    if not 1<=science_per_oid<=6 or not 45<=cutout_arcsec<=90:
        raise ValueError("Image request budget or cutout size out of bounds")
    rows=csv.DictReader(io.StringIO(raw_csv.decode("utf-8-sig")))
    required={"oid","mjd","catflags","filtercode","filefracday",
              "field","ccdid","qid"}
    if not rows.fieldnames or not required.issubset(rows.fieldnames):
        raise ValueError("Missing ZTF acquisition columns")
    groups=defaultdict(list)
    for row in rows:
        oid,band=row["oid"],row["filtercode"]
        if not oid.isdigit() or band not in ("zg","zr","zi"):
            raise ValueError("Unexpected OID/filter")
        mjd=float(row["mjd"])
        mjd_to_approximate_julian_year(mjd)
        if int(row["catflags"]) & 32768:
            continue
        groups[(oid,band)].append((mjd,row))
    result=[]
    for (oid,band),series in sorted(groups.items()):
        if not series:
            continue
        series.sort(key=lambda z:z[0])
        # Quantile-spaced choices; avoid the first/last potentially anomalous
        # observations and do not retry the same filefracday.
        positions=[min(len(series)-1,max(0,round(
            (i+.5)*len(series)/science_per_oid-.5)))
                   for i in range(science_per_oid)]
        positions=list(dict.fromkeys(positions))
        chosen=[]
        observed_filefracdays=set()
        for index in positions:
            mjd,row=series[index]
            if row["filefracday"] in observed_filefracdays:
                continue
            observed_filefracdays.add(row["filefracday"])
            ra,dec=propagate_gaia_position(
                ra_deg,dec_deg,pmra_mas_yr,pmdec_mas_yr,
                mjd_to_approximate_julian_year(mjd))
            chosen.append({
                "kind":"science","mjd":round(mjd,6),
                "url":ztf_science_cutout_url(
                    row,ra_center=ra,dec_center=dec,
                    size_arcsec=cutout_arcsec),
                "expected_ra_deg":ra,"expected_dec_deg":dec,
                "observation_filefracday":str(row["filefracday"]),
            })
        if chosen:
            mjd,row=series[len(series)//2]
            ra,dec=propagate_gaia_position(
                ra_deg,dec_deg,pmra_mas_yr,pmdec_mas_yr,
                mjd_to_approximate_julian_year(mjd))
            chosen.append({
                "kind":"reference_coadd","mjd":None,
                "url":ztf_reference_cutout_url(
                    row,ra_center=ra,dec_center=dec,
                    size_arcsec=cutout_arcsec),
                "expected_ra_deg":ra,"expected_dec_deg":dec,
                "observation_filefracday":None,
            })
        result.append({
            "ztf_oid":oid,"band":band,
            "candidates":chosen,
            "scientific_identity_verified":False,
            "reference_coadd_is_not_independent_science":True,
        })
    return result


def inspect_curve_field_controls(
    curve: dict, *, timeout: float = 6.0,
    science_attempts: int = 6,
    max_reference_attempts: int = 1,
    fetch=fetch_fits_cutout, inspect=inspect_image_with_same_field_controls,
) -> dict:
    """Obey a fixed request budget, keep errors, stop once 2 science successes."""
    if not 1<=science_attempts<=6 or max_reference_attempts not in (0,1):
        raise ValueError("Exceeded instrument archive request budget")
    reports=[]
    n_science_ok=0
    seen_raw=set()
    candidates=[x for x in curve["candidates"] if x["kind"]=="science"]
    for candidate in candidates[:science_attempts]:
        row={"kind":"science","mjd":candidate["mjd"]}
        try:
            raw=fetch(candidate["url"],timeout=timeout)
            outcome=inspect(
                raw,expected_ra_deg=candidate["expected_ra_deg"],
                expected_dec_deg=candidate["expected_dec_deg"],
                image_kind="science")
            row["status"]=outcome["status"]
            row["field_audit"]=outcome
            h=outcome.get("fits_sha256")
            if h and h not in seen_raw and outcome["status"] in (
                    "SAME_IMAGE_RADIAL_SHAPE_COMPARISON_PROVISIONAL",
                    "INSUFFICIENT_UNVERIFIED_FIELD_CONTROLS"):
                seen_raw.add(h)
                n_science_ok+=1
        except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
            row["status"]="IMAGE_TRANSPORT_OR_VALIDATION_FAILED"
            row["error_type"]=type(exc).__name__
            if isinstance(exc,HTTPError):
                row["http_status"]=int(exc.code)
        reports.append(row)
        if n_science_ok>=2:
            break
    if n_science_ok==0 and max_reference_attempts:
        refs=[x for x in curve["candidates"] if x["kind"]=="reference_coadd"]
        for candidate in refs[:max_reference_attempts]:
            row={"kind":"reference_coadd","mjd":None}
            try:
                raw=fetch(candidate["url"],timeout=timeout)
                outcome=inspect(raw,expected_ra_deg=candidate["expected_ra_deg"],
                    expected_dec_deg=candidate["expected_dec_deg"],
                    image_kind="reference_coadd")
                row["status"]=outcome["status"]
                row["field_audit"]=outcome
            except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
                row["status"]="IMAGE_TRANSPORT_OR_VALIDATION_FAILED"
                row["error_type"]=type(exc).__name__
                if isinstance(exc,HTTPError):
                    row["http_status"]=int(exc.code)
            reports.append(row)
    science=[a for a in reports if a["kind"]=="science"
             and a.get("field_audit",{}).get("fits_sha256")
             and a["status"] in (
                "SAME_IMAGE_RADIAL_SHAPE_COMPARISON_PROVISIONAL",
                "INSUFFICIENT_UNVERIFIED_FIELD_CONTROLS")]
    science_by_hash={x["field_audit"]["fits_sha256"]:x for x in science}
    valid=list(science_by_hash.values())
    offsets=[]
    if len(valid)>=2:
        for item in valid:
            fit=item["field_audit"].get("target_single_gaussian_fit",{})
            if "fitted_centroid_east_minus_Gaia_arcsec" in fit and \
               "fitted_centroid_north_minus_Gaia_arcsec" in fit:
                offsets.append((fit["fitted_centroid_east_minus_Gaia_arcsec"],
                                fit["fitted_centroid_north_minus_Gaia_arcsec"]))
    spread=(max(math.hypot(a[0]-b[0],a[1]-b[1])
                for i,a in enumerate(offsets) for b in offsets[i+1:])
            if len(offsets)>=2 else None)
    return {
        "ztf_oid":curve["ztf_oid"],"band":curve["band"],
        "attempts":reports,
        "n_distinct_science_images_screened":len(valid),
        "n_science_images_with_2plus_field_controls":sum(
            x["field_audit"]["n_usable_unclassified_controls"]>=2
            for x in valid),
        "science_repeatability_descriptive":len(offsets)>=2,
        "max_pairwise_fit_centroid_residual_difference_arcsec":(
            round(spread,5) if spread is not None else None),
        "reference_coadds_excluded_from_repeatability":True,
        "gaia_ztf_identity_confirmed":False,
        "field_deblended":False,
        "scientific_psf_calibrated":False,
    }
