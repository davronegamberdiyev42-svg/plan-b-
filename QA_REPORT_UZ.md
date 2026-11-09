# IELTS Boost — Current QA Report

**Build:** 2026-11-08  
**Release:** `49.0.0`  
**Target:** GitHub Pages project subpath `https://davronegamberdiyev42-svg.github.io/plan-b-/`

## Stage 49 automated QA

**Result: 76 / 76 PASS.**

- 19,000 vocabulary records: IDs/headwords unique; actual gloss/IPA/POS coverage reported without inflation.
- 84 daily vocabulary sets / 672 distinct items verified.
- 61-article supplement and 864 sentence patterns retained.
- Stage 42 transcript components and audio storage regression preserved.
- Stage 47 336-skill resource map and Task 1 visual engine preserved.
- Stage 49 CSP, relative manifest, safe backup, state merge, device diagnostics and responsive/a11y CSS checks passed.
- JavaScript syntax: app runtime, backup engine, vocabulary engine, Task 1 engine, adaptive engine and service worker passed.
- Backup engine: 10/10 pure unit assertions.
- HTTP smoke: 13/13 resources returned HTTP 200.

## Inherited regression suites

| Suite | Result |
|---|---:|
| Stage 41 | 21/21 PASS |
| Stage 42 | 23/23 PASS |
| Stage 43 | 39/39 PASS |
| Stage 44 | 30/30 PASS |
| Stage 45 | 33/33 PASS |
| Stage 46 | 47/47 PASS |
| Stage 47 Task 1 | 19/19 PASS |
| Stage 47 integration | 40/40 PASS |

The inherited QA scripts were updated to expect the new active release title and Service Worker cache namespace (`ielts-boost-stage50-shell-v12`). This updates test expectations, not historical curriculum data or user progress keys.

## Browser/device acceptance — not yet passed

Chromium + Playwright was attempted against a local HTTP server. The execution environment returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` before page navigation. Therefore no browser-render, mobile-overflow, download UI, or console assertions ran. Status is `BLOCKED_BY_ENVIRONMENT`, not PASS and not a product failure.

Samsung A14 physical tests remain pending: install, microphone/transcript, PWA scope, offline shell/audio and backup import/export. See `STAGE49_MOBILE_ACCEPTANCE_UZ.md`.

## Important product boundaries

- JSON backup includes app progress, scores, drafts, errors, SRS and settings; it **does not** include IndexedDB audio blobs.
- SHA-256 is integrity checking, not encryption or user authentication.
- Local progress is not encrypted at rest and is not cloud-synced.
- Persistent storage depends on browser permission.
- The app shell is cached by Service Worker; audio is cached when requested, so a first visit still requires connection.
- Web Speech API support varies by browser and may require internet; manual transcript fallback remains.

## Acceptance decision

Stage 49 is ready for the Stage 50 full release validation phase based on static, data, module, regression and HTTP checks. It is **not yet certified as a physical-device/browser-accepted release**.
