# Stage 49 — Samsung Android Acceptance Checklist

**Target:** Samsung A14, Android + Chrome/Samsung Internet.  
**Current status:** Pending real device execution.

## A. Open and install
- [ ] GitHub Pages project URL opens with HTTPS.
- [ ] App loads; no blank page or missing module warning.
- [ ] Browser menu offers Install app / Add to Home screen.
- [ ] Installed shortcut opens the same project subpath.
- [ ] App icon and standalone layout are correct.

## B. Responsive UX
- [ ] Test portrait widths 320, 360, 390 and 430 CSS px.
- [ ] No full-page horizontal overflow.
- [ ] Bottom navigation does not cover the last action or text.
- [ ] Inputs do not cause unexpected zoom.
- [ ] Tables can scroll horizontally within their own container.
- [ ] Focus and skip-link can be reached using keyboard/accessibility tools.

## C. Offline and audio
- [ ] Open all main pages once while online.
- [ ] Play at least one Listening MP3 so it is cached.
- [ ] Enable airplane mode and reopen app.
- [ ] Cached shell and previously requested MP3 still work.
- [ ] Confirm that external TED/YouTube/Podcast and online lookup are unavailable offline (expected).

## D. Speaking and transcript
- [ ] Grant microphone permission.
- [ ] Record Part 1, stop and replay.
- [ ] Record Part 2 and Part 3 separately.
- [ ] Try live transcript if browser exposes SpeechRecognition.
- [ ] If unavailable, use manual transcript or Samsung Keyboard/Gboard dictation.
- [ ] Reload and verify progress/transcript persistence.
- [ ] Export important audio separately.

## E. Backup / restore
- [ ] Export backup JSON.
- [ ] Confirm checksum metadata exists where Web Crypto is available.
- [ ] Copy backup to a safe folder.
- [ ] Import a known valid test backup and verify day, draft, score and error history.
- [ ] Confirm a pre-import safety snapshot downloads.
- [ ] Try a deliberately modified checksum file; import must reject it.
- [ ] Confirm audio is not part of the JSON backup and remains a separate export.

## F. Diagnostics
- [ ] Settings → Refresh diagnostics.
- [ ] Review Secure Context, Storage, Quota, Microphone, MediaRecorder, ASR and Service Worker rows.
- [ ] Settings → Request persistent storage; record whether browser grants or denies it.

Do not mark this checklist PASS until the tests are carried out on the physical device.
