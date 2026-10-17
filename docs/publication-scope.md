# Publication scope and verification

[Back to the project](../README.md)

This documentation update extends the existing public `likeyfung/memristive-neuromorphic-sim` repository. The original source directories remain unchanged. The previous root README is preserved as [original-memristive-readme.md](history/original-memristive-readme.md), from repository commit `2681bdfdb8fab163b516f2b8f04d60e3697380e9`.

## Public in this update

- An English overview, architecture diagram, research journey, evidence summary, and roadmap.
- Aggregate V58 results, with separate accuracy, causal, stress, and event-count interpretations.
- Forty-seven historical reading notes and an index of original/public-copy SHA-256 hashes. Personal home-directory prefixes are replaced with `/LOCAL_USER` in those reading copies; original local documents remain unchanged.

## Retained in the local archive

The newer model source and dependencies, trained model weights, saved neural traces, detailed calibration/test records, circuit decks, and raw electrical waveforms are not uploaded in this documentation release. Complete standalone copies of every historical revision are also not included. The history identifies available branches and gaps rather than implying 58 complete public model releases.

Unrelated applications, personal documents, temporary files, and downloaded third-party papers are excluded.

## Checks performed before publication

The complete local V58 candidate package was checked during publication preparation:

| Check | Outcome |
|---|---|
| Original 85-file experimental source/configuration freeze | Every SHA-256 matched |
| 183 copied V58 source/evidence files | Every copy matched its original |
| Full/compact model smoke test | Identical neuronal spikes |
| Neutral patched-kernel regression | Matched the preserved original kernel |
| Passive-noise reference | Covariance and positive-semidefinite checks passed |
| One ideal ngspice deck replay | Finite output; reproduced 45 writer and 33 receiver spikes |

The full training and evaluation protocol was **not rerun** during publication work. Scores in this public summary come from the preserved original artifacts. The smoke checks validate a limited portion of the implementation and do not independently certify every research conclusion.

Publication checks used Python 3.11.2, NumPy 2.3.5, SciPy 1.17.1, Numba 0.68.0, Matplotlib 3.10.7, and ngspice 46. These describe the verification environment, not necessarily every original research run.

Historical notes are reading copies of earlier records and may contain superseded terminology or commands that refer to the local archive. They are not standalone runnable packages. The [history index](history/INDEX.json) identifies the original source paths and hashes.

No new license is assigned by this documentation update. Existing notices remain applicable.
