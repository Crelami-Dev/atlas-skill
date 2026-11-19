---
name: atlas-critic
description: "Gunakan saat mengevaluasi kualitas akhir halaman web berdasarkan 7 sumbu rubrik desain, tipografi, aksesibilitas, dan kerapian kode untuk memberikan keputusan LOLOS/PASS atau PERBAIKI/FIX. Jangan gunakan sebelum pemeriksaan atlas-checker selesai."
---

# Atlas Critic - Evaluasi Rubrik 7 Sumbu

Tinjau hasil tangkapan layar dari [atlas-checker](../atlas-checker/SKILL.md) bersama panduan [critical-review.md](../../references/critical-review.md) karena penilaian dari kode sumber saja sering melewatkan masalah hierarki visual dan keterbacaan. Berikan skor dari total 100 poin pada 7 sumbu berikut:

| Sumbu | Poin Maks | Hal yang Diperiksa |
|---|---:|---|
| **1. Kejelasan Layar Pertama & Bukti Visual** | 20 | Pengunjung langsung memahami fungsi produk; terdapat elemen visual nyata; CTA utama terlihat jelas pada `1440x900` dan `375x667`. |
| **2. Spesifisitas Domain & Uji Substitusi** | 20 | Tata letak dan konten spesifik terhadap topik proyek; bebas dari 3 kartu ikon generik dan SVG wireframe kotak kaku. |
| **3. Tipografi & Keterbacaan** | 15 | Maksimal 2 keluarga font; angka tabular pada tabel/metrik; tidak ada backtick Markdown yang bocor di elemen HTML. |
| **4. Ritme Permukaan & Kontras** | 15 | Pergantian warna permukaan yang terukur antarbagian; kontras teks memenuhi standar WCAG AA (`>= 4.5:1`). |
| **5. Koreografi Motion Anime.js v4** | 10 | Penggunaan `createScope` dengan `revert()`, properti transform GPU, dan penghormatan terhadap `prefers-reduced-motion`. |
| **6. Kelengkapan 5-State & Kerapian Mobile** | 10 | Kondisi loading, berisi data, kosong, hasil filter nol + tombol reset, dan error ditangani tanpa overflow pada layar `320px`/`375px`. |
| **7. Kebersihan Kode & Keamanan Klien** | 10 | Tidak ada error konsol, tidak ada sink XSS `innerHTML`, tidak ada rahasia bocor, dan seluruh gate statis lulus. |

## Aturan Keputusan (Verdict)

- **`LOLOS` / `PASS` (`>= 88/100` dan tanpa cacat fungsional/visual berat):** Proyek siap diserahkan kepada pengguna beserta catatan batasan pengujian yang jujur.
- **`PERBAIKI` / `FIX` (`< 88/100` atau ditemukan cacat pada tangkapan layar):** Perbaiki hingga 3 masalah utama yang ditemukan, ambil ulang tangkapan layar, dan lakukan verifikasi ulang (maksimal 3 putaran).
