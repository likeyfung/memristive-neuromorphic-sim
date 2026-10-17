# V55: memory traffic, streaming power and tapeout rationale

This is a cost/sensitivity study, not a new model revision or BCI experiment.
Frozen V52 inputs and V54 evidence are under reference/. Earlier revisions are unchanged.

Requirements: Python 3, numpy, matplotlib.

From this folder:

    python3 src/estimate.py
    python3 src/report.py

Open report.html. Figures are available as PNG, SVG and PDF.

Traffic is a modeled read/write payload, not measured SRAM/DRAM counters.
SRAM access/arithmetic energies and digital skipped-update fractions are sensitivity assumptions.
Analog power is a gm-C design estimate, not supply-power simulation or silicon measurement.
Live BCI figures reuse V52 fly-workload event rates; no BCI decoding accuracy is claimed.
No model weights or circuit files are changed, and no test-set optimization was performed.
