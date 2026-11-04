"""Research-quality *ingestion audit* for official IRSA/ZTF light-curve tables.

This is intentionally NOT a scientific classification system. No source is
regarded as a confirmed cross-match from a cone query alone. Light curves
are kept separate by object identifier, passband, and time convention.

Reference: https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from dataclasses import asdict, dataclass
import hashlib
import io
import json
import math
from pathlib import Path
import statistics

from .coordinates import angular_separation_arcsec, validate_icrs

BANDS = {"1": "g", "2": "r", "3": "i", "g": "g", "r": "r", "i": "i",
         "zg": "g", "zr": "r", "zi": "i"}
TIME_COLUMNS = ("mjd", "hmjd", "hjd")  # Explicit priority when several clocks are present
REQUIRED = {"oid", "mag", "magerr", "catflags"}
NULLS = {"", "null", "nan", "--", "none"}


@dataclass(frozen=True)
class PhotometricPoint:
    oid: str
    band: str
    time_value: float
    time_scale: str  # DO NOT mix MJD, HMJD or HJD without explicit conversion.
    magnitude: float
    magnitude_error: float
    catflags: int
    row_number: int
    ra_deg: float | None = None
    dec_deg: float | None = None


def _field(row: dict, key: str) -> str:
    value = row.get(key, "")
    return "" if value is None else str(value).strip()


def _number(row: dict, field: str) -> float:
    raw = _field(row, field)
    if raw.lower() in NULLS:
        raise ValueError(f"Missing {field}")
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {field}")
    return value


def _ipac_rows(text: str) -> list[dict[str, str]]:
    """Parse standard fixed-column IPAC tables without optional dependencies.

    The positions of '|' characters in the header define column boundaries.
    Rows with unsupported/changed IPAC layout fail rather than being silently
    mapped to different photometric columns.
    """
    lines = text.splitlines()
    index = next((i for i, line in enumerate(lines) if line.lstrip().startswith("|")), None)
    if index is None:
        raise ValueError("Not a recognizable IPAC table (missing | header)")
    header = lines[index]
    starts = [i for i, char in enumerate(header) if char == "|"]
    if len(starts) < 3:
        raise ValueError("IPAC header has too few columns")
    columns = [header[a + 1:b].strip().lower() for a, b in zip(starts, starts[1:])]
    if len(columns) != len(set(columns)) or any(not col for col in columns):
        raise ValueError("Duplicate or blank IPAC column names")
    # Up to four metadata rows: name, types, units and null-value sentinels.
    first = index + 1
    while first < len(lines) and lines[first].lstrip().startswith("|"):
        first += 1
    parsed: list[dict[str, str]] = []
    for lineno, line in enumerate(lines[first:], first + 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("\\", "#")):
            continue
        if stripped.startswith("<"):
            raise ValueError(f"Unexpected HTML/XML in IPAC response, line {lineno}")
        if len(line) > starts[-1] and line[starts[-1]:].strip():
            raise ValueError(f"IPAC table contains data past last column on line {lineno}")
        padded = line.ljust(starts[-1])
        values = [padded[a + 1:b].strip() for a, b in zip(starts, starts[1:])]
        parsed.append(dict(zip(columns, values)))
    return parsed


def _csv_rows(text: str) -> list[dict[str, str]]:
    # Allow remote services to include blank lines / preamble comments.
    content = "\n".join(line for line in text.lstrip("\ufeff").splitlines()
                        if line.strip() and not line.lstrip().startswith(("#", "\\")))
    if not content.strip():
        raise ValueError("Empty CSV response")
    if content.lstrip().startswith("<"):
        raise ValueError("HTML/XML response is not a light curve CSV")
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise ValueError("Missing CSV header")
    if not {"oid", "mag"} <= {name.strip().lower() for name in reader.fieldnames}:
        raise ValueError("Unexpected CSV header: oid and mag are required")
    names = [name.strip().lower() for name in reader.fieldnames]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate CSV header columns")
    result = []
    for row in reader:
        if None in row:
            raise ValueError("Extra data cells in ZTF CSV row")
        result.append({key.strip().lower(): val for key, val in row.items()})
    return result


def parse_ztf_table(content: bytes | str) -> tuple[list[dict[str, str]], str]:
    """Return raw rows + recognized source layout, not yet science-valid points."""
    if isinstance(content, bytes):
        text = content.decode("utf-8-sig")
    else:
        text = content.lstrip("\ufeff")
    if len(text) > 25_000_000:
        raise ValueError("Local input larger than 25 MB; use streaming workflow")
    if not text.strip():
        raise ValueError("Empty IRSA response")
    if "<html" in text[:1000].lower() or "<votable" in text[:1000].lower():
        raise ValueError("Unexpected HTML or VOTable; request FORMAT=csv or ipac_table")
    if any(line.lstrip().startswith("|") for line in text.splitlines()[:15]):
        return _ipac_rows(text), "ipac_table"
    if "," in text.splitlines()[0] or any("," in x for x in text.splitlines()[:6]):
        return _csv_rows(text), "csv"
    raise ValueError("Unknown ZTF text layout; require official CSV or IPAC table")


def _quantile(xs: list[float], q: float) -> float:
    if not xs:
        raise ValueError("Cannot take quantile of empty vector")
    xs = sorted(xs)
    loc = (len(xs) - 1) * q
    lo = int(math.floor(loc))
    hi = int(math.ceil(loc))
    return xs[lo] * (hi - loc) + xs[hi] * (loc - lo) if hi != lo else xs[lo]


def _parse_point(row: dict[str, str], lineno: int) -> PhotometricPoint:
    oid = _field(row, "oid")
    if not oid.isdigit() or int(oid) <= 0:
        raise ValueError("invalid_oid")
    raw_band = _field(row, "filtercode") or _field(row, "fid") or _field(row, "filterid")
    band = BANDS.get(raw_band.lower())
    if band is None:
        raise ValueError("unknown_filter")
    present = [x for x in TIME_COLUMNS if _field(row, x).lower() not in NULLS]
    if not present:
        raise ValueError("missing_or_ambiguous_time_column")
    # Real ZTF API tables frequently contain *both* HJD and MJD. Rejecting
    # every such row would lose genuine observations. Prefer MJD unchanged
    # (no hidden time-scale conversions) and check any additional clock for
    # approximate consistency. HJD=HMJD+2400000.5; heliocentric correction
    # is at most minutes. This is a loose input sanity check, not BJD_TDB.
    try:
        clocks = {key: _number(row, key) for key in present}
        if "hjd" in clocks and "hmjd" in clocks and abs(clocks["hjd"] - clocks["hmjd"] - 2400000.5) > 0.002:
            raise ValueError("inconsistent_time_columns")
        if "mjd" in clocks and "hmjd" in clocks and abs(clocks["mjd"] - clocks["hmjd"]) > 0.05:
            raise ValueError("inconsistent_time_columns")
        if "mjd" in clocks and "hjd" in clocks and abs(clocks["hjd"] - clocks["mjd"] - 2400000.5) > 0.05:
            raise ValueError("inconsistent_time_columns")
        time_col = present[0]
        time, scale = clocks[time_col], time_col.upper()
        mag = _number(row, "mag")
        magerr = _number(row, "magerr")
    except ValueError as exc:
        if str(exc) == "inconsistent_time_columns":
            raise
        raise ValueError("invalid_photometry") from exc
    if not 20_000 < time < 3_000_000:
        raise ValueError("invalid_epoch_range")
    if not -10 < mag < 50:
        raise ValueError("invalid_magnitude_range")
    if magerr <= 0 or magerr >= 10:
        raise ValueError("invalid_magnitude_error")
    flags = _field(row, "catflags")
    if not flags or not flags.isdigit():
        raise ValueError("invalid_catflags")
    ra_col = "ra" if _field(row, "ra").lower() not in NULLS else "objra"
    dec_col = "dec" if _field(row, "dec").lower() not in NULLS else "objdec"
    ra_value = _field(row, ra_col)
    dec_value = _field(row, dec_col)
    if ra_value.lower() in NULLS:
        ra_value = ""
    if dec_value.lower() in NULLS:
        dec_value = ""
    if bool(ra_value) != bool(dec_value):
        raise ValueError("incomplete_position")
    if ra_value and dec_value:
        try:
            ra, dec = _number(row, ra_col), _number(row, dec_col)
            validate_icrs(ra, dec)
        except ValueError as exc:
            raise ValueError("invalid_position") from exc
    else:
        ra = dec = None
    return PhotometricPoint(oid, band, time, scale, mag, magerr, int(flags),
                            lineno, ra, dec)


def inspect_ztf_bytes(raw: bytes, *, target_ra: float | None = None,
                      target_dec: float | None = None,
                      radius_arcsec: float = 2.0,
                      catflags_mask: int = 32768,
                      min_good_epochs: int = 30) -> tuple[dict, list[PhotometricPoint]]:
    """Apply reproducible QC and return separate, NOT cross-matched curves.

    Target coordinates must be propagated to the survey epoch independently.
    A proximity match is provisional and not evidence of unique source identity.
    """
    if (target_ra is None) != (target_dec is None):
        raise ValueError("Target RA and Dec must be specified together")
    if target_ra is not None:
        validate_icrs(target_ra, target_dec)
    if not math.isfinite(radius_arcsec) or not 0 < radius_arcsec <= 60:
        raise ValueError("radius must be (0,60] arcsec")
    if not isinstance(catflags_mask, int) or catflags_mask < 0:
        raise ValueError("catflags mask must be nonnegative integer")
    if not isinstance(min_good_epochs, int) or min_good_epochs < 1:
        raise ValueError("min_good_epochs must be positive integer")
    rows, fmt = parse_ztf_table(raw)
    if not rows:
        return ({"source_format": fmt, "raw_rows": 0, "kept_rows": 0,
                 "rejected_reasons": {}, "curves": [], "status": "no_observations",
                 "scientific_membership_verified": False}, [])
    present = set(rows[0])
    if not REQUIRED <= present:
        raise ValueError(f"Missing ZTF required columns: {sorted(REQUIRED - present)}")
    if not any(c in present for c in ("fid", "filtercode", "filterid")):
        raise ValueError("Missing ZTF filter identifier column")
    if not any(c in present for c in TIME_COLUMNS):
        raise ValueError("Missing recognized time column (mjd, hmjd, hjd)")
    failures: Counter = Counter()
    points: list[PhotometricPoint] = []
    seen: set[tuple[str, str, str, float]] = set()
    raw_groups = Counter()
    simultaneous_clock_rows = 0
    for i, row in enumerate(rows, 2):
        simultaneous_clock_rows += sum(_field(row, clock).lower() not in NULLS
                                       for clock in TIME_COLUMNS) > 1
        try:
            point = _parse_point(row, i)
        except (ValueError, OverflowError) as exc:
            # Canonical, auditable rejection reasons; do not include arbitrary payload.
            key = str(exc) if str(exc) in {
                "invalid_oid", "unknown_filter", "missing_or_ambiguous_time_column",
                "invalid_photometry", "invalid_epoch_range", "invalid_magnitude_range",
                "invalid_magnitude_error", "invalid_catflags", "incomplete_position",
                "invalid_position", "inconsistent_time_columns",
            } else "malformed_row"
            failures[key] += 1
            continue
        raw_groups[(point.oid, point.band, point.time_scale)] += 1
        if point.catflags & catflags_mask:
            failures["masked_catflags"] += 1
            continue
        key = (point.oid, point.band, point.time_scale, point.time_value)
        if key in seen:
            failures["duplicate_epoch"] += 1
            continue
        seen.add(key)
        points.append(point)
    by_curve: dict[tuple[str, str, str], list[PhotometricPoint]] = defaultdict(list)
    for point in points:
        by_curve[(point.oid, point.band, point.time_scale)].append(point)
    curves = []
    for (oid, band, scale), observations in sorted(by_curve.items()):
        mags = [p.magnitude for p in observations]
        times = [p.time_value for p in observations]
        errors = [p.magnitude_error for p in observations]
        separations = [angular_separation_arcsec(target_ra, target_dec, p.ra_deg, p.dec_deg)
                       for p in observations if target_ra is not None and p.ra_deg is not None]
        if target_ra is None:
            pos_status = "target_not_supplied"
        elif len(separations) != len(observations):
            pos_status = "position_unverified"
        elif max(separations) > radius_arcsec:
            pos_status = "outside_provisional_radius"
        else:
            pos_status = "inside_provisional_radius"
        dates = sorted(times)
        curves.append({
            "oid": oid, "band": band, "time_scale": scale,
            "raw_rows": raw_groups[(oid, band, scale)],
            "good_epochs": len(observations), "time_span_days": round(dates[-1] - dates[0], 6),
            "median_magnitude": round(statistics.median(mags), 6),
            "robust_amp_p95_p05_mag": round(_quantile(mags, .95) - _quantile(mags, .05), 6),
            "median_magnitude_error": round(statistics.median(errors), 6),
            "median_separation_arcsec": (round(statistics.median(separations), 4)
                                          if separations else None),
            "position_status": pos_status,
            "sufficient_epochs": len(observations) >= min_good_epochs,
            "status": ("provisional_for_review" if len(observations) >= min_good_epochs
                       and pos_status == "inside_provisional_radius" else "needs_review"),
        })
    overlapping_bands = Counter(
        item["band"] for item in curves
        if item["position_status"] == "inside_provisional_radius"
    )
    ambiguous_bands = sorted(band for band, n in overlapping_bands.items() if n > 1)
    if ambiguous_bands:
        for item in curves:
            if item["band"] in ambiguous_bands and item["position_status"] == "inside_provisional_radius":
                item["status"] = "ambiguous_multiple_oids"
    stats = {
        "ambiguous_match_bands": ambiguous_bands,
        "source_format": fmt,
        "time_column_priority": list(TIME_COLUMNS),
        "raw_rows_with_multiple_time_columns": simultaneous_clock_rows,
        "time_columns_are_never_silently_converted": True,
        "raw_rows": len(rows), "kept_rows": len(points),
        "rejected_rows": sum(failures.values()),
        "rejected_reasons": dict(sorted(failures.items())),
        "curve_count": len(curves),
        "curves": curves,
        "status": "inspected_unverified_target" if target_ra is not None else "inspected_no_target",
        "scientific_membership_verified": False,
        "notes": [
            "Source membership never inferred from a ZTF cone-search response.",
            "Preferred clock MJD > HMJD > HJD when more than one provided; approximate clock consistency checked. No conversion to BJD_TDB.",
            "No magnitude outlier clipping: real dips and bursts may be outliers.",
            "Each ZTF OID/passband is audited separately; no forced concatenation.",
            "Object association requires epoch propagation and crowded-field review.",
            "Magnitude statistics are descriptive only; no dipper/burster labels are inferred.",
        ],
    }
    return stats, points


def audit_ztf_file(path: Path, outdir: Path, *, target_ra: float | None = None,
                   target_dec: float | None = None, radius_arcsec: float = 2.0,
                   min_good_epochs: int = 30, mask: int = 32768) -> dict:
    """Create reproducible normalized photometry + audit, verify source SHA256 sidecar."""
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    sidecar = Path(str(path) + ".provenance.json")
    if sidecar.exists():
        previous = json.loads(sidecar.read_text(encoding="utf-8"))
        if previous.get("sha256") != sha:
            raise ValueError("Raw ZTF response changed since its provenance was recorded")
    stats, points = inspect_ztf_bytes(raw, target_ra=target_ra, target_dec=target_dec,
                                      radius_arcsec=radius_arcsec,
                                      min_good_epochs=min_good_epochs,
                                      catflags_mask=mask)
    stats["provenance"] = {
        "original_file": Path(path).name,
        "original_sha256": sha,
        "source_url": (json.loads(sidecar.read_text(encoding="utf-8")).get("url")
                       if sidecar.exists() else None),
        "sidecar_points_to_irsa": sidecar.exists() and
                                   json.loads(sidecar.read_text(encoding="utf-8")).get("url", "").startswith(
                                       "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"),
    }
    output = Path(outdir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "ztf_audit.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    with (output / "photometry_good.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PhotometricPoint.__dataclass_fields__))
        writer.writeheader()
        for point in sorted(points, key=lambda p: (p.oid, p.band, p.time_scale, p.time_value)):
            writer.writerow(asdict(point))
    return stats