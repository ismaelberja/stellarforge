"""Conservative, one-to-one g/r photometric diagnostics.

Two OIDs must have already been separately investigated. This code never
asserts that the selected ZTF objects identify the same Gaia source.
"""
from dataclasses import dataclass, asdict
from math import sqrt, isfinite
from statistics import median

@dataclass(frozen=True)
class PhotometricEpoch:
    oid: str
    band: str
    mjd: float
    mag: float
    magerr: float
    catflags: int = 0

def pair_g_r(epochs: list[PhotometricEpoch], *, oid_g: str, oid_r: str, max_delay_days: float = 0.5) -> dict:
    if not oid_g or not oid_r or oid_g == oid_r:
        raise ValueError("Two distinct OIDs are required")
    if not isfinite(max_delay_days) or not 0 < max_delay_days <= 2:
        raise ValueError("Choose a pairing interval in (0,2] days")
    chosen = [p for p in epochs if p.oid in {oid_g, oid_r}]
    for p in chosen:
        if ((p.oid == oid_g and p.band != "g") or (p.oid == oid_r and p.band != "r")):
            raise ValueError("OID / band conflict")
        if not all(isfinite(v) for v in (p.mjd,p.mag,p.magerr)) or p.magerr <= 0:
            raise ValueError("Invalid photometry")
        if p.catflags & 32768:
            raise ValueError("Quality filtering must precede pairing")
    g = sorted([p for p in chosen if p.oid == oid_g], key=lambda p: p.mjd)
    r = sorted([p for p in chosen if p.oid == oid_r], key=lambda p: p.mjd)
    candidates = sorted((abs(a.mjd-b.mjd), i, j) for i,a in enumerate(g)
                        for j,b in enumerate(r) if abs(a.mjd-b.mjd) <= max_delay_days)
    used_g, used_r, pairs = set(), set(), []
    for dt,i,j in candidates:
        if i in used_g or j in used_r: continue
        used_g.add(i);used_r.add(j)
        a,b=g[i],r[j]
        pairs.append({"g_mjd":a.mjd,"r_mjd":b.mjd,"time_delay_days":dt,
                      "color_g_minus_r_mag":a.mag-b.mag,
                      "color_uncertainty_mag":sqrt(a.magerr**2+b.magerr**2)})
    pairs.sort(key=lambda x:(x["g_mjd"],x["r_mjd"]))
    return {
        "status":"PROVISIONAL_NON_SIMULTANEOUS_COLOR",
        "explicit_g_oid":oid_g,"explicit_r_oid":oid_r,
        "epochs_g":len(g),"epochs_r":len(r),"paired_epochs":len(pairs),
        "median_color":median(x["color_g_minus_r_mag"] for x in pairs) if pairs else None,
        "pairs":pairs,
        "gaia_ztf_source_identity_verified":False,
        "extinction_or_accretion_inferred":False,
    }
