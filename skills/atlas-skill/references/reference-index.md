# Atlas Skill Design Reference Library — Index & Taxonomy
**Dokumen:** `skills/atlas-skill/references/reference-index.md`  
**Versi:** 1.0.0 (Phase 7 Remediation)  
**Tujuan:** Katalog terstruktur dan taksonomi referensi desain berorientasi domain, prinsip kegunaan, pola responsif, serta integritas konten untuk penalaran Atlas Skill.

---

## 1. Peta Taksonomi Dokumen Referensi

Pustaka referensi Atlas Skill diorganisasikan ke dalam modul-modul tematik yang dapat diretrieve secara independen dan deterministik:

| Dokumen | Topik & Cakupan Utama | Kasus Penggunaan Utama |
| :--- | :--- | :--- |
| [`curated-case-studies.md`](curated-case-studies.md) | Kasus referensi terstruktur 12 field lintas 6 domain: *Luxury Horlogerie*, *Technical Infra*, *Creative Agency*, *Data App*, *Typography Specimen*, *Architecture*. | Analisis mendalam visual signature, strategi layout, prinsip transferable, dan batasan anti-pattern. |
| [`design-principles.md`](design-principles.md) | Hukum kegunaan dasar (NN/g), aksesibilitas (W3C WAI WCAG 2.1), hierarki visual (Refactoring UI), performa layout (web.dev CLS). | Panduan dasar kualitas visual dan kelayakan interaksi untuk setiap brief. |
| [`art-direction-archetypes.md`](art-direction-archetypes.md) | 8 arketipe makro arah seni: *Editorial Luxury*, *Technical Instrument*, *Brutalist Monumental*, *Quiet Minimalist*, *Dense Data Board*, *Playful Vibrant*, *Warm Tactile*, *Type-Only Statement*. | Penentuan visual signature, tipografi, warna, dan densitas spasial. |
| [`domain-patterns.md`](domain-patterns.md) | Pola arsitektur informasi spesifik per domain: *Dev-Tool/Infra*, *Luxury Fashion/Horlogerie*, *Creative Agency*, *Enterprise Data App*, *Cultural Institution*, *E-Commerce*. | Rekomendasi seksi, alur kerja domain, model transaksi, dan ritme konten. |
| [`responsive-patterns.md`](responsive-patterns.md) | Strategi adaptasi lintas 5 viewport: Desktop (`1440×900`), Tablet Landscape (`1024×768`), Tablet Portrait (`768×1024`), Modern Mobile (`390×844`), Small Mobile (`320×568`). | Pencegahan kartu yatim piatu (*orphan cards*), batasan floor clamp, mitigasi blowout. |
| [`content-integrity.md`](content-integrity.md) | Doktrin kebenaran konten: Klasifikasi 4 tingkat klaim, larangan metrik/SLA/sertifikasi fiktif, copy berbasis kapabilitas, penggunaan token placeholder. | Verifikasi kejujuran klaim dan pencegahan halusinasi fakta dalam copywriting. |
| [`visual-anti-patterns.md`](visual-anti-patterns.md) | Katalog cacat visual & AI-slop: *Template Skinning Trap*, *Fake Certification Trap*, *Orphan Ampersand Trap*, *Asymmetric Orphan Card*, *Monolithic Linear Stack*. | Pemeriksaan penolakan dini terhadap pola desain murahan atau cacat. |

---

## 2. Taksonomi Domain & Arketipe Pemetaan

```
Category/Domain
  ├── dev-tool / developer / infra / cloud / data
  │     ├── Arketipe Utama: Technical Instrument, Dense Data Board
  │     ├── Pola Alur: Ingestion -> Execution -> Automated Verification
  │     └── Batasan Konten: Larangan klaim SOC 2 / 99.999% tanpa verifikasi brief.
  │
  ├── fashion / luxury / horlogerie / architecture / hospitality
  │     ├── Arketipe Utama: Editorial Luxury, Quiet Minimalist
  │     ├── Pola Alur: Materiality -> Artisanal Mastery -> Private Consultation
  │     └── Batasan Konten: Omit pricing table; gunakan penunjukan/konsultasi privat.
  │
  ├── agency / studio-portfolio / design / creative
  │     ├── Arketipe Utama: Brutalist Monumental, Type-Only Statement
  │     ├── Pola Alur: Strategic Positioning -> Case Studies -> Commission Initiation
  │     └── Batasan Konten: Larangan paket langganan SaaS $49/mo; gunakan model retainer.
  │
  └── data-app / dashboard / analytics
        ├── Arketipe Utama: Dense Data Board, Technical Instrument
        ├── Pola Alur: Source Integration -> Unified Telemetry -> Operational Insight
        └── Batasan Konten: Tabel terstruktur, angka berbasis data riil atau placeholder.
```

---

## 3. Matriks Referensi Situs Nyata Terkurasi (Exemplar Map)

Pustaka menghubungkan penalaran brief ke 202 situs terkurasi dalam `data/sites.json` berdasarkan ID dan arketipe:

| ID Referensi | Nama Situs / Brand | Domain / Kategori | Arketipe Visual | Transferable Principle ("Steal") | Status Bukti |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `aww-seasats` | Seasats Autonomous Surface Vehicles | Technical / Infra | `split-text-media` | Menampilkan kapabilitas instrumen dengan diagram teknis presisi tanpa metrik fiktif. | Terverifikasi Lokal (`data/sites.json`) |
| `aww-pp-neue-montreal` | PP Neue Montreal | Typography / Editorial | `giant-wordmark` | Membagi field dengan hairline horizontal; tipografi poster berskala besar dengan kontras tinggi. | Terverifikasi Lokal (`data/sites.json`) |
| `opl-vessa` | Vessa Watch Atelier | Luxury / Horlogerie | `product-object-centre` | Eksplorasi produk individual terisolasi dengan ruang negatif luas, tanpa tabel harga komersial. | Terverifikasi Lokal (`data/sites.json`) |
| `aww-noho` | Noho Agency | Agency / Creative | `type-poster` | Tipografi kondensasi monumental untuk judul monumen; navigasi samping minimalis. | Terverifikasi Lokal (`data/sites.json`) |
| `opl-rows` | Rows Spreadsheet Platform | Web App / Tool | `centred-statement-media-below` | Pernyataan terpusat diikuti demo interaktif; tata letak padat dan fungsional. | Terverifikasi Lokal (`data/sites.json`) |

---

## 4. Aturan Pengambilan & Penggunaan Referensi
1. **Referensi adalah Sumber Prinsip, Bukan Salinan:** Generator dilarang keras mereproduksi nama brand, teks salinan, aset gambar berhak cipta, atau tata letak identik dari situs referensi.
2. **Determinisme:** Input brief yang sama wajib menghasilkan set referensi terpilih yang sama tanpa randomness.
3. **Traceability:** Setiap keputusan tata letak atau komponen harus dapat dilacak alasannya ke prinsip yang terdokumentasi dalam pustaka ini.

