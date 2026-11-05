"""Standalone CI pilot contract tests, no network or third-party dependencies."""
from pathlib import Path
import importlib.util
import unittest
import tempfile

P=Path(__file__).resolve().parents[1]/'scripts/ci_observational_pilot.py'
SPEC=importlib.util.spec_from_file_location('stellarforge_ci_pilot',P)
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class TestCIPilot(unittest.TestCase):
    def test_official_urls(self):
        for _,_,ra,dec in mod.TARGETS:
            u=mod.make_url(ra,dec)
            self.assertTrue(u.startswith('https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?'))
            self.assertIn('BAD_CATFLAGS_MASK=32768',u)

    def test_flagged_photometry_is_rejected(self):
        data=(b'oid,mjd,mag,magerr,catflags,filtercode\n'
              b'1001,59000,15.1,0.03,0,zg\n'
              b'1001,59001,12.1,0.03,32768,zg\n')
        x=mod.inspect_response(data)
        self.assertEqual(x['rows'],2)
        self.assertEqual(x['qc_accepted'],1)
        self.assertEqual(x['qc_rejected'],1)

    def test_unverified_source_can_never_be_promoted(self):
        raw=b'oid,mjd,mag,magerr,catflags,filtercode\n1001,59000,15.1,0.03,0,zr\n'
        with tempfile.TemporaryDirectory() as td:
            x=mod.run(Path(td),fetcher=lambda url:raw)
            self.assertEqual(x['raw_photometry_responses'],2)
            self.assertEqual(x['verified_gaia_ztf_crossmatches'],0)
            self.assertEqual(x['physical_detections'],0)

    def test_failure_is_not_negative_sky_detection(self):
        def fail(url):raise OSError('network unavailable')
        with tempfile.TemporaryDirectory() as td:
            x=mod.run(Path(td),fetcher=fail)
            self.assertEqual(x['raw_photometry_responses'],0)
            self.assertTrue(all('exception_type' in z for z in x['results']))

    def test_http_status_is_preserved_for_scientific_audit(self):
        from urllib.error import HTTPError
        def fail(url):
            raise HTTPError(url, 503, 'Service unavailable', None, None)
        with tempfile.TemporaryDirectory() as td:
            x=mod.run(Path(td),fetcher=fail)
            self.assertEqual(x['raw_photometry_responses'],0)
            self.assertTrue(all(z['exception_type']=='HTTPError'
                                and z['http_status']==503
                                and z['http_retryable']
                                and z['failure_class']=='HTTP_RESPONSE_ERROR'
                                for z in x['results']))
            self.assertTrue((Path(td)/'PILOT_STATUS.json').is_file())
            self.assertFalse(any(Path(td).glob('*_IRSA_RAW.csv')))

    def test_bad_http_status_is_not_a_valid_no_coverage_claim(self):
        from urllib.error import HTTPError
        def fail(url):
            raise HTTPError(url, 400, 'Bad Request', None, None)
        with tempfile.TemporaryDirectory() as td:
            x=mod.run(Path(td),fetcher=fail)
            self.assertEqual(x['raw_photometry_responses'],0)
            self.assertTrue(all(z['http_status']==400 and not z['http_retryable']
                                for z in x['results']))

    def test_header_only_requires_real_ztf_columns(self):
        with self.assertRaises(ValueError):
            mod.inspect_response(b'error,message\n')
        x=mod.inspect_response(b'oid,mjd,mag,magerr,catflags,filtercode\n')
        self.assertEqual(x['rows'],0)
        self.assertEqual(x['status'],'NO_ROWS_RETURNED_COVERAGE_UNKNOWN')
        self.assertEqual(x['qc_rejected'],0)

    def test_html_is_rejected(self):
        with self.assertRaises(ValueError):mod.inspect_response(b'<html>not a table</html>')

if __name__=='__main__':unittest.main()