---
name: atlas-lean-code
description: "Write lean frontend code with semantic HTML, CSS Grid/Flexbox, narrow local state, and clean lifecycle teardown across React, Next.js, Vue, Svelte, Astro, or Vanilla JS (Gunakan saat menulis kode frontend dengan HTML semantik, CSS Grid/Flexbox, manajemen state lokal yang ramping, dan pembersihan siklus hidup komponen). Do not use for initial design planning."
---

# Atlas Lean Code - Semantik Bersih & Manajemen State Ramping

Kode yang sederhana dan mengikuti standar platform web lebih mudah dipelihara serta jarang mengalami bug tampilan lintas ukuran layar.

## 1. Periksa Konvensi Proyek Host Lebih Dulu

- Baca `package.json`, `tsconfig.json`, struktur folder (`app/`, `pages/`, `src/`), serta konfigurasi CSS yang sudah ada sebelum menambah file baru agar implementasi selaras dengan arsitektur repositori.
- Gunakan komponen bawaan framework yang sudah terpasang (`next/image`, `next/font`, router bawaan) daripada membuat ulang utilitas serupa.

## 2. Tangga Kesederhanaan Implementasi

Pilih lapisan paling dasar yang mampu memenuhi kebutuhan interaksi secara utuh karena abstraksi JavaScript yang berlebihan memperbesar ukuran bundle dan risiko bug state:

1. **HTML5 Semantik:** Gunakan `<main>`, `<nav>`, `<header>`, `<section aria-labelledby>`, `<button type="button">`, `<a href>`, `<details>/<summary>`, dan `<dialog>`.
2. **Tata Letak CSS Modern:** Gunakan CSS Grid (`minmax(0, 1fr)`), Flexbox (`gap`), `clamp()`, `aspect-ratio`, dan variabel `design-tokens.css`. Jangan menghitung lebar kolom dengan listener `resize` JavaScript karena CSS menangani reflow secara jauh lebih cepat.
3. **State Lokal Sempit:** Simpan state di komponen interaktif terkecil dan hitung daftar terfilter atau total secara turunan (`useMemo` / `computed`) agar tidak terjadi ketidakcocokan sinkronisasi antar-state.
4. **Pembersihan Animasi:** Isolasi animasi Anime.js v4 di dalam `createScope({ root })` dan panggil `scope.revert()` saat unmount (lihat [atlas-motion-animejs](../atlas-motion-animejs/SKILL.md)).

## 3. Pencegahan 6 Bug Umum Frontend

- **Luapan Teks pada Flex/Grid:** Tambahkan `min-width: 0` pada elemen anak flex/grid yang memuat judul panjang, URL, atau tabel agar konten membungkus dengan rapi pada layar `320px`.
- **Balapan Request Async / Klik Ganda:** Nonaktifkan tombol kirim saat `isSubmitting` bernilai aktif dan gunakan `AbortController` pada pencarian cepat agar respons lama tidak menimpa hasil terbaru.
- **Key List yang Stabil:** Gunakan ID unik item (`item.id`) sebagai `key` pada daftar yang dapat difilter atau diurutkan karena penggunaan indeks array menyebabkan bug tampilan dan animasi yang salah sasaran.
- **Kontrol Aksesibel:** Berikan `aria-label` pada tombol yang hanya berisi ikon dan pastikan indikator fokus (`:focus-visible`) terlihat jelas untuk navigasi keyboard.
- **Aset Valid:** Pastikan setiap path gambar, SVG, dan font yang dirujuk benar-benar ada di disk agar tidak menimbulkan error `404`.
- **Perapian Akhir:** Hapus import yang tidak terpakai, kelas CSS mati, dan `console.log` debug sebelum menyerahkan hasil.
