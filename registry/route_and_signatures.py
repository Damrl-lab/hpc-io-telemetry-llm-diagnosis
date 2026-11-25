"""Unknown-state registry: two-layer coverage-boundary routing and
state-signature matching, run over the 2,500-record sample.

Layer 1 (feature completeness) routes a job to the registry when any of
four conditions holds:
  (a) EXE_NAME_GENID is null              — executable unattributable
  (b) TOTAL_POSIX_OPENS == 0              — feature rule inapplicable
  (c) NPROCS == 0                         — per-process metrics undefined
  (d) zero POSIX bytes (read+written) while RUN_TIME > 600 s
                                          — instrumentation blind-spot signature
Layer 2 (distributional position) routes a job whose
TOTAL_POSIX_BYTES_WRITTEN or TOTAL_POSIX_BYTES_READ exceeds its year's
95th-percentile reference value. The reference values are recorded
verbatim from the original evaluation run (lightly rounded per-year
p95 values; see BASELINE_P95 below).

State signatures over the five HIGH-SIGNAL metrics
(bytes read, bytes written, POSIX opens, NPROCS, RUN_TIME):
  - exact:    leading 16 hex chars of SHA-256 over the raw values joined
              with "|" — collides only on bit-identical metrics
              (strict lower bound on recurrence)
  - bucketed: order-of-magnitude band tuple (the operational scheme).
              Band edges at powers of ten: 1 KB / 1 MB / 1 GB / 1 TB for
              byte counts; 1 / 10 / 100 / 1,000 / 10,000 for opens and
              process counts and for runtime seconds.
              Example from the paper: 40.1 GB read, 41.3 GB written,
              1,871 opens, 512 procs, 2,636 s  ->  4-4-4-3-4.

Backs: Secs. VI-C and VI-E of the paper (coverage boundary + registry).

VALIDATION TARGETS (from the paper and the documented evaluation, on
the 2,500-record sample) — every value below is reproduced exactly by
this script:
  - routed total: 1,957 (78.3%); Layer 1: 1,877; Layer 2 only: 80;
    classifiable (passed both layers): 543
  - Layer-1 reasons (a job may trigger several):
      EXE_NAME_GENID null 1,252 | zero opens 726 | blind-spot 484
  - bucketed: 141 distinct states, 1,816 recurrences, 92.8% recurrence,
    13.9x deduplication; 32 states recur across year boundaries
  - exact: 1,659 states, 298 recurrences, 15.2%, 1.2x
  - Job 5 signature check: 4-4-4-3-4

Developed with AI assistance (Claude, Anthropic), directed and validated
by the authors. See the paper's AI-generated content disclosure.
"""

import glob
import hashlib

import numpy as np
import pandas as pd

SIG_METRICS = [
    "TOTAL_POSIX_BYTES_READ",
    "TOTAL_POSIX_BYTES_WRITTEN",
    "TOTAL_POSIX_OPENS",
    "NPROCS",
    "RUN_TIME",
]
# Band edges in log10 space, as in the original implementation:
# a value v is banded as digitize(log10(v + 1), edges).
BYTE_EDGES = [0, 3, 6, 9, 12]      # 1 KB, 1 MB, 1 GB, 1 TB boundaries
COUNT_EDGES = [0, 1, 2, 3, 4]      # 1, 10, 100, 1,000, 10,000
EDGES = {
    "TOTAL_POSIX_BYTES_READ": BYTE_EDGES,
    "TOTAL_POSIX_BYTES_WRITTEN": BYTE_EDGES,
    "TOTAL_POSIX_OPENS": COUNT_EDGES,
    "NPROCS": COUNT_EDGES,
    "RUN_TIME": COUNT_EDGES,
}


def exact_signature(row):
    raw = "|".join(str(row[m]) for m in SIG_METRICS)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def bucketed_signature(row):
    bands = [
        int(np.digitize(np.log10(row[m] + 1.0), EDGES[m])) for m in SIG_METRICS
    ]
    return "-".join(map(str, bands))


