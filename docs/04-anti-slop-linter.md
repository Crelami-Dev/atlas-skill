# 04. Anti-Slop yang Terukur

## Tujuan
Mengubah prinsip anti-slop menjadi (a) daftar pola konkret dengan contoh buruk vs baik, dan (b) script pemindai yang menandai pelanggaran.

## Prompt

```
Baca skills/atlas-anti-slop/SKILL.md, skills/atlas-design/SKILL.md, references/critical-review.md, dan skills/atlas-checker/.

Buat dua bagian:

A. Katalog pola slop (`references/slop-patterns.md`)
Untuk tiap pola tulis: nama, ciri yang bisa dideteksi, kenapa dianggap slop, contoh BURUK (kode singkat), contoh BAIK (kode singkat), dan kapan pola itu SAH dipakai. Minimal 15 pola, misalnya:
- gradien ungu-biru generik sebagai identitas utama
- hero tengah + dua tombol + kartu-kartu fitur tiga kolom bergaya sama
- ikon generik pada setiap kartu fitur
- glassmorphism/blur tanpa alasan fungsional
- emoji sebagai ikon UI
- radius dan shadow seragam di semua elemen
- font default sistem tanpa pilihan sadar, atau lebih dari 2 font family
- teks placeholder (lorem ipsum, "Your Company", "Feature One")
- statistik atau testimoni karangan
- animasi dekoratif yang tidak membantu tugas pengunjung
- kontras rendah, target sentuh kecil, heading tidak berurutan
Pola yang butuh penilaian visual ditandai "perlu mata manusia/screenshot" dan tidak dipalsukan sebagai terdeteksi otomatis.

B. Pemindai (`skills/atlas-checker/scripts/slop-scan.mjs`)
1. Node tanpa dependensi runtime; menerima direktori proyek; memindai HTML/CSS/JSX/TSX/Vue/Svelte.
2. Mendeteksi yang bisa dideteksi dengan aturan sederhana: gradien ungu-biru pada elemen besar, jumlah font family, emoji pada elemen UI, lorem ipsum/placeholder, jumlah nilai radius/shadow berbeda, pola grid tiga kartu identik berulang, dan sejenisnya.
3. Keluaran: laporan JSON + ringkasan teks (file, baris, pola, saran perbaikan). Exit code 1 jika ada pelanggaran tingkat "error"; tingkat "warn" tidak menggagalkan.
4. Tiap aturan punya id, tingkat, dan bisa dimatikan lewat file konfigurasi dengan alasan wajib ditulis.
5. Beri tes dengan fixture buruk dan fixture baik di tests/.

Sambungkan ke Fase Verify di SKILL.md: agen wajib menjalankan slop-scan dan menempelkan ringkasannya di laporan akhir. Jelaskan batas pemindai di README: ia menangkap sinyal, bukan menilai keindahan.
```

## Task

- [ ] `references/slop-patterns.md` (minimal 15 pola, contoh buruk vs baik)
- [ ] `slop-scan.mjs` dengan aturan, tingkat error/warn, konfigurasi
- [ ] Fixture dan tes
- [ ] Sambungkan ke Fase Verify
- [ ] Catat batas pemindai di README

## Kriteria selesai

- Fixture buruk memicu exit 1, fixture baik exit 0.
- Setiap pola yang tidak bisa dideteksi otomatis ditandai jujur.
- Laporan akhir agen wajib memuat ringkasan slop-scan.
