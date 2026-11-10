# v1.22 evidence report — original bytes recovered, mocked pipeline tested

**10 November 2026. Two distinct categories of evidence:**

**A. GENUINE historic data transport/provenance:** GitHub Actions
original acquisition run 41997079598, artifact 13401380025,
size 181,170 bytes, original ZIP digest SHA-256
d54246e00d4cf343b0b062b9eb92034e51c735067274a8109e9b2c2c2a2d5167.
Original artifact downloaded privately and ZIP digest matched
the GitHub Actions returned digest. Its four original content
members (2 raw CSV positional responses + acquisition JSON +
report) remain excluded from the public Git repository.
Original ESA Gaia/ZTF identity calibration NOT established.

**B. SYNTHETIC software validation:** a complete no-network mocked
v1.20 original CIDA 11 two-exposure runner successfully
executes with simulated disjoint 4-training/3-held-out star
stamp images. A contrasting mocked branch fails closed if
two holdout sources are removed. This tests Python orchestration,
not an actual original-data scientific instrumental result.

The real manual v1.20 workflow **has not been run** here.
As of this report, no new independent original survey
PSF/WCS, per-exposure CCD covariance, or physical Gaia/ZTF
source identification is scientifically confirmed.

Reproducibility: scripts/check_v122_historic_source_zip.py;
tests/test_v122_historic_archive_integrity.py;
tests/test_v122_complete_mocked_real_pipeline.py;
docs/PHASE122_GUIA_ES.md.

Next: manually run original live ZTF image pilot or
document an authenticated inability to finish. Then
perform the final **v2.0 software portfolio release audit**.
