# Stage 49 — Security & Privacy Model

## Trust boundary

IELTS Boost bu hozircha local-first static web app. User state browser LocalStorage’da, audio recording IndexedDB’da turadi. Server account, cloud sync, app-side at-rest encryption yoki server-side AI credentials mavjud emas.

## Backup guarantees

- JSON export app state’ni ko‘chiradi, lekin audio bloblarni emas.
- SHA-256 browser Web Crypto mavjud bo‘lsa backup payload integrity’sini tekshiradi.
- Checksum authentication emas: u muallifni tasdiqlamaydi va faylni shifrlamaydi.
- Import shape, size, depth, node count, dangerous keys va checksum bo‘yicha tekshiriladi.
- Eski backuplar checksum’siz bo‘lishi mumkin; ularning holati aniq ko‘rsatiladi.
- Importdan oldin safety snapshot download boshlanadi.
- Default state deep merge qilinadi, yangi app versiyasidagi yangi sozlamalar eski backup bilan yo‘qolmaydi.

## Browser security

- Same-origin JavaScript CSP.
- `object-src 'none'`.
- `base-uri 'self'`.
- Strict-origin referrer policy.
- External media / dictionary links HTTPS provider sahifasiga ochiladi.

## Residual risks

- Unlocked shared device/browser profile’da boshqa user local progressni ko‘rishi mumkin.
- Browser/OS storage eviction xavfi saqlanadi.
- Third-party provider videolari va Web Speech xizmatlari ularning o‘z maxfiylik qoidalariga bo‘ysunadi.
- CSP meta policy server HTTP response header darajasidagi CSP bilan bir xil boshqaruv imkonini bermaydi.
- Static GitHub Pages ichiga API secret joylashtirish mumkin emas.

## User recommendations

1. Shaxsiy qurilma va ekran qulfi ishlating.
2. Muhim progressdan keyin JSON backup yuklab oling.
3. Speaking audio fayllarini alohida eksport qiling.
4. Backupni ishonchli, shaxsiy joyda saqlang.
5. Noma’lum JSON backupni import qilmang.
