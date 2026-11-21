# Panduan Instruksi Prompt Atlas-skill (v7.0.0)

Dokumen ini berisi daftar instruksi *prompt* siap pakai untuk mengoperasikan **Atlas-skill** secara akurat pada agen AI coding (**Claude Code, OpenAI Codex, Google Antigravity IDE, Cursor, Windsurf, Cline, dan GitHub Copilot**).

> Sumber aturan dan fase eksekusi berasal dari [SKILL.md](../SKILL.md), [phase-workflow.md](../references/phase-workflow.md), dan [copy-concise.md](../references/copy-concise.md).

---

## 1. Prompt Membangun Halaman atau Aplikasi Baru (`/atlas-skill` & `/atlas-frontend`)

### A. Alur Lengkap dengan Audit Bug & Keamanan Otomatis (`/atlas-skill`)
Gunakan perintah ini saat membangun landing page, dashboard, atau aplikasi web baru dan ingin seluruh fase (**Fase 0–6 Frontend + Fase 7 Bug Hunter, Live CVE, dan Perbaikan Otomatis**) berjalan sampai 0 temuan:

```text
/atlas-skill Bangun [jenis proyek, mis. aplikasi web manajemen inventaris gudang / situs arsitektur] dalam Bahasa [Indonesia/Inggris].
Gunakan token CSS dari design-tokens.css, tipografi <= 2 keluarga font (+ 1 mono), animasi Anime.js v4 mulai 15% viewport (1100–1600 ms, outQuart), dan patuhi prefers-reduced-motion.
Jalankan node scripts/run-gates.mjs --mode full --strict --visual serta quick-check.mjs pada 11 viewport, buka screenshot 1440/768/375 px untuk inspeksi, lalu jalankan Fase 7 QA & security audit hingga 0 FAIL dan 0 WARN.
```

### B. Alur Frontend Saja (`/atlas-frontend`)
Gunakan bila Anda fokus pada UI, desain visual, gerak, dan pemeriksaan browser tanpa audit CVE/keamanan Python Fase 7:

```text
/atlas-frontend Bangun [halaman / komponen, mis. landing page kedai kopi artisan] dengan visual terarah dan foto nyata berlisensi via fetch-photos.mjs.
Siapkan design-brief.md (3 alternatif tata letak berbeda), kunci palet kontras WCAG AA ke design-tokens.css, pasang maksimal 1 heavy scene + 2 light scene yang sesuai subjek, dan verifikasi dengan run-gates.mjs --mode full --strict serta quick-check.mjs.
```

> **Catatan untuk Antigravity / agen tanpa perintah slash:** Bila agen tidak mendukung pemanggilan `/atlas-skill`, buka sesi di direktori proyek setelah menjalankan `npx --yes github:Crelami-Dev/atlas-skill install --agent antigravity --with-rules` dan tulis instruksi: `"Gunakan skill atlas-skill di .agents/skills/atlas-skill/SKILL.md untuk membangun..."`.

---

## 2. Prompt Ringkas / Halaman Kecil (*Compact Track*)

Untuk fitur kecil, halaman dokumentasi, atau perbaikan terarah yang tidak memerlukan 3 kandidat arsitektur penuh, sertakan penanda mode ringkas (`--light`):

```text
/atlas-frontend <!-- atlas-brief: light --> Bangun halaman profil teknis 3 bagian dengan token CSS yang sudah ada, kontrol >= 44 px, dan verifikasi check-brief.mjs --light, check-tokens.mjs, serta quick-check.mjs.
```

---

## 3. Prompt Audit & Perbaikan Terkontrol (`/atlas-bug-hunter`)

### Mode A — Audit Baca-Saja (*Read-Only Discovery*)
Gunakan untuk memetakan cacat fungsional, tata letak responsif, atau risiko OWASP/CVE **tanpa mengubah kode proyek terlebih dahulu**:

```text
/atlas-bug-hunter Audit seluruh proyek ini untuk mencari bug fungsional, cacat UI 375/768/1440 px, dan kerentanan keamanan/CVE. Tulis laporan lengkap ke PROJECT-AUDIT-REPORT.md dan tunggu persetujuan sebelum menyunting kode.
```

### Mode B — Audit + Tambal Otomatis (*Fix & Verify*)
Gunakan ketika Anda langsung ingin masalah diperbaiki dan diuji ulang secara penuh:

```text
/atlas-bug-hunter Periksa dan perbaiki seluruh bug tata letak mobile, error konsol, dan temuan keamanan pada proyek ini. Uji semua fitur dan jalankan ulang run-gates.mjs serta quick-check.mjs hingga 0 error dan 0 warning.
```

---

## 4. Prompt Redesign Halaman Lama dalam 2 Tahap (A Lalu B)

Bila Anda sudah memiliki halaman HTML/React/Next.js yang terasa generik seperti template AI, jalankan dua tahap berurutan agar sistem desain dikunci lebih dulu sebelum merombak layout:

### Tahap A — Bangun Design System Baru Saja
```text
/atlas-frontend Audit halaman yang ada lalu bangun design system BARU (design-brief.md, design-tokens.css, komponen CSS terukur, DESIGN-SYSTEM.md, dan styleguide.html).
Tahap ini HANYA membangun sistem desain: jangan mengubah susunan section halaman utama dulu.
Kunci arah visual (tanpa gradien dekoratif, <= 2 font proporsional + 1 mono, target sentuh >= 44 px) dan verifikasi styleguide.html dengan run-gates.mjs --mode full --strict serta quick-check.mjs.
```

### Tahap B — Susun Ulang Seluruh Halaman Memakai Kontrak Tahap A
```text
/atlas-skill Rombak seluruh halaman di proyek ini memakai HANYA token dan komponen dari DESIGN-SYSTEM.md hasil Tahap A.
Pastikan tiap section memakai pola komposisi yang berbeda (editorial, asimetris, sticky 2 kolom, rail/bento, panel padat), copy ringkas sesuai check-copy.mjs, responsif bersih di 320–1440 px, dan verifikasi semua gate plus screenshot akhir.
```

---

## 5. Checklist Agar Output Agen Tetap Akurat

1. **Sebutkan fakta nyata proyek:** Lampirkan nama produk, perintah CLI asli, atau berkas fakta (`facts.md`) agar agen tidak mengarang testimoni atau angka pengguna palsu.
2. **Sebutkan bahasa output:** Nyatakan eksplisit *"Gunakan Bahasa Indonesia"* atau *"Use English"* agar tombol, label form, dan error validasi konsisten.
3. **Wajibkan inspeksi visual:** Selalu minta agen membuka hasil PNG (`1440x900`, `768/820`, `375x667`) sebelum menyatakan tugas selesai.
