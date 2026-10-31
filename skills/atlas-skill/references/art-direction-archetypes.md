# Atlas Skill Art Direction Archetypes — Visual Signatures & Rules
**Dokumen:** `skills/atlas-skill/references/art-direction-archetypes.md`  
**Status Bukti:** Terverifikasi terhadap 202 Situs Pustaka Kanonikal (`data/sites.json`)  
**Tujuan:** Mendefinisikan profil visual, strategi tipografi, palet, hierarki spasial, dan struktur konten untuk arketipe arah seni makro.

---

## 1. Arketipe: Editorial Luxury (Kemewahan Editorial & Keahlian Klasik)

### 1.1. Konteks & Kecocokan Domain
- **Kategori Cocok:** Fesyen haute couture, horlogerie / jam tangan mewah, arsitektur premium, perhotelan eksklusif, galeri seni rupa.
- **Audiens Target:** Patron kelas atas, kurator seni, kolektor internasional, pembeli barang pesanan khusus (*connoisseurs & high-net-worth patrons*).
- **Tujuan Halaman:** Memancarkan prestise, keanggunan abadi, materialitas murni, dan eksklusivitas tanpa kesan komersial murahan.

### 1.2. Tanda Tangan Visual (Visual Signature)
- **Tipografi:** Serif klasik berbobot anggun (misal: `EB Garamond`, `Bodoni Moda`, `Playfair Display`) dipadukan dengan teks sans-serif halus atau serif berbobot reguler. Tanda baca dan ligatur terawat rapi.
- **Palet Warna:** Warna-warna materi alami dan tenang: *Bone / Ivory* (`#F4F1EA`), *Earthy Muted Chocolate* (`#2C221E`), *Forest / Olive Green* (`#3D6B42`), *Deep Charcoal* (`#1C1917`). Menghindari warna neon atau gradien digital sintetis.
- **Densitas & Skala Spasial:** **Densitas Rendah (`low`)**. Ruang napas sangat lapang (`--space-xl: 5.5rem`, `--space-2xl: 8.0rem`, `--max-width: 1320px`).
- **Pola Komposisi:** Penataan asimetris, ruang negatif yang berani, isolasi objek karya seni terfokus (*centred focus or uneven photo layout*).

### 1.3. Arsitektur Informasi & Kontrak Komponen
- **Pengecualian Slot Wajib:** **Dilarang keras menyertakan seksi `pricing` tier standar software ($49/mo)**. Fesyen mewah tidak menjual produk melalui kartu langganan bulanan SaaS.
- **Panggilan Aksi (CTA):** Bersifat santun dan eksklusif (*"Request Private Appointment"*, *"Explore Atelier"*, *"Inquire for Private Salon"*).
- **Alur Kerja (Workflow):** Harus mencerminkan proses kerajinan (*Artisanal Provenance*), misal: *01 Sourcing Rare Materials $\to$ 02 Atelier Sculpting & Patterning $\to$ 03 Master Hand-Finishing*.

### 1.4. Batasan Responsif & Floor Guard
- **Layar Seluler 320px:** Batas minimum `h1_clamp` **tidak boleh melebihi $2.0\text{rem}$** (32px). Dilarang membiarkan kata panjang memecah ampersand (`&`) ke baris tersendiri.
- **Situs Referensi Kanonikal:** `opl-vessa`, `aww-house-of-honey-1`, `aww-white-desert`.

---

## 2. Arketipe: Technical Instrument (Instrumen Presisi & Infrastruktur)

### 2.1. Konteks & Kecocokan Domain
- **Kategori Cocok:** Perkakas pengembang (*dev-tools*), komputasi awan, kernel telemetri, database terdistribusi, arsitektur jaringan, sistem keamanan.
- **Audiens Target:** Insinyur perangkat lunak, arsitek sistem, site reliability engineers (SRE), ilmuwan data, sysadmin.
- **Tujuan Halaman:** Membuktikan otoritas teknis, determinisme sistem, latensi rendah, throughput tinggi, dan keandalan operasional.

### 2.2. Tanda Tangan Visual (Visual Signature)
- **Tipografi:** Neo-grotesk geometris presisi atau monospaced (misal: `Albert Sans`, `Switzer`, `JetBrains Mono`, `Space Grotesk`). Kerning ketat, penekanan pada kejelasan angka tabular.
- **Palet Warna:** Kontras klinis tinggi: *Sheet & Biro* (putih murni `#FFFFFF` dengan aksen biru royal elektrik `#1D4ED8` dan abu-abu batas `#E5E7EB`) atau *Monochrome Terminal Dark* (`#0D1117` dengan aksen cyan teknis `#06B6D4`).
- **Densitas & Skala Spasial:** **Densitas Tinggi (`high`)**. Layout kompak dan padat (`--space-xl: 2.75rem`, `--space-2xl: 4.5rem`, `--max-width: 1140px`).
- **Pola Komposisi:** Grid kartu telemetri berbatas halus, panel data terstruktur, diagram alir sistem, tabel perbandingan transparan.

