"""Per-year historical baseline: percentile reference distributions for
Theta I/O volume metrics, computed from the 2,500-record sample.

For each sampled year this script computes percentile references for
TOTAL_POSIX_BYTES_WRITTEN and TOTAL_POSIX_BYTES_READ among the
*write-active* (resp. read-active) records — records with a nonzero
value for the metric — and locates an arbitrary job's value within that
reference.

Backs: Sec. VI-B of the paper (historical baseline evaluation).

VALIDATION TARGETS (from the paper, on the 500/year sample with
random_state=42):
  - 2023 write-active p95 of TOTAL_POSIX_BYTES_WRITTEN ~= 2,748 GB
  - Job 5 (COBALT 639510), 41.3 GB written -> 71st percentile of the
    2023 write-active sampled records
If a run does not reproduce these, do not push results — investigate.

Developed with AI assistance (Claude, Anthropic), directed and validated
by the authors. See the paper's AI-generated content disclosure.
"""

import glob
import pandas as pd

GB = 1e9
METRICS = ["TOTAL_POSIX_BYTES_WRITTEN", "TOTAL_POSIX_BYTES_READ"]
PCTS = [50, 90, 95, 99]


def load_samples(pattern="theta_*_sample.csv"):
    frames = [pd.read_csv(f) for f in sorted(glob.glob(pattern))]
    if not frames:
        raise SystemExit("No theta_*_sample.csv files found — run data/extract_samples.py first.")
    return pd.concat(frames, ignore_index=True)


def reference_table(df):
    rows = []
    for year, g in df.groupby("year"):
        for m in METRICS:
            active = g.loc[g[m] > 0, m]
            row = {"year": year, "metric": m, "active_n": len(active)}
            for p in PCTS:
                row[f"p{p}_GB"] = round(active.quantile(p / 100) / GB, 1)
            rows.append(row)
    return pd.DataFrame(rows)


def percentile_of(df, year, metric, value):
    """Percentile of `value` among the active (nonzero) sampled records
    of `metric` in `year` — the facility-relative magnitude judgment of
    Sec. VI-B."""
    active = df.loc[(df["year"].astype(str) == str(year)) & (df[metric] > 0), metric]
    return 100.0 * (active <= value).mean()


if __name__ == "__main__":
    df = load_samples()
    table = reference_table(df)
    print(table.to_string(index=False))

    # Job 5 check (the prediction the reference corrected):
    job5_written = 41.3 * GB
    pct = percentile_of(df, 2023, "TOTAL_POSIX_BYTES_WRITTEN", job5_written)
    print(f"\nJob 5: 41.3 GB written -> {pct:.0f}th percentile of 2023 "
          f"write-active sampled records (paper: 71st)")
