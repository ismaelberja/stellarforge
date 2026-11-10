"""v2.0 package entrypoint and public no-network help text smoke tests."""
import pytest
from stellarforge import __version__
from stellarforge.cli import main


def test_version_flag_reports_current_release(capsys):
    with pytest.raises(SystemExit) as exit_code:
        main(["--version"])
    assert exit_code.value.code == 0
    assert capsys.readouterr().out.strip() == "StellarForge 2.0.0"
    assert __version__ == "2.0.0"


def test_help_refers_to_current_scientific_software(capsys):
    with pytest.raises(SystemExit) as exit_code:
        main(["--help"])
    assert exit_code.value.code == 0
    out = capsys.readouterr().out
    assert "StellarForge" in out
    assert "v2.0" in out
    assert "plan-gaia" in out
    assert "plan-ztf" in out
    assert "batch-ztf" in out
    assert "v0.9" not in out


def test_offline_gaia_query_plan_does_not_access_archive(capsys):
    main(["plan-gaia", "--ra", "70", "--dec", "20",
          "--radius-deg", "0.1", "--max-rows", "10"])
    out = capsys.readouterr().out
    assert "gaiadr3.gaia_source" in out.lower()
    assert "TOP 10" in out
