# Strategi Gambar, Fotografi, & Placeholder Terdesain (`imagery.md`)

Panduan ini mengatur pengambilan keputusan visual untuk domain yang membutuhkan fotografi nyata (portofolio fotografer, restoran/kuliner, produk fisik/e-commerce, properti/real estate, travel/pariwisata, fashion, pernikahan, dan event).

## 1. Alur Keputusan Aset Visual

1. **Kondisi A — Pengguna Menyediakan Aset Nyata:**
   - Gunakan file foto/video yang diberikan pengguna secara langsung karena aset asli merupakan bukti paling jujur bagi pengunjung.
   - Pasang atribut `width`, `height`, `aspect-ratio`, `loading="lazy"` (untuk gambar di bawah lipatan pertama), dan `alt` yang mendeskripsikan isi visual secara spesifik.
2. **Kondisi B — Domain Membutuhkan Foto tetapi Aset Belum Tersedia:**
   - Tetap bangun halaman secara utuh menggunakan **Bingkai Placeholder Editorial Terdesain (`[data-photo-placeholder]`)** agar tata letak, ritme grid, dan proporsi media siap pakai tanpa menunggu aset.
   - Cantumkan permintaan aset foto yang spesifik kepada pengguna pada pesan penutup akhir (misalnya: *"Silakan unggah 3 foto ruang seduh rasio 16:9 dan 4 foto menu rasio 4:5 untuk menggantikan bingkai placeholder saat ini"*).
3. **Kondisi C — Domain Berbasis Data, Kode, atau Tipografi Murni:**
   - Untuk dashboard operasional, dokumentasi API, atau laporan tekstual, gunakan tabel data nyata, cuplikan terminal/kode, atau grafik data-viz terukur tanpa memaksakan foto dekoratif.

## 2. Spesifikasi Bingkai Placeholder Terdesain (`[data-photo-placeholder]`)

Saat membangun halaman dalam **Kondisi B**, setiap placeholder foto wajib memenuhi empat kriteria berikut agar halaman tetap tampak selesai dan mudah diganti:

1. **Rasio Tetap & Dimensi Eksplisit:** Kunci proporsi bingkai sesuai fungsi konten (`aspect-ratio: 16 / 9` untuk lanskap arsitektur/ruang, `aspect-ratio: 4 / 5` untuk potret editorial/fashion/fotografer, atau `aspect-ratio: 1 / 1` untuk detail produk) dengan latar bertekstur halus.
2. **Komposisi Tipografis, Grid Spesimen, atau Tekstur Berlapis:** Isi bingkai dengan struktur metadata fotografi (nomor pelat `PLATE 01`, spesifikasi rasio/resolusi target `1600×2000px • 4:5`, pencahayaan/subjek yang direncanakan) di atas pola grid teknis atau gradasi tonal yang selaras dengan token `--color-surface` dan `--color-blueprint`.
3. **Caption & Alt Text Bermakna:** Gunakan `<figure>` dan `<figcaption>` yang menjelaskan konteks foto yang akan dipasang (bukan `alt="image"` atau `alt="placeholder"`).
4. **Penanda Halus "Ganti dengan Foto":** Tambahkan atribut `data-photo-placeholder="true"` dan lencana kecil yang mudah dihapus (`[Ganti dengan foto: <subjek & rasio>]` / `[Replace with photo: <subject & ratio>]`).

Contoh markup placeholder terdesain yang disarankan:

```html
<figure class="photo-placeholder-frame" data-photo-placeholder="true" data-atlas-proof="editorial-photo-slot">
  <div class="photo-slot-canvas" role="img" aria-label="Slot foto utama: Suasana meja seduh kayu jati menghadap jendela taman Cibeunying (rasio 16:9)">
    <div class="photo-slot-header">
      <span>SLOT FOTO 01 • RASIO 16:9 (1920×1080px)</span>
      <span class="photo-replace-badge">Ganti dengan foto asli</span>
    </div>
    <p class="photo-slot-subject">Subjek: Meja bar pour-over kayu jati dengan pencahayaan alami pagi dari arah timur.</p>
  </div>
  <figcaption>Ruang seduh utama Jl. Taman Cibeunying Selatan No. 14 — menunggu foto dokumentasi lokasi.</figcaption>
</figure>
```

## 3. Pola Visual yang Dilarang Keras

- **Siluet Kartun Bukit + Matahari (`generic-hill-sun-svg`):** Jangan pernah menggambar `<svg>` berisi lingkaran matahari (`<circle>`) di atas kurva/segitiga gunung atau ombak (`<path>`/`<polygon>`) sebagai pengganti foto fotografer, properti, travel, atau restoran karena merusak kredibilitas desain dan langsung terlihat seperti ilustrasi generik AI.
- **Ikon Stock Sebagai Pengganti Foto Produk/Makanan:** Jangan menaruh ikon cangkir atau ikon kamera besar di tengah kotak kosong untuk mewakili foto produk.
- **Klaim Palsu Atas Placeholder:** Jangan memberi label pada kotak warna atau vektor abstrak seolah-olah itu adalah foto dokumenter asli; selalu beri penanda `Ganti dengan foto asli` / `Replace with photo` secara jujur.

## 4. Bagian Wajib "Rencana Gambar" (`## Rencana gambar` / `## Image plan`) di Brief

Untuk setiap proyek pada domain visual (fotografer, restoran, produk, properti, travel, fashion, pernikahan, dan event), `design-brief.md` wajib memuat bagian `## Rencana gambar` (atau `## Image plan`) yang merinci:
- Sumber aset (tersedia dari pengguna vs slot placeholder terdesain yang perlu diganti pengguna).
- Daftar slot gambar utama beserta rasio aspek (`16:9`, `4:5`, `1:1`) dan subjek foto yang dibutuhkan.

## Aturan Tambahan Bingkai & Ilustrasi Teknis

- **Badge Penanda Tetap Satu Baris:** Penanda `"Ganti dengan foto asli"` pada `[data-photo-placeholder]` wajib menggunakan `white-space: nowrap` dan `flex-shrink: 0` agar tidak terlipat ke dua baris di layar mobile `375px`.
- **Larangan Teks SVG Menabrak Garis:** Jangan menaruh elemen `<text>` di atas atau melintasi batas garis (`stroke`) objek di dalam `<svg>`; letakkan anotasi di kolom keterangan HTML terpisah atau di luar koordinat bentuk.
- **Hindari Kotak Kosong di Placeholder:** Setiap bingkai `[data-photo-placeholder]` harus memiliki komposisi tipografis/gradien penuh sesuai rasio aspeknya tanpa menyisakan ruang kosong `> 30%` di sekitar konten.
