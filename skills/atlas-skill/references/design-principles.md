# Atlas Skill Design Principles — Foundational Laws & Guidelines
**Dokumen:** `skills/atlas-skill/references/design-principles.md`  
**Otoritas Sumber:** Nielsen Norman Group (NN/g), W3C WAI (WCAG 2.1 AA), Refactoring UI, web.dev (Google Core Web Vitals)  
**Status Bukti:** Standar Industri Resmi & Praktik Terbaik Terverifikasi

---

## 1. Prinsip Aksesibilitas Web (W3C WAI WCAG 2.1 AA)

Setiap rancangan antarmuka yang dihasilkan Atlas Skill wajib mematuhi standar aksesibilitas berikut secara ketat:

### 1.1. Rasio Kontras Warna (WCAG 1.4.3 & 1.4.11)
- **Teks Reguler (< 18pt / < 24px biasa atau < 14pt / < 19px tebal):** Wajib memenuhi rasio kontras minimal **4.5:1** terhadap warna latar belakang.
- **Teks Besar ($\ge$ 18pt / 24px biasa atau $\ge$ 14pt / 19px tebal):** Wajib memenuhi rasio kontras minimal **3.0:1**.
- **Komponen Antarmuka & Status Grafis (Borders, Icons, Focus Rings):** Wajib memiliki rasio kontras minimal **3.0:1** terhadap warna latar sekitarnya.
- **Larangan Kontras:** Dilarang menggunakan teks abu-abu terang pada latar belakang putih (misal `#A3A3A3` pada `#FFFFFF` yang hanya menghasilkan kontras ~2.3:1).

### 1.2. Ukuran Target Sentuh (Target Size — WCAG 2.5.5 / 2.5.8)
- Seluruh elemen interaktif (tombol, tautan navigasi, accordion toggles, ikon) wajib memiliki area klik/sentuh minimal **$44 \times 44\text{px}$** (atau padding sentuh yang setara) pada layar seluler.
- Tombol aksi tidak boleh terlalu berdekatan (jarak minimum antar target interaktif: **8px**) untuk mencegah kesalahan ketukan pengguna pada layar sentuh.

### 1.3. Hirarki Heading Semantik (WCAG 1.3.1)
- Hanya boleh ada **satu tag `<h1>` per halaman** yang mewakili tujuan utama dokumen.
- Tag `<h2>` harus mendefinisikan seksi-seksi mayor, dan `<h3>` digunakan untuk sub-komponen kartu di dalam seksi tersebut.
- Dilarang melompati level heading (misal dari `<h1>` langsung ke `<h4>` demi tujuan tampilan visual; gunakan kelas CSS untuk penataan gaya).

---

## 2. Hukum Kegunaan Antarmuka (Nielsen Norman Group)

### 2.1. Desain Estetis dan Minimalis (NN/g Heuristic #8)
- Dialog dan tampilan tidak boleh memuat informasi yang tidak relevan atau jarang dibutuhkan.
- Setiap unit informasi tambahan yang tidak perlu akan bersaing dengan unit informasi yang relevan dan mengurangi visibilitas relatifnya.
- **Penerapan Atlas:** Jangan memenuhi situs dengan kartu fitur generik atau lencana klaim kosong. Lebih baik 3 kartu fitur yang relevan secara mendalam daripada 6 kartu klise yang diulang-ulang.

### 2.2. Konsistensi dan Standar (NN/g Heuristic #4)
- Pengguna tidak boleh bertanya-tanya apakah kata, situasi, atau tindakan yang berbeda memiliki arti yang sama.
- Navigasi header harus berada di bagian atas halaman dengan logo di kiri dan link di kanan/tengah. Menu toggle hamburger pada seluler harus menggunakan ikon tiga garis standar (`☰`) dengan atribut `aria-expanded` dan `aria-label`.

### 2.3. Kejelasan Aksi Utama (Fitts's Law & Visual Anchor)
- Setiap halaman wajib memiliki satu tindakan utama (*Primary Action*) yang menonjol secara visual di atas lipatan layar (*above the fold*).
- Tombol sekunder harus memiliki bobot visual yang lebih rendah (misal: gaya *outline* atau *subtle filled*) agar tidak membingungkan pengguna tentang aksi prioritas.

---

## 3. Hirarki Visual & Tata Letak Modern (Refactoring UI)

### 3.1. Hirarki Berbasis Spasi dan Bobot (Bukan Sekadar Garis Pembatas)
- Jangan membatasi setiap elemen dengan kotak bergaris pinggir tebal (*heavy borders*). Gunakan margin spasial yang cukup dan variasi berat font (*font weight*) untuk membedakan kelompok informasi.
- Hubungan kedekatan (*Law of Proximity*): Jarak antara judul kartu dan deskripsinya harus lebih dekat daripada jarak antar kartu yang berbeda.

### 3.2. Skala Spasial Relatif (Proportional Spacing System)
- Gunakan kelipatan skala spasial berbasis `rem` yang teratur (`0.5rem`, `1.0rem`, `1.5rem`, `2.5rem`, `4.0rem`, `6.0rem`).
- Densitas rendah (*low density*) membutuhkan ruang napas lebih besar untuk menciptakan kesan mewah dan tenang. Densitas tinggi (*high density*) membutuhkan ritme rapat yang terstruktur rapi untuk instrumen data.

---

## 4. Stabilitas Visual & Performa Layout (web.dev Core Web Vitals)

### 4.1. Pencegahan Cumulative Layout Shift (CLS)
- Seluruh elemen gambar dan media wajib memiliki atribut dimensi eksplisit `width` dan `height` pada markup HTML untuk memesan ruang sebelum aset dimuat.
- Tipografi eksternal (Google Fonts, Fontshare) wajib disertai `<link rel="preconnect">` dan parameter `display=swap` untuk meminimalkan *Flash of Invisible Text* (FOIT).

### 4.2. Batasan Lantai Responsif (Responsive Floor Constraints)
- Formula fluid `clamp(MIN, PREFERRED, MAX)` wajib memiliki nilai `MIN` yang realistis untuk layar sempit ($\le 360\text{px}$).
- Teks judul utama pada layar 320px tidak boleh melebihi $2.25\text{rem}$ (36px) agar tidak memecah kata panjang (seperti *Craftsmanship* atau *Infrastructure*) menjadi baris tunggal dengan tanda baca yatim piatu.

