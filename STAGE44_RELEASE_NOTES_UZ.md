# Stage 44 Release Notes — Intelligent 1–10 Scoring Engine

## Qo‘shildi

- Alohida `assets/js/core/scoring-engine.js` moduli.
- Baholash manbasi, versiyasi, mezonlar, vaznlar, dalil va raw natija uchun provenance record.
- Reading Accuracy javob kalitidan avtomatik hisoblanadi; Evidence / Strategy / Transfer dalillari alohida talab qilinadi.
- Authentic Listening to‘rtta teng self-review mezoni bilan baholanadi; tashqi audio answer key yo‘qligi yashirilmaydi.
- Writing Task 1 va Task 2 uchun to‘rtta mezonli alohida review; Task 2 ikki baravar og‘irlikdagi qo‘shimcha combined score.
- Kunlik Writing completion reja bo‘yicha Task 1, Task 2 yoki both talabini hisobga oladi.
- Speaking to‘rtta mezonli review; Pronunciation audio evidence bilan gate qilinadi.
- Kundalik self-rating va skill criterion score bir-biridan ajratildi.
- To‘rt skill sahifasida baholash manbasi va dalil qamrovi xulosasi.
- Stage 44 scoring engine Service Worker CORE cache’ga qo‘shildi.

## Saqlandi

- Stage 41–43 curriculum, modul arxitekturasi va progress namespace.
- 84 kun, 4 skill, 61 maqolalik kutubxona, mavjud laboratoriyalar, Listening audio cache va IndexedDB nomi.

## Acceptance

Stage 41: 21/21; Stage 42: 23/23; Stage 43: 39/39; Stage 44: 30/30.

## Ochiq cheklovlar

Haqiqiy AI backend, examiner calibration, Samsung A14 acceptance va to‘liq Chromium E2E ushbu release scope’ida bajarilmadi.
