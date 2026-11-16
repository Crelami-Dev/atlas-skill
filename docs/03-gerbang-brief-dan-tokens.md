# 03. Gerbang Brief dan Design Tokens

## Tujuan
Memaksa agen berpikir sebelum menulis kode: tanpa `design-brief.md` dan file token, fase Build tidak boleh dimulai. Token mencegah nilai asal-asalan, penyebab utama hasil yang terasa "AI banget".

## Prompt

```
Baca SKILL.md, skills/atlas-plan/SKILL.md, skills/atlas-design/SKILL.md, references/typography.md, dan references/interaction-design.md.

Buat dua hal:

A. Template dan validator brief
1. Buat `templates/design-brief.md` dengan bagian wajib: Pengunjung dan tugas utamanya; Konten nyata (tanpa lorem ipsum); Tiga alternatif komposisi (masing-masing: ide, kekuatan, risiko); Pilihan akhir + alasan; Hal yang sengaja DITOLAK dan kenapa; Rencana verifikasi.
2. Buat script `scripts/check-brief.mjs` (Node, tanpa dependensi) yang gagal (exit code 1) jika: file tidak ada, ada bagian wajib yang kosong, jumlah alternatif kurang dari 3, ada "lorem ipsum" atau placeholder seperti "Your Company".
3. Brief maksimal satu halaman; tambahkan batas panjang di validator.

B. Template dan validator token
1. Buat `templates/design-tokens.css` (CSS custom properties) berisi: skala tipografi (ukuran, line-height, letter-spacing), skala spacing, peran warna (bg, surface, text, muted, accent, border, plus state), radius, elevasi/shadow, durasi dan easing motion. Komentar singkat menjelaskan tiap kelompok.
2. Buat `scripts/check-tokens.mjs` yang memindai CSS/HTML/JSX proyek dan gagal jika: ada warna hex/rgb/hsl di luar file token, ada nilai font-size/spacing/radius mentah di luar skala, atau ada lebih dari 2 font family.
3. Daftar pengecualian harus eksplisit (file allowlist), bukan diam-diam.

C. Integrasi
Hubungkan keduanya ke gerbang di SKILL.md: Fase Build hanya boleh mulai setelah `check-brief.mjs` lulus dan token ada. Tambahkan perintah npm (`npm run atlas:brief`, `npm run atlas:tokens` atau padanannya di dokumentasi untuk proyek target).

Tambahkan tes di folder tests/ untuk kedua script (kasus lulus dan kasus gagal). Jalankan npm test dan laporkan hasilnya.
```

## Task

- [ ] `templates/design-brief.md`
- [ ] `scripts/check-brief.mjs` + tes
- [ ] `templates/design-tokens.css`
- [ ] `scripts/check-tokens.mjs` + tes
- [ ] Sambungkan ke gerbang fase di SKILL.md
- [ ] Dokumentasi cara menjalankan di proyek target

## Kriteria selesai

- Brief kosong atau berisi lorem ipsum membuat script exit 1.
- Warna hex di luar file token membuat check-tokens exit 1.
- Semua tes lulus.
