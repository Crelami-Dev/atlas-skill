# Panduan Alur Kerja Fase Atlas (Phase 0 - Phase 6)

Dokumen ini memuat rincian teknis untuk setiap fase eksekusi yang dirujuk dari [SKILL.md](../SKILL.md).

## Phase 0 - Penentuan Arah Visual (`deal-direction.mjs`)

Saat proyek belum memiliki sistem token bawaan, jalankan pemilih arah visual deterministik:

```sh
node <atlas>/scripts/deal-direction.mjs --prompt "<permintaan pengguna>" --project <project-root> --write-tokens
```

Alasan aturan: model bahasa cenderung kembali ke warna ungu-biru generik atau latar abu-abu datar jika palet dan pasangan tipografi tidak dikunci sejak awal.

## Phase 1 - Perencanaan Brief (`atlas-plan`)

Baca [atlas-plan](../skills/atlas-plan/SKILL.md), [design-brief.md](../templates/design-brief.md) (Indonesia) atau [design-brief.en.md](../templates/design-brief.en.md) (Inggris), serta [composition-selection.md](composition-selection.md).

- **Jalur Lengkap (Full Track):** Tulis 3 alternatif komposisi struktural (`### Alternatif 1..3` atau `### Alternative 1..3`) dan verifikasi dengan `node <atlas>/scripts/check-brief.mjs design-brief.md`.
- **Jalur Ringan (Compact Track untuk prompt kecil/jelas):** Tambahkan komentar `<!-- atlas-brief: light -->` di `design-brief.md` (atau jalankan `check-brief.mjs --light`) agar cukup mengisi tujuan pengunjung, konten nyata, pilihan komposisi, dan rencana verifikasi tanpa perlu membuat 3 alternatif penuh.
- **Kejujuran Konten:** Jangan mengarang klaim jumlah pelanggan atau testimoni fiktif karena data palsu merusak kredibilitas produk dan melanggar pemeriksaan anti-slop.

## Phase 2 - Riset Domain (`atlas-research` - Opsional pada Jalur Ringan)

Baca [atlas-research](../skills/atlas-research/SKILL.md), [research-template.md](research-template.md), dan [domain-reasoning.md](domain-reasoning.md).

- Lewati pembuatan `research-notes.md` pada prompt kecil dengan domain yang sudah jelas, kecuali pengguna meminta riset referensi atau domain proyek belum dikenal.
- Saat riset dijalankan, catat mekanisme yang diadaptasi (`DIADAPTASI`) dan elemen klise yang ditolak (`DITOLAK`) agar antarmuka mengambil pola fungsional tanpa menjiplak satu situs sumber.

## Phase 3 - Sistem Token & Ritme Permukaan (`atlas-design`)

Baca [atlas-design](../skills/atlas-design/SKILL.md), [typography.md](typography.md), dan [interaction-design.md](interaction-design.md).

1. **Maksimal 2 Keluarga Font:** Batasi tipografi hingga maksimal 2 keluarga font di `design-tokens.css` karena terlalu banyak font memperlambat pemuatan halaman dan mengaburkan hierarki baca.
2. **Variasi Polaritas Permukaan:** Gunakan minimal 3 token warna permukaan secara bergantian agar pergantian antarbagian halaman mudah dipindai secara visual.
3. **Verifikasi Token:** Jalankan `node <atlas>/scripts/check-tokens.mjs <project-root> --tokens <token-file>` untuk memeriksa tidak ada nilai hex mentah yang bocor di luar file token.

## Phase 4 - Implementasi UI, Bukti Visual, & Motion (`atlas-lean-code` + `atlas-motion-animejs`)

Baca [atlas-anti-slop](../skills/atlas-anti-slop/SKILL.md), [atlas-motion-animejs](../skills/atlas-motion-animejs/SKILL.md), [animejs-v4-playbook.md](animejs-v4-playbook.md), [atlas-lean-code](../skills/atlas-lean-code/SKILL.md), dan [accessibility-and-behavior.md](accessibility-and-behavior.md).

1. **Elemen Visual Nyata:** Sertakan elemen visual nyata (`<img>`, `<picture>`, `<canvas>`, `<video>`, `<svg data-viz>`, atau `[data-atlas-proof]`) pada halaman pendaratan karena halaman berisi teks semata sulit menunjukkan konteks produk secara cepat. Untuk halaman dokumentasi atau tipografi murni, tambahkan `<!-- atlas-proof: not-applicable -->`.
2. **Hindari SVG Wireframe Kotak Kaku:** Jangan menggambar diagram `<svg>` kotak/poligon mentah dengan banyak label teks sebagai pengganti UI karena sulit dibaca di layar sempit dan tampak seperti kerangka belum selesai.
3. **Sintaks Anime.js v4 & Visibilitas Awal:** Gunakan named imports Anime.js v4 di dalam `createScope({ root, mediaQueries })` dan jangan menyembunyikan konten awal dengan `opacity: 0` di CSS statis karena kegagalan skrip atau SSR akan membuat halaman tampak kosong.
4. **Kunci Lebar Grid Mobile (`min-width: 0`):** Gunakan `minmax(0, 1fr)` dan `min-width: 0` pada elemen anak CSS Grid agar tabel atau blok kode panjang tidak menimbulkan luapan horizontal pada layar 320px-375px.

## Phase 5 - Pemeriksaan Gate & Tangkapan Layar (`atlas-checker`)

Baca [atlas-checker](../skills/atlas-checker/SKILL.md) dan [visual-review.md](visual-review.md).

Jalankan pemeriksaan terpadu:
```sh
node <atlas>/scripts/run-gates.mjs <project-root> --mode full --visual <entry-html-or-url> --shots-dir maintenance/screenshots
```
Buka hasil tangkapan layar PNG (`1440x900` dan `375x667`) menggunakan alat pembaca gambar jika tersedia, karena pemeriksaan kode statis saja tidak dapat mendeteksi teks terpotong, tumpang-tindih elemen, atau kontras visual yang buruk di browser nyata.

## Phase 6 - Evaluasi Rubrik (`atlas-critic`)

Baca [atlas-critic](../skills/atlas-critic/SKILL.md) dan [critical-review.md](critical-review.md). Nilai hasil berdasarkan 7 sumbu rubrik dan berikan status `LOLOS` (`PASS`) jika skor mencapai minimal 88/100 tanpa cacat fungsional/visual utama, atau `PERBAIKI` (`FIX`) beserta daftar perbaikan spesifik.
