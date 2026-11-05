"""v1.4: Gaia DR3 field-neighbour audit and ZTF science-image review links.

An independent Gaia cone query can reveal catalogued near neighbours, but
neither a sparse Gaia field nor a successful FITS URL confirms a clean PSF.
No automated astrophysical source assignment is performed here.
"""
from __future__ import annotations

import csv
import io
import math
from pathlib import Path
import re
import statistics
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .association import mjd_to_approximate_julian_year, propagate_gaia_position
from .coordinates import angular_separation_arcsec, validate_icrs

GAIA_TAP_URL = "https://gaia.ari.uni-heidelberg.de/tap/sync"
IRSA_SCIENCE_ROOT = "https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci"
GAIA_COLUMNS = (
    "source_id", "ra", "dec", "pmra", "pmdec", "parallax",
    "phot_g_mean_mag", "ruwe", "ra_error", "dec_error",
)
MAX_GAIA_ROWS = 200


def make_gaia_adql(ra_deg: float, dec_deg: float,
                   radius_arcsec: float = 15.0) -> str:
    """Bounded Gaia DR3 cone query in ICRS; no target-ID substitutions."""
    validate_icrs(ra_deg, dec_deg)
    if not math.isfinite(radius_arcsec) or not 0 < radius_arcsec <= 30:
        raise ValueError("Gaia neighbour radius must be in (0,30] arcsec")
    r = radius_arcsec / 3600.0
    cols = ", ".join(GAIA_COLUMNS)
    return (
        f"SELECT TOP {MAX_GAIA_ROWS} {cols} FROM gaiadr3.gaia_source "
        f"WHERE 1=CONTAINS(POINT('ICRS',ra,dec),"
        f"CIRCLE('ICRS',{ra_deg:.10f},{dec_deg:.10f},{r:.12f}))"
    )


def fetch_gaia_csv(ra_deg: float, dec_deg: float, *,
                   radius_arcsec: float = 15.0,
                   timeout_sec: float = 30.0) -> bytes:
    """Fetch a small public Gaia DR3 CSV via TAP; NO auth or local caching."""
    adql = make_gaia_adql(ra_deg, dec_deg, radius_arcsec)
    if not 1 <= timeout_sec <= 90:
        raise ValueError("Timeout must be 1..90 seconds")
    form = urlencode({
        "REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql,
    }).encode("ascii")
    req = Request(
        GAIA_TAP_URL, form,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": "StellarForge/1.4 scientific Gaia DR3 field audit"},
        method="POST",
    )
    with urlopen(req, timeout=timeout_sec) as resp:
        data = resp.read(2_000_001)
    if not data or len(data) > 2_000_000:
        raise ValueError("Empty or excessive Gaia TAP response")
    return data


def _float_or_none(value: str | None) -> float | None:
    if value is None or str(value).strip().lower() in ("", "--", "null", "nan"):
        return None
    f = float(value)
    if not math.isfinite(f):
        raise ValueError("Non-finite numeric Gaia field")
    return f


def parse_gaia_csv(raw: bytes) -> list[dict]:
    """Reject VOTable/HTML/errors; require stable Gaia DR3 column names."""
    text = raw.decode("utf-8-sig")
    if text.lstrip().startswith(("<", "{")):
        raise ValueError("Gaia response is not CSV")
    text = "\n".join(x for x in text.splitlines()
                     if x.strip() and not x.lstrip().startswith("#"))
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not set(GAIA_COLUMNS).issubset(reader.fieldnames):
        raise ValueError("Gaia TAP CSV missing expected columns")
    out = []
    seen = set()
    for row in reader:
        if None in row:
            raise ValueError("Unexpected extra fields in Gaia TAP CSV")
        sid = str(row["source_id"]).strip()
        if not sid.isdigit() or sid in seen:
            raise ValueError("Invalid or duplicated Gaia DR3 source ID")
        seen.add(sid)
        ra, dec = _float_or_none(row["ra"]), _float_or_none(row["dec"])
        if ra is None or dec is None:
            raise ValueError("Gaia source without ICRS position")
        validate_icrs(ra, dec)
        out.append({
            "source_id": sid, "ra": ra, "dec": dec,
            "pmra": _float_or_none(row["pmra"]),
            "pmdec": _float_or_none(row["pmdec"]),
            "parallax": _float_or_none(row["parallax"]),
            "phot_g_mean_mag": _float_or_none(row["phot_g_mean_mag"]),
            "ruwe": _float_or_none(row["ruwe"]),
            "ra_error_mas": _float_or_none(row["ra_error"]),
            "dec_error_mas": _float_or_none(row["dec_error"]),
        })
    return out