### 2.3. Arsitektur Informasi & Kontrak Komponen
- **Integritas Konten:** **Dilarang keras mengarang metrik SLA fiktif (misal "99.999% uptime") atau sertifikasi keamanan palsu ("SOC 2")** kecuali brief menyediakannya. Gunakan deskripsi kapabilitas sistem riil (misal *"Sub-millisecond local overhead"*, *"Deterministic zero-allocation loops"*).
- **Panggilan Aksi (CTA):** Tindakan berorientasi teknis (*"Deploy Kernel"*, *"Inspect Benchmarks"*, *"Read Documentation"*).
- **Alur Kerja (Workflow):** Harus mencerminkan alur teknis instrumen (*"01 Instrument & Install"*, *"02 Telemetry Ingestion"*, *"03 Automated Verification"*).
- **Harga (Pricing):** Relevan dengan model konsumsi dev-tool (misal: *Developer / Team / Dedicated Cluster*).

### 2.4. Batasan Responsif & Floor Guard
- **Layar Seluler 320px:** Tipografi high-density secara alami aman pada layar kecil (`clamp(1.85rem, ...)`). Grid kartu metrik wajib runtuh menjadi 1 kolom pada $\le 768\text{px}$.
- **Situs Referensi Kanonikal:** `aww-seasats`, `opl-rows`, `aww-aspen-search`.

---

## 3. Arketipe: Brutalist Monumental (Poster Berani & Monumen Nama)

### 3.1. Konteks & Kecocokan Domain
- **Kategori Cocok:** Agensi desain kreatif, studio identitas merek, festival kebudayaan, pameran seni independen, firma arsitektur avant-garde.
- **Audiens Target:** Direktur desain, pimpinan kreatif merek (*brand leaders*), kurator festival, eksekutif pemasaran.
- **Tujuan Halaman:** Menampilkan otoritas kreatif tak tertandingi, keberanian visual, ketajaman konseptual, dan diferensiasi pasar radikal.

### 3.2. Tanda Tangan Visual (Visual Signature)
- **Tipografi:** Tipografi kondensasi monumental berskala raksasa (misal: `Anton`, `Oswald`, `Bebas Neue`) dipadukan dengan sans-serif kontemporer netral (misal: `Work Sans`, `Inter`). Leading sangat rapat (0.9–1.0), skala display masif.
- **Palet Warna:** Kontras tinggi yang kuat: *Black & Crimson* (`#0A0A0A` latar hitam pekat dengan aksen merah kirmizi membara `#E11D48`) atau *Stark Monochrome Duotone* (`#000000` / `#FFFFFF`).
- **Densitas & Skala Spasial:** **Densitas Sedang (`med`)**. Proporsi seimbang dengan margin samping tegas (`--space-xl: 4.0rem`, `--max-width: 1200px`).
- **Pola Komposisi:** Tipografi berfungsi sebagai elemen arsitektur tata letak itu sendiri (*type-as-layout*), garis hairline pembagi horizontal tegas.

### 3.3. Arsitektur Informasi & Kontrak Komponen
- **Integritas Konten:** Dilarang mengarang jumlah penghargaan fiktif (*"140+ Awards"*) atau klaim durasi usia palsu (*"12yr Leadership"*). Tonjolkan metodologi, arah artistik, dan lingkup keahlian.
- **Panggilan Aksi (CTA):** Bersifat penugasan proyek (*"Initiate Commission"*, *"Review Case Studies"*, *"Start Strategic Dialogue"*).
- **Harga (Pricing):** Dilarang menggunakan paket langganan murah software bulanan ($49/mo). Jika seksi harga disertakan, gunakan model perikatan penugasan studio (*"Brand Sprint"*, *"Full Identity Architecture"*, *"Retainer Partnership"*).
- **Alur Kerja (Workflow):** Mencerminkan tahapan kreatif strategis (*"01 Context & Immersion"*, *"02 Systemic Conception"*, *"03 Multi-Touchpoint Rollout"*).

### 3.4. Batasan Responsif & Floor Guard
- **Tablet Portrait (768px):** Hindari kartu yatim piatu pada grid metrik/bukti. Gunakan susunan 2×2 simetris.
- **Situs Referensi Kanonikal:** `aww-noho`, `aww-pp-neue-montreal`, `aww-ai-in-design-report-2026`.

---

## 4. Arketipe: Dense Data Board (Papan Data Padat & Aplikasi)

### 4.1. Konteks & Kecocokan Domain
- **Kategori Cocok:** Dasbor analitik, aplikasi keuangan, platform observabilitas, panel manajemen sumber daya cloud.
- **Audiens Target:** Operator data, analis keuangan, insinyur DevOps.
- **Tanda Tangan Visual:** Tipografi tabular rapi, kartu grup modular, indikator status semantik hijau/kuning/merah, garis kisi halus, pemanfaatan penuh lebar layar.
- **Situs Referensi Kanonikal:** `opl-rows`, `taste:app:data-table-explorer`.

