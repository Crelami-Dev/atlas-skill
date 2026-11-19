---
name: atlas-anti-slop
description: "Gunakan saat menulis atau meninjau salinan teks, struktur komponen, dan gaya visual untuk mendeteksi serta menghapus 18 pola klise AI (slop) menggunakan slop-scan.mjs. Jangan gunakan untuk logika non-UI."
---

# Atlas Anti-Slop - Pemeriksaan Pola Klise UI

Pola klise AI (*slop*) muncul ketika halaman diisi dengan struktur template generik dan jargon pemasaran tanpa kaitan dengan domain proyek. Baca [slop-patterns.md](../../references/slop-patterns.md) dan jalankan pemindai `slop-scan.mjs` pada Fase 4 dan Fase 6.

## 1. Perbandingan Kode Buruk vs Baik

### Kontras A: Bagian Pembuka (Hero) & Teks

Contoh yang dihindari (template SaaS ungu-biru generik dengan klaim tanpa bukti):
```html
<section class="text-center py-24 bg-gradient-to-r from-purple-600 to-blue-600">
  <span class="rounded-full px-4 py-1 bg-white/10">✨ Solusi Komprehensif Di Era Digital</span>
  <h1 class="bg-clip-text text-transparent">Transformasi Bisnis Anda Secara Seamless</h1>
  <p>Dipercaya oleh 10.000+ tim inovatif di seluruh dunia.</p>
</section>
```

Contoh yang disarankan (spesifik terhadap domain, berbasis bukti, dan memakai token):
```html
<section class="hero-split" data-hero>
  <div class="hero-copy">
    <p class="eyebrow">Bengkel Restorasi Jam Mekanik • Cikini, sejak 2014</p>
    <h1 data-hero-title>Servis mesin otomatis Swiss & Jepang dengan garansi kalibrasi 12 bulan.</h1>
    <p class="lead">Pemeriksaan amplitudo di ruang tunggu tanpa biaya cek awal. Estimasi pengerjaan 5–10 hari kerja tergantung ketersediaan suku cadang asli.</p>
    <div class="hero-actions">
      <a data-primary class="btn-primary" href="#estimasi">Cek Estimasi Servis</a>
      <a class="btn-secondary" href="#alamat">Jam Buka & Lokasi</a>
    </div>
  </div>
  <figure class="hero-evidence">
    <img src="/assets/timegrapher-bench.webp" width="960" height="720" alt="Pengujian akurasi mesin jam pada alat timegrapher" />
    <figcaption>Kalibrasi posisi 5-arah sebelum serah terima.</figcaption>
  </figure>
</section>
```

### Kontras B: Penyajian Fitur dan Bukti

- **Hindari 3 Kartu Ikon/Emoji Identik:** Tiga kartu berisi `🚀 Cepat`, `🔒 Aman`, dan `💎 Terbaik` tidak memberi informasi baru kepada pengunjung karena dapat ditempelkan ke situs apa pun tanpa perubahan makna.
- **Gunakan Bukti Spesifik Domain:** Ganti kata sifat umum dengan tabel spesifikasi, rincian harga, kalkulator interaktif, atau tahapan proses yang menjawab pertanyaan nyata pengunjung.

## 2. Daftar Periksa Sebelum Selesai

1. **Uji Substitusi:** Jika nama merek diganti menjadi "CloudAI" dan 90% isi halaman masih terasa cocok, ubah dua bagian pertama agar menampilkan alur kerja atau data spesifik milik subjek.
2. **Bebas Frasa Klise:** Hapus frasa seperti `solusi komprehensif`, `di era digital`, `inovasi tanpa batas`, `unlock the power`, `elevate`, `seamless`, `revolutionize`, dan `"Bukan sekadar X, tapi Y"` karena menurunkan kejelasan pesan.
3. **Tanpa Ornamen Tanpa Fungsi:** Hindari bola blur bercahaya dekoratif, titik lampu lalu-lintas jendela palsu pada situs non-developer, dan animasi melayang tanpa henti di dekat teks bacaan karena mengganggu fokus baca.
4. **Verifikasi Pemindai:** Jalankan `node <atlas>/skills/atlas-checker/scripts/slop-scan.mjs <project-root>` hingga menghasilkan `0` error dan periksa setiap peringatan yang muncul.

- **Kontrol Debug State Terbuka:** Jangan merender dropdown atau tombol pemilih state (`Populated / Loading / Empty / Error`) di UI produksi karena itu adalah alat uji pengembang; jika diperlukan untuk pengujian, beri atribut `hidden` secara default dan hanya tampilkan saat URL memuat `?debug=1`.