def audit_neighbours(gaia_rows: list[dict], *, target_id: str,
                     ra_deg: float, dec_deg: float,
                     epoch_jyear: float,
                     cone_arcsec: float = 15.0) -> dict:
    """Rank catalogued Gaia field objects at nominal ZTF epoch.

    The distance is a 2D proper-motion approximation, not PSF deblending.
    A missing target or a row-cap prevents a positive 'clear' statement.
    """
    validate_icrs(ra_deg, dec_deg)
    if not str(target_id).isdigit():
        raise ValueError("Target ID must be Gaia DR3 numeric string")
    if not math.isfinite(epoch_jyear) or not 2016.0 <= epoch_jyear <= 2035.0:
        raise ValueError("Unexpected ZTF observation epoch")
    if not math.isfinite(cone_arcsec) or not 0 < cone_arcsec <= 30:
        raise ValueError("Bad cone radius")
    matches = [x for x in gaia_rows if x["source_id"] == str(target_id)]
    if len(matches) != 1:
        return {
            "status": "TARGET_NOT_IN_RETURNED_GAIA_CONE",
            "target_gaia_source_verified": False,
            "cone_radius_arcsec": cone_arcsec,
            "n_sources_returned": len(gaia_rows),
            "truncated_by_max_rows": len(gaia_rows) >= MAX_GAIA_ROWS,
            "nearby_sources": [],
            "image_blending_ruled_out": False,
        }
    main = matches[0]
    target_g = main["phot_g_mean_mag"]
    motion = main["pmra"] is not None and main["pmdec"] is not None
    target_epoch_pos = (
        propagate_gaia_position(main["ra"], main["dec"],
                                main["pmra"], main["pmdec"], epoch_jyear)
        if motion else (main["ra"], main["dec"])
    )
    neighbours = []
    for row in gaia_rows:
        if row["source_id"] == str(target_id):
            continue
        pm_known = row["pmra"] is not None and row["pmdec"] is not None
        obj_epoch_pos = (
            propagate_gaia_position(row["ra"], row["dec"],
                                    row["pmra"], row["pmdec"], epoch_jyear)
            if pm_known else (row["ra"], row["dec"])
        )
        sep = angular_separation_arcsec(
            target_epoch_pos[0], target_epoch_pos[1],
            obj_epoch_pos[0], obj_epoch_pos[1])
        mag = row["phot_g_mean_mag"]
        neighbours.append({
            "gaia_dr3_source_id": row["source_id"],
            "gaia_g_mag": mag,
            "delta_g_neighbour_minus_target": round(mag - target_g, 4)
                if mag is not None and target_g is not None else None,
            "separation_at_reference_epoch_arcsec": round(
                angular_separation_arcsec(main["ra"], main["dec"],
                                          row["ra"], row["dec"]), 5),
            "separation_at_nominal_ztf_epoch_arcsec": round(sep, 5),
            "two_dimensional_pm_available": pm_known,
            "gaia_ruwe": row["ruwe"],
        })
    neighbours.sort(key=lambda x: x["separation_at_nominal_ztf_epoch_arcsec"])
    complete = len(gaia_rows) < MAX_GAIA_ROWS
    return {
        "status": "GAIA_NEIGHBOUR_SCREEN_NOT_IMAGE_VALIDATION"
            if complete else "QUERY_TRUNCATED_REQUIRES_RECHECK",
        "target_gaia_source_verified": True,
        "target_gaia_g_mag": target_g,
        "target_gaia_ruwe": main["ruwe"],
        "target_ruwe_exceeds_1p4_quality_screen": (
            main["ruwe"] is not None and main["ruwe"] > 1.4),
        "target_gaia_parallax_mas": main["parallax"],
        "target_pm_available": motion,
        "epoch_jyear": round(epoch_jyear, 6),
        "cone_radius_arcsec": cone_arcsec,
        "n_sources_returned": len(gaia_rows),
        "truncated_by_max_rows": not complete,
        "n_other_gaia_sources_within_2_arcsec": sum(
            n["separation_at_nominal_ztf_epoch_arcsec"] <= 2 for n in neighbours),
        "n_other_gaia_sources_within_5_arcsec": sum(
            n["separation_at_nominal_ztf_epoch_arcsec"] <= 5 for n in neighbours),
        "n_other_gaia_sources_within_15_arcsec": sum(
            n["separation_at_nominal_ztf_epoch_arcsec"] <= 15 for n in neighbours),
        "nearby_sources": neighbours,
        "image_blending_ruled_out": False,
        "unresolved_or_non_gaia_contaminants_excluded": False,
    }


