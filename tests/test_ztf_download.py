import hashlib
import json
from unittest.mock import patch
import pytest
from stellarforge.ztf import build_ztf_url, fetch_ztf_raw


class FakeResponse:
    headers = {"Content-Type": "text/plain"}
    def __init__(self, payload): self.payload = payload
    def read(self, n=-1): return self.payload
    def __enter__(self): return self
    def __exit__(self, *args): return False


def test_download_provenance_without_network(tmp_path):
    url = build_ztf_url(65, 25)
    raw = b"\\ Simple IPAC Table\n| mjd | mag |\n"
    with patch("stellarforge.ztf.urlopen", return_value=FakeResponse(raw)):
        meta = fetch_ztf_raw(url, tmp_path / "raw" / "target.tbl")
    assert (tmp_path / "raw" / "target.tbl").read_bytes() == raw
    assert meta["sha256"] == hashlib.sha256(raw).hexdigest()
    assert json.loads((tmp_path / "raw" / "target.tbl.provenance.json").read_text())["status"] == "unvalidated_raw_response"


def test_no_html_saved(tmp_path):
    url = build_ztf_url(65, 25)
    with patch("stellarforge.ztf.urlopen", return_value=FakeResponse(b"<html>Fail</html>")):
        with pytest.raises(ValueError):
            fetch_ztf_raw(url, tmp_path / "target.tbl")
    assert not (tmp_path / "target.tbl").exists()


def test_only_irsa_source_allowed(tmp_path):
    with pytest.raises(ValueError):
        fetch_ztf_raw("https://example.com/test", tmp_path / "file")