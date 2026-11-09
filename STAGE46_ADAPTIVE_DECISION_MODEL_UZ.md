# Stage 46 — Adaptive Scoring & Decision Rules

## Purpose

Select the next useful learning action from evidence already stored in IELTS Boost without replacing the four compulsory skill blocks or claiming a formal IELTS score.

## Reading and Listening

- Primary measure: answer-key-verified raw accuracy.
- Minimum sample gate: 3 independent attempts.
- Existing Stage 45 anti-duplication policy applies: repeating an identical prompt updates its latest result but does not inflate independent sample count.
- Where a listening source does not provide a verified answer key, the engine does not invent raw accuracy. The in-app question bank can still provide objective results.

## Writing and Speaking

- Four criteria are kept separate.
- At least 3 of 4 criteria must have at least 2 recorded observations before criterion records become a primary diagnostic signal.
- Stage 44 rubric and weighting rules remain in place. Writing Task 2 remains twice the weight of Task 1 in the combined writing practice index on days requiring both.
- Any stored row that comes from learner self-review is disclosed as such. It cannot be presented as independent examiner scoring.
- Speaking pronunciation requires audio evidence; transcript-only analytics cannot measure pronunciation.

## Trend and error signals

- Falling trend: minimum 4 scored sessions; drop threshold at or below -0.5 internal points.
- Repeated error logs are grouped by skill and error category and may trigger targeted repair.
- Evidence coverage is a data-quality signal, not proof of answer correctness.

## Adaptive plan contract

- Gentle: at most 1 extra action.
- Balanced: at most 2 extra actions.
- Full: at most 3 extra actions.
- Four daily skills remain mandatory.
- No timer or required daily duration is introduced (`timeLimit: null`).
- An adaptive plan is a recommendation only. It must not silently skip, rewrite or mark complete any core day.

## Explicit limitations

- Deterministic local rules; no generative AI backend.
- Not an IELTS examiner and not an official IELTS band conversion.
- Recommendations are only as reliable as the source data.
