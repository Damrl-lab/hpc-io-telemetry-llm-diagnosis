"""Provenance analysis: EXE_NAME_GENID null rates by year.

The field holds anonymized numeric hash identifiers, not readable
executable names. Its population collapses between 2020 and 2021 — an
abrupt change, uniform across job types, aligned with the data-export
format rather than any workload covariate: a data-pipeline change, not
a workload shift. The finding motivates mandatory provenance checking
(remediation 4): provenance checks run upstream of statistics and
diagnosis.

Backs: Sec. VI-F of the paper (provenance case study).

VALIDATION TARGETS (from the paper, on the 500/year sample):
  - null rates: 2018 0% | 2020 0% | 2021 88.8% | 2022 75.0% | 2023 86.6%
  - cross-year hash overlap: 2021<->2022: 4 | 2021<->2023: 2 | 2022<->2023: 2
If a run does not reproduce these, do not push results — investigate.

Developed with AI assistance (Claude, Anthropic), directed and validated
by the authors. See the paper's AI-generated content disclosure.
"""

import glob
import itertools

import pandas as pd

if __name__ == "__main__":
    frames = [pd.read_csv(f) for f in sorted(glob.glob("theta_*_sample.csv"))]
    if not frames:
        raise SystemExit("No theta_*_sample.csv files found — run data/extract_samples.py first.")
    df = pd.concat(frames, ignore_index=True)

    print("EXE_NAME_GENID null rate by year "
          "[paper: 0 / 0 / 88.8 / 75.0 / 86.6 %]:")
    for year, g in df.groupby("year"):
        rate = 100 * g["EXE_NAME_GENID"].isna().mean()
        print(f"  {year}: {rate:5.1f}%  ({int(g['EXE_NAME_GENID'].isna().sum())} of {len(g)})")

    print("\ncross-year overlap of hash identifiers "
          "[paper: 21-22: 4 | 21-23: 2 | 22-23: 2]:")
    ids = {
        str(year): set(g["EXE_NAME_GENID"].dropna().unique())
        for year, g in df.groupby("year")
    }
    for a, b in itertools.combinations(sorted(ids), 2):
        shared = len(ids[a] & ids[b])
        if shared:
            print(f"  {a} <-> {b}: {shared} shared")
