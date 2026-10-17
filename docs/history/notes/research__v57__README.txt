# V57 — Integrated tapeout decision brief

Chinese narrative with exportable English-labeled figures. No architecture changes or new neural experiments.
Sources from V52/V54/V55/V56 are frozen under reference/ with hashes.

Requirements: Python 3, numpy, matplotlib.

    python3 src/build.py

Open report.html. PNG / SVG / PDF figures are in figures/.
New calculation: calibration and unmodeled-power budget compatible with 2x decoder-energy advantage.
All energy estimates are conditional, not measured chip supply energy.
