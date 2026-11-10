"""Renderability, source reconciliation and safety gates for portfolio SVGs.

Figures are intentionally descriptive aggregates from committed reports
rather than original astronomical FITS source pixels.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG_PATHS = (
    ROOT / "docs/figures/taurus-gaia-coverage.svg",
    ROOT / "docs/figures/ztf-original-psf-quality.svg",
)
SVG = "{http://www.w3.org/2000/svg}"


def test_both_figure_files_are_accessible_safe_self_contained_svg():
    for p in SVG_PATHS:
        source = p.read_text(encoding="utf-8")
        root = ET.fromstring(source)
        assert root.tag == SVG + "svg"
        assert root.attrib.get("role") == "img"
        assert root.find(SVG + "title") is not None
        assert len(root.find(SVG + "title").text) > 30
        assert root.find(SVG + "desc") is not None
        assert len(root.find(SVG + "desc").text) > 100
        assert not root.findall(".//" + SVG + "script")
        assert not root.findall(".//" + SVG + "image")
        assert not re.search(r"https?://", source.replace(
            "http://www.w3.org/2000/svg", ""))
        assert "Source:" in source
        assert any(
            "NOT" in x or "Not" in x or "No confirmed" in x
            for x in (source, root.find(SVG + "desc").text)
        )


def test_gaia_figure_reconciles_to_source_mirror_report():
    report = (ROOT / "reports/selection_bias_v1.1/REPORT.md").read_text(
        encoding="utf-8")
    chart = SVG_PATHS[0].read_text(encoding="utf-8")
    assert "**Members:** 532 adopted" in report
    assert "**Gaia IDs:** 467" in report
    assert "no Gaia ID: 65" in report
    assert "**Gaia coverage:** 87.8%" in report
    assert 467 + 65 == 532
    assert ">532<" in chart
    assert ">467<" in chart
    assert ">65<" in chart
    assert "87.8% with Gaia ID" in chart


def test_real_image_figures_match_four_observational_epochs():
    report = (ROOT / "reports/masked_spatial_psf_v1.16/"
              "REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md").read_text(
                  encoding="utf-8")
    figure = SVG_PATHS[1].read_text(encoding="utf-8")
    rows = [
        ("FT Tau", "58388.389016", 2, 2, 0),
        ("FT Tau", "58491.184780", 4, 3, 1),
        ("CIDA 11", "58475.113750", 5, 5, 0),
        ("CIDA 11", "58849.135984", 5, 3, 2),
    ]
    for source, mjd, count, passed, review in rows:
        assert re.search(
            rf"\| {re.escape(source)} \| {re.escape(mjd)} \| "
            rf"{count} \| {passed} \|", report
        )
        assert f"MJD {mjd}" in figure
        assert f">{count} fits<" in figure
        assert count == passed + review
    assert sum(row[2] for row in rows) == 16
    assert sum(row[3] for row in rows) == 13
    assert sum(row[4] for row in rows) == 3
    assert "13 / 16 provisional quality passes" in figure
    assert "NOT independent held-out stars" in figure
    assert "No confirmed Gaia" in figure


def test_readme_displays_both_original_source_figures_and_no_overclaim():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert chr(96)*3 + "mermaid" in readme
    for p in SVG_PATHS:
        assert p.exists()
        assert p.relative_to(ROOT).as_posix() in readme
    assert "not independent new-star empirical PSF validation" in readme
    assert "not companion detections" in readme
    assert "reports/selection_bias_v1.1/REPORT.md" in readme
    assert "reports/masked_spatial_psf_v1.16/REAL_ZTF_PIXEL_RESIDUALS_EVIDENCE.md" in readme
