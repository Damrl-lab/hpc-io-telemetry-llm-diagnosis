"""Deterministic opens-per-process feature rule.

Applicability: the rule applies if and only if the job has nonzero
POSIX opens (and nonzero NPROCS). For applicable jobs it computes
r = TOTAL_POSIX_OPENS / NPROCS and assigns one of three access-pattern
classes from r (classification exactly as in the original evaluation):
  - file-per-process          when 1 <= r <= 10
  - shared-file N-to-1        when r < 1 (fewer opens than processes)
  - many-files-per-process    otherwise (r > 10)

Jobs with zero POSIX opens are routed to the registry with no class
guessed — the rule's own applicability precondition.

Backs: Sec. VI-D of the paper (deterministic feature rule).

VALIDATION TARGETS (from the paper, on the 2,500-record sample) —
every value below is reproduced exactly by this script:
  - applicable: 1,774 of 2,500 (71.0%); routed (zero opens): 726 (29.0%)
  - per-year applicable/routed:
      2018: 328/172 | 2020: 251/249 | 2021: 454/46 |
      2022: 355/145 | 2023: 386/114
  - class shares among applicable jobs:
      many-files-per-process 947 (53.4%) | file-per-process 669 (37.7%) |
      shared-file N-to-1 158 (8.9%)
  - Job 3 check: 192 / 48 = 4.00 -> file-per-process
  - Job 1 check: 2,104 / 512 = 4.11 -> file-per-process

Developed with AI assistance (Claude, Anthropic), directed and validated
by the authors. See the paper's AI-generated content disclosure.
"""

import glob
import pandas as pd

def classify(opens, nprocs):
    if opens <= 0 or nprocs <= 0:
        return "routed-to-registry"
    r = opens / nprocs
    if 1 <= r <= 10:
        return "file-per-process"
    if r < 1:
        return "shared-file-N-to-1"
    return "many-files-per-process"


if __name__ == "__main__":
    frames = [pd.read_csv(f) for f in sorted(glob.glob("theta_*_sample.csv"))]
    if not frames:
        raise SystemExit("No theta_*_sample.csv files found — run data/extract_samples.py first.")
    df = pd.concat(frames, ignore_index=True)

    df["class"] = [
        classify(o, n) for o, n in zip(df["TOTAL_POSIX_OPENS"], df["NPROCS"])
    ]
    counts = df["class"].value_counts()
    total = len(df)
    applicable = total - counts.get("routed-to-registry", 0)

    print(f"total jobs:        {total}")
    print(f"rule-applicable:   {applicable} ({100*applicable/total:.1f}%)   [paper: 1,774 / 71.0%]")
    print(f"routed (0 opens):  {counts.get('routed-to-registry', 0)} "
          f"({100*counts.get('routed-to-registry', 0)/total:.1f}%)   [paper: 726 / 29.0%]")
    print("\nclass shares among applicable jobs [paper: many 53.4% | fpp 37.7% | N-to-1 8.9%]:")
    for c in ["many-files-per-process", "file-per-process", "shared-file-N-to-1"]:
        n = counts.get(c, 0)
        print(f"  {c:24s} {n:5d}  ({100*n/applicable:.1f}%)")

    print(f"\nJob 3 check: 192 opens / 48 procs -> {classify(192, 48)}  [paper: file-per-process]")
    print(f"Job 1 check: 2104 opens / 512 procs -> {classify(2104, 512)}  [paper: file-per-process]")
