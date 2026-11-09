# IELTS Boost — Final Release 50.0.0

84 kunlik IELTS Academic platformasi. Har kuni 4 skill majburiy; kunlik vaqt limiti yo‘q. 10 ta asosiy laboratoriya, 1–10 ichki baholash, Reading/Listening evidence workflows, Writing Task 1 original visual intelligence, Speaking Studio/transcript fallback, adaptive learning, Vocabulary SRS, resource library, PWA/offline shell va backup/restore.

## Asosiy tarkib
- 84 kun; 336 majburiy skill sessiyasi.
- 840 Reading savoli; 420 Listening savoli; 84 bundled Listening MP3.
- 84 Task 1 original vizuali (line/bar/pie/table/process/map — har biri 14).
- 84 Task 2 prompti.
- 10 primary labs; 61 supplement maqola; 864 Sentence Patterns.
- 19 000 qidiruv indeksi; 677 complete offline glossary yozuvi; 672 core day-pack.

## Local run
Static project; build tool shart emas. `file://` bilan emas, HTTPS hosting yoki localhost server orqali oching. GitHub Pages uchun barcha fayl/papkalarni repository root’ga ko‘chiring. `manifest.webmanifest` va Service Worker project-relative, GitHub Pages subpath uchun mo‘ljallangan.

## GitHub Pages — Plan-B
1. Repository: `plan-b-`.
2. URL: `https://davronegamberdiyev42-svg.github.io/plan-b-/`.
3. ZIP’ni Extract qil va ichidagi barcha fayl/papkalarni repository root’iga joyla.
4. `index.html`, `assets/`, `data/`, `audio/`, `tools/`, `sw.js`, `manifest.webmanifest` va iconlar root’da bo‘lishi shart.
5. Settings → Pages → Deploy from a branch → `main` → `/(root)`.
6. Saytni HTTPS manzili orqali och; `file://` orqali emas.
7. Birinchi yuklanishda internet yoqilgan bo‘lsin, keyin Chrome menyusidan Install app / Add to Home screen qil.

## Privacy / audio / transcript
- Progress browser profile’da local saqlanadi; cloud sync yo‘q, app-side at-rest encryption yo‘q.
- JSON backup IndexedDB audio bloblarini o‘z ichiga olmaydi; Speaking yozuvlarini alohida eksport qiling.
- SHA-256 checksum encryption emas; u fayl integrity tekshiradi.
- Live SpeechRecognition browser va ba’zan internetga bog‘liq; manual transcript/keyboard dictation fallback bor. Server-side STT bu release’da ulanmagan.
- External TED/YouTube/podcast/caption availability provider va internetga bog‘liq.

## Halol qabul holati
- Automated Stage50 QA: 59/59 PASS.
- Stage50 engine: 36/36 PASS.
- Audio: 84/84 ffprobe valid.
- HTTP smoke: 21/21.
- Browser E2E: `BLOCKED_BY_ENVIRONMENT` — build muhiti localhost navigatsiyasini `ERR_BLOCKED_BY_ADMINISTRATOR` bilan blokladi; browser assertion bajarilmadi.
- Samsung Galaxy A14 physical acceptance: pending; `STAGE50_MOBILE_ACCEPTANCE_UZ.md` ga qarang.
- No Lighthouse score claimed; large initial data payload needs real-device performance measurement.
- This is independent practice software, not official IELTS and does not guarantee an IELTS band.

## QA files
`STAGE50_MASTER_REPORT_UZ.md`, `STAGE50_QA_RESULTS.json`, `STAGE50_CHROMIUM_ACCEPTANCE.json`, `STAGE50_MOBILE_ACCEPTANCE_UZ.md`, `STAGE50_KNOWN_LIMITATIONS_UZ.md`.
