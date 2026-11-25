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
| `data/extract_samples.py` | Deterministic 500-records-per-year sampling from the public CSVs | Sec. III |
| `baselines/per_year_percentiles.py` | Per-year percentile references; facility-relative magnitude judgment | Sec. VI-B |
| `feature_rule/opens_per_process.py` | Opens-per-process rule and access-pattern classification | Sec. VI-D |
| `registry/route_and_signatures.py` | Two-layer coverage routing; exact + bucketed state signatures | Secs. VI-C, VI-E |
| `provenance/exe_name_genid_null_rates.py` | EXE_NAME_GENID null-rate analysis by year | Sec. VI-F |

## Reproducing the paper's numbers

1. Download the public ALCF Theta Darshan annual CSV files (2018, 2020,
   2021, 2022, 2023) from the [ALCF public data repository](https://reports.alcf.anl.gov/data/).
2. Run `python3 data/extract_samples.py` in the folder containing the
   CSVs. Sampling is deterministic (`random_state=42`), producing
   `theta_<year>_sample.csv` (500 records each).
3. Run each analysis script in the folder containing the sample files:

```
python3 baselines/per_year_percentiles.py
python3 feature_rule/opens_per_process.py
python3 registry/route_and_signatures.py
python3 provenance/exe_name_genid_null_rates.py
```

Each script prints its results next to the corresponding published
number. Key expected values:

| Result | Expected | Paper |
|---|---|---|
| Feature-rule applicability | 1,774 / 2,500 (71.0%) | Sec. VI-D |
| Zero-opens jobs routed | 726 (29.0%) | Sec. VI-D |
| Jobs routed to registry | 1,957 (78.3%) | Sec. VI-E |
| Distinct states (bucketed signature) | 141 (13.9× deduplication) | Sec. VI-E |
| Instance-level recurrence | 92.8% | Sec. VI-E |
| Cross-year states | 32 | Sec. VI-E |
| Job 5 write volume percentile (2023) | 71st (p95 ≈ 2,748 GB) | Sec. VI-B |
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

## AI assistance

The analysis scripts were developed with AI assistance (Claude,
Anthropic), directed and validated by the authors, as disclosed in the
paper. All study design, experiments, data analyses, results, and
conclusions are the authors' own.

## Acknowledgments

This work was supported by NSF grants CSR-2402328, CAREER-2338457,
CSR-2406069, CSR-2323100, and CCF-2621730. This research used data from
the Argonne Leadership Computing Facility, a U.S. Department of Energy
Office of Science user facility supported under Contract
DE-AC02-06CH11357.
