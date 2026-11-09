# IELTS Boost — Stage 42 Master Report

**Release:** 42.0.0  
**Date:** 2026-11-08  
**Base:** Stage 41 Audit Baseline  
**Focus:** Speaking Transcript Reliability & Recovery

## 1. Stage maqsadi

Oldingi buildlarda Speech-to-Text ba'zan umuman matn bermagan, audio yozish bilan transcript esa bir-biriga aralashib ketgan. Stage 42 ushbu ikki mexanizmni aniq ajratadi va browser ASR ishlamay qolganida foydalanuvchining matn kiritish yo'lini saqlaydi.

## 2. Root-cause xulosasi

- `MediaRecorder` mikrofon audiosini yozib, IndexedDB'ga saqlaydi.
- `SpeechRecognition` / `webkitSpeechRecognition` esa browser yoki platforma speech service orqali matnni aniqlaydi. Bu ikki API bir xil narsa emas.
- `SpeechRecognition` browserlar bo'yicha cheklangan qo'llovga ega. MDN uni “Limited availability” deb belgilaydi; ayrim Chrome muhitlarida audio serverdagi tanish xizmatiga yuboriladi va offline ishlamasligi mumkin.
- Demak, audio blob saqlanganining o'zi undan transcript yaratilganini anglatmaydi.
- Avvalgi ASR restart sikli bir tanish sessiyasi tugab, yangisi boshlanganida matn indekslari qayta boshlanishi mumkinligini hisobga olmagan; bu qayta ulanish vaqtida takroriy matn xavfini keltirib chiqaradi.

## 3. Stage 42 da bajarilgan texnik ishlar

1. **Segment whitelist:** Part 1, Part 2, Part 3 va Daily Challenge alohida transcript target sifatida nazorat qilinadi.
2. **Single active session:** bir vaqtda faqat bitta ASR sessiyasi ishlaydi. Yangi Part ishga tushsa, avvalgi sessiya bekor qilinadi va oldingi matn saqlanadi.
3. **Final / interim separation:** vaqtinchalik recognition natijasi field’da ko'rsatiladi, ammo yakuniy transcript sifatida saqlanmaydi. Faqat `isFinal` natija commit qilinadi.
4. **Duplicate protection:** har bir recognizer sessiyasining `baseText` qiymati va natija indekslari alohida yuritiladi. Browser service qayta ulanganda yangi segment faqat oldingi yakuniy matndan keyin qo'shiladi.
5. **Autosave:** har bir final natija va foydalanuvchining manual/keyboard tahriri mavjud app state’ga darhol saqlanadi.
6. **Bounded reconnect:** tabiiy uzilishdan keyin maksimal 12 marta qayta ulanish; ketma-ket ikki `no-speech` holatidan keyin to'xtash.
7. **Error recovery:** permission, service-not-allowed, audio-capture, network, language-not-supported, language-unavailable, no-speech va aborted holatlari foydalanuvchiga o'zbekcha tushuntiriladi.
8. **Manual safety:** foydalanuvchi matn maydonini qo'lda tahrir qilsa, ustidan ASR yozib yubormasligi uchun live recognition to'xtaydi; kechikib kelgan eventlar e'tiborga olinmaydi.
9. **Keyboard fallback:** SpeechRecognition mavjud bo'lmasa, foydalanuvchi o'sha raw transcript maydonida yozishi yoki Android keyboard voice typing’dan foydalanishi mumkin.
10. **Language memory:** har bir target uchun tanlangan `en-GB` / `en-US` tili saqlanadi. Til o'zgarsa, joriy recognition to'xtaydi va yangi til bilan qayta boshlash so'raladi.
11. **Lifecycle:** boshqa transcript segmentini ochish, boshqa app sahifasiga o'tish, kunni almashtirish yoki sahifani yopish faol recognition’ni to'xtatadi.
12. **Preservation:** oldingi transcript field’lari, state key’lari, Part-by-Part audio IndexedDB key’lari va full-session recorder o'chirilmagan.
13. **Cache release:** Service Worker Stage 42 shell/audio cache versiyasiga ko'tarildi.

