# Benchmarking Coverage-Aware LLM Diagnosis on HPC I/O Telemetry

Analysis scripts for the paper:

> Anxhela Nano, Mayur Akewar, and Janki Bhimani.
> "Benchmarking Coverage-Aware LLM Diagnosis on HPC I/O Telemetry."
> BPOD Workshop, IEEE International Conference on Big Data
> (IEEE BigData 2026), Phoenix, AZ, USA, December 2026.

The paper evaluates when large language models can and cannot be trusted
to diagnose HPC I/O telemetry (ALCF Theta Darshan logs, 2017–2023). It
identifies **retrieval-dependent normalization** as the key failure mode
— the model reasons well over patterns it can see but cannot judge
magnitudes without historical context — and evaluates a deterministic
evidence layer (a feature rule, per-year historical baselines, and an
unknown-state registry) on 2,500 production job records.

## Repository contents

| Path | Purpose | Backs (in paper) |
|---|---|---|
| `prompts/condition_one.md` | Minimal prompt: job record + four diagnostic questions | Sec. IV |
| `prompts/condition_two_structured_prompt.txt` | Structured analyst prompt (verbatim Fig. 1) | Fig. 1, Sec. IV |
| `data/` | The 2,500-record evaluation sample + the deterministic extraction script | Sec. III |
| `baselines/per_year_percentiles.py` | Per-year percentile references; facility-relative magnitude judgment | Sec. VI-B |
| `feature_rule/opens_per_process.py` | Opens-per-process rule and access-pattern classification | Sec. VI-D |
| `registry/route_and_signatures.py` | Two-layer coverage routing; exact + bucketed state signatures | Secs. VI-C, VI-E |
| `provenance/exe_name_genid_null_rates.py` | EXE_NAME_GENID null-rate analysis by year | Sec. VI-F |

## Reproducing the paper's numbers

`data/` contains the 2,500-record evaluation sample (500 records per
year, all analysis columns), derived from the public ALCF dataset. To
reproduce it from scratch instead, download the annual CSVs from the
[ALCF public data repository](https://reports.alcf.anl.gov/data/) and
run `data/extract_samples.py` (deterministic, `random_state=42`).

Run the analyses from inside `data/` (the scripts read
`theta_*_sample.csv` from the current directory):

```
cd data
python3 ../baselines/per_year_percentiles.py
python3 ../feature_rule/opens_per_process.py
python3 ../registry/route_and_signatures.py
python3 ../provenance/exe_name_genid_null_rates.py
```

Each script prints its results next to the corresponding published
number. **All of the following are reproduced exactly:**

| Result | Value | Paper |
|---|---|---|
| Feature-rule applicability | 1,774 / 2,500 (71.0%); 726 routed (29.0%) | Sec. VI-D |
| Access-pattern class shares | many 947 (53.4%) · fpp 669 (37.7%) · N-to-1 158 (8.9%) | Sec. VI-A |
| Jobs routed to registry | 1,957 (78.3%) — Layer 1: 1,877; Layer 2: 80; classifiable: 543 | Sec. VI-E |
| Distinct states (bucketed signature) | 141 (13.9× deduplication, 1,816 recurrences) | Sec. VI-E |
| Instance-level recurrence | 92.8% | Sec. VI-E |
| Cross-year states | 32 | Sec. VI-E |
| Exact-signature bound | 1,659 states, 15.2% recurrence | Sec. VI-E |
| Job 5 write volume percentile (2023) | 71st (write-active p95 = 2,748 GB) | Sec. VI-B |
| Job 5 state signature | 4-4-4-3-4 | Sec. VI-E |
| EXE_NAME_GENID null rates | 0 / 0 / 88.8 / 75.0 / 86.6 % | Sec. VI-F |

The LLM stage itself (Llama 3.3 70B under the two prompt conditions) is
a proposed integration in the architecture; the prompting experiment of
Sec. IV used the materials in `prompts/` and was graded manually against
pre-defined deterministic criteria, as described in the paper.

## Data

This work uses the publicly released ALCF Theta Darshan dataset
(Argonne Leadership Computing Facility, a U.S. Department of Energy
Office of Science user facility). The dataset is not redistributed here.

Requirements: Python 3 with `pandas` and `numpy`.

## Acknowledgments

This work was supported by NSF grants CSR-2402328, CAREER-2338457,
CSR-2406069, CSR-2323100, and CCF-2621730. This research used data from
the Argonne Leadership Computing Facility, a U.S. Department of Energy
Office of Science user facility supported under Contract
DE-AC02-06CH11357.
