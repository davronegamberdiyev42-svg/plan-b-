# Stage 48 — SRS Model and Migration

## Maqsad

So‘zni ma’nosini ko‘rmasdan eslashga urinishdan keyin rating berish. SRS rating til sifati, CEFR yoki IELTS band emas; bu o‘quvchining eslab qolish qulayligi haqidagi self-report.

## 4 ta rating

| Rating | Dastlabki interval | Keyingi interval mantiqi |
|---|---:|---|
| Again | 0 kun | Shu kunning o‘zida qayta ko‘rish; lapse +1; success count reset |
| Hard | 1 kun | 2-review bosqichida 4 kun; keyin old interval × capped ease-based multiplier |
| Good | 1 kun | 2-review bosqichida 6 kun; keyin old interval × ease |
| Easy | 4 kun | 2-review bosqichida 8 kun; keyin old interval × ease × 1.3 |

Ease factor: initial 2.3; bounds 1.3–3.0. History: last 20 review events. Due date: browser local calendar date. Timestamp: ISO 8601.

Bu canonical SM-2 algoritmining to‘liq nusxasi emas; SM-2-inspired, tushuntiriladigan, local four-button scheduler.

## Retrieval gate

Ma’no, Uzbek gloss va example bo‘lgan karta avval `details` orqali ochiladi. Shu ochilmaguncha Again/Hard/Good/Easy tugmalari disabled. So‘ng rating saqlanadi va keyingi due sana ko‘rsatiladi.

## Legacy compatibility

Queue quyidagilarni ko‘radi:
- `state.savedCards` va `state.srsReviews`;
- Stage 37 `vocabulary.srs` yozuvlari (`reps`/`interval` maydonlari eski formatda bo‘lishi mumkin);
- Stage 37 vocabulary favourites.

Legacy kartalar yangi UI’da yo‘qolmaydi. Ularga rating berilganda `count`, `intervalDays`, `ease` va history bilan yangi `state.srsReviews` formatiga ko‘chiriladi. Eski Stage 37 yozuvlari o‘chirib tashlanmaydi.

## SRS’ga kirish talabi

Bundled entry uchun English definition, Uzbek gloss, example va POS talab qilinadi. Browser cache’dagi online draft’lar `verifiedByUser` belgisi aniq true bo‘lmaguncha SRS’ga qo‘shilmaydi.

## Limitations

- Review button rating’i obyektiv test emas.
- Scheduler ko‘p faktorli cognitive science modelini da’vo qilmaydi.
- Morphological variants/paraphrases exact recall’da avtomatik qabul qilinmaydi.
- Browser storage local; bu release’da cloud sync qo‘shilmagan.
