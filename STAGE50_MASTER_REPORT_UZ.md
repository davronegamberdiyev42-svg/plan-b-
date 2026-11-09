# IELTS Boost — Stage 50 Final Release Master Report

**Release:** 50.0.0  
**Sana:** 2026-11-09  
**Holat:** Yakuniy build yaratildi; avtomatik QA o‘tdi. Chromium va real qurilma acceptance testlari tashqi muhitda yakunlanishi kerak.

## 1. Yakuniy mahsulot

IELTS Boost — 84 kunlik mustaqil IELTS Academic tayyorgarlik platformasi. To‘rtta skillning barchasi har kuni majburiy: Reading, Listening, Writing va Speaking. Kunlik daqiqalar limiti yo‘q. 10 ta asosiy laboratoriya qo‘shimcha mashq sifatida ishlaydi.

## 2. Kontent inventari

| Tarkib | Yakuniy miqdor |
|---|---:|
| O‘quv kunlari | 84 |
| Majburiy skill sessiyalari | 336 |
| Reading savollari | 840 |
| Listening savollari | 420 |
| Listening MP3 | 84 |
| Writing Task 1 original vizual datasetlari | 84 |
| Task 1 vizual turlari | 6 × 14 |
| Writing Task 2 promptlari | 84 |
| Speaking Part 1 / Part 2 / Part 3 | 252 / 84 / 252 |
| Asosiy laboratoriyalar | 10 |
| Qo‘shimcha maqolalar | 61 |
| Sentence Patterns | 864 |
| Vocabulary indeks yozuvlari | 19 000 |
| To‘liq offline bilingual glossary | 677 |
| 84 kunlik asosiy vocabulary | 672 |
| Listening tashqi resurs xaritasi | 84 kunlik assignment; 28 noyob resurs qayta ishlatiladi |

84 ta MP3 `ffprobe` orqali tekshirildi: **84/84 container/stream tekshiruvi o‘tdi**.

## 3. Asosiy tizimlar

- Stage 42: Speaking audio yozish va browser SpeechRecognition transcript mexanizmlari ajratilgan; reconnect/manual-edit xavfsizligi bor. Server-side STT yo‘q.
- Stage 43: HTML/CSS/JS/data modullarga ajratilgan. Katta `app-data.json` hali bitta katta resurs bo‘lib yuklanadi; target qurilmada performance o‘lchanishi kerak.
- Stage 44: 1–10 ichki scoring, skill mezonlari va baho manbasi ajratilgan. Bu rasmiy IELTS band converter emas.
- Stage 45: 10 ta laboratoriyada diagnostika, maqsadli mashq va transfer yo‘llari mavjud.
- Stage 46: yetarli dalil bo‘lgandagina zaiflik/trend xulosasi beruvchi lokal adaptive advisor. Generativ AI backend ulanmagan.
- Stage 47: 336 skill-resource map, 84 Task 1 original visual dataset, 84 kunlik Listening companion xaritasi.
- Stage 48: Vocabulary qamrovi ochiq ko‘rsatiladi; SRS history/review va transfer completion qoidalari kuchaytirilgan.
- Stage 49: responsive UX, CSP, local-first diagnostics, checksum backup/restore, offline shell/audio caching.
- Stage 50: final release identity; deployment-relative PWA manifest validator; Settings acceptance panel; yakuniy regression suite.

## 4. Stage 50’da tuzatilgan nuqson

Oldingi PWA readiness tekshiruvi repository path `/plan-b-/` ni hard-code qilgan edi. Manifest esa Stage 49’dan boshlab relative `./` scope ishlatadi. Bu boshqa repository subpath’da noto‘g‘ri diagnostika chiqarishi mumkin edi. Stage 50’da `pwa-validation.js` qo‘shilib, `id`, `scope`, `start_url` manifest URL’iga nisbatan yechiladi va joriy sahifaning scope ichida ekanligi tekshiriladi. Eski PWA check yangi validatorga yo‘naltirildi.

## 5. QA natijalari

