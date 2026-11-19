# Standar Komposisi & Kepadatan Visual (Atlas v6.0)

Dokumen ini menetapkan aturan komposisi halaman yang dapat diperiksa secara terukur agar setiap section memiliki bobot visual yang seimbang, mudah dipindai, dan bebas dari ruang kosong yang tidak disengaja.

## 1. Satu Titik Fokus Kuat per Section

- Setiap `<section>` wajib memiliki tepat satu titik fokus visual atau tipografis yang memimpin mata pengunjung (misalnya: angka/pernyataan kunci berskala `--text-2xl`/`--text-3xl`, tabel perbandingan utama, panggung media/foto berbingkai, atau matriks jadwal).
- Jangan menaruh dua komponen besar dengan bobot visual setara yang saling berebut perhatian di dalam satu viewport tanpa hierarki primer-sekunder yang jelas.

## 2. Ukuran Teks Isi Minimal 16px

- Teks paragraf isi (`<p>`) dan item daftar bacaan utama (`<li>`) wajib memiliki ukuran terkomputasi minimal `16px` (`1rem` / `var(--text-base)`) agar nyaman dibaca di layar desktop maupun ponsel tanpa perlu memperbesar layar.
- Ukuran di bawah `16px` (`--text-sm` atau `--text-xs`) hanya boleh dipakai untuk metadata sekunder, label kolom tabel, badge status, atau caption gambar (`<figcaption>`).

## 3. Lebar Baris Bacaan 60–75 Karakter (60ch–75ch)

- Batasi lebar kontainer paragraf naratif pada `60ch` hingga `75ch` (misalnya `max-width: 68ch`).
- Baris teks yang membentang penuh selebar kontainer `1200px+` melelahkan mata saat berpindah baris, sedangkan kolom teks utama yang terlalu sempit (`< 45ch` di desktop) membuat ritme baca terputus-putus.

## 4. Tidak Ada Area Kosong Besar yang Tidak Disengaja

- Hindari kotak kartu, panggung SVG, atau section tinggi (`> 260px`) yang menyisakan lebih dari 85% ruang kosong tanpa fungsi komposisi.
- Jika sebuah gambar atau diagram berukuran ringkas, sesuaikan tinggi kontainer dengan rasio kontennya (`aspect-ratio` atau `height: auto`) daripada memaksakan `min-height: 500px` yang kosong.

## 5. Kepadatan Konten Kartu yang Masuk Akal

- Setiap kartu di dalam grid harus memuat informasi yang membantu keputusan pengguna (misalnya: judul spesifik, 2–3 atribut/data konkret, dan tautan/tindakan jelas), bukan sekadar satu kalimat klise pendek di dalam kotak besar.
- Batasi jumlah titik data per kartu maksimal 3–4 elemen agar kartu tidak berubah menjadi dinding teks sempit.

## 6. Larangan Section Gelap Berisi Paragraf Panjang Saja

- Section berlatar gelap (`--color-blueprint` / `luminance < 0.12`) berfungsi sebagai penegas ritme (anchor) untuk spesifikasi teknis, kutipan pendek berdampak tinggi, matriks angka, kode, atau panggung media.
- Jangan menaruh paragraf prosa panjang (`> 420` karakter teks `<p>` berturut-turut) sendirian di atas latar gelap tanpa struktur tabel, kartu, daftar spesifikasi (`<dl>`), atau media visual, karena teks panjang berlatar gelap menyebabkan kelelahan visual (halation).

## 7. Pemeriksaan Otomatis di `visual_dom_inspector.py`

Script `skills/atlas-checker/scripts/visual_dom_inspector.py` memeriksa aturan komposisi ini secara langsung pada DOM yang dirender oleh Headless Chromium:
- `body-font-too-small`: Memperingatkan jika ada paragraf isi `<p>` di dalam `<main>` dengan `font-size < 16px`.
- `line-measure-too-wide`: Memperingatkan jika paragraf bacaan panjang memiliki lebar render `> 820px` (melampaui ~75–80 karakter pada ukuran font standar).
- `excessive-empty-area`: Memperingatkan jika `<section>` berukuran besar memiliki rasio cakupan elemen konten `< 14%` (ruang kosong tak disengaja `> 86%`).
- `dark-section-long-prose-only`: Memperingatkan jika `<section>` berlatar gelap hanya berisi paragraf panjang tanpa elemen struktural/media.
- `low-text-contrast`: Menandai error jika rasio kontras WCAG antara warna teks terkomputasi dan warna latar efektif jatuh di bawah `4.5:1` (atau `3.0:1` untuk teks `>= 24px`).
- `desktop-overflow` / `mobile-viewport-blowout-*`: Menandai error jika terjadi overflow horizontal pada viewport desktop, tablet, atau mobile.
