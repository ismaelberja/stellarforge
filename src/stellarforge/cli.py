"""Small, offline-first command-line interface for first research phase."""
import argparse
from pathlib import Path
from .gaia import gaia_cone_adql, gaia_datalink_instructions
from .catalog import read_membership, write_audit
from .pilot import propose_pilot, write_pilot
from .gaia_batch import exact_ids_query
from .ztf import build_ztf_url, fetch_ztf_raw
from .ztf_photometry import audit_ztf_file
from .variability import analyze_normalized_file
from .events import screen_normalized_file
from .batch import run_batch
from .luhman2023 import download_pinned_mirror, validate_technical_seed, parse_membership_mrt, audit_seed_against_full_mrt


def main(argv=None):
    parser = argparse.ArgumentParser(description="StellarForge — Taurus / ZTF research pipeline (v0.9)")
    sub = parser.add_subparsers(dest="command", required=True)
    gaia = sub.add_parser("plan-gaia", help="Print ADQL technical query, no remote access")
    gaia.add_argument("--ra", type=float, required=True)
    gaia.add_argument("--dec", type=float, required=True)
    gaia.add_argument("--radius-deg", type=float, default=0.1)
    gaia.add_argument("--max-rows", type=int, default=100)

    ztf = sub.add_parser("plan-ztf", help="Print IRSA API URL, no remote access")
    ztf.add_argument("--ra", type=float, required=True)
    ztf.add_argument("--dec", type=float, required=True)
    ztf.add_argument("--radius-arcsec", type=float, default=2.0)
    ztf.add_argument("--bands", nargs="+", choices=["g", "r", "i"], default=["g", "r"])

    fetch = sub.add_parser("fetch-ztf", help="Fetch one vetted target and save provenance")
    fetch.add_argument("--ra", type=float, required=True)
    fetch.add_argument("--dec", type=float, required=True)
    fetch.add_argument("--radius-arcsec", type=float, default=2.0)
    fetch.add_argument("--output", type=Path, required=True)

    cat = sub.add_parser("audit-members", help="Audit a verified-membership CSV and write source provenance")
    cat.add_argument("--input", type=Path, required=True)
    cat.add_argument("--reference-url", required=True)
    cat.add_argument("--output", type=Path, default=Path("reports/membership_audit.json"))

    pilot = sub.add_parser("propose-pilot", help="Prepare a balanced provisional II/III sample")
    pilot.add_argument("--input", type=Path, required=True)
    pilot.add_argument("--output", type=Path, default=Path("reports/pilot_proposal.json"))
    pilot.add_argument("--catalog-verified", action="store_true", help="Only set following independent review of exact paper Table 2")

    inspect = sub.add_parser("inspect-ztf", help="Audit saved IRSA CSV/IPAC light curves without claiming a scientific match")
    inspect.add_argument("--input", type=Path, required=True)
    inspect.add_argument("--output", type=Path, default=Path("reports/generated/ztf_audit"))
    inspect.add_argument("--target-ra", type=float)
    inspect.add_argument("--target-dec", type=float)
    inspect.add_argument("--radius-arcsec", type=float, default=2.0)
    inspect.add_argument("--min-good-epochs", type=int, default=30)
    inspect.add_argument("--mask", type=int, default=32768)

    luhman = sub.add_parser("fetch-luhman-2023", help="Fetch pinned 532-row machine-readable Luhman table + provenance")
    luhman.add_argument("--output", type=Path, default=Path("data/raw/luhman_2023_taurus_table2_mrt.txt"))

    seed = sub.add_parser("audit-technical-seed", help="Audit 24 real catalog rows; no disk-class claims")
    seed.add_argument("--input", type=Path, default=Path("data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"))
    seed.add_argument("--full-mrt", type=Path, help="Optional pinned catalog for row-by-row comparison")

    variability = sub.add_parser("analyze-ztf", help="Exploratory variability features + provisional period, never auto-classifies")
    variability.add_argument("--input", type=Path, required=True, help="Normalized QC accepted CSV output of inspect-ztf")
    variability.add_argument("--output", type=Path, default=Path("reports/generated/variability.json"))
    variability.add_argument("--min-good-epochs", type=int, default=30)
    variability.add_argument("--min-period", type=float, default=0.5)
    variability.add_argument("--max-period", type=float, default=30.0)
    variability.add_argument("--permutations", type=int, default=0)

    event = sub.add_parser("screen-events", help="Exploratory dip/brightening event screen on a QC-normalized file")
    event.add_argument("--input", type=Path, required=True)
    event.add_argument("--output", type=Path, default=Path("reports/generated/event_candidates.json"))
    event.add_argument("--min-epochs", type=int, default=30)

    pilot_batch = sub.add_parser("batch-ztf", help="Plan/retry ZTF pilot. Dry-run unless --execute")
    pilot_batch.add_argument("--seed", type=Path, default=Path("data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv"))
    pilot_batch.add_argument("--output", type=Path, default=Path("reports/generated/ztf_batch"))
    pilot_batch.add_argument("--max-targets", type=int, default=24)
    pilot_batch.add_argument("--radius-arcsec", type=float, default=2.)
    pilot_batch.add_argument("--execute", action="store_true", help="Explicitly authorize real network queries; no cross-match inferred")

    batch = sub.add_parser("plan-gaia-batch", help="Print exact-Gaia-ID ADQL from a membership file")
    batch.add_argument("--input", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.command == "plan-gaia":
        print(gaia_cone_adql(args.ra, args.dec, args.radius_deg, args.max_rows))
        print("\n" + gaia_datalink_instructions())
    elif args.command == "plan-ztf":
        print(build_ztf_url(args.ra, args.dec, args.radius_arcsec, tuple(args.bands)))
    elif args.command == "audit-members":
        records = read_membership(args.input)
        result = write_audit(args.input, records, reference_url=args.reference_url, output=args.output)
        print(f"Adopted Taurus records in supplied file: {result['adopted_member_rows']}")
        print(f"Published reference: {result['published_adopted_member_count']}; verified count match: {result['matches_published_count']}")
        print(f"Full audit written to {args.output}")
    elif args.command == "propose-pilot":
        proposal = propose_pilot(read_membership(args.input), catalog_verified=args.catalog_verified)
        write_pilot(args.output, proposal)
        print(f"Status: {proposal['status']}; targets proposed: {len(proposal['targets'])}")
        print(f"Science gate passed: {proposal['may_start_observational_ingestion']}")
    elif args.command == "inspect-ztf":
        result = audit_ztf_file(args.input, args.output, target_ra=args.target_ra,
                                target_dec=args.target_dec, radius_arcsec=args.radius_arcsec,
                                min_good_epochs=args.min_good_epochs, mask=args.mask)
        print(f"Raw points: {result['raw_rows']}, QC-accepted: {result['kept_rows']}, "
              f"separate curves: {result.get('curve_count', 0)}")
        print("Unverified association: researcher must confirm target identity and astrometry")
    elif args.command == "fetch-luhman-2023":
        audit = download_pinned_mirror(args.output)
        print(f"MRT verified (third-party pinned mirror): {audit['record_count']} rows, "
              f"{audit['with_gaia_dr3_source_id']} Gaia IDs")
        print(f"Source stored at: {args.output}; published-byte comparison still pending")
    elif args.command == "audit-technical-seed":
        audit = (audit_seed_against_full_mrt(args.full_mrt.read_bytes(), args.input)
                 if args.full_mrt else validate_technical_seed(args.input))
        print(f"Technical coordinate seed: {audit['rows']} Taurus members in "
              f"{audit['named_groups']} groups; NOT scientific pilot")
        print("Source copy is from public pinned mirror; publisher-byte crosscheck pending")
    elif args.command == "analyze-ztf":
        diagnostics = analyze_normalized_file(args.input, args.output,
            min_good_epochs=args.min_good_epochs, min_period=args.min_period,
            max_period=args.max_period, permutations=args.permutations)
        print(f"Exploratory diagnostics: {diagnostics['n_curves']} separate ZTF curves; NO physical classifications")
        print(f"Output: {args.output}")
    elif args.command == "screen-events":
        outcome = screen_normalized_file(args.input, args.output, min_epochs=args.min_epochs)
        print(f"Screened {outcome['n_curves']} separate curves. Event candidates are NOT physical detections.")
        print(f"Output: {args.output}")
    elif args.command == "batch-ztf":
        outcome = run_batch(args.seed, args.output, execute=args.execute,
                            radius_arcsec=args.radius_arcsec, max_targets=args.max_targets)
        print(f"Mode: {outcome['mode']}; targets: {outcome['n_targets_in_batch']}; status: {outcome['counts']}")
        print("All source associations require proper-motion and multi-source review.")

    elif args.command == "plan-gaia-batch":
        print(exact_ids_query(read_membership(args.input)))
    else:
        url = build_ztf_url(args.ra, args.dec, args.radius_arcsec)
        manifest = fetch_ztf_raw(url, args.output)
        print("Downloaded RAW response; not yet scientifically validated.")
        print(f"Source SHA256: {manifest['sha256']}")


if __name__ == "__main__":
    main()