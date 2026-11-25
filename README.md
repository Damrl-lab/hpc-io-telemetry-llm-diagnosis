# Benchmarking Coverage-Aware LLM Diagnosis on HPC I/O Telemetry

Analysis scripts for the paper:

> Anxhela Nano, Mayur Akewar, and Janki Bhimani.
> "Benchmarking Coverage-Aware LLM Diagnosis on HPC I/O Telemetry."
> BPOD Workshop, IEEE International Conference on Big Data (IEEE BigData 2026),
> Phoenix, AZ, December 2026.

The paper evaluates when large language models can and cannot be trusted to
diagnose HPC I/O telemetry (ALCF Theta Darshan logs, 2017–2023), identifies
retrieval-dependent normalization as the key failure mode, and evaluates a
deterministic evidence layer - a feature rule, per-year historical baselines,
and an unknown-state registry - on 2,500 production job records.

## Status

The analysis scripts are being finalized and will be released here before the
conference (December 2026).

## Data

This work uses the publicly released ALCF Theta Darshan dataset.
