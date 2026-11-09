# IELTS Boost — Stage 49 Master Report

**Release:** 49.0.0  
**Sana:** 2026-11-08  
**Bosqich:** Professional UI/UX, Security & Performance

## Maqsad

Stage 49 vazifasi — Stage 48 dagi ishlaydigan platformani saqlagan holda mobil qulaylik, klaviatura accessibility, PWA manzillari, offline holat ko‘rsatkichi, local data backup/restore va qurilma diagnostikasini kuchaytirish.

## Amalga oshirilgan ishlar

### 1. Mobil UI/UX va accessibility
- 320px dan boshlab ekran kengligi uchun overflow himoyasi.
- Mobil navigatsiya, safe-area padding va 44px minimum touch target yondashuvi.
- Skip-to-content havolasi va `main` landmark uchun focus target.
- `:focus-visible`, reduced-motion va forced-colors qo‘llovi.
- Uzun jadval, matn, audio/video va media elementlari uchun responsive cheklovlar.
- Inputlarda mobil qurilmalarda avtomatik zoomni kamaytirish uchun 16px matn.

### 2. PWA va deploy portability
- `manifest.webmanifest` ichidagi `id`, `start_url`, `scope`, icon va shortcut yo‘llari `./` asosida.
- Service Worker `ROOT` ni `self.registration.scope` dan hosil qiladi; project subpath uchun qattiq repository nomi yo‘q.
- Shell cache: `ielts-boost-ielts-boost-stage50-shell-v12`.
- Stage 42 Listening audio cache `ielts-boost-stage42-audio-v3` saqlab qolindi.
- Offline banner internet yo‘q holatini ko‘rsatadi; tashqi video, online dictionary va ayrim Web Speech xizmatlari ishlamasligi mumkinligi aytiladi.
- Audio birinchi marta so‘ralganda cache qilinadi; birinchi tashrifda barcha audio avtomatik offline bo‘lib qoladi deb da’vo qilinmaydi.

### 3. Content Security Policy va local privacy
- Same-origin script policy (`script-src 'self'`).
- `object-src 'none'`, `base-uri 'self'`, strict-origin referrer policy.
- Media, fonts, images va external HTTPS iframe uchun kerakli ruxsatlar qoldirilgan.
- Ilova local-first: progress shu browser profili ichida turadi; app tomonidan at-rest encryption yoki cloud sync yo‘q.
- Settings sahifasida bu maxfiylik chegaralari ochiq aytilgan.

### 4. Backup va restore
- JSON backup envelope format 2.
- Web Crypto mavjud bo‘lsa SHA-256 checksum.
- Importda 40MB hajm chegarasi, JSON parse, shape validation, chuqurlik/node budget va xavfli object key tekshiruvi.
- Checksum mos kelmasa import rad etiladi.
- Eski checksum bo‘lmagan backuplar tuzilma tekshiruvidan keyin `legacy-unchecksummed` sifatida qabul qilinadi.
- Importdan oldin joriy state uchun `pre-import-safety` snapshot download ishga tushiriladi.
- `mergeBackupState()` eski backupdan kelgan maydonlarni yangi default state bilan chuqur birlashtiradi; yangi versiyadagi default fieldlar eski backup sabab yo‘qolmaydi.
- Speaking/Listening audio bloblari IndexedDB’da alohida. JSON backup ichiga audio kirmaydi; bu UI’da aytiladi.

### 5. Storage va qurilma diagnostikasi
Settings ichida quyidagilar ko‘rsatiladi: Secure Context, LocalStorage, IndexedDB, persistent storage holati, quota estimate, microphone API, MediaRecorder, SpeechRecognition availability, Service Worker, page control, network va viewport.

`navigator.storage.persist()` faqat foydalanuvchi tugmasi orqali so‘raladi; browser rad qilishi mumkin.

## Tekshiruv natijalari

| Tekshiruv | Natija |
|---|---:|
| Stage 49 QA | **76/76 PASS** |
| Backup engine unit test | **10/10 PASS** |
| Stage 41 regression | 21/21 PASS |
| Stage 42 regression | 23/23 PASS |
| Stage 43 regression | 39/39 PASS |
| Stage 44 regression | 30/30 PASS |
| Stage 45 regression | 33/33 PASS |
| Stage 46 regression | 47/47 PASS |
| Stage 47 Task 1 engine | 19/19 PASS |
| Stage 47 integration | 40/40 PASS |
| HTTP smoke | 13/13 HTTP 200 |

### Brauzer acceptance holati

Chromium/Playwright sinovi ishga tushirildi, biroq execution environment localhost manzilini `ERR_BLOCKED_BY_ADMINISTRATOR` bilan blokladi. Sahifaga navigatsiya boshlanmaganligi sababli browser-render, mobile overflow, backup download UI va console error tekshiruvlari **BLOCKED**, PASS emas.

### Haqiqiy qurilma acceptance

Samsung A14’da quyidagilar hali foydalanuvchi qurilmasida tekshirilishi kerak:
- GitHub Pages project-subpath’dan ochilishi.
- Chrome’da Add to Home Screen / Install.
- Offline shell va oldin yuklangan audio.
- Mikrofon ruxsati, MediaRecorder va transcript.
- Backup export/import va audio alohida eksporti.
- 320–430px ekranlarda ko‘rinish.

## Muhim cheklovlar

1. Backup JSON audio bloblarni o‘z ichiga olmaydi. Speaking/Listening yozuvlarini alohida yuklab olish kerak.
2. Backup checksum encryption emas; u fayl buzilgan/o‘zgartirilganini aniqlash uchun.
3. Browser storage OS/browser tomonidan tozalanishi mumkin; persistent storage API kafolat emas.
4. Ilova local-first; cloud sync va at-rest encryption mavjud emas.
5. Web Speech API qo‘llovi browser va internetga bog‘liq; manual transcript fallback saqlanadi.
6. Full browser E2E va real phone acceptance pending.

## Deploy

Current project target `DEPLOY_TARGET.txt` ichida qayd qilingan. Manifest va SW relative bo‘lib, GitHub Pages project subpath bilan ishlashga mo‘ljallangan. ZIP’ni repository root’ga joylashtirishdan oldin eski branch/commit backupini saqlang. Yangi Service Worker shell cache aktiv bo‘lgach, bir marta online sahifani qayta oching.
