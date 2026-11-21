---
title: Gate Deterministik & Pemeriksa
description: Cara menjalankan run-gates.mjs, quick-check.mjs, check-copy.mjs, check-tokens.mjs, dan check-brief.mjs.
---

Atlas tidak mengandalkan kepatuhan prosa semata: setiap fase kritis dikunci oleh pemeriksa deterministik berbasis Node.js (ditambah inspeksi Chromium headless opsional).

## Ringkasan Jalur Pemeriksaan

Semua gate statis (`1–5` dan `4b`) berjalan lewat satu perintah terpadu:

```sh
# Menjalankan Gate 1, 2, 3, 4, 4b, dan 5 secara berurutan
node scripts/run-gates.mjs /jalur/proyek-target --mode full --strict

# Sertakan Gate 6 (tangkapan layar browser headless & audit DOM via Python + Playwright)
node scripts/run-gates.mjs /jalur/proyek-target --mode full --strict --visual /jalur/proyek-target/index.html --shots-dir ./maintenance/screenshots
```

Mode `--mode light` melewati `1. Brief Gate` (`check-brief.mjs`) bila proyek menggunakan mode ringkas atau tidak memakai brief penuh, sedangkan `--strict` mengubah setiap peringatan (`WARN`) pada `check-copy` dan `check-visual-proof` menjadi kegagalan (`exit 1`).

## Rincian Setiap Pemeriksa

### 1. Brief Gate (`scripts/check-brief.mjs`)
Memastikan `design-brief.md` valid sebelum kode UI ditulis:
- Memeriksa batas panjang halaman tunggal (`<= 7000` karakter) dan melarang teks placeholder (`lorem ipsum`, `your company`, `acme corp`).
- Wajib memuat bagian inti dalam Bahasa Inggris maupun Indonesia: tujuan pengunjung, konten nyata, pilihan akhir dan alasan, rencana verifikasi, serta (pada mode penuh) **3 alternatif komposisi** (`### Alternative 1..3` / `### Alternatif 1..3`) dan hal yang ditolak.
- Mendukung mode ringkas melalui flag `--light` atau komentar HTML `<!-- atlas-brief: light -->`.
- Jika `--require-image-plan` aktif atau terdapat bagian `## Signature idea`, memvalidasi bahwa ID `scene:` cocok dengan `templates/scene-catalog.json`.

```sh
node scripts/check-brief.mjs /jalur/proyek-target/design-brief.md
```

### 2. Tokens Gate (`scripts/check-tokens.mjs`)
Mencegah kebocoran nilai mentah di luar berkas token desain:
- Membaca berkas CSS token yang ditunjuk via `--tokens <path>` (atau mendeteksi kandidat standar seperti `design-tokens.css`, `src/styles/tokens.css`, `app/globals.css`).
- Memeriksa berkas `.css`, `.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`, dan `.astro` untuk memastikan tidak ada warna hex/RGB mentah, jarak piksel/rem sewenang-wenang, atau atribut `style="..."` mentah di luar berkas token (pengecualian eksplisit per berkas bisa dicatat lewat `.atlas-token-allowlist.json`).

```sh
node scripts/check-tokens.mjs /jalur/proyek-target --tokens /jalur/proyek-target/design-tokens.css
```

### 3. Motion v4 Gate (`scripts/check-motion-v4.mjs`)
Memverifikasi implementasi animasi kompatibel dengan Anime.js v4 dan aman tanpa JavaScript:
- Melarang sintaks usang Anime.js v3 (`anime({ targets: ... })`, `easing:`, `import * as anime`).
- Memastikan elemen `[data-reveal]` / judul hero tidak disembunyikan dengan `opacity: 0` atau `visibility: hidden` pada CSS statis (perangkap SSR/no-JS).

```sh
node scripts/check-motion-v4.mjs /jalur/proyek-target
```

### 4. Anti-Slop Scanner (`skills/atlas-checker/scripts/slop-scan.mjs`)
Memindai sinyal kode dari 18 pola AI slop (gradasi neon ungu-biru, ikon emoji pada tombol/kartu, proliferasi font `> 2` keluarga proporsional, frasa marketing generik, dropdown debug state switcher yang bocor ke produksi, serta instruksi pengganti foto di DOM). Lihat daftar polanya di [18 Pola Anti-Slop](/atlas-skill/id/anti-slop/patterns/).

```sh
node skills/atlas-checker/scripts/slop-scan.mjs /jalur/proyek-target
```

### 4b. Concise Copy Gate (`scripts/check-copy.mjs`)
Menegakkan disiplin teks ringkas sesuai [panduan copy ringkas](/atlas-skill/id/guides/concise-copy/):
- Anggaran layar pertama: H1 ideal `<= 10` kata (fail pada `16`), baris pendukung `<= 28` kata (`45`), total layar pertama `< 55` kata (`85`), serta menyertakan fakta konkret.
- Anggaran per bagian: paragraf `<= 45` kata (`80`), satu halaman landing ideal `~700` kata, tombol `<= 5` kata diawali kata kerja dan melarang label kabur (`Learn more`, `Read more`, `Click here`, `Selengkapnya`, `Submit`).
- Halaman dokumentasi atau artikel panjang dapat dikecualikan dari batas panjang kata menggunakan `<!-- atlas-copy: long-form -->` (label tombol kabur tetap diperiksa).

```sh
node scripts/check-copy.mjs /jalur/proyek-target --strict
```

### 5. Visual Proof Gate (`scripts/check-visual-proof.mjs`)
Memastikan halaman memiliki bukti visual nyata (`<img>`, `<picture>`, `<canvas>`, `<video>`, `<svg data-viz>`, atau `[data-atlas-proof]`), memiliki variasi polaritas permukaan (`>= 3` surface roles), serta bebas dari wireframe SVG mentah atau instruksi placeholder foto yang bocor (`<!-- atlas-proof: not-applicable -->` tersedia untuk halaman teks murni).

### 6. Browser Audit: Gate 6 & `quick-check.mjs`
- **Gate 6 (`skills/atlas-checker/scripts/visual_dom_inspector.py`):** Dipicu oleh `run-gates.mjs --visual`. Mengambil tangkapan layar `1440x900`, `820x1180`, dan `375x667`, memverifikasi kontras warna efektif, mendeteksi elemen tumpang tindih atau grid yang terjepit (`mobile-squeezed-grid`).
- **`quick-check.mjs`:** Pemeriksa mandiri Node.js + Playwright untuk **11 ukuran viewport** (`320x568` hingga `1440x900`), uji klik menu/tab (`--click-test`), audit loop tanpa tombol jeda, stack panjang di ponsel, dan tata letak tablet potret (`600 px` & `768 px`). Lihat seluruh kode temuannya di [Kamus Kode Temuan](/atlas-skill/id/checks/findings-dictionary/).

```sh
node skills/atlas-checker/scripts/quick-check.mjs /jalur/proyek/index.html --shots ./maintenance/browser --click-test
```
