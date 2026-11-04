"""Gaia DR3 TAP/ADQL smoke-test query construction.

An astrometric cone search is *not* a youth-membership determination. Luhman
(2023) will provide the membership reference; this query only checks the
Gaia TAP infrastructure and reports epoch-photometry availability flags.

Epoch photometry itself is available via DataLink, not the TAP table.
"""
from __future__ import annotations

import math
from .coordinates import validate_icrs


def gaia_cone_adql(ra_deg: float, dec_deg: float,
                   radius_deg: float = 0.1, max_rows: int = 100) -> str:
    validate_icrs(ra_deg, dec_deg)
    if not math.isfinite(radius_deg) or not 0 < radius_deg <= 5.0:
        raise ValueError("radius_deg must be >0 and <=5 for pilot queries")
    if not isinstance(max_rows, int) or not 1 <= max_rows <= 5000:
        raise ValueError("max_rows must be integer from 1 to 5000")
    return f"""-- Gaia DR3 technical smoke test; NOT a Taurus membership filter.
SELECT TOP {max_rows}
  g.source_id, g.ra, g.dec, g.parallax, g.parallax_error,
  g.pmra, g.pmdec, g.ruwe, g.phot_g_mean_mag, g.bp_rp,
  g.has_epoch_photometry
FROM gaiadr3.gaia_source AS g
WHERE 1 = CONTAINS(
  POINT('ICRS', g.ra, g.dec),
  CIRCLE('ICRS', {ra_deg:.9f}, {dec_deg:.9f}, {radius_deg:.9f})
)
ORDER BY g.phot_g_mean_mag ASC
"""


def gaia_datalink_instructions() -> str:
    return (
        "Gaia DR3 individual epoch photometry requires astroquery.gaia.Gaia.load_data("
        "ids=[verified_source_id], retrieval_type='EPOCH_PHOTOMETRY', "
        "data_release='Gaia DR3'). These results are not guaranteed for every Gaia source. "
        "Use has_epoch_photometry to check availability; access is via DataLink, not TAP."
    )