def ztf_science_cutout_url(row: dict, *,
                           ra_center: float, dec_center: float,
                           size_arcsec: float = 45) -> str:
    """Construct a single image cutout URL from actual exposure identifiers.

    Does not fetch the FITS image or certify its availability or astrometry.
    """
    validate_icrs(ra_center, dec_center)
    if not math.isfinite(size_arcsec) or not 15 <= size_arcsec <= 90:
        raise ValueError("Cutout size must be 15..90 arcsec")
    fracday = str(row["filefracday"])
    if not re.fullmatch(r"\d{14}", fracday):
        raise ValueError("Invalid ZTF filefracday")
    field = str(row["field"])
    if not field.isdigit() or not 1 <= int(field) <= 999999:
        raise ValueError("Invalid ZTF field ID")
    band = str(row["filtercode"]).lower()
    if band not in ("zg", "zr", "zi"):
        raise ValueError("Invalid ZTF filter")
    # IRSA photometry CSV uses hex strings (e.g. ccdid='0xf', qid='0x3').
    try:
        ccdid = int(str(row["ccdid"]), 0)
        qid = int(str(row["qid"]), 0)
    except ValueError as exc:
        raise ValueError("Invalid ZTF CCD or quadrant") from exc
    if not 1 <= ccdid <= 16 or not 1 <= qid <= 4:
        raise ValueError("CCD or quadrant out of range")
    filename = (f"ztf_{fracday}_{int(field):06d}_{band}_c{ccdid:02d}"
                f"_o_q{qid}_sciimg.fits")
    date_path = f"{fracday[:4]}/{fracday[4:8]}/{fracday[8:]}"
    query = urlencode({
        "center": f"{ra_center:.8f},{dec_center:.8f}",
        "size": f"{size_arcsec:g}arcsec",
        "gzip": "false",
    })
    return f"{IRSA_SCIENCE_ROOT}/{date_path}/{filename}?{query}"


def ztf_reference_cutout_url(row: dict, *,
                             ra_center: float, dec_center: float,
                             size_arcsec: float = 45) -> str:
    """Official ZTF reference-image cutout URL, not proof of image availability."""
    validate_icrs(ra_center, dec_center)
    if not math.isfinite(size_arcsec) or not 15 <= size_arcsec <= 90:
        raise ValueError("Cutout size must be 15..90 arcsec")
    field = str(row["field"])
    band = str(row["filtercode"]).lower()
    if not field.isdigit() or not 1 <= int(field) <= 999999:
        raise ValueError("Bad ZTF reference field")
    if band not in ("zg", "zr", "zi"):
        raise ValueError("Bad ZTF reference filter")
    try:
        ccd = int(str(row["ccdid"]), 0)
        qid = int(str(row["qid"]), 0)
    except ValueError as exc:
        raise ValueError("Bad ZTF reference detector") from exc
    if not 1 <= ccd <= 16 or not 1 <= qid <= 4:
        raise ValueError("Reference detector out of range")
    field6 = f"{int(field):06d}"
    name = f"ztf_{field6}_{band}_c{ccd:02d}_q{qid}_refimg.fits"
    path = (f"https://irsa.ipac.caltech.edu/ibe/data/ztf/products/ref/"
            f"{field6[:3]}/field{field6}/{band}/ccd{ccd:02d}/q{qid}/{name}")
    return path + "?" + urlencode({
        "center": f"{ra_center:.8f},{dec_center:.8f}",
        "size": f"{size_arcsec:g}arcsec", "gzip": "false",
    })


