# 08. Eval A/B: Dengan vs Tanpa Skill

## Tujuan
Mendapat bukti bahwa skill benar-benar memperbaiki hasil. Ini yang paling menentukan arah iterasi berikutnya, dan bahan README yang meyakinkan.

## Prompt

```
Baca evals/scenarios.md, tests/, dan README.md.

Buat kerangka eval A/B:
1. `evals/prompts/`: 8 prompt desain tetap dan beragam (mis. landing page SaaS, portofolio fotografer, halaman event, dashboard sederhana, halaman produk, situs restoran, halaman donasi, docs landing). Tiap prompt satu file, isi kebutuhan dan konten nyata, tanpa menyebut gaya visual.
2. `evals/run-protocol.md`: protokol menjalankan tiap prompt dua kali pada agen/model yang sama: (A) tanpa skill, (B) dengan skill. Simpan output ke `evals/results/<tanggal>/<prompt>/A` dan `/B`, termasuk screenshot di 3 viewport (375, 820, 1440) memakai checker.
3. `evals/rubric.md`: rubrik skor 1-5 untuk: hierarki visual, tipografi, kekhasan (tidak generik), kekonsistenan sistem, responsif, aksesibilitas dasar, kejujuran konten. Tiap skor punya deskripsi jangkar. Penilaian dilakukan buta (nama A/B diacak) oleh manusia; sertakan template lembar skor.
4. `evals/compare.mjs`: gabungkan hasil skor + hasil slop-scan + hasil checker menjadi tabel perbandingan (A vs B) per prompt dan rata-rata.
5. Tambahkan bagian README "Bukti" yang diisi setelah eval pertama: 3 contoh before/after dan tabel ringkas. Jangan mengarang angka; biarkan placeholder jelas sampai eval benar-benar dijalankan.

Jalankan validasi paket. Laporkan apa yang sudah siap dan apa yang harus kujalankan/nilai sendiri.
```

## Task

- [ ] 8 prompt tetap di `evals/prompts/`
- [ ] Protokol A/B
- [ ] Rubrik skor + lembar skor buta
- [ ] `compare.mjs`
- [ ] Bagian "Bukti" di README (placeholder jujur)
- [ ] Jalankan eval pertama, nilai, isi README

## Kriteria selesai

- Semua prompt dan protokol bisa diulang oleh orang lain.
- Hasil A dan B tersimpan dengan screenshot.
- README hanya memuat angka dari eval yang sungguh dijalankan.
