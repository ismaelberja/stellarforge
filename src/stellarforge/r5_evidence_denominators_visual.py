"""Plot original R2–R4 denominators in three expressly non-comparable panels.

Never draw a fictitious six-ObjectID-to-24-Gaia-star-to-684-epoch funnel.
Only real source access / original quality bit15 counts appear; zero
physical source authentication is an evidence gate, not a null variable.
"""
from __future__ import annotations
from html import escape


def r5_independent_denominator_svg(report:dict)->str:
    observed=report["denominator_locked_descriptive_summary_not_population_inference"]
    groups=[
        (
            "24 frozen Gaia source IDs",
            "denominator: Gaia TECHNICAL TARGETS (not parent census)",
            "24 ≠ random Taurus star sample",
            24,
            [
                ("Published Gaia IDs",24,"24/24 original Luhman table"),
                ("Gaia preliminary QC",17,"17/24"),
                ("Gaia astrometry review",7,"7/24"),
                ("ZTF cone results",22,"22/24 positional response; NOT identities"),
                ("Physical ZTF matches",0,"0/24 source identification certified"),
            ]
        ),
        (
            "6 fixed ZTF survey ObjectIDs",
            "denominator: SURVEY LABELS (not 6 independent stars)",
            "FT Tau/CIDA 11 original working-label contexts",
            6,
            [
                ("Fixed ZTF ObjectIDs",6,"6/6 preregistered from R2"),
                ("IRSA exact-ID CSV",3,"3/6 real original DR24 CSVs"),
                ("Archive timeouts",3,"3/6 no response after fixed retry"),
                ("Gaia counterparts",0,"0/6 physically authenticated"),
            ],
        ),
        (
            "684 original ZTF epoch rows",
            "denominator: INDIVIDUAL SURVEY MEASUREMENTS",
            "3 returned exact-ObjectID CSVs · bit15 screen only",
            684,
            [
                ("Original photometry",684,"684/684 original queried rows"),
                ("Bit15 accepted",591,"591/684 probably usable"),
                ("Bit15 flagged",93,"93/684 masked, not a stellar rate"),
            ]
        ),
    ]
    expected={
        "gaia_physically_identified_with_ZTF_of_original_24":(0,24),
        "gaia_positions_with_any_original_ZTF_positional_rows_of_original_24":(22,24),
        "gaia_only_preliminary_quality_pass_of_original_24":(17,24),
        "gaia_astrometry_requires_review_of_original_24":(7,24),
        "original_ZTF_exact_oid_dr24_source_csvs_returned_of_six_fixed_oids":(3,6),
        "original_ZTF_exact_oid_server_timeouts_twice_of_six_fixed_oids":(3,6),
        "original_ztf_catflags_bit15_retained_source_rows_of_684":(591,684),
        "original_ztf_catflags_bit15_rejected_source_rows_of_684":(93,684),
    }
    for key,(n,N) in expected.items():
        x=observed[key]
        if x.get("n")!=n or x.get("N")!=N:
            raise ValueError(f"Real figure original source numerators changed: {key}")
    out=[
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="800" viewBox="0 0 1100 800" role="img" aria-labelledby="r5Title r5Desc">',
        '<title id="r5Title">Taurus R5 observed data: three non-interchangeable denominators for Gaia targets, ZTF survey ObjectIDs and original per-epoch lightcurve rows</title>',
        '<desc id="r5Desc">Separate non-funnel panels. Gaia: 24 technical literature source IDs, 17 preliminary astrometry passes, seven reviews, 22 positional ZTF response successes but zero authenticated physical crossmatches. ZTF survey objects: six original ObjectIDs, three source CSV successes, three archive timeouts and zero physical Gaia matches. Photometry: 684 original measurement rows from three ZTF source CSVs, 591 accepted using the ZTF bit15 mask, 93 flagged; bit15 masking is not the strict all-flags-zero rule. These numbers are not a representative sample or a stellar variability detection.</desc>',
        '<rect width="1100" height="800" fill="#fff" rx="16"/>',
        '<rect width="1100" height="6" fill="#166B87"/>',
        '<text x="34" y="47" font-family="Arial, sans-serif" font-size="27" font-weight="bold" fill="#19374E">Taurus R5 · independent science gates</text>',
        '<text x="34" y="80" font-family="Arial, sans-serif" font-size="16" fill="#637587">Same evidence, THREE denominators · not a sequential source-survival funnel</text>',
    ]
    # Three independent quantitative cards. The lengths are normalized
    # ONLY *inside their own respective source-population denominator*.
    for i,(title,denominator,subtitle,N,rows) in enumerate(groups):
        x=32+i*359
        out.extend([
            f'<g data-denominator="{N}" data-panel="{i+1}">',
            f'<rect x="{x}" y="112" width="342" height="553" rx="10" fill="#F4F7FA" stroke="#D9E3EA"/>',
            f'<text x="{x+16}" y="148" font-family="Arial, sans-serif" font-size="19" font-weight="bold" fill="#173A50">{escape(title)}</text>',
            f'<text x="{x+16}" y="172" font-family="Arial, sans-serif" font-size="12" fill="#59738C">{escape(denominator)}</text>',
            f'<text x="{x+16}" y="192" font-family="Arial, sans-serif" font-size="11" fill="#59738C">{escape(subtitle)}</text>',
        ])
        for j,(name,n,description) in enumerate(rows):
            y=222+j*80
            width=298*n/N
            fill="#1C8A87" if (i==2 and j==1) or (i!=2 and j==1) else "#5597AE"
            if n==0: fill="#AD5C44"
            if name in ("Gaia astrometry review","Archive timeouts","Bit15 flagged"):fill="#D39B4C"
            out.extend([
                f'<g data-metric="{escape(name)}" data-count="{n}" data-base="{N}">',
                f'<text x="{x+17}" y="{y}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#1D4359">{escape(name)}</text>',
                f'<rect x="{x+17}" y="{y+10}" width="298" height="16" rx="4" fill="#E4EAF0"/>',
                f'<rect x="{x+17}" y="{y+10}" width="{width:.3f}" height="16" rx="4" fill="{fill}"/>',
                f'<text x="{x+315}" y="{y}" font-family="Arial, sans-serif" font-size="13" text-anchor="end" fill="#2E5064">{n}/{N}</text>',
                f'<text x="{x+17}" y="{y+45}" font-family="Arial, sans-serif" font-size="11" fill="#5D7282">{escape(description)}</text>',
                '</g>'
            ])
        out.append('</g>')
    out.extend([
        '<rect x="32" y="685" width="1034" height="91" rx="8" fill="#EAF1F7"/>',
        '<text x="48" y="711" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#42596E">Independent scientific physical ID and instrument calibration: NOT VERIFIED. R5 methodological review: COMPLETE.</text>',
        '<text x="48" y="731" font-family="Arial, sans-serif" font-size="12" fill="#486274">0 authenticated Gaia–ZTF matches means insufficient validation evidence, NOT that the stars are physically non-variable.</text>',
        '<text x="48" y="750" font-family="Arial, sans-serif" font-size="12" fill="#486274">Original sources: Luhman (2023) Table 2; R2 Gaia + IRSA; R3 DR24 first/retry; R4 yearly-binned original source audit.</text>',
        '</svg>'
    ])
    return "\n".join(out)+"\n"
