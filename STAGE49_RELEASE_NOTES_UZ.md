# Stage 49 Release Notes — 49.0.0

## Added
- Responsive mobile and accessibility layer.
- Same-origin script CSP, strict-origin referrer policy.
- Project-subpath-relative PWA manifest and Service Worker root.
- Online/offline chip and explanatory offline banner.
- Backup envelope v2 with SHA-256 checksum.
- Backup import validation: 40MB limit, required structures, nesting/node budget, forbidden keys and checksum verification.
- Pre-import safety snapshot download.
- Deep merge of imported state with new application defaults.
- Persistent-storage request and browser/device diagnostics.

## Preserved
- 84-day Academic curriculum and all 4 mandatory skills.
- Stage 42 Speaking transcript workflow and existing local storage namespace.
- IndexedDB database `IELTSBoostMedia`.
- Stage 42 audio cache `ielts-boost-stage42-audio-v3`.
- Stage 47 Task 1, listening, 336 skill resource mapping.
- Stage 48 vocabulary index, daily 672-word core and SRS.

## Known limitations
- JSON backup excludes IndexedDB audio blobs.
- Local progress is not encrypted at rest and not cloud-synced.
- Persistent storage depends on browser grant.
- First visit requires network for application shell; audio is cached when requested.
- Full Chromium E2E blocked by `ERR_BLOCKED_BY_ADMINISTRATOR` before localhost navigation.
- Physical Samsung A14 acceptance pending.
