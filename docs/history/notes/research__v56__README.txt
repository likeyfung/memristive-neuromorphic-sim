# V56: audit the existing ngspice implementation

This is a new analysis folder. V54 circuits/results and V55 estimates remain unchanged.

Saved original V54 waveforms are copied losslessly into reference/saved_waveforms.npz.
The original .dat SHA-256 and source path are recorded in reference/trace_provenance.json.
This audit does not rerun ngspice or train a new network.

Reproduce with Python 3 + numpy + matplotlib:

    python3 src/audit.py
    python3 src/report.py

Open report.html. Figures are PNG / SVG / PDF. Results are results/audit.json.

Waveforms are from the fixed-workload equivalent-reduced simulation, while hardware inventory is the full-array netlist.
42,529 events counts only recurrent deliveries arriving by the episode end.
Element signal energy is not supply energy. No VDD/current-sense power model exists in this behavioral circuit.
Voltage scaling, noise, routing hardware and transistor-level supply modeling remain future work.
