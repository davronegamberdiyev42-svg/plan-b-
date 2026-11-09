# IELTS Boost — Stage 41 release notes

**Release label:** 41.0.0-audit-baseline  
**Date:** 2026-11-08  
**Base application:** Stage 40.0.0

### Included
- `STAGE41_MASTER_AUDIT_UZ.md`
- `STAGE41_REQUIREMENTS_TRACEABILITY_UZ.md`
- `STAGE41_FEATURE_INVENTORY_UZ.csv`
- `STAGE41_QA_RESULTS.json`
- `tools/qa_stage41.py`

### Compatibility
- `index.html`, `manifest.webmanifest`, `sw.js`, original localStorage state keys and audio files are unchanged from the Stage 40 baseline.
- No user progress or IndexedDB records are migrated or deleted in this audit release.
- Deployment target remains the target already declared by the source ZIP: `/plan-b-/`. Verify the actual GitHub repository before publishing.

### Known limitations carried forward
- Live transcription depends on browser SpeechRecognition support, microphone permission and network conditions.
- Saved audio is not automatically transcribed by a bundled server-side STT service.
- Real Samsung A14 microphone, transcription and PWA install tests remain device acceptance items.
