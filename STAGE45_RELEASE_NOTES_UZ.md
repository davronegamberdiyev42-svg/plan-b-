# Stage 45 Release Notes — 45.0.0

## Added
- `assets/js/core/lab-quality-engine.js` pure quality/adaptive helper module.
- Evidence provenance for P37 lab attempts.
- Distinct-prompt sample gating and weakest objective mode selection.
- Optional fresh transfer challenges for all 10 labs.
- Wrong-answer cause selection and repair-plan capture.
- Reading/Listening transfer source phrase checks.
- Listening transfer full-playback gate.
- Stage 45 evidence overview and explicit practice-index labels.
- Stage 45 QA suite and test matrix.

## Changed
- P37 `/10`/XP history remains but is labelled practice-completion index.
- Lab progress bar now uses recent answer-key accuracy only when 3 distinct objective prompts are available.
- Core P37 objective records are restricted to answer-key labs.
- Daily optional lab rounds are explicitly not a daily requirement.

## Preserved
- 84-day Academic plan and all four mandatory skill sessions each day.
- P37 live 10-lab system.
- Classic 100-mode archive.
- Stage 42 transcript/audio state and audio cache.
- Stage 43 modular shell.
- Stage 44 general skill-scoring engine and assessment history.
- 61-article supplemental library and all audio assets.

## Known limitations
- No external AI API / server backend has been connected.
- Open-ended lab quality still needs independent human/AI criterion review.
- Real Samsung A14 microphone acceptance is pending.
- Chromium E2E navigation was blocked in the build environment; static and Node tests passed instead.