| Suite | Natija |
|---|---:|
| Stage 50 full final QA | **59/59 PASS** |
| Stage 50 cross-engine invariants | **36/36 PASS** |
| Stage 48 vocabulary engine | 34/34 PASS |
| Stage 49 backup engine | 10/10 PASS |
| Stage 46 adaptive engine | 47/47 PASS |
| Stage 47 Task 1 engine | 19/19 PASS |
| Stage 41 curriculum/transcript regression | 21/21 PASS |
| Stage 42 transcript regression | 23/23 PASS |
| Stage 43 architecture regression | 39/39 PASS |
| Stage 44 scoring regression | 30/30 PASS |
| Stage 45 laboratory regression | 33/33 PASS |
| Stage 47 resource integration | 40/40 PASS |
| Local HTTP resource smoke | 21/21 HTTP 200 |
| Audio validation | 84/84 valid |

Regression suite natijalari alohida suite’lardir; ularning sonlarini bitta umumiy mustaqil assertion soni sifatida qo‘shib yubormaslik kerak.

## 6. Acceptance cheklovlari — yashirilmaydi

### Chromium E2E

Stage 50 Playwright/Chromium acceptance urinishida execution environment `ERR_BLOCKED_BY_ADMINISTRATOR` bilan localhost navigatsiyasini to‘xtatdi. **0/1 flow boshlang‘ich assertion bajarildi**; bu browser PASS ham, product FAIL ham emas — `BLOCKED_BY_ENVIRONMENT`. Hisobot: `STAGE50_CHROMIUM_ACCEPTANCE.json`.

### Samsung Galaxy A14

Haqiqiy qurilmada quyidagi acceptance sinovlari foydalanuvchi tomonidan bajarilishi kerak: GitHub Pages yuklanishi, PWA install, offline shell/audio, microphone/MediaRecorder, live transcript yoki manual fallback, backup/restore, 320–430px ekran, barcha 4 skill va audio playback. Checklist: `STAGE50_MOBILE_ACCEPTANCE_UZ.md`.

### Mahsulot cheklovlari

- Progress LocalStorage/browser profile’da; cloud sync yo‘q.
- App-side at-rest encryption yo‘q. Qurilma profilingni himoyalash lozim.
- JSON backup IndexedDB audio bloblarini o‘z ichiga olmaydi; audio kliplarni alohida eksport qilish kerak.
- SHA-256 checksum fayl yaxlitligini tekshiradi, shifrlash yoki foydalanuvchini autentifikatsiya qilish emas.
- Live transcript browser SpeechRecognition’ga bog‘liq; mavjudlik va internet talabi browserga qarab farq qiladi. Server-side STT ulanmagan.
- Tashqi TED/YouTube/podcast havolalari va captionlar provayderga bog‘liq; ular offline kafolatlanmaydi.
- `app-data.json` katta initial payload bo‘lib qolmoqda. Lighthouse/Web Vitals yoki Samsung real-device performance balli da’vo qilinmaydi.
- AI backend yo‘q; adaptive advisor deterministik/local qoidalarga asoslangan.
- Bu mustaqil o‘quv mahsuloti, rasmiy IELTS mahsuloti emas va band score kafolatlamaydi.

## 7. Yakuniy xulosa

Stage 50 release build va avtomatik qabul testlari tayyor. “Barcha qurilmalarda 100% tekshirildi” degan da’vo qilinmaydi. Release’ni ommaga tarqatishdan avval deploy target repository nomini tekshirish va Samsung A14 acceptance checklistini bajarish shart.


## Final Plan-B package patch
Current target is GitHub repository `plan-b-` (https://davronegamberdiyev42-svg.github.io/plan-b-/). The previous hard-coded Stage 40 PWA path was converted to project-relative resolution. A startup watchdog and explicit app boot-ready/failure markers were added. Service Worker shell cache is v12 while the dedicated audio cache remains unchanged. All 84 MP3 files and the main 84-day app-data JSON were checked byte-for-byte against the uploaded source package. Static checks and Stage 50 JS engine tests pass; live hosting and physical-device acceptance remain pending.
