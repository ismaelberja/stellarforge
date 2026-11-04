"""Unit tests for the provisional multi-band diagnostic."""
import unittest
from stellarforge.chromaticity import PhotometricEpoch, pair_g_r

def pt(oid, band, mjd, mag, err=0.05):
    return PhotometricEpoch(oid, band, mjd, mag, err)

class ColorMatchingTests(unittest.TestCase):
    def test_pair_and_uncertainties(self):
        x=pair_g_r([pt("11","g",59000,15,0.3),pt("22","r",59000.1,14,0.4)],oid_g="11",oid_r="22")
        self.assertEqual(x["paired_epochs"],1)
        self.assertAlmostEqual(x["pairs"][0]["color_g_minus_r_mag"],1.0)
        self.assertAlmostEqual(x["pairs"][0]["color_uncertainty_mag"],0.5)
        self.assertFalse(x["gaia_ztf_source_identity_verified"])

    def test_requires_two_distinct_source_ids(self):
        with self.assertRaises(ValueError):
            pair_g_r([],oid_g="11",oid_r="11")

    def test_no_interpolation_if_epochs_far_apart(self):
        x=pair_g_r([pt("11","g",59000,15),pt("22","r",59002,14)],oid_g="11",oid_r="22")
        self.assertEqual(x["paired_epochs"],0)

    def test_never_reuse_observation(self):
        x=pair_g_r([pt("11","g",59000,15),pt("11","g",59000.1,16),
                    pt("22","r",59000.09,14)],oid_g="11",oid_r="22")
        self.assertEqual(x["paired_epochs"],1)

    def test_quality_flag_blocks_point(self):
        with self.assertRaises(ValueError):
            pair_g_r([PhotometricEpoch("11","g",59000,15,.05,32768)],
                     oid_g="11",oid_r="22")

if __name__ == "__main__":
    unittest.main()
