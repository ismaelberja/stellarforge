import pytest
from stellarforge.gaia import gaia_cone_adql, gaia_datalink_instructions


def test_adql_metadata_and_limits():
    query = gaia_cone_adql(65, 20, 0.25, 50)
    assert "gaiadr3.gaia_source" in query
    assert "g.has_epoch_photometry" in query
    assert "TOP 50" in query
    assert "CIRCLE('ICRS', 65.000000000, 20.000000000, 0.250000000)" in query


def test_rejects_large_cones_and_rows():
    with pytest.raises(ValueError):
        gaia_cone_adql(65, 20, 10)
    with pytest.raises(ValueError):
        gaia_cone_adql(65, 20, max_rows=1000000)


def test_datalink_not_claimed_to_be_in_tap():
    note = gaia_datalink_instructions()
    assert "EPOCH_PHOTOMETRY" in note
    assert "DataLink" in note