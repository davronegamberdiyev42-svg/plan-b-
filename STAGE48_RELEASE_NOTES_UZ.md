# Stage 48 Release Notes — Vocabulary & Resource Intelligence

## Yangi imkoniyatlar

- 19,000 vocabulary index uchun qamrovni aniq ko‘rsatadigan data dashboard.
- 672 item’li 84-day core’ning 100% complete offline glossary va dual IPA field qamrovi.
- 677 complete offline glossary record, 4,000 pronunciation-only record va missing-field farqi UI’da oshkor qilinadi.
- 19K search uchun precomputed normalized cache va coverage filters.
- Stage 36, Stage 37 va current local vocabulary cache’lar birlashtiriladi.
- Token/phrase-boundary transfer matcher substring false positive’larni yo‘q qiladi.
- 8-item daily active-recall quiz va 12+ so‘zli lexical transfer.
- Kun tugallanishi: 6/8 exact recall + 2 target terms + 12+ word transfer.
- Source-led collocation note (learner annotation, auto-verification emas).
- SM-2-inspired Again/Hard/Good/Easy SRS; reveal-first gate; last-20 review history.
- Stage 37 legacy SRS/favourite records queue’da saqlanadi va rating paytida migratsiya qilinadi.
- Cambridge discrepancy IPA source metadata qo‘shildi.

## Saqlanganlar

- 84 kun × 4 majburiy skill.
- 84 listening MP3 va Stage 42 audio cache.
- 10 asosiy laboratoriya va Classic arxiv.
- 61 maqola va 864 sentence pattern.
- 84 original Task 1 visual va Stage 47 resource mapping.
- Existing localStorage va IndexedDB namespace.

## QA

- Stage 48: 58/58 PASS.
- Stage 41–47 inherited regression suites: barcha PASS.
- Local HTTP smoke: 11/11 status 200.
- Chromium end-to-end: environment `ERR_BLOCKED_BY_ADMINISTRATOR` sababli pending, PASS emas.
- Samsung A14 physical acceptance: pending.

## Ma’lum cheklovlar

19,000 qidiriladigan yozuv 19,000 to‘liq glossary degani emas. Offline complete glossary 677; daily core 672. CEFR labels estimate. IPA field mavjudligi audio/ekspert verified degani emas. Online lookup draft’lari learner review talab qiladi.
