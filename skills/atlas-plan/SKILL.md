---
name: atlas-plan
description: "Plan web page structure, visitor tasks, real content inventory, layout alternatives, and viewport budgets before writing UI code (Gunakan saat merencanakan struktur halaman web, inventaris konten, alternatif tata letak, dan anggaran viewport sebelum menulis kode UI). Do not use for tiny CSS patches or single-line fixes."
---

# Atlas Plan - Perencanaan Struktur dan Konten

Menyusun rencana singkat sebelum menulis HTML/JSX mencegah agen langsung menyalin tata letak hero-tengah + 3 kartu yang seragam. Buat `design-brief.md` memakai [design-brief.md](../../templates/design-brief.md) (Indonesia) atau [design-brief.en.md](../../templates/design-brief.en.md) (Inggris).

## 1. Jalur Lengkap vs Jalur Ringan (Compact Track)

- **Jalur Lengkap (Full Track):** Digunakan untuk aplikasi multi-bagian atau desain ulang penuh. Mencakup 6 bagian brief dan minimal 3 alternatif komposisi (`### Alternatif 1..3` atau `### Alternative 1..3`).
- **Jalur Ringan (Compact Track):** Digunakan untuk prompt singkat atau halaman sederhana. Tambahkan `<!-- atlas-brief: light -->` di bagian atas brief (atau jalankan `check-brief.mjs --light`) sehingga cukup mendokumentasikan tugas pengunjung, konten nyata, pilihan komposisi, dan rencana verifikasi tanpa mewajibkan 3 alternatif komposisi atau `research-notes.md`.

## 2. Rumuskan Satu Kalimat Tugas Pengunjung

Ubah permintaan umum menjadi tugas pengguna yang dapat diamati:
- **Kurang Spesifik:** "Website modern untuk kedai kopi."
- **Spesifik:** "Pengunjung dari profil sosial media di layar 375x667 dapat memeriksa kisaran harga menu, jam operasional hari ini, dan membuka peta lokasi dalam maksimal dua langkah."

## 3. Kejujuran Konten

Jangan menulis teks placeholder (`Lorem ipsum`, `Your Company`) atau mengarang statistik dan testimoni fiktif karena klaim palsu menurunkan kepercayaan pengguna dan ditolak oleh pemeriksaan `check-brief.mjs` serta `slop-scan.mjs`.

## 4. Rencana Gambar (Wajib untuk Domain Visual)

Untuk domain yang membutuhkan fotografi (fotografer, restoran, produk, properti, travel, fashion, pernikahan, event), wajib sertakan bagian `## Rencana gambar` (atau `## Image plan`) di brief sesuai [imagery.md](../../references/imagery.md) karena proyek visual tanpa strategi aset yang jelas akan jatuh ke ilustrasi siluet generik.

## 5. Anggaran Viewport & Rencana Motion

- **Layar Mobile (`320x568` & `375x667`):** Pastikan judul tidak lebih dari 4 baris dan tombol tindakan utama terlihat tanpa geser horizontal (`scrollWidth <= innerWidth`) agar pengguna perangkat kecil dapat langsung berinteraksi.
- **Koreografi Anime.js v4:** Rencanakan maksimal 2-3 momen animasi fungsional dengan durasi masuk di bawah `1200ms` dan dukungan `prefers-reduced-motion` agar animasi membantu orientasi visual tanpa memperlambat interaksi.

## Perintah Verifikasi

Jalankan `node <atlas>/scripts/check-brief.mjs design-brief.md` (tambahkan `--light` untuk brief jalur ringan) dan pastikan keluar dengan status `PASS`.
