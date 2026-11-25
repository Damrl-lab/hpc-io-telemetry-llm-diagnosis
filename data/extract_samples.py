"""Extract the 2,500-record evaluation sample from the public ALCF Theta
Darshan annual CSV files (500 records per year: 2018, 2020, 2021, 2022,
2023).

This reproduces the sampling used throughout the paper: for each annual
file, read the first 5,000 rows (restricted to the columns below) and
draw 500 of them with a fixed seed (random_state=42), so the sample is
deterministic given the public CSVs.

Input : the public ALCF Theta Darshan annual CSVs (not redistributed
        here; place them next to this script or edit the paths below).
Output: theta_<year>_sample.csv, one per year.

Backs: Sec. III (Dataset and Case Selection) of the paper.

Developed with AI assistance (Claude, Anthropic), directed and validated
by the authors. See the paper's AI-generated content disclosure.
"""

import pandas as pd

FILES = {
    "2018": "ANL-ALCF-DARSHAN-THETA_20180101_20181231.csv",
    "2020": "ANL-ALCF-DARSHAN-THETA_20200101_20201231.csv",
    "2021": "ANL-ALCF-DARSHAN-THETA_20210101_20211231.csv",
    "2022": "ANL-ALCF-DARSHAN-THETA_20220101_20221231.csv",
    "2023": "ANL-ALCF-DARSHAN-THETA_20230101_20231231.csv",
}

# Union of the columns used across the paper's analyses (baselines,
# feature rule, registry routing, provenance).
COLS = [
    "TOTAL_POSIX_BYTES_WRITTEN",
    "TOTAL_POSIX_BYTES_READ",
    "TOTAL_POSIX_OPENS",
    "TOTAL_POSIX_READ_TIME",
    "TOTAL_POSIX_WRITE_TIME",
    "TOTAL_POSIX_META_TIME",
    "NPROCS",
    "RUN_TIME",
    "EXE_NAME_GENID",
    "COBALT_JOBID",
]

if __name__ == "__main__":
    for year, fname in FILES.items():
        try:
            df = pd.read_csv(fname, usecols=lambda c: c in COLS, nrows=5000)
            sample = df.sample(n=min(500, len(df)), random_state=42)
            sample["year"] = year
            sample.to_csv(f"theta_{year}_sample.csv", index=False)
            print(f"{year}: {len(sample)} rows extracted")
        except FileNotFoundError:
            print(f"{year}: file not found — check filename/path")
