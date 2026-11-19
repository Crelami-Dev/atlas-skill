# Strategi Gambar, Fotografi, & Pelat Spesimen Editorial (`imagery.md`)

Panduan ini mengatur pengambilan keputusan visual untuk domain yang biasanya bergantung pada fotografi (portofolio fotografer, restoran/kuliner, produk fisik/e-commerce, properti/real estate, travel/pariwisata, fashion, pernikahan, dan event).

## 1. Alur Keputusan Aset Visual

1. **Kondisi A — Pengguna Menyediakan Aset Nyata:**
   - Gunakan file foto/video yang diberikan pengguna secara langsung karena aset asli merupakan bukti paling jujur bagi pengunjung.
   - Pasang atribut `width`, `height`, `aspect-ratio`, `loading="lazy"` (untuk gambar di bawah lipatan pertama), dan `alt` yang mendeskripsikan isi visual secara spesifik.
2. **Kondisi B — Domain Visual tetapi Aset Foto Belum Tersedia:**
   - Tetap bangun halaman secara utuh menggunakan **Pelat Spesimen Editorial / Teknis Spesifik-Domain (`data-photo-slot="..."` + `data-atlas-proof="..."`)** agar komposisi, ritme grid, dan proporsi media tampak **100% selesai** bagi pengunjung tanpa menampilkan teks instruksi internal.
   - **Dilarang Keras di DOM Pengunjung:** Jangan pernah merender teks instruksi untuk pemilik proyek/developer di UI pengunjung seperti `"Ganti dengan foto asli"`, `"Replace with photo"`, `"SLOT FOTO 01"`, `"PHOTO SLOT"`, `"menunggu foto"`, `"Subjek: ..."`, `"[Data Klien Diperlukan]"`, atau kelas `.photo-replace-badge`.
   - **Penandaan Diam-Diam untuk Handoff:** Tandai slot media yang nantinya bisa diganti dengan foto nyata hanya lewat atribut HTML senyap (`data-photo-slot="hero-16x9"`, `data-aspect="16:9"`) serta daftar slot di `design-brief.md` (`## Rencana gambar` / `## Image plan`) dan pesan penutup kepada pengguna (misalnya: *"Slot media telah ditandai dengan `data-photo-slot`. Silakan kirim 3 foto ruang seduh rasio 16:9 dan 4 foto menu rasio 4:5 jika ingin mengganti pelat spesimen saat ini dengan foto asli."*).
3. **Kondisi C — Domain Berbasis Data, Kode, atau Tipografi Murni:**
   - Untuk dashboard operasional, dokumentasi API, atau laporan tekstual, gunakan tabel data nyata, cuplikan terminal/kode, atau grafik data-viz terukur tanpa memaksakan foto dekoratif.

## 2. Pola Pelat Spesimen Spesifik-Domain (Kondisi B)

Saat membangun halaman dalam **Kondisi B**, isi setiap bingkai `<figure data-photo-slot="..." data-atlas-proof="...">` dengan materi domain yang bernilai nyata bagi pengunjung dan bertumpu penuh pada token `--color-*` serta `--font-*`:

- **Fotografer / Arsitektur:** Pelat Monograf & Eksposur Pameran (nomor pelat `PLATE I`, judul seri karya, metadata teknis nyata `35mm • f/2.8 • 1/125s • ISO 400`, gradien pencahayaan terarah, dan catatan kuratorial).
- **Event / Simposium / Festival:** Pelat Denah Panggung & Akustik Ruang atau Poster Tipografi Kronologis (kapasitas kursi, dimensi panggung, jarak pandang, dan jadwal sesi).
- **Produk Fisik / E-Commerce:** Pelat Potongan Material & Dimensi Teknis (toleransi milimeter, lapisan material, komposisi berat, serta perbandingan *swatch* warna/tekstur interaktif).
- **Restoran / Kafe / Kuliner:** Pelat Asal Panen & Profil Cita Rasa (elevasi kebun, proses fermentasi/sangrai, suhu penyajian, catatan rasa, dan pasangan hidangan).
- **Pernikahan / Seremonial:** Pelat Monogram Cetak & Peta Lokasi Acara (inisial tipografis, koordinat/rute lokasi, dan kartu penunjuk waktu).

Contoh markup pelat spesimen yang bersih (tanpa bocoran instruksi placeholder di UI pengunjung):

```html
<figure class="editorial-plate" data-photo-slot="cibeunying-bar-16x9" data-aspect="16:9" data-atlas-proof="editorial-plate">
  <div class="editorial-plate-stage" role="img" aria-label="Studi pencahayaan pagi meja bar kayu jati menghadap taman Cibeunying">
    <div class="editorial-plate-meta">
      <span>PLATE 01 · CIBEUNYING</span>
      <span>16:9 · 07:30 WIB · ORIENTASI TIMUR</span>
    </div>
    <p class="editorial-plate-caption">Meja seduh kayu jati tiga meter dengan pencahayaan alami pagi dan stasiun pour-over berjarak 45 cm antar tamu.</p>
  </div>
  <figcaption>Ruang seduh utama Jl. Taman Cibeunying Selatan No. 14 — kapasitas 18 kursi bar.</figcaption>
</figure>
```

## 3. Pola Visual yang Dilarang Keras

- **Kebocoran Instruksi Placeholder (`leaked-photo-placeholder-ui`):** Dilarang keras menampilkan kalimat seperti `"Ganti dengan foto asli"`, `"Replace with photo"`, `"SLOT FOTO 01"`, `"Image Placeholder"`, `"[Data Klien Diperlukan]"`, atau `"menunggu foto dokumentasi"` di elemen teks maupun `aria-label`.
- **Siluet Kartun Bukit + Matahari (`generic-hill-sun-svg`):** Jangan pernah menggambar `<svg>` berisi lingkaran matahari (`<circle>`) di atas kurva/segitiga gunung atau ombak (`<path>`/`<polygon>`) sebagai pengganti foto karena langsung terlihat seperti ilustrasi generik AI.
- **Ikon Stock atau Gambar Rusak (`broken-images`):** Jangan menaruh ikon kamera/cangkir di tengah kotak kosong, dan jangan pernah mengarahkan `<img src="...">` ke path lokal yang tidak ada atau URL eksternal yang belum diverifikasi.
- **Teks SVG Menabrak Garis (`svg-text-overlap`):** Jangan menaruh `<text>` di atas atau melintasi batas garis (`stroke`) objek di dalam `<svg>`; letakkan anotasi di elemen HTML terpisah.

## 4. Bagian Wajib "Rencana Gambar" (`## Rencana gambar` / `## Image plan`) di Brief

Untuk setiap proyek pada domain visual (fotografer, restoran, produk, properti, travel, fashion, pernikahan, dan event), `design-brief.md` wajib memuat bagian `## Rencana gambar` (atau `## Image plan`) yang merinci:
- Sumber aset (tersedia dari pengguna vs pelat spesimen editorial dengan atribut `data-photo-slot` untuk disambungkan nanti).
- Daftar slot gambar utama beserta rasio aspek (`16:9`, `4:5`, `1:1`) dan aset foto yang diminta ke pengguna di pesan akhir.
