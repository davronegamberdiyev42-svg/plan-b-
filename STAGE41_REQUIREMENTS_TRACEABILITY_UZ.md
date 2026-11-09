# Stage 41 — Talablar xaritasi (Requirements Traceability)

Ushbu hujjat foydalanuvchi tasdiqlagan Master Specification va yuborilgan Stage 40 ZIP ichidagi dalillarni bog‘laydi.

| ID | Yakuniy talab | Joriy dalil | Holat | Qaror |
|---|---|---|---|---|
| R-01 | IELTS Academic | AppData plan Academic curriculum deb belgilangan; foydalanuvchi Academic'ni tasdiqladi | Mavjud | Academic-only deb rasmiylashtirish |
| R-02 | 84 kun | `plan.days` va `core.days` = 84 | PASS | Saqlash |
| R-03 | Har kuni 4 skill majburiy | Har kun `reading/listening/writing/speaking` mavjud — 336/336 | PASS | Saqlash |
| R-04 | Kunlik qat'iy vaqt limiti yo‘q | Plan design note: no daily minute quota | PASS | Timer faqat ixtiyoriy mashq vositasi |
| R-05 | 1–10 sifat baholash | `scoring_rubric` va Stage 40 rubric; process score bilan official IELTS band farqlangan | Qisman | Stage 44: mezonlar → real score engine integratsiyasi |
| R-06 | 10 ta yuqori sifatli laboratoriya | 10 noyob `P37_MODULES` ID | PASS (mavjudlik) | Stage 45: to‘liq functional/quality regression |
| R-07 | Sifat miqdordan ustun | 100 legacy mode alohida Classic bo‘limda; 10 lab asosiy | Qisman | Takroriy UI va kontentni audit qilish |
| R-08 | 61 maqola qo‘shimcha kutubxonasi | `library.articles` = 61 | PASS (mavjudlik) | Qo‘shimcha resurs; public copyright review alohida |
| R-09 | Eng kuchli transcript | Web Speech API live path bor; server STT yo‘q; real qurilma sinovi yo‘q | FAIL / kritik | Stage 42 majburiy |
| R-10 | Speaking audio saqlanishi | MediaRecorder + IndexedDB implementation mavjud | Qisman | Stage 42/46: recovery va actual device test |
| R-11 | Chuqur maslahatchi | Deterministic transcript heuristics va rule-based adaptation mavjud; real AI backend yo‘q | Qisman | AI advisory engine alohida backend bosqichida |
| R-12 | Adaptiv mashq | Stage 37 lablarida zaif natijaga qarab tavsiyalar bor | Qisman | Stage 46: evidence-led adaptation validation |
| R-13 | 19k vocabulary | 19,000 searchable entries; 677 fully complete offline glosses | Qisman | Vocabulary coverage'ni bosqichma-bosqich oshirish |
| R-14 | Progress yo‘qolmasligi | Local state, Stage namespace va IndexedDB blob storage mavjud | Qisman | Migration/backup/restore regression talab qilinadi |
| R-15 | PWA/offline | Manifest, Service Worker, audio range cache | Qisman | Samsung A14 va real browser acceptance kerak |
| R-16 | Yakuniy mustaqil ZIP | Hozirgi arxiv to‘liq 84 MP3 bilan mavjud | Qisman | Har bir stage'dan keyin testlangan release |

## Muhim status izohi

`PASS (mavjudlik)` elementning ma'lumot yoki kod sifatida borligini bildiradi. U to‘liq ishlashi, foydalanuvchi qurilmasida ishlashi yoki ekspert tomonidan tasdiqlanganini bildirmaydi. Stage 41'dan keyingi ishlarning barchasi shu farqni saqlashi kerak.
