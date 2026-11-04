"""Official IRSA/ZTF public light-curve API: query planning + provenance.

https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html

This module does NOT infer YSO membership from a cone search. The user must
supply positions from a scientifically vetted external membership catalogue.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .coordinates import validate_icrs

BASE_URL = "https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
ALLOWED_BANDS = frozenset({"g", "r", "i"})


def build_ztf_url(
    ra_deg: float,
    dec_deg: float,
    radius_arcsec: float = 2.0,
    bands: tuple[str, ...] = ("g", "r"),
    bad_catflags_mask: int = 32768,
    output_format: str = "ipac_table",
) -> str:
    """Build a URL to the published ZTF light-curve API with valid parameters."""
    validate_icrs(ra_deg, dec_deg)
    if not math.isfinite(radius_arcsec) or not 0 < radius_arcsec <= 600:
        raise ValueError("radius_arcsec must be in (0, 600]")
    if not bands or len(set(bands)) != len(bands) or not set(bands) <= ALLOWED_BANDS:
        raise ValueError("Bands must be a non-empty, unique subset of g, r, i")
    if not isinstance(bad_catflags_mask, int) or bad_catflags_mask < 0:
        raise ValueError("bad_catflags_mask must be nonnegative integer")
    if output_format not in {"csv", "ipac_table"}:
        raise ValueError("output_format must be csv or ipac_table")
    params = {
        "POS": f"CIRCLE {ra_deg:.9f} {dec_deg:.9f} {radius_arcsec / 3600.0:.9f}",
        "BANDNAME": ",".join(bands),
        "BAD_CATFLAGS_MASK": str(bad_catflags_mask),
        "FORMAT": output_format,
    }
    return f"{BASE_URL}?{urlencode(params)}"


def fetch_ztf_raw(url: str, output_path: Path, *, timeout_sec: float = 45) -> dict:
    """Save *raw response* + SHA256 provenance; no claim of scientific validation.

    Download a single vetted target's light curve. Only official IRSA API URLs
    can be used. Rate limits/retries and collection scale arrive in a later phase.
    """
    if not url.startswith(BASE_URL + "?"):
        raise ValueError("Only the official IRSA ZTF light-curve API is allowed")
    if timeout_sec <= 0 or timeout_sec > 300:
        raise ValueError("timeout_sec must be between 0 and 300 seconds")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "StellarForge-research/0.1 (academic prototype)"})
    with urlopen(req, timeout=timeout_sec) as response:
        raw = response.read(20_000_000 + 1)
        if len(raw) > 20_000_000:
            raise ValueError("Response exceeds 20 MB. Use the bulk-access workflow")
        content_type = response.headers.get("Content-Type", "")
    if raw.lstrip().lower().startswith((b"<html", b"<!doctype html")):
        raise ValueError("IRSA returned an HTML page, not a light-curve table")
    if not raw.strip():
        raise ValueError("Empty IRSA response")
    temporary = output_path.with_name(output_path.name + ".partial")
    temporary.write_bytes(raw)
    temporary.replace(output_path)
    manifest = {
        "url": url,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "content_type": content_type,
        "status": "unvalidated_raw_response",
        "notice": "Validate schema, data quality and multi-oid/photometric bands separately",
    }
    output_path.with_name(output_path.name + ".provenance.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    return manifest