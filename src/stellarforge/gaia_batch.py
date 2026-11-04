"""Gaia DR3 exact-ID ADQL: catalog identity takes precedence over proximity.

The output is only an ADQL query. Network retrieval is a separate, auditable step.
"""
from __future__ import annotations

from .catalog import Member


def exact_ids_query(members: list[Member], *, max_ids: int = 200) -> str:
    if not 1 <= max_ids <= 200:
        raise ValueError("max_ids must be between 1 and 200")
    ids = sorted({int(m.gaia_dr3_source_id) for m in members if m.gaia_dr3_source_id})
    if not ids:
        raise ValueError("No verified Gaia source identifiers in input")
    if len(ids) > max_ids:
        raise ValueError(f"Too many Gaia IDs ({len(ids)}); split the batch deliberately")
    # The exact unsigned-integer validation occurs in catalog._gaia_id.
    values = ", ".join(str(n) for n in ids)
    return f"""-- Metadata lookup for externally vetted Taurus members.
-- This query does NOT determine membership, which is fixed in the input catalog.
SELECT g.source_id, g.ra, g.dec, g.ref_epoch,
       g.pmra, g.pmdec, g.pmra_error, g.pmdec_error,
       g.parallax, g.parallax_error, g.ruwe,
       g.phot_g_mean_mag, g.bp_rp, g.has_epoch_photometry
FROM gaiadr3.gaia_source AS g
WHERE g.source_id IN ({values})
"""