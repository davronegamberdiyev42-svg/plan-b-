# Android / Samsung A14 — IELTS Boost Final Release 50

1. GitHub Pages HTTPS manzilini Chrome’da och. `file://` orqali ishga tushirma.
2. Online paytda Home, 4 skill, Vocabulary, Settings va kerakli Listening audio sahifalarini bir marta och.
3. Chrome menyusi → **Install app** yoki **Add to Home screen**. “Install app” ko‘rinishi browser eligibility qaroriga bog‘liq.
4. Speaking uchun Chrome site settings’dan Microphone → Allow ber.
5. Settings → PWA → **Check install readiness**: manifest, relative project scope, icons va Service Worker tekshiriladi.
6. Settings → device diagnostics: Secure Context, LocalStorage, IndexedDB, quota, MediaRecorder, SpeechRecognition va Service Worker holatini ko‘r.
7. Settings → **Export verified backup JSON** orqali muntazam progress backup ol.
8. Speaking Studio’dagi muhim audio yozuvlarni alohida eksport qil. JSON backup IndexedDB audio bloblarini o‘z ichiga olmaydi.

## Offline sinovi
- Avval online paytda ilovani va zarur MP3 treklarni och: audio birinchi marta so‘ralganda cache qilinadi.
- Keyin airplane mode yoqib, sahifani qayta och. Shell va oldin cache qilingan audio mavjud bo‘lishi mumkin.
- Tashqi TED/YouTube/podcast, online dictionary va ayrim SpeechRecognition xizmatlari offline ishlamasligi kutiladi.

## Transcript
Live transcript browser SpeechRecognition API’ga, mikrofon ruxsatiga va ba’zan internetga bog‘liq. U bo‘lmasa Manual Transcript yoki Samsung Keyboard/Gboard voice typing’dan foydalan. Server-side STT bu release’da ulanmagan.

## Backup va privacy
SHA-256 checksum fayl yaxlitligini tekshiradi, encryption emas. Progress local browser profile’da saqlanadi; app-side encryption at rest va cloud sync yo‘q. JSON backup audio bloblarni saqlamaydi. Noma’lum JSON faylni import qilma; importdan oldin app safety snapshot chiqaradi.

## Final physical acceptance
Barcha bandlarni bajarib natijani qayd et: `STAGE50_MOBILE_ACCEPTANCE_UZ.md`. Chromium automation bu build muhitida localhost navigatsiyasi `ERR_BLOCKED_BY_ADMINISTRATOR` bilan to‘xtagani sabab Samsung qurilmada mustaqil tekshiruv shart.
