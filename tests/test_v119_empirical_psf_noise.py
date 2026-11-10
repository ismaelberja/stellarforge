"""v1.19 deterministic synthetic-only gates; NO original ZTF source images."""
import numpy as np
import pytest

from stellarforge.v119_empirical_psf_noise import (
    RegisteredStar, train_and_holdout_empirical_psf,
    diagonal_ccd_variance_dn2, estimate_blank_sky_aperture_correlation,
    public_aggregate_only,
)


def fake_stars(n=5, *, seed=119, widened_holdout=False):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[-11:12, -11:12]
    out = []
    for j in range(n):
        width = 1.65 if widened_holdout and j == n - 1 else 1.35
        p = np.exp(-(x*x+y*y)/(2*width*width))
        p /= p.sum()
        img = 210. + (12000 + j * 250) * p + rng.normal(0, 2, p.shape)
        out.append(RegisteredStar(str(100000+j), "original-exposure-a",
                                  img, np.zeros(img.shape, dtype=np.uint16)))
    return out


def test_synthetic_distinct_star_model_and_holdouts():
    sample = fake_stars(6)
    result = train_and_holdout_empirical_psf(sample[:4], sample[4:])
    assert result["n_distinct_training_stars"] == 4
    assert result["n_distinct_heldout_stars"] == 2
    assert result["empirical_psf"].shape == (23, 23)
    assert result["empirical_psf"].sum() == pytest.approx(1.0)
    assert all(v["status"] == "DESCRIPTIVE_HELDOUT_PROFILE_OK"
               for v in result["heldout_results"])
    assert result["internal_psf_training_and_validation_star_ids_disjoint"]
    assert not result["original_ztf_psf_training_membership_verified"]
    assert not result["genuine_independent_ztf_wcs_or_psf_calibration"]
    pub = public_aggregate_only(result)
    assert "empirical_psf" not in pub and "source_ids" not in repr(pub)
    assert "100000" not in repr(pub)


def test_distinct_stars_not_same_star_new_epoch():
    s = fake_stars()
    duplicate = RegisteredStar(s[0].gaia_source_id, s[0].exposure_id,
                               s[0].pixels_dn, s[0].mask_bits)
    with pytest.raises(ValueError, match="Duplicate"):
        train_and_holdout_empirical_psf(s[:3], [s[3], duplicate])


def test_epoch_mixing_rejected_before_stellar_model():
    s = fake_stars()
    v = s[4]
    altered = RegisteredStar(v.gaia_source_id, "other-original-exposure",
                             v.pixels_dn, v.mask_bits)
    with pytest.raises(ValueError, match="one science exposure"):
        train_and_holdout_empirical_psf(s[:3], [s[3], altered])


def test_too_few_distinct_training_and_validation_stars():
    s = fake_stars()
    with pytest.raises(ValueError, match="Insufficient distinct"):
        train_and_holdout_empirical_psf(s[:2], s[2:4])
    with pytest.raises(ValueError, match="Insufficient distinct"):
        train_and_holdout_empirical_psf(s[:4], s[4:5])


@pytest.mark.parametrize("mask_pixel", [256, 1, 4096])
def test_bad_detector_core_flags_rejected(mask_pixel):
    s = fake_stars()
    im = s[0].mask_bits.copy()
    im[11, 11] = mask_pixel
    changed = RegisteredStar(s[0].gaia_source_id, s[0].exposure_id,
                             s[0].pixels_dn, im)
    with pytest.raises(ValueError, match="Masked/saturated"):
        train_and_holdout_empirical_psf([changed, *s[1:3]], s[3:])


def test_source_detection_flag_not_a_bad_pixel():
    s = fake_stars()
    m = s[0].mask_bits.copy()
    m[11, 11] = 2  # ZTF source-marker bit 1 is not a deleterious flag
    changed = RegisteredStar(s[0].gaia_source_id, s[0].exposure_id,
                             s[0].pixels_dn, m)
    assert train_and_holdout_empirical_psf(
        [changed, *s[1:3]], s[3:])["n_distinct_training_stars"] == 3


