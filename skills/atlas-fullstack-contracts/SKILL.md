---
name: atlas-fullstack-contracts
description: "Gunakan saat menghubungkan UI frontend ke API atau adaptor data mock bertipe, mengatur batas sesi autentikasi, variabel lingkungan, dan metadata SEO/OpenGraph. Jangan gunakan untuk komponen presentasi murni tanpa data atau metadata halaman."
---

# Atlas Fullstack Contracts & Kesiapan Proyek

Modul ini mengatur batas antara antarmuka pengguna dengan lapisan data, autentikasi, variabel lingkungan, dan metadata dokumen.

## 1. Lapisan Data dan Adaptor Layanan (`src/data/` atau `src/services/`)

Pisahkan definisi tipe dan pemanggilan data dari komponen tampilan karena menyisipkan array objek besar langsung di dalam komponen JSX/Vue membuat kode sulit diuji dan dipelihara:

- **Skema Domain Bertipe:** Definisikan tipe TypeScript, JSDoc, atau skema validasi untuk entitas utama (`Product`, `BookingSlot`, `ApiError`) di modul terpisah.
- **Batas Layanan yang Jelas:** Arahkan pembacaan dan perubahan data melalui fungsi layanan (`getRooms()`, `submitInquiry(payload)`). Jika proyek berupa prototipe frontend tanpa backend aktif, simpan perubahan state secara lokal dan beri label simulasi secara jujur agar pengguna tidak mengira transaksi nyata telah terkirim ke server.

## 2. Keamanan Sisi Klien & Batas Autentikasi

- **Perlindungan Rahasia Lingkungan:** Jangan menempatkan kunci API privat, kredensial database, atau secret penandatanganan di dalam variabel `NEXT_PUBLIC_*`, `VITE_*`, `PUBLIC_*`, atau bundle klien karena seluruh kode frontend dapat dibaca langsung oleh publik di browser. Sediakan `.env.example` berisi contoh placeholder yang aman.
- **Pencegahan XSS DOM:** Hindari memasukkan string dari pengguna atau parameter URL ke dalam `dangerouslySetInnerHTML`, `v-html`, atau `.innerHTML` karena membuka celah eksekusi skrip lintas situs (XSS).
- **Status Sesi:** Jika aplikasi memiliki fitur login, sediakan tampilan yang jelas untuk kondisi belum masuk, sedang memproses, kredensial ditolak, dan sesi kedaluwarsa.

## 3. Metadata Dokumen, Aset, & Pencegahan CLS

- Tetapkan `<title>`, `<meta name="description">`, atribut `<html lang="...">`, struktur landmark (`<header>`, `<main id="main-content">`, `<footer>`), serta tautan lewati-ke-konten (skip link).
- Sediakan metadata OpenGraph (`og:title`, `og:description`, `og:type`) dan favicon lokal/inline SVG agar browser tidak menghasilkan error `404 /favicon.ico` di konsol.
- Cantumkan atribut `width` dan `height` (atau `aspect-ratio` CSS) pada setiap elemen `<img>`, `<video>`, dan `<svg>` agar browser dapat mengalokasikan ruang sebelum gambar selesai dimuat.