def route(df):
    bytes_total = df["TOTAL_POSIX_BYTES_READ"] + df["TOTAL_POSIX_BYTES_WRITTEN"]
    l1 = (
        df["EXE_NAME_GENID"].isna()
        | (df["TOTAL_POSIX_OPENS"] == 0)
        | (df["NPROCS"] == 0)
        | ((bytes_total == 0) & (df["RUN_TIME"] > 600))
    )
    # Layer-2 thresholds as used in the original evaluation run
    # (per-year p95 reference values from the original baseline
    # computation; recorded verbatim from the original implementation).
    BASELINE_P95 = {
        2018: {"written": 1.4e12, "read": 1.0e12},
        2020: {"written": 675.4e6, "read": 500.0e6},
        2021: {"written": 3.3e9, "read": 3.0e9},
        2022: {"written": 1.3e9, "read": 1.0e9},
        2023: {"written": 1.4e12, "read": 103.0e9},
    }
    crossed = pd.Series(False, index=df.index)
    for year, g in df.groupby("year"):
        t = BASELINE_P95.get(int(year))
        if t is None:
            continue
        crossed.loc[g.index] |= (g["TOTAL_POSIX_BYTES_WRITTEN"] > t["written"]) | (
            g["TOTAL_POSIX_BYTES_READ"] > t["read"]
        )
    l2_only = crossed & ~l1
    return l1, crossed, l2_only


if __name__ == "__main__":
    frames = [pd.read_csv(f) for f in sorted(glob.glob("theta_*_sample.csv"))]
    if not frames:
        raise SystemExit("No theta_*_sample.csv files found — run data/extract_samples.py first.")
    df = pd.concat(frames, ignore_index=True)

    l1, crossed, l2_only = route(df)
    routed = df[l1 | l2_only].copy()
    n = len(df)

    print(f"total jobs:            {n}")
    print(f"routed to registry:    {len(routed)} ({100*len(routed)/n:.1f}%)   [paper: 1,957 / 78.3%]")
    print(f"  by Layer 1:          {int(l1.sum())}   [documented: 1,877]")
    print(f"  by Layer 2 only:     {int(l2_only.sum())}   [documented: 80]")
    print(f"  classifiable:        {n - len(routed)}   [documented: 543]")
    print("Layer-1 reasons [documented: null 1,252 | zero-opens 726 | blind-spot 484]:")
    bytes_total = df["TOTAL_POSIX_BYTES_READ"] + df["TOTAL_POSIX_BYTES_WRITTEN"]
    print(f"  EXE_NAME_GENID null: {int(df['EXE_NAME_GENID'].isna().sum())}")
    print(f"  zero POSIX opens:    {int((df['TOTAL_POSIX_OPENS'] == 0).sum())}")
    print(f"  blind-spot:          {int(((bytes_total == 0) & (df['RUN_TIME'] > 600)).sum())}")

    for name, fn, exp_states, exp_rate in [
        ("bucketed", bucketed_signature, 141, 92.8),
        ("exact", exact_signature, 1659, 15.2),
    ]:
        sigs = routed.apply(fn, axis=1)
        states = sigs.nunique()
        recur = len(sigs) - states
        print(f"\n{name} signatures   [paper: {exp_states} states, {exp_rate}% recurrence]")
        print(f"  distinct states:   {states}")
        print(f"  recurrences:       {recur} ({100*recur/len(sigs):.1f}%)")
        print(f"  deduplication:     {len(sigs)/states:.1f}x")
        if name == "bucketed":
            cross = (
                routed.assign(sig=sigs)
                .groupby("sig")["year"].nunique()
            )
            print(f"  cross-year states: {int((cross >= 2).sum())}   [paper: 32]")

    # Job 5 signature check
    job5 = {"TOTAL_POSIX_BYTES_READ": 40.1e9, "TOTAL_POSIX_BYTES_WRITTEN": 41.3e9,
            "TOTAL_POSIX_OPENS": 1871, "NPROCS": 512, "RUN_TIME": 2636}
    print(f"\nJob 5 bucketed signature: {bucketed_signature(job5)}   [paper: 4-4-4-3-4]")
