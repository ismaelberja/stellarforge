"""v1.2 offline plot regression; fixtures are synthetic and never Taurus results."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/plot_v12_raw_ztf.py"
SPEC = importlib.util.spec_from_file_location("stellarforge_v12_plot", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class TestV12RawPlot(unittest.TestCase):
    def fixture(self, location: Path, corrupt: bool = False) -> Path:
        csv_bytes = (
            b"oid,filtercode,field,mjd,mag,magerr,catflags\n"
            b"123,zg,609,59000,15.1,0.03,0\n"
            b"123,zg,609,59001,15.2,0.04,32768\n"
            b"321,zr,609,59001,14.1,0.04,0\n"
        )
        manifest = {
            "results": [{
                "target": "SYNTHETIC_FIXTURE",
                "gaia_dr3_id": "123456789",
                "acquisition_status": "RAW_HTTP_RESPONSE_SAVED_ASSOCIATION_UNVERIFIED",
                "raw_sha256": "bad_hash" if corrupt else hashlib.sha256(csv_bytes).hexdigest(),
            }]
        }
        file = location / "synthetic_test_artifact.zip"
        with ZipFile(file, "w") as archive:
            archive.writestr("PILOT_STATUS.json", json.dumps(manifest))
            archive.writestr("123456789_IRSA_RAW.csv", csv_bytes)
        return file

    def test_oids_stay_separate_and_flagged_rows_masked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            out = base / "plots"
            results = module.make_plots(self.fixture(base), out)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["n_distinct_oid_bands"], 2)
            self.assertEqual(results[0]["n_plotted"], 2)
            self.assertEqual(results[0]["n_masked_catflags_32768"], 1)
            self.assertFalse(results[0]["gaia_ztf_identity_verified"])
            self.assertTrue((out / results[0]["plot"]).is_file())
            summary = json.loads((out / "PRELIMINARY_FIGURE_MANIFEST.json").read_text())
            self.assertEqual(summary["scientific_status"], "UNVERIFIED_CONE_QUERY")

    def test_mismatched_sha_blocks_plot(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(ValueError):
                module.make_plots(self.fixture(base, corrupt=True), base / "plots")


if __name__ == "__main__":
    unittest.main()
