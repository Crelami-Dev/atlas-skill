---
name: atlas-frontend-design
description: "Design, build, and audit anti-slop web interfaces, landing pages, dashboards, CSS token systems, and Anime.js v4 motion (Gunakan saat merancang, membangun, atau meninjau antarmuka web, landing page, dashboard, dan animasi Anime.js v4). Do not use for pure backend scripts, database migrations, or CLI tools without a web UI."
---

# Atlas Frontend & Motion Design System (v7.0.0)

Alur kerja terstruktur untuk merancang dan memverifikasi antarmuka web, arketipe tata letak, sistem token CSS, komponen form, arsitektur state UI, serta animasi Anime.js v4. Lihat rincian tiap fase di [phase-workflow.md](references/phase-workflow.md).

## Pilih Jalur Eksekusi

| Jalur | Kapan Digunakan | Fase & Artefak yang Dijalankan |
|---|---|---|
| **Full Mode (Proyek Kompleks / Domain Baru)** | Aplikasi web baru multi-bagian, desain ulang penuh, atau domain yang belum dikenal | Fase 0-6: `deal-direction.mjs`, `design-brief.md` (3 alternatif + rencana gambar), `research-notes.md`, `design-tokens.css`, `run-gates.mjs`, dan inspeksi tangkapan layar |
| **Compact Track (Prompt Kecil / Domain Jelas)** | Halaman tunggal atau prompt singkat dengan konteks domain yang sudah jelas | Fase 0, 1, 3-6: `deal-direction.mjs`, brief singkat (`<!-- atlas-brief: light -->`), tanpa `research-notes.md` kecuali diminta, `design-tokens.css`, dan `run-gates.mjs` |
| **Feature / Component Mode** | Menambah komponen, tabel, atau animasi pada proyek yang sudah ada | Fase 3-6: gunakan token proyek yang ada, terapkan 5 state UI, sintaks Anime.js v4, dan verifikasi visual |
| **Light Patch Mode** | Perbaikan kecil pada teks, spasi, atau bug responsif | Fase 4-5: jalankan `run-gates.mjs --mode light` dan periksa tampilan akhir |

## Ringkasan Fase & Modul

1. **Phase 0 - Arah Visual & Arketipe:** Jalankan `node <atlas>/scripts/deal-direction.mjs --prompt "<prompt>" --project <root> --write-tokens` untuk memilih arketipe struktural dan token WCAG AA, atau tanyakan klarifikasi nada ke pengguna bila `needsClarification: true`.
2. **Phase 1 - Rencana & Brief:** Baca [atlas-plan](skills/atlas-plan/SKILL.md) dan gunakan [design-brief.md](templates/design-brief.md) atau [design-brief.en.md](templates/design-brief.en.md), termasuk bagian `Rencana gambar` pada domain visual.
3. **Phase 2 - Riset Referensi (Kondisional):** Baca [atlas-research](skills/atlas-research/SKILL.md) hanya jika pengguna meminta riset atau domain belum dikenal.
4. **Phase 3 - Sistem Visual, Komposisi & Gambar:** Baca [atlas-design](skills/atlas-design/SKILL.md), [composition-selection.md](references/composition-selection.md), [composition.md](references/composition.md), [imagery.md](references/imagery.md), dan [design-tokens.css](templates/design-tokens.css).
5. **Phase 4 - Implementasi & Motion:** Baca [atlas-lean-code](skills/atlas-lean-code/SKILL.md), [atlas-ui-architecture](skills/atlas-ui-architecture/SKILL.md), [atlas-fullstack-contracts](skills/atlas-fullstack-contracts/SKILL.md), [atlas-anti-slop](skills/atlas-anti-slop/SKILL.md), dan [atlas-motion-animejs](skills/atlas-motion-animejs/SKILL.md).
6. **Phase 5 - Verifikasi Gate & Visual:** Baca [atlas-checker](skills/atlas-checker/SKILL.md), jalankan `node <atlas>/scripts/run-gates.mjs <root> --mode full`, dan inspeksi tangkapan layar lewat `visual_dom_inspector.py`.
7. **Phase 6 - Kritik Terstruktur:** Baca [atlas-critic](skills/atlas-critic/SKILL.md) dan berikan penilaian `LOLOS` (`PASS`) atau `PERBAIKI` (`FIX`) berdasarkan [critical-review.md](references/critical-review.md).

## Aturan Keras & Alasannya

- **Batasi pola hero 2 kolom + kartu workbench hanya untuk aplikasi/dashboard:** Memaksakan toolbar pencarian/filter/Reset pada halaman restoran, portofolio, acara, atau pernikahan membuat semua situs terlihat seperti template SaaS yang seragam.
- **Jangan tampilkan kontrol pemilih state debug (Populated/Loading/Empty/Error) di UI produksi:** Dropdown penguji state adalah alat pengembang yang membingungkan pengunjung akhir, sehingga harus disembunyikan di balik `?debug=1` jika tetap diperlukan.
- **Gunakan foto asli atau pelat spesimen editorial spesifik-domain (`data-photo-slot`), bukan badge placeholder atau siluet SVG bukit dan matahari:** Ikon placeholder generik dan lencana instruksi seperti `"Ganti dengan foto asli"` atau `"SLOT FOTO 01"` merusak kredibilitas visual pengunjung; tandai slot foto hanya lewat atribut `data-photo-slot` dan minta foto asli di pesan chat penutup.
- **Berikan aturan style eksplisit pada semua kontrol form (input, select, textarea, button):** Kontrol form bawaan browser yang tidak di-style merusak kesatuan visual, kontras fokus, dan keterbacaan state error/disabled.
- **Jaga ukuran teks isi minimal 16px dengan lebar baris 60–75 karakter dan maksimal 2 keluarga huruf:** Tipografi yang terlalu kecil atau terlalu lebar melelahkan mata pembaca, sementara kelebihan font memperlambat pemuatan halaman.
- **Jangan menyembunyikan konten awal dengan `opacity: 0` di CSS statis:** Halaman akan tampak kosong jika JavaScript gagal dimuat, tertunda, atau dirender melalui SSR.
