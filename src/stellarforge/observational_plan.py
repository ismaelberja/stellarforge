"""Pre-registered two-target real-catalog, unexecuted ZTF acquisition plan.

The data are real Luhman (2023) coordinates in a pinned third-party mirror;
this script neither downloads ZTF lightcurves nor verifies a ZTF counterpart.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Sequence

from .association import propagate_gaia_position
from .luhman2023 import MIRROR_BLOB_SHA1, validate_technical_seed
from .ztf import build_ztf_url

FIRST_TARGETS = ("FT Tau", "CIDA 11")


def make_pilot_plan(seed_path: Path, targets: Sequence[str] = FIRST_TARGETS,
                    *, radius_arcsec: float = 2.0,
                    illustrative_epoch_year: float = 2021.0) -> dict:
    """Describe a 2-object pilot, selection and cross-matching limitations."""
    audit = validate_technical_seed(seed_path)
    if not targets or len(targets) > 5 or len(set(targets)) != len(targets):
        raise ValueError("Pilot must specify 1..5 distinct real-catalog object names")
    if not 0 < radius_arcsec <= 10:
        raise ValueError("Choose a query radius in (0,10] arcsec")
    with Path(seed_path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    indexed = {r["name"]: r for r in rows if r["name"]}
    plans=[]
    for name in targets:
        if name not in indexed:
            raise ValueError(f"Target name is not in verified seed: {name}")
        r = indexed[name]
        if r.get("reference") != "Gaia":
            raise ValueError("Target position reference is not Gaia")
        ra,dec,pmra,pmdec = (float(r[v]) for v in ("ra","dec","pmra","pmdec"))
        propagated=propagate_gaia_position(ra,dec,pmra,pmdec,illustrative_epoch_year)
        plans.append({
            "catalog_name": name,
            "gaia_dr3_source_id": r["gaia"],
            "two_mass_id": r.get("mass", ""),
            "kinematic_group": r["group"],
            "gmag": float(r["gmag"]),
            "catalog_ra_deg": ra,
            "catalog_dec_deg": dec,
            "pmra_star_mas_per_year":pmra,
            "pmdec_mas_per_year":pmdec,
            "illustrative_epoch_julian_year":illustrative_epoch_year,
            "illustrative_propagated_ra_deg":propagated[0],
            "illustrative_propagated_dec_deg":propagated[1],
            "ztf_api_query_url":build_ztf_url(ra,dec,radius_arcsec=radius_arcsec,
                                             bands=("g","r"),output_format="csv"),
            "source_publisher_independently_compared":False,
            "ztf_query_performed":False,
            "ztf_coverage_confirmed":False,
            "ztf_source_association_confirmed":False,
            "irsa_observations_received":0,
            "disk_class_known_from_independent_source":False,
            "actual_ztf_observation_epochs_known":False,
            "requires_source_image_review":True,
        })
    return {
        "version":"0.7",
        "status":"PRE_REGISTERED_CATALOG_PILOT_UNEXECUTED",
        "catalogue":"Luhman (2023) Taurus adopted members, Table 2",
        "doi":"10.3847/1538-3881/ac9da3",
        "mirror_git_blob_sha1":MIRROR_BLOB_SHA1,
        "seed_sha256":hashlib.sha256(Path(seed_path).read_bytes()).hexdigest(),
        "seed_audit":audit,
        "selection_rule":"Named FT Tau and CIDA 11 from different groups, Gaia positions, moderate G mag; technical access pilot, not a representative science sample",
        "query_radius_arcsec":radius_arcsec,
        "epoch_note":"2021.0 is a nominal engineering example, not actual IRSA exposure epochs",
        "pilot_targets":plans,
        "required_scientific_gates":[
            "Check original publisher Table 2 against pinned mirror",
            "Make official IRSA request and retain raw bytes + URL + SHA-256",
            "Verify photometric flags/identity of separate ZTF OIDs in g/r",
            "Propagate Gaia coordinates to actual ZTF epochs and inspect images for crowding",
            "Construct independently vetted same-field, same-exposure control stars",
            "Fit variability and perform injection/recovery using the actual time sampling",
            "Only then consider physical dipper or burster interpretations",
        ],
        "new_observational_claims":0,
    }


def save_pilot_plan(path: Path, plan: dict) -> None:
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.partial')
    tmp.write_text(json.dumps(plan,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    tmp.replace(path)