@pytest.mark.parametrize("offset", [(0.09, 0), (0, float("nan")), (2, 0)])
def test_stars_without_independent_subpixel_registration_rejected(offset):
    s = fake_stars()
    v = s[0]
    bad = RegisteredStar(v.gaia_source_id, v.exposure_id,
                         v.pixels_dn, v.mask_bits, offset)
    with pytest.raises(ValueError, match="registered"):
        train_and_holdout_empirical_psf([bad, *s[1:3]], s[3:])


@pytest.mark.parametrize("invalid", [1.25, -1, float("nan"), 65536])
def test_fractional_negative_nonfinite_mask_rejected(invalid):
    s = fake_stars()
    m = s[0].mask_bits.astype(float)
    m[0, 0] = invalid
    v = s[0]
    with pytest.raises(ValueError, match="bitmask"):
        train_and_holdout_empirical_psf(
            [RegisteredStar(v.gaia_source_id, v.exposure_id, v.pixels_dn, m),
             *s[1:3]], s[3:])


def test_nonfinite_source_pixels_rejected():
    s = fake_stars()
    a = s[0].pixels_dn.copy()
    a[11, 11] = np.inf
    v = s[0]
    with pytest.raises(ValueError, match="nonfinite"):
        train_and_holdout_empirical_psf(
            [RegisteredStar(v.gaia_source_id, v.exposure_id, a, v.mask_bits),
             *s[1:3]], s[3:])


def test_broadened_unseen_validation_profile_triggers_review():
    s = fake_stars(6, widened_holdout=True)
    result = train_and_holdout_empirical_psf(s[:4], s[4:])
    assert result["n_heldout_profile_reviews"] >= 1


def test_diagonal_ccd_noise_units_include_source_sky_and_read():
    got = diagonal_ccd_variance_dn2(
        np.array([[100., 0.]]), sky_dn=40., gain_e_per_dn=2.,
        read_noise_e=4.)
    np.testing.assert_allclose(got, [[74., 24.]])


@pytest.mark.parametrize("kwargs", [
    {"sky_dn": -1., "gain_e_per_dn": 2., "read_noise_e": 4.},
    {"sky_dn": 40., "gain_e_per_dn": 0., "read_noise_e": 4.},
    {"sky_dn": 40., "gain_e_per_dn": 2., "read_noise_e": -1.},
])
def test_unphysical_ccd_noise_rejected(kwargs):
    with pytest.raises(ValueError, match="physical"):
        diagonal_ccd_variance_dn2(np.zeros((2, 2)), **kwargs)


def test_negative_source_and_nonfinite_source_rejected():
    for array in (np.array([[-1.]]), np.array([[np.nan]])):
        with pytest.raises(ValueError):
            diagonal_ccd_variance_dn2(
                array, sky_dn=50., gain_e_per_dn=2., read_noise_e=4.)


def test_correlated_and_uncorrelated_blank_sky_are_distinct():
    rng = np.random.default_rng(119)
    aperture = np.ones((7, 7), dtype=bool)
    independent = rng.normal(0, 2, (512, 7, 7))
    correlated = independent + rng.normal(0, 3, (512, 1, 1))
    a = estimate_blank_sky_aperture_correlation(independent, aperture)
    b = estimate_blank_sky_aperture_correlation(correlated, aperture)
    assert .65 < a["empirical_variance_ratio"] < 1.35
    assert b["empirical_variance_ratio"] > 5
    assert not b["survey_uncertainty_calibrated"]


def test_fewer_than_16_external_sky_windows_rejected():
    with pytest.raises(ValueError, match="independent blank-sky"):
        estimate_blank_sky_aperture_correlation(
            np.ones((8, 7, 7)), np.ones((7, 7), dtype=bool))


def test_never_publish_raw_array_from_partial_result():
    with pytest.raises(ValueError, match="Incomplete"):
        public_aggregate_only({"status": "TRANSPORT_FAILED"})
