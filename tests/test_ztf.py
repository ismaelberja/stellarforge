import math
import pytest
from urllib.parse import parse_qs, urlsplit
from stellarforge.ztf import build_ztf_url


def test_url_is_documented_and_encoded():
    url = build_ztf_url(65.0, 25.0, 2, ("g", "r"))
    parts = urlsplit(url)
    assert parts.netloc == "irsa.ipac.caltech.edu"
    params = parse_qs(parts.query)
    assert params["POS"] == ["CIRCLE 65.000000000 25.000000000 0.000555556"]
    assert params["BANDNAME"] == ["g,r"]
    assert params["BAD_CATFLAGS_MASK"] == ["32768"]
    assert params["FORMAT"] == ["ipac_table"]


@pytest.mark.parametrize("radius,bands", [(-1, ("g",)), (0, ("g",)), (601, ("g",)), (1, ("u",)), (1, ()), (1, ("g", "g"))])
def test_bad_query_parameters(radius, bands):
    with pytest.raises(ValueError):
        build_ztf_url(60, 20, radius, bands)


def test_invalid_dec():
    with pytest.raises(ValueError):
        build_ztf_url(60, math.nan)