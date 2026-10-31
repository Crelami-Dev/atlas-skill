# Atlas Skill Responsive Patterns — Multi-Viewport Architecture
**Dokumen:** `skills/atlas-skill/references/responsive-patterns.md`  
**Status Bukti:** Terverifikasi Pengujian Headless Browser Chrome CDP (5 Viewports)  
**Tujuan:** Menetapkan aturan mitigasi layout responsif, pencegahan orphan cards, dan batasan lantai tipografi dari 1440px hingga 320px.

---

## 1. Matriks 5 Viewport Standar Atlas Skill

| Viewport ID | Dimensi ($W \times H$) | Tipe Perangkat | Karakteristik Stres Layout | Strategi Penanganan Utama |
| :--- | :--- | :--- | :--- | :--- |
| `desktop` | `1440 × 900` | Monitor Desktop Standar | Lebar melimpah, risiko stretched content. | Batasi kontainer utama dengan `--max-width` (1140px–1320px). |
| `tablet_landscape` | `1024 × 768` | Tablet Mode Lanskap | Transisi dekstop ke sentuh. | Grid 3 atau 4 kolom mengalir seimbang. |
| `tablet` | `768 × 1024` | Tablet Mode Potret (iPad) | **Rentan Cacat Kartu Yatim Piatu (Orphan Cards).** | Atur grid 4-item menjadi susunan **2×2 simetris**. |
| `mobile` | `390 × 844` | Ponsel Modern (iPhone 14/15) | Interaksi sentuh 1 tangan, ruang vertikal dominan. | Runtuhkan grid kartu ke 1-kolom, pertahankan 2-kolom untuk Bento. |
| `mobile_small` | `320 × 568` | Ponsel Sempit (iPhone SE 1st) | **Rentan Cacat Ampersand Yatim Piatu & Overflow.** | Batasi minimum `clamp()` judul ke $\le 2.0\text{rem}$, padding kontainer 16px. |

---

## 2. Pola Penanganan Tablet Portrait (768px): Pencegahan Kartu Yatim Piatu

### 2.1. Diagnosis Masalah Nyata
Aturan CSS umum:
```css
.proof-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
```
Pada viewport 768px dengan padding kontainer 24px kiri/kanan (lebar kontainer efektif ~720px):
- `720px / 200px` menghasilkan ruang untuk **3 kolom** selebar ~230px.
- Jika terdapat 4 kartu proof: 3 kartu mengisi Baris 1, dan **1 kartu tersisa sendirian di Baris 2**.
- Tampilan menjadi sangat timpang secara estetika (3 kartu di atas, 1 kartu sendirian di pojok kiri bawah).

### 2.2. Pola Solusi Responsif Wajib
Gunakan media query terarah pada breakpoint tablet:
```css
@media (min-width: 641px) and (max-width: 900px) {
  .proof-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}
```
Dengan aturan ini, 4 kartu akan terbagi seimbang menjadi **susunan 2×2** yang rapi dan simetris, tanpa meninggalkan kartu yatim piatu.

---

## 3. Pola Penanganan Layar Sempit (320px): Batasan Lantai Tipografi (Floor Clamp)

### 3.1. Diagnosis Masalah Nyata
Pada densitas rendah (Maison Atelier):
```css
/* CACAT: Minimum clamp terlalu besar */
h1 { font-size: clamp(2.75rem, 5vw + 1rem, 5rem); }
```
- Nilai minimum `2.75rem` = **44px**.
- Pada layar 320px dengan padding kontainer 16px kiri dan kanan, lebar tersedia hanya **288px**.
- Kata panjang seperti `"Craftsmanship"` (14 karakter) membutuhkan lebar ~260px pada ukuran 44px.
- Akibatnya, browser terpaksa memecah kata per kata ke baris baru:
  ```text
  Maison Atelier
  — Timeless
  Craftsmanship
  &             <-- Ampersand terisolasi di baris tersendiri (cacat visual)
  Architectural
  Form
  ```

### 3.2. Pola Solusi Floor Clamp Wajib
Turunkan nilai batas bawah `clamp()` pada heading densitas rendah:
```css
/* BENAR: Nilai minimum dibatasi pada 2.0rem (32px) */
h1 {
  font-size: clamp(2.0rem, 5vw + 0.75rem, 4.5rem);
  line-height: 1.15;
}
```
Pada ukuran 32px (`2.0rem`), frasa `"Craftsmanship &"` dapat tertampung dalam satu baris, mengeliminasi ampersand yatim piatu dan memulihkan keterbacaan editorial yang elegan.

---

## 4. Pola Pencegahan Overflow Layar Sempit (Zero-Blowout Contract)

Untuk menjamin `scrollWidth == clientWidth == 320px`:
1. **Aturan Grid Kartu Fitur:**
   ```css
   .features-grid {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
     gap: var(--space-md);
   }
   @media (max-width: 768px) {
     .features-grid {
       grid-template-columns: 1fr;
     }
   }
   ```
2. **Aturan Kontainer:**
   Dilarang menetapkan lebar elemen anak lebih besar daripada `100%` atau menetapkan nilai `min-width` absolut yang melebihi 280px.
3. **Word Break & Hyphens:**
   Sertakan `overflow-wrap: break-word` pada paragraf body dan lead text untuk mencegah kata teknis panjang (misal URL atau identifier kelas kode) mendesak batas viewport.

