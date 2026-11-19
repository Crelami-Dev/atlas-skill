---
name: atlas-design
description: "Gunakan saat menerjemahkan brief dan hasil deal-direction menjadi sistem token CSS, hierarki tipografi 2-font, kontras warna WCAG AA, dan struktur layout makro yang berbeda per domain. Jangan gunakan untuk logika backend atau audit keamanan."
---

# Atlas Design - Sistem Token, Kontras, & Keberagaman Arketipe Struktur

Baca `design-brief.md` dan `.atlas-direction.json` (dari [deal-direction.mjs](../../scripts/deal-direction.mjs)), lalu tetapkan variabel di `design-tokens.css` mengacu pada [design-tokens.css](../../templates/design-tokens.css) serta strategi visual di [imagery.md](../../references/imagery.md).

## 1. Larangan Kerangka Seragam ("Hero 2-Kolom + Kartu Workbench Filter")

Jangan menggunakan susunan *"hero dua kolom di kiri + kartu workbench berisi Search/Filter/Reset di kanan + band berselang-seling"* untuk semua jenis situs karena membuat restoran, halaman acara, dan SaaS terlihat seperti satu template yang hanya ditukar warnanya. Ikuti `dealtPrimaryDirection.macroLayout` dari `.atlas-direction.json`:

| Domain Proyek | Struktur Layout Makro yang Wajib Dipakai | Hal yang Dilarang |
|---|---|---|
| **Restoran / Kafe / Kuliner** | **Full-Bleed Atmospheric Cover + Bar Jam/Alamat + Buku Menu Cetak 2-Kolom** | Dilarang memasang kotak pencarian/dropdown filter di hero atau grafik kurva garis kecil. |
| **Event / Simposium / Festival** | **Poster Tipografi Swiss Lebar Penuh (Tanggal/Lokasi Raksasa) + Grid Pembicara & Tabel Kronologis** | Dilarang memakai hero 2-kolom ala SaaS atau diagram busur kecil yang menyisakan ruang kosong. |
| **Portofolio Fotografer / Arsitek** | **Kolofon Tipis di Atas + Grid Pameran Pelat Asimetris (16:9 & 4:5) + Biografi di Bawah** | Dilarang menaruh input search/select/Reset di atas galeri karya. |
| **Donasi / Laporan Tahunan** | **Dossier Editorial 1-Kolom (68ch) + Kutipan Margin + Grafik Alokasi & Tabel Audit** | Dilarang memakai shell dashboard atau toolbar filter di bagian pembuka. |
| **Toko Online / Produk Fisik** | **Panggung Galeri Produk Multi-Sudut (60%) + Panel Varian/Ukuran & Akordeon Spesifikasi (40%)** | Dilarang memasang toolbar pencarian tabel pada halaman satu produk. |
| **Dashboard Operasional / Keuangan** | **App Shell Layar Penuh (Sidebar Kiri + Baris KPI + Tabel Data Padat dengan Pencarian/Filter)** | Dilarang memasang banner hero pemasaran besar yang memakan ruang kerja. |
| **Dokumentasi Developer** | **Portal 3-Panel (Pohon Navigasi Kiri + Panduan & Tab Kode + Daftar Isi Kanan)** | Dilarang memakai tata letak landing page promosi. |
| **Pernikahan / Hukum / Pendidikan** | **Kresta Undangan Terpusat & Linimasa** (Pernikahan), **Matriks Praktik Bernomor** (Hukum), **Jalur Silabus Mingguan** (Pendidikan) | Dilarang mencampur elemen dashboard SaaS ke situs seremonial atau korporat. |

## 2. Kontras WCAG AA, Maksimal 2 Font, & Bukti Visual Kaya

1. **Kepatuhan Kontras WCAG AA:** Pastikan setiap pasangan teks dan latar di `design-tokens.css` memiliki rasio kontras minimal `4.5:1` agar teks selalu terbaca jelas.
2. **Maksimal 2 Keluarga Font:** Deklarasikan paling banyak 2 keluarga font di `design-tokens.css` untuk menjaga kecepatan muat dan konsistensi hierarki.
3. **Strategi Gambar & Placeholder Terdesain:** Ikuti alur keputusan di [imagery.md](../../references/imagery.md): (a) gunakan aset pengguna bila tersedia; (b) bila domain butuh foto (fotografer, restoran, produk, properti, travel, fashion, event, pernikahan) namun aset belum ada, bangun dengan bingkai placeholder berasio tetap (`data-photo-placeholder`), komposisi tipografis/tekstur kaya, caption/alt bermakna, dan penanda halus `"Ganti dengan foto asli"` sembari meminta foto asli kepada pengguna di pesan akhir. Jangan menggambar siluet SVG bukit+matahari generik.

## Perintah Verifikasi

Jalankan `node <atlas>/scripts/check-tokens.mjs <project-root> --tokens <token-file>` dan `node <atlas>/scripts/check-visual-proof.mjs <project-root>`.
