# IELTS Boost — Stage 48 Master Report

**Release:** 48.0.0  
**Sana:** 2026-11-08  
**Bosqich:** Vocabulary & Resource Intelligence  
**Holat:** Implementatsiya va avtomatik QA yakunlandi; haqiqiy browser/Android acceptance pending.

## 1. Maqsad

19 000 ta indeks yozuvini 19 000 ta tayyor lug‘at deb ko‘rsatmaslik; mavjud 84 kunlik vocabulary core, offline gloss qamrovi, IPA maydonlari, CEFR taxminlari, qidiruv, transfer va SRS sifatini aniq ajratish. Mavjud foydalanuvchi ma’lumotlarini yo‘qotmasdan Stage 36/37 va asosiy vocabulary cache’larini bitta qidiruv/tahlil oqimida birlashtirish.

## 2. Haqiqiy lug‘at qamrovi

| Ko‘rsatkich | Haqiqiy miqdor | Izoh |
|---|---:|---|
| Qidiriladigan headword/phrase indeksi | 19,000 | Barchasi unique ID va normalized headword |
| To‘liq offline glossary | 677 | English definition + Uzbek gloss + example + POS |
| 84 kunlik core | 672 | 84 × 8; core’dagi barcha yozuvlar yuqoridagi 4 maydon bilan to‘liq |
| Core US + UK IPA maydonlari | 672/672 | Maydon mavjud; audio/ekspert tasdig‘i degani emas |
| US IPA field mavjud | 15,678 | Maydon mavjudligi, sifati alohida tekshirilishi kerak |
| UK IPA field mavjud | 11,678 | Maydon mavjudligi, sifati alohida tekshirilishi kerak |
| POS field mavjud | 4,541 | POS to‘liq bo‘lmagan yozuvlar avtomatik to‘ldirilmagan |
| Pronunciation-only yozuvlar | 4,000 | CMUdict asosidagi indeks; glossary emas, Uzbek/definition/example/POS/UK IPA to‘liq emas |
| CEFR estimate | 15,000 | B2: 12,831; C1: 2,169; rasmiy sertifikat emas |
| CEFR not assessed | 4,000 | Talaffuz-only cohort |
| Kamida bitta asosiy gloss maydoni yetishmaydi | 18,323 | To‘liq glossary sifatida hisoblanmaydi |
| Normalized duplicate headword | 0 | Exact normalized string duplicate topilmadi |

**Muhim:** 19,000 — search index hajmi. U 19,000 ta to‘liq tarjimali, IPA’si tekshirilgan yoki CEFR darajasi ekspert tomonidan tasdiqlangan so‘z degani emas. Faqat 677 ta to‘liq glossary record offline mavjud; 84 kunlik 672 core esa ularning ichida.

### 84-day core IPA tuzatishi

Core ichidagi `discrepancy` (ID 13277) uchun UK/US IPA maydoni bo‘sh edi. Cambridge Dictionary pronunciation entry manbasi yozib qo‘yilib, IPA maydoni `/dɪˈskrep.ən.si/` bilan to‘ldirildi. Source URL data ichida saqlangan. Bu yozuv uchun ham hozirgi audio talaffuzni Cambridge player orqali qayta eshitish tavsiya etiladi.

## 3. Vocabulary UI va qidiruv

- 19K qidiruv indeksi bir marta normalizatsiya qilinadi; har bir keypress’da 19K yozuvni qayta normallashtirish yo‘q.
- 24 tadan sahifalab ko‘rsatish va qamrov filtrlari: all, 84-day core, complete offline gloss, needs review, US+UK IPA, US IPA, pronunciation-only, saved.
- Qidiruv Stage 36 cache, Stage 37 cache va joriy `state.vocabCache` ichidagi foydalanuvchi qo‘shgan ma’lumotni birlashtiradi.
- Qidiruv matni va sahifa offset’i saqlanadi.
- Kunlik 84-day core ID’lari `Map` orqali olinadi; 19K massiv bo‘ylab har item uchun takroriy `find()` qilinmaydi.
- CEFR qiymati `estimate` yoki `not assessed` sifatida ko‘rsatiladi.
- IPA maydoni mavjudligi mustaqil audio/ekspert tekshiruvi deb ko‘rsatilmaydi.

## 4. Kunlik 8 birlikli o‘quv sikli

Har kuni 8 ta complete lexical unit:

1. Headword/phrase va POS.
2. English definition, Uzbek meaning, example.
3. US/UK IPA field status va Cambridge/Oxford dictionary link.
4. Active recall: definition/Uzbek gloss’dan exact headword’ni yozish.
5. Context transfer: kamida 2 ta target termni alohida word/phrase sifatida ishlatgan 12+ so‘zli yozuv.
6. Collocation note: learner kiritgan phrase va dictionary source; u avtomatik verified deb hisoblanmaydi.
7. Reading/Listening/Writing/Speaking bo‘yicha self-report tracker.

Kunlik vocabulary pack faqat **kamida 6/8 exact recall + 2 ta target term + 12+ so‘zli transfer matni** bajarilganda tugallangan deb belgilanadi. Quiz javobi yoki transfer matni o‘zgartirilsa, oldingi quiz natijasi va completion belgisi bekor qilinadi. Transfer tekshiruvi grammatika yoki tabiiylik sifatini baholamaydi — faqat exact word/phrase mavjudligini tekshiradi.

