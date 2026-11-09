# Stage 40 — Advanced Mastery Upgrade

## Speaking Studio
- Part 1, Part 2, Part 3, daily challenge alohida transcript state’da saqlanadi.
- Recognition status va segment-specific language selector. ASR started/stopped timestamps saqlanadi.
- Transcript analytics: segment word count, sentence length, lexical diversity/density, filler signals, repeated content words, discourse markers, clause signals, possible grammar patterns, ASR confidence.
- Pronunciation Lab mustaqil MediaRecorder + IndexedDB recorder, replay, target focus, 6 self-review checkpoints. Pronunciation auto-scoring yo‘q.
- Fluency Lab four-part argument plan + live spoken-response transcript.

## Games
- 10 modules preserved; 100 old Power Labs preserved.
- 24 collocation questions; 24 grammar questions, each has explanation and transfer requirement.
- Paraphrase meaning gate: claim, scope, certainty, time.
- Pronunciation round is gated by a real saved audio recording.
- Fluency round requires a saved 25+ word spoken transcript.
- XP, mastery, attempts and adaptive weakest-lab performance board persist.

## Vocabulary
- 19,000 words remain indexed and searchable.
- First 4,000 are IPA cohort, first 4,000 are Uzbek translation lookup pool; first 9,000 definition/phonetic lookup pool.
- Batch lookups (10/20) resume from local cursor and save successful results. Failed lookups are reported; no synthetic/gloss-fabrication.
- IPA may be lexicon/eSpeak-generated; MyMemory is machine translation and requires sense verification.

## PWA
- Manifest id/scope/start_url explicit for `/plan-b-/`.
- any + maskable icon PNGs in correct pixel dimensions.
- App metadata deduplicated; `rel=manifest` absolute project path.
- Stage40 service-worker cache namespace; core app/icon shell install is atomic, optional favicons do not block SW install; audio range requests cached.
- Diagnostic shows per-icon decode, scope, SW active/controller, standalone mode and install prompt event separately.
