# Samsung Galaxy A14 — Stage 50 Physical Acceptance Checklist

**Repository:** `plan-b-`  
**GitHub Pages:** `https://davronegamberdiyev42-svg.github.io/plan-b-/`  
**Holat:** pending — telefonning o‘zida bajar.

## A. Release va PWA
- [ ] GitHub repository nomi `plan-b-` ekanini tasdiqla.
- [ ] GitHub Pages HTTPS URL ochiladi; 84-day home sahifasi yuklanadi.
- [ ] Browser DevTools/Chrome site info: manifest topiladi, `id/scope/start_url` shu project subpath ichida.
- [ ] Settings → PWA → Check install readiness: manifest, 192/512 icons, active Service Worker PASS.
- [ ] Chrome ⋮ menyusida “Install app”/“Add to Home screen” mavjudligi tekshiriladi; browser qarori majburlanmaydi.
- [ ] Ilova standalone oynada ochiladi (agar Chrome installable deb tan olsa).

## B. 4 majburiy skill
- [ ] Day 1–84 ro‘yxati ochiladi; 4 skill ham ko‘rinadi.
- [ ] Reading: matn, savol, javob, evidence va save ishlaydi.
- [ ] Listening: Day 1 va Day 84 MP3 ijro etiladi; internet o‘chirilgandan keyin oldin so‘ralgan audio cache’dan o‘ynaydi.
- [ ] Writing Task 1: chart/visual va 4-part planner ko‘rinadi, draft saqlanadi.
- [ ] Writing Task 2: essay draft saqlanadi, scoring provenance ko‘rinadi.
- [ ] Speaking: mikrofon permission, MediaRecorder, playback, download tekshiriladi.
- [ ] Speaking transcript: Part 1, Part 2, Part 3 va Daily Challenge sinov qilinadi. ASR ishlamasa manual/keyboard fallback ishlatiladi.

## C. Vocabulary, labs va progress
- [ ] 19K index qidiruvi; aniq token matching; 672 core pack.
- [ ] SRS: reveal → Again/Hard/Good/Easy → due date yangilanadi.
- [ ] Recall quiz: 6/8 + 2 target terms + 12-word transfer gate.
- [ ] 10 primary labs ochiladi va natijalar saqlanadi.
- [ ] Progress/Errors/Adaptive recommendation ko‘rinadi; yetarli evidence bo‘lmasa xulosa berilmaydi.

## D. Backup/restore va offline
- [ ] Settings → Export verified backup JSON.
- [ ] Yuklangan JSON ichidagi SHA-256 envelope tekshiriladi.
- [ ] Test nusxasini import qilganda safety snapshot avtomatik taklif etiladi.
- [ ] Tampered backup checksum mismatch bilan rad etiladi.
- [ ] Audio kliplarni Speaking Studio’dan alohida eksport qilib saqlash.
- [ ] Airplane mode’da app shell va oldindan cache qilingan audio ishlashini tekshirish.
- [ ] Online video, dictionary va ayrim SpeechRecognition xizmatlari offline ishlamasligi kutiladi.

## E. Ekran va qurilma
- [ ] 320px, 360px, 390px va 430px kengliklarda sahifa gorizontal overflow qilmaydi.
- [ ] Buttons/touch targets qo‘l bilan bosishga qulay.
- [ ] Landscape holat, Android keyboard ochilgandagi layout tekshiriladi.
- [ ] Bir necha kunlik real foydalanishdan keyin storage/quota va backup yana tekshiriladi.

**Natijani qayd et:** sana, Chrome versiyasi, Android versiyasi, ekran o‘lchami, har bir test PASS/FAIL va xato skrinshotlari.
