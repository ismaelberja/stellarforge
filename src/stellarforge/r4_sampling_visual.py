"""Accessible source-only SVG of real R3 original ZTF annual-bin coverage.

No imaginary simulated times or window powers are plotted here.
The synthetic cadence examples live ONLY in the distinct method report.
"""
from __future__ import annotations

from html import escape


def original_zft_r4_coverage_svg(report:dict)->str:
    if (report.get("real_original_ztf_OIDs_with_QC_annual_bins") != 3
            or report.get("original_ztf_OIDs_with_unavailable_server_responses") != 3
            or not isinstance(report.get("source_observations"),list)
            or len(report["source_observations"])!=6):
        raise ValueError("SVG must show original three real source curves and three archival failures")
    x0=335
    cellw=73
    gap=5
    pitch=cellw+gap
    lines=[
        '<svg xmlns="http://www.w3.org/2000/svg" width="1030" height="660" '
        'viewBox="0 0 1030 660" role="img" aria-labelledby="r4title r4desc">',
        '<title id="r4title">Original ZTF DR24 relative 365-day cadence coverage for three survey ObjectIDs; other three archive requests timed out twice</title>',
        '<desc id="r4desc">Original data-derived source-only figure. First three ZTF ObjectIDs returned 70, 117 and 404 quality-accepted visits. Their individual 365-day bins are anchored to each separate source first accepted epoch, so columns are NOT common calendar dates. Two exact OIDs have two consecutive genuinely empty within-span bins. Missing beyond a source span is NOT zero. Three other ObjectIDs timed out twice and have UNKNOWN coverage. The figure does not show real visit timestamps, a real spectral window, a physical Gaia source match, photometric light curves or astronomical variability.</desc>',
        '<rect width="1030" height="660" rx="14" fill="#fff"/>',
        '<rect width="1030" height="5" fill="#146A83"/>',
        '<text x="30" y="47" font-family="Arial, sans-serif" font-size="25" font-weight="700" fill="#19334E">Taurus R4 · original ZTF time coverage</text>',
        '<text x="30" y="75" font-family="Arial, sans-serif" font-size="15" fill="#556982">Quality-accepted visits per 365-day bin · each ObjectID has its own start date</text>',
        '<rect x="30" y="92" width="368" height="30" rx="6" fill="#E4F2F8"/>',
        '<text x="43" y="112" font-family="Arial, sans-serif" font-size="14" font-weight="600" fill="#14516E">591 accepted visits · 3 genuine ZTF OIDs</text>',
        '<rect x="410" y="92" width="330" height="30" rx="6" fill="#FFF0E5"/>',
        '<text x="423" y="112" font-family="Arial, sans-serif" font-size="14" font-weight="600" fill="#81521D">3 other OIDs: archive timeouts (UNKNOWN)</text>',
    ]
    for i in range(8):
        lines.append(f'<text x="{x0+i*pitch+cellw/2:.1f}" y="150" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#64768A">Bin {i+1}</text>')
    for i,r in enumerate(report["source_observations"]):
        oid=escape(str(r["original_ztf_oid"]))
        band=escape(str(r["original_ztf_filter"]))
        y=166+i*59
        lines.append(f'<text x="30" y="{y+22}" font-family="monospace" font-size="15" font-weight="600" fill="#18344F">{oid}  ({band})</text>')
        if r["cadence_metric_computable"]:
            counts=r["original_relative_365day_bins_anchored_at_first_QC_epoch"]
            n=r["technical_source_qc_accepted_epochs"]
            lines.append(f'<text x="30" y="{y+43}" font-family="Arial, sans-serif" font-size="12" fill="#617286">{n} genuine QC visits · native MJD</text>')
            for j in range(8):
                cx=x0+j*pitch
                if j>=len(counts):
                    lines.append(f'<g data-oid="{oid}" data-bin="{j+1}" data-state="OUTSIDE_SOURCE_SPAN">'
                                 f'<rect x="{cx}" y="{y}" width="{cellw}" height="46" rx="5" fill="#E8EDF2"/>'
                                 f'<text x="{cx+cellw/2:.1f}" y="{y+29}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#8A97A5">—</text></g>')
                else:
                    nbin=counts[j]
                    bg=("#FFFFFF" if nbin==0 else
                        "#D9F0EA" if nbin<20 else
                        "#ABDCCC" if nbin<50 else
                        "#69BDAF" if nbin<80 else "#268D83")
                    fg="#805C4B" if nbin==0 else "#163F3D"
                    lines.append(f'<g data-oid="{oid}" data-bin="{j+1}" data-count="{nbin}">'
                                 f'<rect x="{cx}" y="{y}" width="{cellw}" height="46" rx="5" fill="{bg}" stroke="#D0DAE1"/>'
                                 f'<text x="{cx+cellw/2:.1f}" y="{y+29}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="600" font-size="18" fill="{fg}">{nbin}</text></g>')
        else:
            lines.append(f'<g data-oid="{oid}" data-state="ARCHIVE_TIMEOUT_UNKNOWN">'
                         f'<rect x="{x0}" y="{y}" width="{8*pitch-gap}" height="46" rx="6" fill="#F6EBE5" stroke="#D9C3B0"/>'
                         f'<text x="{x0+14}" y="{y+28}" font-family="Arial, sans-serif" font-size="15" fill="#85552F">Not retrieved · timed out twice · unknown, not 0 visits</text></g>')
    lines.extend([
        '<rect x="29" y="533" width="971" height="100" rx="8" fill="#F3F6F9"/>',
        '<text x="43" y="555" font-family="Arial, sans-serif" font-size="13" fill="#405A72">Green cells: authentic QC-retained ZTF counts in a source-relative 365-day bin.</text>',
        '<text x="43" y="574" font-family="Arial, sans-serif" font-size="13" fill="#405A72">0 = genuine within-span empty bin; — = beyond source recorded span; beige = archive timeout, not a detection limit.</text>',
        '<text x="43" y="594" font-family="Arial, sans-serif" font-size="13" font-weight="600" fill="#6C5265">These are NOT synchronized calendar bins, actual visit times, measured periodograms, or Gaia-matched stellar light curves.</text>',
        '<text x="43" y="614" font-family="Arial, sans-serif" font-size="12" fill="#556982">Source: original DR24 Actions 43593335135 + 43593994009; SHA-anchored R3 no-raw derived receipts.</text>',
        '</svg>'
    ])
    return "\n".join(lines)+"\n"