## 5. Transfer matcher

Avvalgi substring usuli `art` so‘zini `party` ichidan noto‘g‘ri topishi mumkin edi. Yangi engine token/phrase boundary matcher ishlatadi:

- `art` → `party` ichida topilmaydi.
- `art` → mustaqil so‘z yoki `art-based` ichida topiladi.
- `long term` va `long-term` phrase yozilishi moslashtiriladi.
- `drift off` `drifting off` bilan avtomatik tenglashtirilmaydi; bu stemming/morphology engine emas.

Bu semantik paraphrase aniqlagich emas; transferning faqat exact lexical presence qatlamidir.

## 6. SRS — retrieval-first, four-button scheduler

- Again / Hard / Good / Easy — eslab qolish self-rating’i; til darajasi yoki IELTS bahosi emas.
- Avval ma’noni ochish talab qilinadi; reveal qilinmaguncha rating tugmalari disabled.
- Again: interval 0 kun, shu kunda qayta ko‘riladi; lapse +1, success count reset.
- Hard: boshlang‘ich interval 1 kun; keyingi bosqichlar avvalgi interval va ease’ga bog‘liq.
- Good: 1 kun, keyingi birinchi takror 6 kun, so‘ng ease-based interval.
- Easy: 4 kun, keyingi birinchi takror 8 kun, so‘ng uzunroq ease-based interval.
- Ease factor 1.3–3.0 oralig‘ida cheklanadi; boshlang‘ich 2.3.
- Oxirgi 20 review event tarixi saqlanadi.
- Local calendar date ishlatiladi, UTC sana bilan Tashkent local date farqi yuzaga kelmasligi uchun.
- Stage 37 eski SRS yozuvlari va favourites queue’da saqlanadi; rating berilganda yangi formatga ko‘chiriladi. Eski source record o‘chirilmaydi.
- Online translation/lookup draft’lari aniq sense, tarjima va source’ni learner tekshirmaguncha SRS’ga kiritilmaydi.

Bu SM-2’dan ilhomlangan soddalashtirilgan local scheduler; canonical SM-2 implementatsiyasi yoki ilmiy o‘lchangan forgetting curve deb da’vo qilinmaydi.

## 7. Texnik arxitektura va backward compatibility

- `assets/js/core/vocabulary-engine.js` alohida testlanadigan pure module sifatida ajratildi.
- `app.js` bu module’ni import qiladi.
- `data/app-data.json` 19K vocabulary record va 84-day packs’ni saqlaydi.
- `assets/css/stage48.css` Vocabulary UI uchun responsive styles beradi.
- Existing `localStorage` namespace o‘zgarmadi.
- `IELTSBoostMedia` IndexedDB database o‘zgarmadi.
- Stage 42 audio cache key o‘zgarmadi; 84 MP3 saqlangan.
- Service Worker namespace `ielts-boost-stage48`, shell cache `shell-v9`; Stage 47 assetlar va Stage 48 CSS/engine precache qilinadi.
- 61 maqola kutubxonasi va 864 sentence pattern saqlangan.

## 8. QA

**Stage 48: 58/58 PASS** (data audit, module unit tests, JS syntax, local HTTP smoke, stage regression). 11 ta asosiy HTML/CSS/JS/JSON/SW/audio resurs local HTTP serverda 200 javob qaytardi.

| Regression suite | Natija |
|---|---:|
| Stage 41 | 21/21 PASS |
| Stage 42 | 23/23 PASS |
| Stage 43 | 39/39 PASS |
| Stage 44 | 30/30 PASS |
| Stage 45 | 33/33 PASS |
| Stage 46 | 47/47 PASS |
| Stage 47 Task 1 engine | 19/19 PASS |
| Stage 47 resource integration | 40/40 PASS |
| Stage 48 | 58/58 PASS |

## 9. Ochiq cheklovlar

- Chromium E2E boshlashga urinish qilindi, lekin `page.goto(http://127.0.0.1:PORT/)` muhit siyosati tomonidan `ERR_BLOCKED_BY_ADMINISTRATOR` bilan bloklandi. Shuning uchun brauzer interaksiyasi PASS deb ko‘rsatilmaydi.
- Samsung A14’da real PWA install, offline reload, Gboard/Samsung keyboard, microphone, transcript va backup/restore fizik sinovlari hali pending.
- Online lookup natijalari draft; ma’no/Uzbek gloss/source sense-by-sense tekshirilishi kerak.
- 11,678 UK IPA field mavjud bo‘lishi ularning hammasi to‘g‘ri/ekspert tasdiqlanganini bildirmaydi. Audio bilan tekshirish davomiy ish.
- 15,000 CEFR labels estimate; word sense bo‘yicha rasmiy CEFR certification emas.

## 10. Release fayllari

- `STAGE48_VOCABULARY_INDEX_AUDIT_UZ.csv` — 19,000 record uchun field-by-field audit.
- `STAGE48_QA_RESULTS.json` — 58/58 test va Stage 41–47 regression tafsilotlari.
- `STAGE48_BROWSER_ACCEPTANCE_STATUS.json` — Chromium acceptance bloklanganligi qaydi.
- `STAGE48_SRS_MODEL_UZ.md` — scheduler va legacy migration qoidalari.
- `STAGE48_DATA_COVERAGE.json` — data coverage machine-readable summary.