## 4. Transcript va audio endi qanday ishlaydi?

- Live transcript: browser `SpeechRecognition` ishlasa, tanilgan yakuniy so'zlar tegishli Part’ning raw transcript field’iga yoziladi.
- Interim matn: vaqtinchalik ko'rinish; final bo'lmaguncha saqlanmaydi.
- Manual transcript: foydalanuvchi matn yozishi yoki Android klaviaturasining mikrofonidan foydalanishi mumkin; input autosave qilinadi.
- Audio evidence: Part audio recorder hali ham alohida ishlaydi va audio blob IndexedDB’da saqlanadi.
- Audio-to-text cloud backend: **Stage 42 da ulanmagan.** Saqlangan audio faylning o'zidan server orqali transcript olish uchun xavfsiz backend, autentifikatsiya, maxfiy API secret va foydalanuvchi roziligi kerak. GitHub Pages ichidagi statik JavaScriptga provider API key joylashtirilmaydi.
- Pronunciation: ASR confidence pronunciation score emas; talaffuzni audio tinglab alohida ko'rib chiqish kerak.

## 5. QA natijalari

`python tools/qa_stage42.py` natijasi: **22/22 PASS**.

Tekshiruvlar:
- embedded appData JSON;
- inline JS va Service Worker syntax;
- 4 ta transcript target;
- final/interim ajratilishi;
- reconnect duplicate protection;
- 12 restart / 2 no-speech chegarasi;
- error mapping va manual fallback;
- local progress autosave;
- old audio storage funksiyalarining saqlanganligi;
- 8 ta pure helper assertion;
- mock SpeechRecognition lifecycle: final commit → reconnect → stop → manual overwrite protection.

Stage 41 static QA ham qayta bajarildi: **21/21 PASS**.

### Test chegaralari

- Real microphone permission va live speech service browser tomonidan beriladi; mock test buni tasdiqlamaydi.
- Container Chromium testini ishga tushirish `ERR_BLOCKED_BY_ADMINISTRATOR` bilan bloklandi. Shu sababli real DOM/browser interaction PASS deb belgilanmagan.
- Samsung A14 Chrome va Samsung Internet sinovlari hali bajarilmagan. Ular `STAGE42_TRANSCRIPT_ACCEPTANCE_UZ.md` bo'yicha foydalanuvchi qurilmasida tasdiqlanishi kerak.
- SpeechRecognition barcha browserlarda mavjud emas; online speech-service talab qilinishi mumkin.

## 6. O'zgarmagan narsalar

- IELTS Academic, 84 kun va har kuni 4 majburiy skill.
- 1–10 internal learning-quality scoring tamoyili.
- 10 ta asosiy laboratoriya va Classic Power Labs arxivi.
- 61 maqolali kutubxona.
- Reading, Listening, Writing, Speaking kontenti va oldingi progress state key’lari.
- Part audio blobs uchun IndexedDB saqlash mexanizmi.

## 7. Release qarori

**Stage 42 implementation + simulated QA: PASS.**  
**Haqiqiy Samsung qurilma acceptance: PENDING.**  
**Server-side saved-audio transcription: NOT INCLUDED / NEXT BACKEND TASK.**

Stage 42 transcript lifecycle’ni ancha chidamli qiladi, lekin browser/OS speech recognition xizmatining mavjudligi yoki aniqligini kafolatlamaydi.

## 8. Manbalar

- MDN, SpeechRecognition — browser support “Limited availability”; ayrim Chrome implementatsiyalarida audio server-based recognition service’ga yuboriladi, shu sababli offline ishlamasligi mumkin: https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition
- MDN, Web Speech API — SpeechRecognition va SpeechSynthesis alohida API qismlari, local/on-device ishlash imkoniyatlari browser support va policy’ga bog'liq: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
