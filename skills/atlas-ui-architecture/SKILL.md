---
name: atlas-ui-architecture
description: "Gunakan saat merancang arsitektur aplikasi web multi-tampilan, dashboard, tabel data, sistem filter, modal/drawer, dan formulir interaktif. Jangan gunakan untuk halaman artikel statis tanpa interaksi data."
---

# Atlas UI Architecture - Arsitektur Aplikasi & Kontrak 5-State

Gunakan modul ini saat membangun aplikasi yang memiliki navigasi antar-tampilan, daftar atau tabel dinamis, pencarian/filter, dialog, atau formulir input.

## 1. Pemilihan App Shell Sesuai Jenis Proyek

Pilih kerangka navigasi yang sesuai dengan tugas utama pengguna agar ruang layar tidak habis oleh navigasi yang tidak perlu:

| Jenis Proyek | App Shell Desktop | Adaptasi Mobile (`<= 767px`) |
|---|---|---|
| Situs Editorial / Layanan | Bar navigasi atas + CTA fokus + indeks footer | Bar atas ringkas + drawer layar penuh yang mendukung tombol `Escape` |
| Dashboard / Aplikasi SaaS | Sidebar kiri yang dapat diciutkan (`240px` / `64px`) + panel kerja utama | Navigasi bawah (maksimal 4-5 menu) atau slide-over drawer tanpa overflow horizontal |
| Katalog / E-Commerce / Booking | Header filter lengket + grid katalog + ringkasan pesanan | Bar filter/ringkasan bawah yang membuka dialog lembar (sheet) |
| Dokumentasi / Basis Pengetahuan | 3 kolom (`navigasi kiri` + `teks 65ch` + `daftar isi kanan`) | 1 kolom baca + `<details>` daftar isi yang dapat dibuka di bagian atas |

## 2. Kontrak 5-State untuk Tampilan Berbasis Data

Setiap daftar, tabel, grafik, atau hasil pencarian perlu mendukung 5 kondisi tampilan berikut karena pengguna nyata akan mengalami jeda jaringan, data kosong, atau pencarian tanpa hasil:

1. **Loading State:** Kerangka placeholder (`aria-busy="true"`) dengan tinggi yang sesuai ukuran elemen akhir agar tidak menimbulkan pergeseran tata letak (CLS).
2. **Populated State:** Data terstruktur dengan pemotongan teks yang aman (`min-width: 0`) dan angka berformat tabular (`font-variant-numeric: tabular-nums`).
3. **Empty Dataset State:** Penjelasan jelas mengapa belum ada data beserta tombol tindakan untuk membuat atau mengimpor entri pertama.
4. **Filtered Zero-Match State:** Berbeda dari dataset kosong; tampilkan kata kunci/filter yang tidak cocok dan sediakan tombol **"Reset Filter"** satu klik untuk memulihkan daftar.
5. **Error / Recovery State:** Pesan kesalahan yang menjelaskan penyebab kegagalan serta tombol **"Coba Lagi" / "Retry"** yang mempertahankan input pengguna.


- **Larangan Dropdown Debug di UI Produksi:** Jangan pernah menampilkan dropdown pemilih state (`Populated / Loading / Empty / Error`) secara terlihat kepada pengunjung halaman karena kontrol tersebut adalah alat pengembang, bukan fitur pengguna. Tampilkan state berdasarkan interaksi data nyata (atau sembunyikan penguji state di balik parameter URL `?debug=1` dengan atribut `hidden` secara default). Selain itu, jangan memasang tombol `Search / Filter / Reset` pada halaman naratif, restoran, undangan, atau portofolio yang hanya memiliki sedikit item.

## 3. Tabel Responsif, Dialog, dan Formulir

- **Tabel Data Lebar:** Bungkus tabel di dalam kontainer `overflow-x: auto` tersendiri agar tabel yang memiliki banyak kolom tidak merusak lebar viewport halaman utama di layar ponsel.
- **Dialog & Drawer Aksesibel:** Gunakan elemen `<dialog>` bawaan (atau kelola fokus, `Escape`, dan pengembalian fokus ke tombol pemicu) karena `<div onClick>` tanpa manajemen fokus tidak dapat diakses lewat keyboard.
- **Label & Validasi Formulir:** Pasangkan `<label>` eksplisit di atas setiap input karena atribut `placeholder` hilang saat pengguna mulai mengetik. Nonaktifkan tombol kirim selama proses pengiriman berlangsung untuk mencegah pengiriman ganda.
