# Stage 44 — Scoring Model Reference

## Umumiy qoida

Barcha natijalar **0–10 ichki formative practice-quality index** sifatida saqlanadi. U IELTS bandiga tenglashtirilmaydi.

## Formula

- `objectiveAccuracy(correct,total) = round1(correct / total × 10)`; raw count butun son bo‘lishi va `0 ≤ correct ≤ total` sharti bilan.
- Reading: `0.50 × accuracy + 0.20 × evidence + 0.15 × strategy + 0.15 × transfer`.
- Authentic Listening: `0.25 × criterion1 + 0.25 × criterion2 + 0.25 × criterion3 + 0.25 × criterion4`.
- Writing task score: `0.25 × TA/TR + 0.25 × CC + 0.25 × LR + 0.25 × GRA`.
- Writing combined practice index: `(Task1 + 2 × Task2) / 3`.
- Speaking: `0.25 × FC + 0.25 × LR + 0.25 × GRA + 0.25 × Pronunciation`.

## Kunlik Writing qoidasi

`primary_task = task1`: Task 1 review kunlik Writing uchun yetarli.

`primary_task = task2`: Task 2 review kunlik Writing uchun yetarli.

`primary_task = both`: ikkala review talab qilinadi va 1:2 combined index ishlatiladi.

## Source provenance

- `answer_key`: tekshiriladigan javob kalitidan kelgan natija.
- `learner_self_review`: foydalanuvchi o‘zi qo‘ygan mezon ballari.
- `answer_key_plus_learner_self_review`: aralash Reading natijasi.
- `teacher_review`, `ai_assisted`, `deterministic_rule`, `imported_legacy`: schema darajasida qo‘llab-quvvatlanadi, ammo bu relizda real tashqi AI yoki examiner baholash endpointi ulanmagan.

## Evidence coverage

Har bir dalil maydoni minimal 10 belgidan iborat bo‘lishi tekshiriladi. Bu faqat to‘ldirilish qamrovi; matnning mazmuniy kuchi, IELTS examiner ishonchi yoki statistik confidence sifatida talqin qilinmaydi.
