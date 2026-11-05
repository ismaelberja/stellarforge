"""Reproduce v1.2 ZTF cone-search plots from a PRIVATE GitHub Actions ZIP.

The plots contain actual IRSA-returned raw photometry, NOT independently
authenticated Gaia/ZTF counterparts or physical variability classifications.
No source CSV is copied into the repository or the output directory.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile


def make_plots(artifact_zip: Path, output: Path) -> list[dict]:
    """Verify raw hashes, retain separate OIDs and bands, and plot MJD vs mag."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    results = []
    with ZipFile(artifact_zip) as archive:
        manifest = json.loads(archive.read("PILOT_STATUS.json"))
        for target in manifest["results"]:
            if target.get("acquisition_status") != "RAW_HTTP_RESPONSE_SAVED_ASSOCIATION_UNVERIFIED":
                continue
            gaia_id = target["gaia_dr3_id"]
            raw = archive.read(f"{gaia_id}_IRSA_RAW.csv")
            actual_sha = hashlib.sha256(raw).hexdigest()
            if actual_sha != target["raw_sha256"]:
                raise ValueError(f"Raw SHA-256 mismatch for target {gaia_id}")
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
            required = {"oid", "filtercode", "field", "mjd", "mag", "magerr", "catflags"}
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ValueError(f"Invalid source table columns for {gaia_id}")
            curves = defaultdict(list)
            rejected = 0
            for row in reader:
                if int(row["catflags"]) & 32768:
                    rejected += 1
                    continue
                curve = (row["filtercode"], row["field"], row["oid"])
                if not row["oid"].isdigit() or row["filtercode"] not in {"zg", "zr", "zi"}:
                    raise ValueError("Invalid IRSA curve identifier")
                curves[curve].append((float(row["mjd"]), float(row["mag"])))
            if not curves:
                raise ValueError(f"No usable photometric rows for {gaia_id}")
            fig, ax = plt.subplots(figsize=(12, 6.5))
            for (band, field, oid), points in sorted(curves.items()):
                ax.scatter(
                    [p[0] for p in points], [p[1] for p in points],
                    s=13, alpha=0.7,
                    label=f"{band} / field {field} / oid {oid} (n={len(points)})",
                    linewidths=0,
                )
            ax.set_xlabel("Modified Julian Date (MJD)")
            ax.set_ylabel("ZTF magnitude (raw diagnostic; physical interpretation pending)")
            ax.invert_yaxis()
            ax.grid(alpha=0.2)
            ax.legend(fontsize=8)
            ax.set_title(
                f"ZTF cone-search near {target['target']} — Gaia/ZTF identity UNVERIFIED"
            )
            ax.text(
                .5, -.16,
                "Actual IRSA-returned photometry; OIDs remain separate. "
                "No source identification or event classification.",
                ha="center", va="top", transform=ax.transAxes, fontsize=9,
            )
            fig.tight_layout()
            filename = f"ZTF_POSITION_QUERY_{gaia_id}_UNVERIFIED.png"
            fig.savefig(output / filename, dpi=160, bbox_inches="tight")
            plt.close(fig)
            results.append({
                "target_query": target["target"], "gaia_dr3_id": gaia_id,
                "raw_sha256": actual_sha,
                "n_plotted": sum(len(p) for p in curves.values()),
                "n_masked_catflags_32768": rejected,
                "n_distinct_oid_bands": len(curves),
                "plot": filename,
                "gaia_ztf_identity_verified": False,
                "physical_variability_claimed": False,
            })
    (output / "PRELIMINARY_FIGURE_MANIFEST.json").write_text(
        json.dumps({"results": results, "scientific_status": "UNVERIFIED_CONE_QUERY"},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot privately archived IRSA raw queries")
    parser.add_argument("artifact_zip", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/generated/v1.2_plots"))
    args = parser.parse_args()
    print(json.dumps(make_plots(args.artifact_zip, args.output), indent=2))


if __name__ == "__main__":
    main()