def selected_image_links(ztf_csv: bytes, *, target_ra_deg: float,
                         target_dec_deg: float,
                         target_pmra: float, target_pmdec: float) -> dict:
    """One median-epoch, quality-masked science-exposure link per OID/band."""
    reader = csv.DictReader(io.StringIO(ztf_csv.decode("utf-8-sig")))
    required = {"oid", "mjd", "catflags", "filtercode", "filefracday",
                "field", "ccdid", "qid"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValueError("Missing scientific exposure columns")
    groups = {}
    all_mjds = []
    for row in reader:
        oid, band = row["oid"], row["filtercode"]
        if not oid.isdigit() or band not in ("zg", "zr", "zi"):
            raise ValueError("Invalid ZTF OID or passband")
        mjd = float(row["mjd"])
        mjd_to_approximate_julian_year(mjd)
        if int(row["catflags"]) & 32768:
            continue
        groups.setdefault((oid, band), []).append((mjd, row))
        all_mjds.append(mjd)
    if not all_mjds:
        raise ValueError("No quality-masked MJD epochs")
    selected = []
    for (oid, band), rows in sorted(groups.items()):
        rows.sort(key=lambda x: x[0])
        mjd, row = rows[len(rows) // 2]
        jyear = mjd_to_approximate_julian_year(mjd)
        ra, dec = propagate_gaia_position(
            target_ra_deg, target_dec_deg, target_pmra, target_pmdec, jyear)
        selected.append({
            "oid": oid, "band": band,
            "exposure_mjd": round(mjd, 6),
            "ztf_field": row["field"],
            "ztf_ccdid": row["ccdid"],
            "ztf_quadrant": row["qid"],
            "image_cutout_url": ztf_science_cutout_url(
                row, ra_center=ra, dec_center=dec),
            "reference_cutout_url": ztf_reference_cutout_url(
                row, ra_center=ra, dec_center=dec),
            "image_fits_retrieved": False,
            "image_wcs_and_psf_review_complete": False,
        })
    return {
        "representative_gaia_screen_epoch_jyear": round(
            mjd_to_approximate_julian_year(statistics.median(all_mjds)), 6),
        "n_selected_cutouts": len(selected),
        "image_cutouts": selected,
        "image_blending_verified_clean": False,
    }


def probe_ztf_image_header(image_url: str, *, timeout_sec: float = 18.0,
                           opener=urlopen) -> dict:
    """Probe only the FITS header of an official image; never archive pixels.

    A valid FITS signature confirms transport, not correct WCS, clean PSF,
    deblending or physical source identity.
    """
    u = urlparse(image_url)
    if (u.scheme != "https" or u.hostname != "irsa.ipac.caltech.edu"
            or not (u.path.startswith("/ibe/data/ztf/products/sci/")
                    or u.path.startswith("/ibe/data/ztf/products/ref/"))
            or u.username is not None or u.password is not None):
        raise ValueError("Disallowed image URL")
    if not 1 <= timeout_sec <= 45:
        raise ValueError("Bad image timeout")
    request = Request(image_url, headers={"User-Agent":
                                         "StellarForge/1.4 provenance-only FITS header probe"})
    try:
        with opener(request, timeout=timeout_sec) as response:
            first = response.read(80)
        return {
            "status": "FITS_HEADER_TRANSPORT_CONFIRMED"
                if first.startswith(b"SIMPLE  =") else "UNRECOGNIZED_RESPONSE",
            "fits_image_fully_downloaded": False,
            "wcs_and_psf_physically_inspected": False,
            "astrophysical_identity_confirmed": False,
        }
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        record = {
            "status": "IMAGE_TRANSPORT_FAILED",
            "error_type": type(error).__name__,
            "fits_image_fully_downloaded": False,
            "wcs_and_psf_physically_inspected": False,
            "astrophysical_identity_confirmed": False,
        }
        if isinstance(error, HTTPError):
            record["http_status"] = int(error.code)
        return record
