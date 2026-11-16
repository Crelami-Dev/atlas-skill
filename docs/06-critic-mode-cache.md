# 06. Critic Terpisah, Mode Penuh/Ringan, Cache Riset

## Tujuan
Berat yang efektif: proses ketat untuk pekerjaan besar, jalur ringan untuk perubahan kecil, review oleh "mata kedua", dan riset yang tidak diulang tanpa alasan.

## Prompt

```
Baca SKILL.md (router), skills/atlas-checker/SKILL.md, skills/atlas-research/SKILL.md, dan references/critical-review.md.

Implementasikan tiga hal:

A. Critic terpisah
1. Buat `skills/atlas-critic/SKILL.md`: instruksi untuk review desain oleh konteks yang terpisah dari pembuat. Input: brief, token, screenshot, laporan checker dan slop-scan. Output: laporan terstruktur berisi masalah berat (harus diperbaiki), saran, dan verdict LOLOS/PERBAIKI.
2. Di Fase Critique pada SKILL.md: jika tool mendukung subagent atau sesi baru, jalankan critic di sana; jika tidak, agen memakai prompt critic dengan aturan "anggap ini karya orang lain, cari kelemahan dulu". Maksimal 2 putaran perbaikan, lalu laporkan sisa masalah dengan jujur.
3. Critic dilarang memuji tanpa bukti; setiap temuan merujuk elemen atau screenshot tertentu.

B. Mode penuh vs ringan
1. Dokumentasikan kriteria: PENUH untuk halaman/desain baru, redesign, atau perubahan arah visual; RINGAN untuk perubahan kecil (warna, spacing, teks, bug visual).
2. MODE RINGAN tetap wajib: memakai token yang ada, menjalankan check-tokens dan slop-scan, dan satu screenshot sebelum/sesudah. Tidak wajib: riset ulang dan tiga alternatif komposisi.
3. Jika ragu, default PENUH. Jika perubahan "kecil" ternyata menyentuh banyak file atau komposisi, naikkan ke PENUH.

C. Cache riset
1. Simpan riset di `research/<slug-proyek>/` dengan tanggal dan ringkasan hasil.
2. Aturan di atlas-research: pakai ulang cache jika brief tidak berubah dan umur cache kurang dari 30 hari; riset ulang jika brief berubah atau cache lebih lama dari itu. Catat alasannya di research-notes.md.

Perbarui evals/scenarios.md dengan skenario untuk ketiganya, dan jalankan npm run validate.
```

## Task

- [ ] `skills/atlas-critic/SKILL.md`
- [ ] Fase Critique di router (maks 2 putaran)
- [ ] Definisi mode penuh vs ringan + aturan naik mode
- [ ] Aturan cache riset (30 hari / brief berubah)
- [ ] Skenario eval baru
- [ ] Validate lulus

## Kriteria selesai

- Critic menghasilkan verdict dan temuan berbukti.
- Perubahan kecil tidak memicu riset ulang penuh.
- Router merujuk atlas-critic.
