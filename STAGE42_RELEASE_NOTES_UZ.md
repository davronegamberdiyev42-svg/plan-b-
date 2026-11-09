# IELTS Boost Stage 42 — Release Notes

**Release:** 42.0.0  
**Date:** 2026-11-08  
**Type:** Speaking transcript reliability / recovery

### Added
- Segment-aware ASR session controller for Part 1, Part 2, Part 3 and Daily Challenge.
- Final/interim result separation and stable base-text handling across recognizer restarts.
- Per-final-result autosave and per-segment ASR source/language/confidence metadata.
- Bounded reconnect (12) and no-speech stop threshold (2).
- Uzbek status/error handling for permission, network, microphone, language and service failures.
- Explicit manual/keyboard dictation fallback next to each live transcript field.
- Transcript Reliability status panel on Speaking page.
- Protection against late ASR results overwriting manual edits.

### Preserved
- Existing Speaking raw transcript fields and saved transcript content.
- Part-specific audio recordings in IndexedDB.
- Full-session recording flow.
- Legacy progress and local storage namespaces.
- Existing four-skill and 84-day curriculum.

### Fixed / improved
- Reconnect no longer blindly appends every result from a fresh recognition index to the previous text.
- Interim recognition text is not committed as final.
- Switching Part, page or day stops the previous recognition session.
- Changing recognition language requires a clean restart.
- Clear action is segment-specific.

### Limitations
- `SpeechRecognition` remains browser/device-dependent and may use an online service.
- Manual typing / Android keyboard voice typing remains the fallback where live ASR is unsupported.
- No backend is bundled for transcribing an already-saved audio blob. Do not place API provider secrets into the static frontend.
- Physical Samsung A14 acceptance tests remain pending.

### Verification
- Stage 42 QA: 22/22 static + unit + mocked lifecycle checks PASS.
- Stage 41 regression QA: 21/21 PASS.
- Real Android microphone / speech-service QA: PENDING.

Run: `python tools/qa_stage42.py`
