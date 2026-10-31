# Atlas Skill Visual Anti-Patterns — AI-Slop & Template Rejection Catalog
**Dokumen:** `skills/atlas-skill/references/visual-anti-patterns.md`  
**Status Bukti:** Teridentifikasi pada Sign-off Audit Phase 7 (`docs/phase-7/P7_FINAL_SIGNOFF_REPORT.md`)  
**Tujuan:** Katalog perangkap desain murahan (*AI-slop*), sindrom template, dan cacat visual yang wajib ditolak oleh auditor dan generator Atlas Skill.

---

## 1. Perangkap 1: Template Skinning Trap (Satu Cetakan Berjuta Warna)

### 1.1. Gejala Klinis
- Struktur DOM halaman identik 100% antar industri yang sama sekali berbeda:
  `Hero (1-col) -> Proof (4-col) -> Features (6-col) -> Workflow (3-step) -> Pricing (3-tier) -> FAQ (3-item) -> CTA Box`.
- Satu-satunya perbedaan antara situs alat telemetri teknis (`Vektor Platform`) dan atelier fesyen mewah (`Maison Atelier`) hanyalah penggantian nilai variabel CSS (`--color-accent`, `--font-display`).
- Teks alur kerja dan teks kartu harga menggunakan kata-kata yang persis sama.

### 1.2. Mengapa Ini Diklasifikasikan Sebagai Slop?
Ini memperlakukan rekayasa arah seni (*art direction engineering*) seperti sekadar memasang wallpaper. Pengunjung website langsung merasakan bahwa situs tersebut adalah hasil cetakan template generik yang tidak memiliki jiwa atau arsitektur informasi autentik.

### 1.3. Aturan Pencegahan Wajib
- **Domain Slot Filtering:** Jangan memaksakan seksi `pricing` pada domain fesyen mewah, seni rupa, atau institusi budaya.
- **Domain Cadence:** Seksi alur kerja, harga, dan FAQ harus dihasilkan secara dinamis berdasarkan domain industri, bukan disalin dari string statis internal.

---

## 2. Perangkap 2: Fake Certification & Metric Trap (Halusinasi Kredibilitas)

### 2.1. Gejala Klinis
- Generator secara otomatis mencetak lencana audit kepatuhan: *"SOC 2 — Audited Enterprise Compliance"*.
- Generator mencetak jaminan ketersediaan: *"99.999% Continuous Infrastructure Uptime"*, angka latensi *"<1ms"*, angka penghargaan *"140+ Honors"*, atau usia perusahaan *"12yr Leadership"* padahal pengguna tidak pernah menyebutkannya dalam brief.

### 2.2. Mengapa Ini Diklasifikasikan Sebagai Slop?
Ini adalah kebohongan faktual (*hallucinatory fabrication*). Jika klien mempublikasikan website ini ke publik, mereka dapat dituntut atas klaim iklan palsu, penipuan rekam jejak, atau pelanggaran kepatuhan hukum serius terhadap auditor SOC 2.

### 2.3. Aturan Pencegahan Wajib
- Mematuhi Doktrin Kebenaran Konten ([`content-integrity.md`](content-integrity.md)).
- Ketika brief tidak menyediakan angka statistik, generator **wajib menggunakan klaim kapabilitas berbasis kualitatif (Tier 2)** atau **placeholder terstruktur (Tier 3)**.

---

## 3. Perangkap 3: Orphaned Punctuation Trap (Tanda Baca Yatim Piatu)

### 3.1. Gejala Klinis
- Pada layar seluler sempit (320px–360px), teks judul utama terpecah secara canggung sehingga simbol ampersand (`&`), tanda hubung em-dash (`—`), atau kata 1 huruf (seperti `a` atau `I`) terisolasi sendirian di satu baris penuh.
- Contoh nyata pada Maison Atelier di 320px:
  ```text
  Craftsmanship
  &             <-- Cacat Tipografi Yatim Piatu
  Architectural
  ```

### 3.2. Mengapa Ini Diklasifikasikan Sebagai Slop?
Ini mencerminkan tipografi amatir yang tidak memperhitungkan rasio panjang baris (*measure*) dan batasan lantai responsif.

### 3.3. Aturan Pencegahan Wajib
- Batasi nilai minimum formula `clamp()` judul pada layar kecil ke maksimal $2.0\text{rem}$ ($32\text{px}$).
- Terapkan `text-wrap: balance` pada tag `<h1>` dan `<h2>` di CSS.

---

## 4. Perangkap 4: Asymmetrical Orphan Card Trap (Kartu Yatim Piatu di Tablet)

### 4.1. Gejala Klinis
- Grid 4 elemen (`.proof-grid`) pada layar tablet portrait (768px) menampilkan 3 kartu di baris pertama dan **1 kartu tersisa sendirian di baris kedua** dengan ruang kosong di samping kanannya.

### 4.2. Mengapa Ini Diklasifikasikan Sebagai Slop?
Tata letak terlihat rusak atau belum selesai dikerjakan, menghancurkan keseimbangan visual komposisi.

### 4.3. Aturan Pencegahan Wajib
- Terapkan breakpoint tablet eksplisit `grid-template-columns: repeat(2, minmax(0, 1fr))` pada rentang `641px–900px` untuk menjamin susunan 2×2 yang simetris dan rapi.

---

## 5. Perangkap 5: Monolithic Internal Jargon Leakage (Kebocoran Istilah Internal)

### 5.1. Gejala Klinis
- Teks yang dihasilkan untuk website klien memuat istilah-istilah internal pembuat sistem Atlas Skill sendiri, seperti:
  - *"Bespoke art direction system"* di paket harga klien.
  - *"Harmonize macro art direction"* di langkah alur kerja klien.
  - *"Visual assets resolved through resilient pipeline"* di FAQ klien.

### 5.2. Mengapa Ini Diklasifikasikan Sebagai Slop?
Pengunjung website klien merasa bingung karena disuguhi jargon pengembang AI generator alih-alih proposisi nilai dari produk yang sedang mereka telusuri.

### 5.3. Aturan Pencegahan Wajib
- Pisahkan kamus istilah internal alat rekayasa (*internal tool lexicon*) dari kamus copywriting publik domain klien (*domain client lexicon*).

