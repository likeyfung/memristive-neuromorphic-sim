# Archive and verification

The repository contains the original memristive implementation, research notes for the later models, and aggregate V58 results. The newer source, trained weights, neural traces, detailed trial records, and circuit files remain in the local archive.

The previous repository introduction is preserved in [original-memristive-readme.md](history/original-memristive-readme.md), from commit `2681bdfdb8fab163b516f2b8f04d60e3697380e9`.

## Historical records

The [index](history/INDEX.json) lists 47 reading copies of earlier notes, with source paths and SHA-256 hashes. Personal home-directory prefixes were replaced with `/LOCAL_USER`; the original local documents were preserved.

These notes record the work as it stood at each revision. Some terminology and commands have since changed, and the notes do not form standalone runnable packages. The [development history](research-history.md) explains the main branches and gaps.

## Checks on V58

| Check | Outcome |
|---|---|
| Original 85-file experimental source/configuration freeze | Every SHA-256 matched |
| 183 copied V58 source/evidence files | Every copy matched its original |
| Full/compact model smoke test | Identical neuronal spikes |
| Neutral patched-kernel regression | Matched the preserved original kernel |
| Passive-noise reference | Covariance and positive-semidefinite checks passed |
| One ideal ngspice deck replay | Finite output; reproduced 45 writer and 33 receiver spikes |

The full training and evaluation protocol was not rerun for this publication. Reported scores come from the preserved experimental artifacts. These integrity and smoke checks cover only part of the implementation.

The verification environment was Python 3.11.2, NumPy 2.3.5, SciPy 1.17.1, Numba 0.68.0, Matplotlib 3.10.7, and ngspice 46. Earlier experiments may have used different versions.

No additional license is assigned by these documentation changes. Existing notices remain applicable.
