# StellarForge v0.6 — 24 REAL Taurus catalog positions

This folder contains calculations based on a **real, provisional 24-star technical subset of Luhman (2023) Table 2**, obtained from a pinned public third-party mirror. They are **not ZTF light-curve measurements**. The exact original publisher bytes remain to be crosschecked.

`TAURUS_24_NOMINAL_EPOCH_POSITIONS.csv` contains the literature Gaia J2016.0 sky positions and proper motions and approximate calculated positions at an **illustrative** J2021.0 reference epoch. `ASTROMETRIC_ENGINEERING_AUDIT.json` hashes the 24-target input and summarizes the displacement statistics. The [plot](TAURUS_24_PROPER_MOTIONS_REAL_CATALOG.png) shows proper-motion vectors in RA* and Dec from the published catalog (mas/year).

Across the 24 objects: median displacement **0.112673 arcsec**, maximum **0.145100 arcsec** over the illustrative five-year propagation. Actual source association must use observation-specific epochs, parallax, Gaia covariance and cutout inspection. **No counterparts have been confirmed.**

Original paper: K. L. Luhman (2023), AJ 165, 37, DOI 10.3847/1538-3881/ac9da3. Mirror: https://github.com/themariavincent/get_targets/blob/7b6a5c83eca81fc66e50cb4889ee35cb28861367/taurus_sources.txt .