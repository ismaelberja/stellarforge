"""v1.20: synthetic-only tests of preregistration and actual-format FITS gates.

No real ZTF/Gaia data, and no test validates original DAOPhot
training-star independence, physical source identity or WCS accuracy.
"""
import hashlib
import io

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from stellarforge.v119_empirical_psf_noise import train_and_holdout_empirical_psf
from stellarforge.v120_observed_star_cohort import (
    preregister_strict_cohort, screen_fixed_cohort_native_catalogue,
    registered_star_from_masked_original_fits, public_v120_summary,
)

TARGET = "3419110734340795648"
RA, DEC = 70.0, 20.0


def row(sid, *, offset_arcsec=0, quality=True):
    return {
        "source_id": str(sid),
        "ra": RA + offset_arcsec / (3600 * np.cos(np.radians(DEC))),
        "dec": DEC + (20 if offset_arcsec else 0) / 3600,
        "g_mag": 15.4 if quality else 21.0, "g_flux_snr": 110.0,
        "ruwe": 1.1, "duplicated_source": False,
        "astrometric_params_solved": 31, "pmra": 1.0, "pmdec": -1.0,
        "parallax": 2.5, "ra_error_mas": .2, "dec_error_mas": .2,
        "pmra_error_mas_yr": .3, "pmdec_error_mas_yr": .3,
    }


def cohort_rows(n=10):
    return [row(TARGET)] + [
        row(3419111000000000000 + j, offset_arcsec=50. + 12*j)
        for j in range(n)
    ]


def registered_cohort():
    return preregister_strict_cohort(
        cohort_rows(), target_id=TARGET, prior_ids={TARGET, "1111111111111111111"})


def make_frame(*, center_x=35.3, center_y=35.4,
               shift_mask_x=0, bad=0, split=False,
               intensity=19000., seed=120):
    rng = np.random.default_rng(seed)
    yy, xx = np.indices((72, 72))
    z = (330. + rng.normal(0, 1.7, (72, 72))
         + intensity * np.exp(-((xx-center_x)**2 +
                                  (yy-center_y)**2) / (2*1.4**2)))
    m = np.zeros((72, 72), dtype=np.uint16)
    m[35, 35] = bad
    w = WCS(naxis=2)
    w.wcs.crpix = [center_x+1, center_y+1]
    w.wcs.crval = [RA, DEC]
    w.wcs.cdelt = [-1/3600., 1/3600.]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    sci_h = w.to_header()
    w.wcs.crpix = [center_x+1+shift_mask_x, center_y+1]
    mask_h = w.to_header()
    a, b = io.BytesIO(), io.BytesIO()
    fits.PrimaryHDU(z.astype(np.float32), header=sci_h).writeto(a)
    fits.PrimaryHDU(m, header=mask_h).writeto(b)
    return a.getvalue(), b.getvalue()


def build_star(sci, msk, source_id=3419111000000000001,
               native_x=1535.3, native_y=1539.4):
    return registered_star_from_masked_original_fits(
        sci, msk, gaia_source_id=str(source_id),
        exposure_id="ztf_exact_original_science_2026_unit_fixture",
        native_source_ra=RA, native_source_dec=DEC,
        native_detector_x=native_x, native_detector_y=native_y)


def test_preregister_seven_strict_stars_in_disjoint_groups_before_pixels():
    result = registered_cohort()
    assert result["n_preselected_strict_sources"] == 7
    assert result["n_expected_training_sources"] == 4
    assert result["n_expected_holdout_sources"] == 3
    assert len(set((*result["training_source_ids"],
                    *result["holdout_source_ids"]))) == 7
    assert result["selection_fixed_before_native_ztf_catalogue_and_pixels"]
    assert not result["original_ztf_psf_training_star_membership_verified"]


def test_gaia_too_few_strict_sources_cannot_proceed():
    result = preregister_strict_cohort(
        cohort_rows(4), target_id=TARGET, prior_ids={TARGET})
    assert result["status"] == "INSUFFICIENT_STRICT_GAIA_ONLY_COHORT"
    assert not result["training_source_ids"]
    assert not result["holdout_source_ids"]


def test_preregister_does_not_let_target_appear_in_training():
    with pytest.raises(ValueError, match="historical target"):
        preregister_strict_cohort(cohort_rows(), target_id=TARGET,
                                  prior_ids={"1111111111111111111"})


def test_preregistered_native_catalogue_preserves_train_test_assignment():
    cohort = registered_cohort()
    ids = (*cohort["training_source_ids"], *cohort["holdout_source_ids"])
    ra = np.array([100. + j * .01 for j in range(7)])
    dec = np.full(7, 22.0)
    cat = {
        "status": "ORIGINAL_ZTF_PSF_CATALOGUE_PARSED_UNVERIFIED",
        "rows": {
            "ra": ra, "dec": dec, "sourceid": np.arange(1, 8),
            "flags": np.zeros(7, dtype=int),
            "snr": np.full(7, 45.),
            "chi": np.array([1., 1., 3., 1., 1., 1., 1.]),
            "sharp": np.zeros(7), "flux": np.full(7, 9000.),
            "sigflux": np.full(7, 70.),
            "xpos": np.full(7, 1600.), "ypos": np.full(7, 1620.),
        },
    }
    positions = [
        {"source_id": sid, "geocentric_parallax_adjusted_ra_deg": float(ra[i]),
         "geocentric_parallax_adjusted_dec_deg": float(dec[i])}
        for i, sid in enumerate(ids)
    ]
    out = screen_fixed_cohort_native_catalogue(cat, positions[::-1], cohort)
    assert out["n_native_training_candidates"] == 3
    assert out["n_native_holdout_candidates"] == 3
    assert [q["gaia_source_id"] for q in out["train_screens"]] == list(ids[:4])
    assert out["source_group_assignment_unchanged_after_screen"]


