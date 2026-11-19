---
name: atlas-checker
description: "Run the 5 static run-gates.mjs validators plus multi-viewport browser screenshot and DOM aesthetic inspection before delivering any UI project (Gunakan saat menjalankan 5 pemeriksaan statis run-gates.mjs serta pengambilan dan inspeksi tangkapan layar browser multi-viewport sebelum menyerahkan proyek UI). Do not use for projects without web UI code."
---

# Atlas Checker - Pemeriksaan Gate Terpadu & Verifikasi Tangkapan Layar

Kode yang lolos pemeriksaan sintaks statis masih bisa mengalami teks terpotong, elemen bertumpuk, atau overflow horizontal di browser nyata. Fase 5 menggabungkan 5 pemeriksaan statis dengan inspeksi tangkapan layar multi-viewport.

## Langkah 1 - Jalankan Gate Statis & Ambil Tangkapan Layar

Jalankan skrip terpadu `run-gates.mjs`:

```sh
node <atlas>/scripts/run-gates.mjs <project-root> --mode full --visual <entry-html-or-url> --shots-dir maintenance/screenshots
```

Urutan pemeriksaan yang dijalankan:
1. [check-brief.mjs](../../scripts/check-brief.mjs) — Memeriksa kelengkapan bagian brief (Indonesia atau Inggris, mode penuh atau `--light`).
2. [check-tokens.mjs](../../scripts/check-tokens.mjs) — Memastikan maksimal 2 keluarga font dan tidak ada warna/skala mentah yang bocor di luar `design-tokens.css`.
3. [check-motion-v4.mjs](../../scripts/check-motion-v4.mjs) — Memeriksa sintaks Anime.js v4, pembersihan `createScope`, dan ketiadaan `opacity: 0` statis pada konten utama.
4. [slop-scan.mjs](scripts/slop-scan.mjs) — Memindai pola klise AI, teks placeholder, dan sintaks Anime.js v3.
5. [check-visual-proof.mjs](../../scripts/check-visual-proof.mjs) — Memeriksa keberadaan elemen visual nyata, ketiadaan backtick Markdown mentah di HTML, dan ketiadaan SVG wireframe kaku (gunakan `--strict` untuk menjadikan peringatan bukti visual sebagai error).
6. [visual_dom_inspector.py](scripts/visual_dom_inspector.py) atau [quick-check.mjs](scripts/quick-check.mjs) (opsional saat Chromium/Playwright tersedia) — Merender viewport `1440x900`, `390x844`, `375x667`, dan `320x568`, menyimpan tangkapan layar PNG, serta memeriksa overflow horizontal dan gambar rusak.

## Langkah 2 - Periksa Tangkapan Layar PNG (Saat Alat Pembaca Gambar Tersedia)

Buka file PNG yang dihasilkan (`desktop_1440_top.png`, `desktop_1440_mid.png`, `mobile_375x667_top.png`) menggunakan alat pembaca gambar (`view_file` atau `Read`) karena pemeriksaan visual langsung dapat menemukan cacat tata letak yang tidak terlihat dari stdout JSON:
- Periksa apakah judul, tabel, dan tombol utama di `1440x900` dan `375x667` terbaca utuh tanpa terpotong.
- Periksa apakah pergantian warna permukaan antarbagian terlihat rapi dan selaras.
- Jika ditemukan cacat visual pada tangkapan layar, perbaiki CSS/HTML terkait dan jalankan ulang pemeriksaan sebelum lanjut ke [atlas-critic](../atlas-critic/SKILL.md).
