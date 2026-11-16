# 05. Checker yang Gagal Tegas + Doctor

## Tujuan
Membuat "selesai" hanya sah jika ada bukti. Jika alat verifikasi tidak tersedia, agen harus melapor "tidak terverifikasi", bukan "lulus".

## Prompt

```
Baca skills/atlas-checker/SKILL.md, skills/atlas-checker/scripts/quick-check.mjs, bin/ (installer), dan docs/INSTALLATION.md.

Tugas:
1. quick-check.mjs: tetapkan kontrak exit code yang jelas: 0 = lulus, 1 = ada pelanggaran, 2 = tidak bisa dijalankan (mis. Playwright/Chromium tidak ada). Output akhir selalu satu baris status: PASS, FAIL, atau UNVERIFIED, diikuti ringkasan.
2. Simpan hasil terstruktur ke `maintenance/browser/report.json` (viewport, pemeriksaan, status tiap pemeriksaan, path screenshot). Pemeriksaan yang dilewati ditulis SKIPPED beserta alasannya, jangan dihitung lulus.
3. Perintah `doctor` pada installer: periksa versi Node (>= 22), Playwright dan Chromium (atau ATLAS_PLAYWRIGHT_PACKAGE / ATLAS_BROWSER_PATH), dan keberadaan folder skill. Cetak langkah pasang yang konkret untuk yang kurang, termasuk catatan untuk Windows (path dan PowerShell) dan macOS/Linux.
4. Aturan di SKILL.md Fase Verify: agen dilarang menyatakan selesai bila status bukan PASS. Jika UNVERIFIED, laporan akhir wajib berkata "tidak terverifikasi secara visual" dan menyebut penyebabnya.
5. Aturan screenshot: agen wajib benar-benar membuka dan memeriksa screenshot minimal untuk satu viewport mobile dan satu desktop, dan menulis temuan visual (bukan hanya angka checker).
6. Tambahkan tes untuk kontrak exit code (gunakan target lokal sederhana atau mock).

Jalankan npm test dan laporkan hasilnya.
```

## Task

- [ ] Kontrak exit code 0/1/2 + status PASS/FAIL/UNVERIFIED
- [ ] `report.json` terstruktur
- [ ] Perintah `doctor` (Node, Playwright, Chromium, catatan Windows)
- [ ] Aturan "dilarang klaim selesai" di SKILL.md
- [ ] Aturan pemeriksaan screenshot
- [ ] Tes

## Kriteria selesai

- Tanpa Playwright, checker keluar dengan kode 2 dan status UNVERIFIED.
- `doctor` memberi instruksi jelas untuk setiap dependensi yang kurang.
