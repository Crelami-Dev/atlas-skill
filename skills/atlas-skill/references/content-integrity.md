# Atlas Skill Content Integrity — Truthfulness Doctrine & Anti-Hallucination
**Dokumen:** `skills/atlas-skill/references/content-integrity.md`  
**Otoritas:** Kebijakan Kepatuhan Fakta & Integritas Komersial Atlas Skill  
**Status Bukti:** Wajib Dipatuhi oleh Seluruh Generator & Composer

---

## 1. Doktrin Kebenaran Konten (The Truthfulness Doctrine)

Sebuah sistem AI frontend engineering bertaraf produksi tidak boleh mengorbankan integritas hukum dan kredibilitas komersial demi membuat sebuah landing page terlihat meyakinkan. Mengarang klaim metrik, garansi ketersediaan, atau sertifikasi audit adalah bentuk malpraktik rekayasa perangkat lunak (*hallucinatory malpractice*).

---

## 2. Taksonomi 4 Tingkat Klaim Konten (4-Tier Claim Classification)

Setiap kalimat, angka, metrik, lencana (*badge*), dan kartu sosial proof yang dihasilkan generator wajib diklasifikasikan ke dalam 4 kategori berikut:

```
Tier 1: Factual Backed (Didukung Bukti Eksplisit Brief)
   │    Contoh: Nama proyek, kategori bisnis, deskripsi produk dari user.
   ▼
Tier 2: Qualitative / Aspirational (Deskripsi Nilai Tanpa Angka Terukur)
   │    Contoh: "Sub-Millisecond Overhead", "Handcrafted in Private Ateliers".
   ▼
Tier 3: Explicit Structured Placeholders (Penanda Data Riil Diperlukan)
   │    Contoh: "[Verified Latency Benchmark]", "[Insert Company Age]".
   ▼
Tier 4: Forbidden Fabrications (HALUSINASI TERLARANG - HARUS DITOLAK)
        Contoh: "SOC 2 Audited", "99.999% SLA", "140+ Awards", "12yr History".
```

### 2.1. Tingkat 1: Faktual Didukung Sumber (Factual Backed)
- **Definisi:** Klaim yang memiliki dasar langsung dari teks input `ProductBrief` atau manifes aset yang diberikan pengguna.
- **Status:** **DIIZINKAN**.

### 2.2. Tingkat 2: Proposisi Nilai Kualitatif / Aspiratif (Qualitative Aspirational)
- **Definisi:** Narasi deskriptif yang mengartikulasikan kapabilitas arsitektural atau nilai estetika tanpa menyebut angka atau statistik terukur spesifik.
- **Contoh Aman:**
  - Dev-tool: *"Deterministic state transitions guaranteed across partitions."*
  - Luxury: *"Every silhouette is refined through exacting atelier restraint."*
  - Agency: *"Partnering with ambitious founders to articulate authentic brand identities."*
- **Status:** **DIIZINKAN & DIREKOMENDASIKAN** ketika brief tidak menyediakan data kuantitatif.

### 2.3. Tingkat 3: Placeholder Terstruktur Eksplisit (Explicit Placeholders)
- **Definisi:** Penanda yang secara jujur mengindikasikan bahwa suatu metrik atau testimonial spesifik perlu diisi oleh pemilik produk sebelum situs dipublikasikan ke produksi.
- **Contoh:** `data-metric-placeholder="uptime-sla"`, teks tampilan `[Your Verified Metric]`.
- **Status:** **DIIZINKAN** dalam mode scaffold / pengujian.

### 2.4. Tingkat 4: Halusinasi Terlarang (Forbidden Fabrications)
- **Definisi:** Setiap penyebutan angka terukur, persentase statistik, klaim audit hukum/keamanan, jumlah penghargaan, atau riwayat tahun yang **tidak tercantum dalam brief**.
- **Status:** **DILARANG KERAS (FORBIDDEN)**. Kemunculan klaim Tier 4 dalam hasil render menyebabkan kegagalan audit kepatuhan (*hard compliance failure*).

---

## 3. Daftar Hitam Halusinasi Faktual (Blacklist of Fabricated Claims)

Generator dilarang keras menghasilkan string atau komponen berikut secara sepihak:

| Kategori Terlarang | Contoh Halusinasi Nyata yang Ditemukan di P7 | Bahaya & Dampak Hukum | Solusi Pengganti yang Sah |
| :--- | :--- | :--- | :--- |
| **Sertifikasi Keamanan & Kepatuhan** | `"SOC 2 — Audited Enterprise Compliance"`, `"ISO 27001 Certified"`, `"HIPAA Compliant"` | **Pelanggaran Kepatuhan Berat:** Menyatakan kelulusan audit keamanan pihak ketiga secara palsu. | Gunakan kapabilitas arsitektural: *"Continuous Invariant Verification"*, *"Role-Based Cryptographic Controls"*. |
| **Jaminan SLA Performa** | `"99.999% Continuous Infrastructure Uptime"` | **Pelanggaran Kontrak Komersial:** Menjanjikan batas downtime maksimal 5.26 menit/tahun tanpa verifikasi infrastruktur riil. | Gunakan kapabilitas keandalan: *"High Availability Architecture"*, *"Resilient Multi-Region Failover"*. |
| **Metrik Latensi Spesifik** | `"<1ms Median Global Telemetry Latency"` | **Klaim Iklan Palsu:** Menjanjikan angka latensi jaringan global tanpa pengukuran riil. | Gunakan deskripsi desain sistem: *"Low-Latency Event Pipelines"*, *"Zero-Allocation Runtime Pathways"*. |
| **Riwayat Penghargaan & Usia** | `"140+ International Design Honors"`, `"12yr Strategic Industry Leadership"` | **Penipuan Rekam Jejak:** Mengarang riwayat berdirinya agensi atau prestasi fiktif. | Gunakan fokus keahlian metodologi: *"Systemic Typography"*, *"Proprietary Brand Architecture"*. |
| **Jumlah Cabang / Lokasi Fisik** | `"Private Client Salons in 12 Capitals"` | **Klaim Keberadaan Fisik Palsu:** Mengarang alamat atau kantor salon di 12 negara. | Gunakan fokus kuratorial: *"Private Client Consultations"*, *"Bespoke Commission Atelier"*. |
| **Statistik Kepuasan Pengguna** | `"4.9 / 5 User Satisfaction"`, `"10x Operational Velocity"` | **Testimonial Sintetis Palsu:** Mengarang metrik ulasan pelanggan. | Gunakan fokus luaran: *"Built for Operational Rigor"*, *"Accelerated Development Cycles"*. |

---

## 4. Larangan Kebocoran Template Internal (Template Leakage Ban)

Dilarang keras menyisipkan teks atau istilah internal sistem Atlas Skill sendiri ke dalam website klien yang dihasilkan, termasuk:
- Dilarang menjual *"Bespoke art direction system"* atau *"Custom typography pairing"* di seksi harga klien.
- Dilarang menjelaskan *"Harmonize macro art direction"* di seksi alur kerja klien.
- Dilarang menanyakan *"How do you guarantee distinctive visual aesthetic?"* atau *"Is output dependent on external runtime frameworks?"* di seksi FAQ klien.
- Setiap teks di seksi Workflow, Pricing, dan FAQ **wajib bersumber dari domain klien**, bukan dari deskripsi kerja generator Atlas.