def test_native_screen_rejects_substituted_source():
    cohort = registered_cohort()
    positions = [{"source_id": "7777777777777777777"}] * 7
    with pytest.raises(ValueError, match="fixed Gaia cohort"):
        screen_fixed_cohort_native_catalogue({}, positions, cohort)


def test_native_screen_rejects_incomplete_gaia_registration():
    small = preregister_strict_cohort(
        cohort_rows(4), target_id=TARGET, prior_ids={TARGET})
    with pytest.raises(ValueError, match="preregistration"):
        screen_fixed_cohort_native_catalogue({}, [], small)


def test_ztf_science_mask_fits_wcs_register_stamp_and_source_phase():
    sci, msk = make_frame()
    star, qa = build_star(sci, msk)
    assert star.pixels_dn.shape == (23, 23)
    assert star.mask_bits.shape == (23, 23)
    assert qa["max_mask_science_wcs_offset_pixels"] < .01
    assert qa["registered_centroid_proxy_max_abs_offset_pixels"] < .08
    assert qa["interpolated_pixels_are_correlated"]
    assert not qa["original_daophot_training_star_exclusion_verified"]


def test_registration_does_not_claim_native_independent_wcs():
    sci, msk = make_frame()
    _, qa = build_star(sci, msk)
    assert not qa["native_source_identity_independently_authenticated"]
    assert qa["native_psfcat_phase_max_difference_pixels"] < .01


@pytest.mark.parametrize("bit", [1, 4, 256, 4096])
def test_original_bad_or_saturated_core_rejected_even_after_interpolation(bit):
    sci, msk = make_frame(bad=bit)
    with pytest.raises(ValueError, match="Masked/saturated"):
        build_star(sci, msk)


def test_source_marker_not_a_detector_bad_bit():
    sci, msk = make_frame(bad=2)
    star, _ = build_star(sci, msk)
    assert star.mask_bits[11, 11] == 0


def test_wcs_mismatch_fails_closed_before_source_model():
    sci, msk = make_frame(shift_mask_x=.2)
    with pytest.raises(ValueError, match="misregistered"):
        build_star(sci, msk)


def test_native_catalogue_subpixel_phase_mismatch_blocks_registration():
    sci, msk = make_frame()
    with pytest.raises(ValueError, match="phase"):
        build_star(sci, msk, native_x=1535.0)


def test_artificial_off_center_source_is_not_a_valid_registered_star():
    sci, msk = make_frame(center_x=35.3, center_y=35.4)
    # A forged/incorrect WCS pointing to the wrong peak is rejected by
    # the image-centering proxy, even if the native subpixel phase matches.
    with pytest.raises(ValueError, match="centroid proxy"):
        registered_star_from_masked_original_fits(
            sci, msk, gaia_source_id="3419111000000000001",
            exposure_id="ztf_exact_original_science_2026_unit_fixture",
            native_source_ra=RA + 1/3600., native_source_dec=DEC,
            native_detector_x=1535.3, native_detector_y=1539.4)


def test_full_five_distinct_synthetic_fits_after_wcs_registration():
    registered = []
    for j in range(5):
        sci, msk = make_frame(seed=120+j, intensity=15000+1500*j)
        star, _ = build_star(sci, msk, 3419111000000000001 + j)
        registered.append(star)
    result = train_and_holdout_empirical_psf(registered[:3], registered[3:])
    assert result["n_distinct_training_stars"] == 3
    assert result["n_distinct_heldout_stars"] == 2
    assert not result["original_ztf_psf_training_membership_verified"]
    assert result["n_heldout_profile_reviews"] == 0


def test_aggregate_whitelist_never_serializes_source_ids_or_original_pixels():
    cohort = registered_cohort()
    digest = hashlib.sha256(b"synthetic").hexdigest()
    summary = public_v120_summary(
        cohort=cohort, widecone_sha256=digest, formal_gaia_sha256=digest,
        frame_summaries=[{"field": "CIDA 11", "band": "zg",
                          "mjd": 58475.11375,
                          "n_native_train": 4, "n_native_holdout": 3,
                          "n_registered_train": 3, "n_registered_holdout": 2,
                          "n_mask_or_registration_failures": 2,
                          "image_access_failures": 0,
                          "empirical_psf_status": "INTERNAL_DISTINCT_STAR_PSF_HOLDOUT_COMPLETED",
                          "n_heldout_profile_reviews": 0}])
    assert "3419111000" not in str(summary)
    assert "training_source_ids" not in str(summary)
    assert "pixels" not in str(summary)
    assert not summary["independent_survey_psf_or_wcs_calibration_completed"]


def test_public_summary_rejects_unknown_fields_instead_of_leaking_raw():
    cohort = registered_cohort()
    digest = hashlib.sha256(b"synthetic").hexdigest()
    with pytest.raises(ValueError, match="Unapproved"):
        public_v120_summary(
            cohort=cohort, widecone_sha256=digest, formal_gaia_sha256=digest,
            frame_summaries=[{"raw_psf_pixels": [[0.,1.]]}])
