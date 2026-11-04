import math
import pytest
from stellarforge.coordinates import (
    angular_separation_arcsec, approximate_proper_motion_position, validate_icrs,
)


def test_identity_and_symmetry():
    assert angular_separation_arcsec(40, 30, 40, 30) == pytest.approx(0.0)
    a = angular_separation_arcsec(12, 32, 359.99, -14)
    b = angular_separation_arcsec(359.99, -14, 12, 32)
    assert a == pytest.approx(b, rel=1e-12)


def test_wraparound_ra():
    value = angular_separation_arcsec(359.999, 0, 0.001, 0)
    assert value == pytest.approx(7.2, abs=1e-8)


def test_near_pole_distance_is_finite():
    assert math.isfinite(angular_separation_arcsec(180, 89.999, 0, 89.999))


@pytest.mark.parametrize("ra,dec", [(-1, 0), (360, 0), (20, 91), (20, -91), (math.nan, 0)])
def test_invalid_positions(ra, dec):
    with pytest.raises(ValueError):
        validate_icrs(ra, dec)


def test_approximate_pm_correct_units():
    ra, dec = approximate_proper_motion_position(10, 0, 100, -200, 10)
    assert ra == pytest.approx(10 + 1000 / 3_600_000)
    assert dec == pytest.approx(-2000 / 3_600_000)


def test_propagation_rejects_pole():
    with pytest.raises(ValueError):
        approximate_proper_motion_position(10, 90, 1, 1, 1)