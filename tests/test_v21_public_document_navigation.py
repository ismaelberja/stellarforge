"""v2.1 public README/Spanish/English portfolio navigation links stay local.

No HTTP calls, hidden source downloads or reliance on third-party asset hosts.
External literature/repository URLs are documentary references only.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

import pytest

ROOT=Path(__file__).resolve().parents[1]
PUBLISHED_DOCS=(
    "README.md","EMPEZAR_AQUI.md","RELEASE_NOTES_v2.1.md",
    "docs/V21_GUIA_ES.md","docs/V21_PORTFOLIO_CV_ES_EN.md",
    "docs/V21_REPRODUCIBILITY_AND_SCIENCE_LIMITS.md",
    "docs/V21_VISUAL_EVIDENCE.md",
    "docs/V21_RELEASE_ACCEPTANCE_PLAN.md",
)
LINK=re.compile(r"!?\[[^\]\n]*\]\(([^)\s]+)(?:\s[^)]*)?\)")


@pytest.mark.parametrize("source",PUBLISHED_DOCS)
def test_current_portfolio_markdown_navigation_is_not_broken(source):
    markdown=ROOT/source
    body=markdown.read_text(encoding="utf-8")
    assert len(body)>=200 and "[" in body
    n_resolved=0
    for match in LINK.finditer(body):
        address=match.group(1)
        if address.startswith(("https://","http://","mailto:","tel:","#")):
            continue
        assert not address.startswith(("javascript:","file:","data:"))
        local=unquote(address.split("#")[0].split("?")[0])
        assert local, f"Empty local link in {source}"
        path=(markdown.parent/local).resolve()
        assert path.is_relative_to(ROOT), f"Path traversal in {source}: {address}"
        assert path.is_file(), f"Broken local source/visual link in {source}: {address}"
        n_resolved+=1
    assert n_resolved>=1, f"Current v2.1 document has no local project evidence links: {source}"


def test_quantitative_chart_and_old_banners_are_separate_visual_evidence():
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    assert "docs/figures/fttau-six-original-native-spatial-psf-quality-v21.svg" in readme
    assert "docs/figures/taurus-gaia-coverage.svg" in readme
    assert "docs/figures/ztf-original-psf-quality.svg" in readme
    assert "docs/figures/stellarforge-conceptual-hero.webp" in readme
    assert "docs/figures/stellarforge-conceptual-atlas.webp" in readme
    assert "AI-generated" in readme
    assert "not actual telescope photographs" in readme
    assert "not companion detections" in readme
