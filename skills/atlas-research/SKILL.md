---
name: atlas-research
description: "Conduct domain reference research and UI mechanism comparisons before designing a new project in an unfamiliar domain (Gunakan saat membutuhkan riset referensi domain atau perbandingan pola antarmuka sebelum mendesain proyek baru pada domain yang belum dikenal). Do not use for small, obvious prompts or bug fixes."
---

# Atlas Research - Analisis Mekanisme Referensi

Riset domain membantu menemukan struktur informasi yang relevan dengan topik tanpa menyalin tampilan situs lain. Pada Jalur Ringan (prompt singkat dengan domain yang sudah familier), pembuatan `research-notes.md` bersifat opsional kecuali diminta secara eksplisit oleh pengguna.

## 1. Jalur Pengumpulan Bukti

Ketika riset diperlukan, gunakan alat yang tersedia di lingkungan agen untuk menyusun `research-notes.md` berdasarkan [research-template.md](../../references/research-template.md):

1. **Inspeksi Browser Langsung:** Gunakan alat browser atau `node <atlas>/skills/atlas-research/scripts/capture-references.mjs --out ./maintenance/research <url>` pada 3-5 situs referensi yang relevan.
2. **Pencarian Web Agen:** Jika browser headless tidak tersedia, gunakan fitur pencarian web dan pembaca halaman untuk memeriksa referensi domain dan pembanding lintas industri.
3. **Lingkungan Offline:** Jangan mengarang URL atau berpura-pura membuka situs ketika akses jaringan mati karena referensi fiktif menyesatkan keputusan desain. Catat `riset live tidak dapat dilakukan (offline environment)` dan gunakan panduan [domain-reasoning.md](../../references/domain-reasoning.md).

## 2. Pemisahan Mekanisme dan Klise Visual

Untuk setiap referensi yang diperiksa, catat dua hal di `research-notes.md`:
- **PRINSIP DIADAPTASI:** Bagaimana urutan informasi, kepadatan data, atau kedekatan filter membantu menyelesaikan tugas pengunjung.
- **ELEMEN DITOLAK:** Warna merek, efek dekoratif berat, atau pembajakan scroll yang sengaja tidak ditiru agar proyek tetap orisinal dan ringan di perangkat mobile.

## 3. Penggunaan Ulang Catatan Riset

Jika `design-brief.md` tidak berubah dan `research-notes.md` berusia kurang dari 30 hari, gunakan kembali catatan yang sudah ada agar iterasi berjalan efisien.
