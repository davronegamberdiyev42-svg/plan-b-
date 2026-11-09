# Stage 46 — Release Notes

## Adaptive Learning & Intelligence Engine

- Added `assets/js/core/adaptive-engine.js` (46.0.0), a deterministic and explainable local decision engine.
- Added an **Intelligence** tab to the learning analytics dashboard.
- Reading/Listening answer-key evidence is used as a primary objective signal only after at least 3 independent samples.
- Writing/Speaking criterion records require at least 3 criteria with 2 observations each; saved learner self-review is not represented as an independent examiner score.
- Declining trend requires at least 4 scored sessions.
- Repeated error signals and Stage 45 laboratory outcomes inform recommendations.
- Adaptive plans add at most 1–3 optional focus steps; all 4 compulsory daily skills and the full 84-day plan stay intact. No daily time limit is introduced.
- The Criterion Map was relabelled to avoid implying that self-review values alone prove mastery.
- Runtime metadata now identifies Stage 46.0.0.
- Service Worker precaches the new module; shell cache is `shell-v7` and the existing Listening audio cache name is retained.

## Verification

- Stage 46 engine + app wiring: 47/47 PASS.
- Stage 41: 21/21 PASS.
- Stage 42: 23/23 PASS (mocked lifecycle; physical device acceptance remains pending).
- Stage 43: 39/39 PASS.
- Stage 44: 30/30 PASS.
- Stage 45: 33/33 PASS.
- Local HTTP static resource smoke: 10/10 PASS.
- JavaScript module and Service Worker syntax checks: PASS.

## Limitations

The advisor is not connected to Claude, ChatGPT or another generative model. It is not an IELTS examiner and does not assign an official IELTS band. Full browser E2E and Samsung A14 hardware acceptance remain pending.

## Stage 47

The user-requested Resource Integration & Verification stage is specified but has **not** started. It awaits confirmation of (1) original IELTS-style charts rather than copies of Barron's protected graphics and (2) official embeds/links only, with episode-level content screening and no downloading/re-hosting.
