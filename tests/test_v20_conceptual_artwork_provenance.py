"""Documentation-only QA for two generated StellarForge banner illustrations.

An artwork must not masquerade as a real ZTF/FITS image or PSF fit.
No network calls and no original survey pixels are used.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTWORKS = {
    "stellarforge-conceptual-hero.webp":
        "6de019a05810f647e12bc8db375f5d48cfdceaef993a940bf5a1e341cf301545",
    "stellarforge-conceptual-atlas.webp":
        "eb94ccb0407a7fe85cea9be437fe058a679666db0ea039df98a60104b8f45e35",
}


def test_documentation_illustrations_are_real_local_bounded_webps():
    for name, digest in ARTWORKS.items():
        item = ROOT / "docs/figures" / name
        payload = item.read_bytes()
        assert 40_000 < len(payload) < 150_000
        assert payload[:4] == b"RIFF"
        assert payload[8:12] == b"WEBP"
        assert hashlib.sha256(payload).hexdigest() == digest


def test_readme_distinguishes_ai_illustrations_from_real_ztf_data():
    readme = (ROOT / "README.md").read_text(encoding="utf8")
    for name in ARTWORKS:
        assert f"docs/figures/{name}" in readme
    assert "AI-generated" in readme
    assert "not actual telescope photographs" in readme
    assert "fictional graphics, not authentic measurements" in readme
    assert "reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md" in readme
    assert "docs/figures/taurus-gaia-coverage.svg" in readme
    assert "docs/figures/ztf-original-psf-quality.svg" in readme
    assert "532" in readme and "467" in readme
    assert "16" in readme and "13" in readme and "3" in readme


def test_illustration_provenance_documented_without_science_overclaim():
    method = (ROOT / "docs/V2_VISUAL_EVIDENCE.md").read_text(encoding="utf8")
    guide = (ROOT / "docs/V2_GUIA_ES.md").read_text(encoding="utf8")
    assert "NOT survey photographs" in method
    assert "not measured quantities" in method
    assert "original FITS" in method
    assert "No son fotografías" in guide
    assert "gráficos científicos auténticos" in guide.lower()
