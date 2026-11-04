"""Reproduce observationally informed *catalogue* bias plot (no lightcurve claims)."""
from __future__ import annotations
from pathlib import Path
import json
from stellarforge.selection_bias import audit_seed_selection

ROOT = Path(__file__).resolve().parents[1]


def main() -> dict:
    x = audit_seed_selection(ROOT/'data/research_seed/TAURUS_24_PROVISIONAL_GAIA_POSITIONS.csv')
    out = ROOT/'reports/selection_bias_v1.1'
    out.mkdir(parents=True, exist_ok=True)
    (out/'MIRROR_SELECTION_AUDIT.json').write_text(json.dumps(x, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    lines = [
       '# StellarForge v1.1 — Taurus selection-bias audit', '',
       '> **Science-status boundary:** Figures originate from the pinned public **mirror** of Luhman (2023) Table 2. Publisher-original byte comparison remains pending. This is not a ZTF light-curve analysis.', '',
       f'- **Members:** {x["total_members"]} adopted; **Gaia IDs:** {x["with_gaia_id"]}; no Gaia ID: {x["without_gaia_id"]}.',
       f'- **Gaia coverage:** {x["gaia_fraction"]:.1%} (descriptive Wilson interval: {x["gaia_fraction_wilson95"][0]:.1%}–{x["gaia_fraction_wilson95"][1]:.1%}).',
       f'- **Key bias:** {x["gaia_missing_without_group"]}/{x["without_gaia_id"]} Gaia-missing sources lack a named group in this copy. Missing group is NOT evidence of non-membership.',
       f'- **Eligibility restriction:** 12≤G≤17 and Gaia ID identifies {x["g12_17_gaia_total"]} sources, of which {x["g12_17_gaia_with_named_group"]} have a named kinematic group.',
       f'- **Pilot:** {x["seed_members"]} objects, deliberately distributed over {x["seed_group_coverage"]} groups; {x["fraction_of_total_catalog_in_seed"]:.1%} of the complete catalog.',
       '- **Disk classes verified:** 0. **Verified Taurus ZTF curves:** 0. No scientific variable/non-variable labeling is justified.', '',
       '## Group-level sampling / Gaia coverage','',
       '| Group | Adopted | Gaia ID | Gaia 12≤G≤17 | Pilot objects | Pilot / eligible |',
       '|---|---:|---:|---:|---:|---:|',
    ]
    for q in sorted(x['group_table'],key=lambda t:t['group']):
       frac = (f'{q["fraction_of_eligible_pool_selected"]:.1%}'
               if q['fraction_of_eligible_pool_selected'] is not None else 'n/a')
       lines.append(f'| {q["group"]} | {q["catalog_members"]} | {q["with_gaia_id"]} | {q["gaia_g12_17"]} | {q["technical_seed_selected"]} | {frac} |')
    lines.extend(['', 'The 24-source seed should **not** be used to estimate a regional event rate.',
                  'Systematic Gaia availability, brightness, crowding, disk classifications and ZTF time coverage need explicit inclusion criteria before inference.',
                  '', '### Provenance', '',
                  f'- Third-party mirror git blob SHA-1: `{x["underlying_catalog_git_blob_sha1"]}`',
                  '- Primary paper: Luhman (2023), AJ 165 37, DOI 10.3847/1538-3881/ac9da3.',
                  '- No original-publisher-byte verification, no photometric claims.', ''])
    (out/'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    try:
        import matplotlib.pyplot as plt
        rows=sorted((t for t in x['group_table'] if t['group']!='unassigned'),
                    key=lambda t:t['catalog_members'])
        y=list(range(len(rows)))
        fig,ax=plt.subplots(figsize=(11,7))
        ax.barh([v-.2 for v in y],[t['catalog_members'] for t in rows],height=.38,alpha=.8,label='All adopted catalogue members')
        ax.barh([v+.2 for v in y],[t['technical_seed_selected'] for t in rows],height=.38,label='24-source technical pilot')
        ax.set_yticks(y,labels=[t['group'] for t in rows]);ax.set_xlabel('Sources per kinematic group')
        ax.set_title('Taurus technical seed: not representative of group sizes')
        ax.legend(loc='lower right');ax.grid(alpha=.15,axis='x')
        fig.tight_layout();fig.savefig(out/'TAURUS_GROUP_SELECTION_REAL_CATALOG.png',dpi=180)
        plt.close(fig)
        fig,ax=plt.subplots(figsize=(8,4.8))
        tick=['Gaia ID','No Gaia ID']
        xx=[x['with_gaia_id'],x['without_gaia_id']]
        ax.bar(tick,xx);ax.set_ylim(0,560);ax.set_ylabel('Adopted Taurus members')
        for i,n in enumerate(xx):ax.text(i,n+9,str(n),ha='center',weight='bold')
        ax.set_title('Gaia availability in the pinned Luhman (2023) mirror')
        fig.tight_layout();fig.savefig(out/'TAURUS_GAIA_ID_AVAILABILITY_REAL_CATALOG.png',dpi=180)
        plt.close(fig)
    except ImportError:
        pass
    return x

if __name__=='__main__':
    report=main()
    print(json.dumps({k:report[k] for k in ('total_members','with_gaia_id','gaia_missing_without_group','seed_members','seed_group_coverage')},indent=2))