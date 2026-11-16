# Atlas Skill: Paket Prompt & Task Perbaikan

Paket ini berisi prompt siap tempel untuk agen coding (Claude Code, Codex, dll.) beserta daftar task dan kriteria selesai. Satu file = satu pekerjaan, jadi jalankan satu per satu, jangan digabung.

## Urutan eksekusi

| No | File | Tujuan | Prioritas |
|----|------|--------|-----------|
| 01 | `01-repo-hygiene.md` | Lisensi, nama, README, release, cara install | Tinggi (cepat) |
| 02 | `02-skill-router.md` | `SKILL.md` jadi router pendek dengan gerbang fase | Tinggi |
| 03 | `03-gerbang-brief-dan-tokens.md` | Brief dan design tokens wajib sebelum coding | Tinggi |
| 04 | `04-anti-slop-linter.md` | Daftar pola slop + script pemindai | Tinggi |
| 05 | `05-checker-hard-fail.md` | Checker gagal tegas + `doctor` | Sedang |
| 06 | `06-critic-mode-cache.md` | Critic terpisah, mode penuh/ringan, cache riset | Sedang |
| 07 | `07-riset-aman.md` | Aturan riset referensi yang aman dan terbatas | Sedang |
| 08 | `08-eval-ab.md` | Eval A/B dengan vs tanpa skill | Tinggi (bukti) |

## Cara pakai

1. Buka agen di root repo `atlas-skill`.
2. Salin bagian **Prompt** dari satu file, tempel ke agen.
3. Setelah agen selesai, cek bagian **Kriteria selesai** satu per satu.
4. Commit per file (satu commit per pekerjaan) supaya mudah di-review dan dibatalkan.

## Aturan umum untuk semua prompt

- Agen wajib membaca isi repo yang ada dulu sebelum mengubah apa pun.
- Jangan menghapus fitur yang sudah ada tanpa menyebutkannya di ringkasan.
- Laporan akhir agen harus berisi: apa yang diubah, bukti (output perintah), dan apa yang belum diverifikasi.
- Kalau ada yang tidak jelas, agen menulis asumsinya, bukan menebak diam-diam.
