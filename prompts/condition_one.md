# Condition One — minimal prompt

Condition One consists of the job record followed by the four diagnostic
questions below, with no further instructions. Together with the
structured prompt in `condition_two_structured_prompt.txt` (Fig. 1 of the
paper), these constitute the complete prompt material of the experiment
(Sec. IV of the paper).

The four diagnostic questions, asked in this order for every job:

1. What is currently happening with this job's I/O behavior?
2. Is this normal for an HPC job or something unusual?
3. What is causing the patterns you observe?
4. What should the storage system operator do right now?

Model: Llama 3.3 70B. Responses were graded against deterministic
criteria written before grading, under the four-label taxonomy of
Sec. IV-B (Correct, Missing, Partial, Resolved-by-structure; judgments
labeled Incorrect / Unsupported / Acceptable per Sec. IV-B).
