# Atlas Skill Curated Case Studies — Reference Exemplars
**Dokumen:** `skills/atlas-skill/references/curated-case-studies.md`  
**Tujuan:** Pustaka kasus referensi terstruktur lintas domain dengan 12 atribut wajib untuk memandu penalaran komposisi dan integritas konten.  
**Batasan Akses Web & Integritas:** Tidak ada web scraping langsung pada sesi ini. Data bersumber dari analisis arsip lokal 202 situs terverifikasi di `data/sites.json` dan dokumentasi kurasi repositori.

---

## 1. Kasus: Vessa Watch Atelier (`opl-vessa`)

- **1. Identity:**
  - URL: `https://vessa-watches.com/` (arsip referensi OnePageLove/Awwwards)
  - Nama Brand: Vessa Watch Atelier
  - Kategori / Domain: `luxury` / `horlogerie` (Fesyen & Jam Tangan Mewah)
  - Tanggal Akses / Sumber: 30 Oktober 2026 (Terverifikasi dari arsip lokal `data/sites.json#opl-vessa`)
- **2. Context:**
  - Model Bisnis: Penjualan jam tangan mekanis pesanan khusus (*bespoke commission* & koleksi bernomor seri terbatas).
  - Target Audiens: Kolektor internasional, patron jam tangan independen, penikmat horologi tinggi.
  - Tujuan Halaman: Membangun reputasi keahlian mekanis (*artisanal mastery*), memikat patron untuk janji temu privat (*private salon consultation*).
- **3. Visual Signature:**
  - Editorial klasik berwibawa, ketenangan absolut (*stillness*), materialitas taktil, ruang bernapas luas.
- **4. Information Architecture:**
  - Navigasi Minimalis $\to$ Hero Fokus Objek Tunggal $\to$ Materialitas & Komponen Kaliber $\to$ Filosofi Atelier $\to$ Permintaan Janji Temu Privat $\to$ Footer Legal.
  - **Ditiadakan:** Seksi tabel harga komersial SaaS ($49/mo), tombol "Beli Sekarang", dan lencana diskon.
- **5. Layout Strategy:**
  - Tata letak asimetris satu objek terpusat (*product-object-centre*), batas kontainer maksimal 1320px, ruang vertikal lapang (`--space-xl: 5.5rem`, `--space-2xl: 8.0rem`).
- **6. Typography:**
  - Display: Serif klasik berbobot anggun (mirip `EB Garamond`), tracking -0.01em, leading 1.05.
  - Body: Serif reguler proporsional, leading 1.6, keterbacaan tinggi.
- **7. Color Strategy:**
  - Latar belakang: *Bone Ivory* (`#F4F1EA`).
  - Teks: *Deep Charcoal* (`#1C1917`).
  - Aksen: *Forest Green* (`#3D6B42`) untuk tombol interaksi santun.
- **8. Interaction Strategy:**
  - Stillness dominan, transisi halus tanpa animasi melayang yang berlebihan.
  - Aksi utama: *"Request Private Appointment"*. Aksi sekunder: *"Explore Atelier"*.
- **9. Responsive Behavior:**
  - Desktop: Objek jam tangan berada di tengah panggung dengan ruang negatif luas di kiri dan kanan.
  - Mobile (390px): Teks dan visual bertransisi vertikal; tombol aksi menumpuk secara nyaman.
  - Small Mobile (320px): Batasan `clamp` judul diatur pada $2.0\text{rem}$ agar kata panjang tidak memecah baris secara canggung.
- **10. Transferable Principles ("Steal"):**
  - Isolasi objek produk karya seni di tengah kanvas bersih dengan ruang negatif luas.
  - Ganti harga komersial dengan penunjukan salon privat untuk menjaga prestise mewah.
  - Gunakan narasi materialitas dan disiplin tradisi studio alih-alih klaim kehebatan diri.
- **11. Anti-Patterns & Constraints:**
  - Dilarang keras menampilkan paket langganan bulanan ($49/mo, $129/mo).
  - Dilarang mengarang jumlah cabang kota ("12 Capitals") jika tidak diverifikasi pemilik atelier.
- **12. Evidence Status:**
  - `[Observasi Arsip Lokal Terverifikasi dari data/sites.json]` untuk struktur layout dan tipografi; `[Interpretasi Rekayasa Domain]` untuk adaptasi aturan responsif 320px.

---

## 2. Kasus: Seasats Autonomous Surface Vehicles (`aww-seasats`)

- **1. Identity:**
  - URL: `https://seasats.com/` (arsip referensi Awwwards Site of the Day)
  - Nama Brand: Seasats
  - Kategori / Domain: `dev-tool` / `infra` (Kendaraan Laut Otonom & Sistem Komputasi Lapangan)
  - Tanggal Akses / Sumber: 30 Oktober 2026 (Terverifikasi dari arsip lokal `data/sites.json#aww-seasats`)
- **2. Context:**
  - Model Bisnis: Penyediaan perangkat keras kapal otonom bertenaga surya dan platform telemetri data oseanografi.
  - Target Audiens: Insinyur sistem maritim, peneliti iklim, operator armada pertahanan, ilmuwan data.
  - Tujuan Halaman: Membuktikan daya tahan fisik, keandalan telemetri misi jangka panjang, dan integrasi API sensor.
- **3. Visual Signature:**
  - Instrumen teknis klinis, tata letak padat sarat data (*technical instrument*), kontras tinggi, garis hairline presisi.
- **4. Information Architecture:**
  - Header Navigasi Teknis $\to$ Hero Split Teks-Media $\to$ Diagram Arsitektur Sensor $\to$ Kapabilitas Subsistem $\to$ Alur Operasional Lapangan $\to$ Konsultasi Teknis $\to$ Footer Spesifikasi.
- **5. Layout Strategy:**
  - Grid dua kolom modular split (*split-text-media*), lebar kontainer kompak 1140px, densitas tinggi (`--space-xl: 2.75rem`), pembatas seksi berupa hairline halus 1px.
- **6. Typography:**
  - Display & Text: Neo-grotesk teknis (mirip `Albert Sans` atau `Switzer`), penekanan pada angka tabular, tracking netral, hierarki heading kompak.
- **7. Color Strategy:**
  - *Sheet & Biro*: Canvas putih murni (`#FFFFFF`), teks hitam tinta pekat (`#0F172A`), aksen biru royal elektrik (`#1D4ED8`) untuk status operasional aktif.
- **8. Interaction Strategy:**
  - Gerakan minimal (*stillness*), penekanan pada diagram interaktif dan peragaan status sensor.
  - Aksi utama: *"Inspect Architecture"*. Aksi sekunder: *"Download Mission Data"*.
- **9. Responsive Behavior:**
  - Desktop: Teks di sisi kiri, diagram mekanis di sisi kanan sejajar.
  - Mobile (390px/320px): Diagram bertumpuk di bawah teks; kartu kapabilitas runtuh menjadi 1 kolom tanpa overflow horizontal.
- **10. Transferable Principles ("Steal"):**
  - Tampilkan diagram arsitektur teknis atau potongan struktur internal alih-alih foto ilustrasi generik.
  - Nyatakan kapabilitas operasional berdasarkan batas fisik nyata, bukan klaim pemasaran bombastis.
  - Alur kerja wajib mencerminkan tahapan instalasi dan pengujian lapangan nyata.
- **11. Anti-Patterns & Constraints:**
  - Dilarang keras mengarang lencana "SOC 2" atau "99.999% SLA" jika tidak ada data uji terverifikasi.
  - Dilarang menjual "Custom typography pairing" pada produk sistem instrumen.
- **12. Evidence Status:**
  - `[Observasi Arsip Lokal Terverifikasi dari data/sites.json]` untuk struktur grid dan palet; `[Interpretasi Rekayasa Domain]` untuk kebijakan integritas data teknis.

---

## 3. Kasus: Noho Creative Studio (`aww-noho`)

- **1. Identity:**
  - URL: `https://noho.studio/` (arsip referensi Awwwards Site of the Day)
  - Nama Brand: Noho Studio
  - Kategori / Domain: `agency` / `creative` (Studio Identitas & Arah Seni Kontemporer)
  - Tanggal Akses / Sumber: 30 Oktober 2026 (Terverifikasi dari arsip lokal `data/sites.json#aww-noho`)
- **2. Context:**
  - Model Bisnis: Konsultasi strategi merek, tipografi proprietari, dan perancangan lingkungan digital untuk perusahaan visioner.
  - Target Audiens: Direktur desain, pendiri korporasi, pemimpin budaya (*brand directors & cultural leaders*).
  - Tujuan Halaman: Menegaskan otoritas artistik, memamerkan portofolio terpilih, dan membuka negosiasi komisi proyek bernilai tinggi.
- **3. Visual Signature:**
  - *Brutalist Monumental*, tipografi display raksasa terkondensasi, kontras monokrom tajam dengan aksen merah membara.
- **4. Information Architecture:**
  - Navigasi Minimal $\to$ Hero Pernyataan Monumental $\to$ Disiplin & Sudut Pandang $\to$ Portofolio Kasus Terpilih $\to$ Metodologi Kolaborasi $\to$ Inisiasi Penugasan $\to$ Footer Indeks.
- **5. Layout Strategy:**
  - Tipografi berfungsi sebagai arsitektur visual utama (*type-poster*), batas kontainer 1200px, ritme seimbang densitas sedang (`--space-xl: 4.0rem`).
- **6. Typography:**
  - Display: Display kondensasi ekstra tebal (mirip `Anton` atau `Oswald`), leading sangat rapat (0.95), ukuran hingga skala poster.
  - Text: Neo-grotesk netral (mirip `Work Sans` atau `Inter`) untuk teks keterangan proyek.
- **7. Color Strategy:**
  - *Black & Crimson*: Latar hitam pekat (`#0A0A0A`), teks putih gading (`#F8FAFC`), aksen merah kirmizi (`#E11D48`).
- **8. Interaction Strategy:**
  - Aksi utama: *"Initiate Commission"*. Aksi sekunder: *"Review Case Studies"*.
  - Transisi teks tajam, fokus pada kekuatan tipografi statis yang commanding.
- **9. Responsive Behavior:**
  - Desktop: Judul membentang penuh di seluruh lebar kontainer.
  - Tablet (768px): Grid metrik diatur simetris 2×2 untuk mencegah kartu yatim piatu.
  - Mobile (320px): Font display kondensasi menyusut secara proporsional tanpa memecah kata pendek.
- **10. Transferable Principles ("Steal"):**
  - Gunakan judul display skala besar sebagai jangkar perhatian utama.
  - Ganti kartu paket harga software SaaS bulanan ($49/mo) dengan model komisi penugasan studio.
  - Alur kerja harus menjelaskan metodologi pemikiran kreatif (Imersi $\to$ Konsepsi $\to$ Peluncuran).
- **11. Anti-Patterns & Constraints:**
  - Dilarang mengarang angka penghargaan palsu ("140+ Awards") atau usia fiktif ("12yr").
  - Dilarang memaksakan kartu langganan bulanan murah yang merusak citra eksklusif agensi.
- **12. Evidence Status:**
  - `[Observasi Arsip Lokal Terverifikasi dari data/sites.json]` untuk gaya tipografi poster; `[Interpretasi Rekayasa Domain]` untuk model perikatan komisi.

---

## 4. Kasus: Rows Spreadsheet & Analytics (`opl-rows`)

- **1. Identity:**
  - URL: `https://rows.com/` (arsip referensi OnePageLove)
  - Nama Brand: Rows
  - Kategori / Domain: `web-app` / `data-app` (Aplikasi Spreadsheet & Analitik Data Modern)
  - Tanggal Akses / Sumber: 30 Oktober 2026 (Terverifikasi dari arsip lokal `data/sites.json#opl-rows`)
- **2. Context:**
  - Model Bisnis: Freemium PLG (Product-Led Growth) dengan tier tim berbayar.
  - Target Audiens: Analis data, manajer produk, tim operasi bisnis.
  - Tujuan Halaman: Menunjukkan kemudahan integrasi API dan kapabilitas olah data visual langsung di browser.
- **3. Visual Signature:**
  - Bersih, terstruktur, tabel data interaktif dengan aksen hijau operasional, densitas tinggi.
- **4. Information Architecture:**
  - Header App Shell $\to$ Hero Pernyataan Terpusat $\to$ Pratinjau Interaktif Langsung $\to$ Integrasi Sumber Data $\to$ Template Populer $\to$ Harga Berbasis Kolaborator $\to$ CTA.
- **5. Layout Strategy:**
  - *Centred Statement Media Below*, kontainer lebar 1200px, grid kartu integrasi modular.
- **6. Typography:**
  - Tipografi neo-grotesk bersih berkarakter fungsional (`Switzer`), font angka monospace untuk tabel.
- **7. Color Strategy:**
  - Latar terang netral, batas kartu abu-abu tipis 1px, aksen hijau status (`#10B981`).
- **8. Interaction Strategy:**
  - Uji coba interaktif di tempat, tombol aksi utama: *"Start Building Free"*.
- **9. Responsive Behavior:**
  - Tabel data menggunakan pembungkus scroll horizontal internal yang terisolasi tanpa memicu overflow halaman.
- **10. Transferable Principles ("Steal"):**
  - Tampilkan pratinjau produk nyata langsung di bawah pernyataan hero.
  - Kelompokkan kartu integrasi secara teratur dengan rasio 3 kolom atau 4 kolom seimbang.
- **11. Anti-Patterns & Constraints:**
  - Jangan biarkan container scroll data merusak `scrollWidth` halaman utama.
- **12. Evidence Status:**
  - `[Observasi Arsip Lokal Terverifikasi dari data/sites.json]`.

---

## 5. Kasus: PP Neue Montreal Type Specimen (`aww-pp-neue-montreal`)

- **1. Identity:**
  - URL: `https://neuemontreal.com/` (arsip referensi Awwwards Site of the Day)
  - Nama Brand: PP Neue Montreal
  - Kategori / Domain: `publishing` / `typography` (Spesimen Tipografi & Buku Panduan Budaya)
  - Tanggal Akses / Sumber: 30 Oktober 2026 (Terverifikasi dari arsip lokal `data/sites.json#aww-pp-neue-montreal`)
- **2. Context:**
  - Model Bisnis: Lisensi jenis huruf font komersial dan buku panduan kota Montreal vintage.
  - Target Audiens: Desainer grafis, penerbit buku, direktur seni.
  - Tujuan Halaman: Memamerkan fleksibilitas bobot font dari Thin hingga Bold dalam konteks editorial nyata.
- **3. Visual Signature:**
  - *Retro-modernist print poster*, garis hairline pembagi horizontal tebal, warna cetak buku vintage (coral red, near-black, cream).
- **4. Information Architecture:**
  - Wordmark Raksasa $\to$ Pernyataan Editorial $\to$ Tabel Perbandingan Bobot $\to$ Kolase Spesimen $\to$ Lisensi Font.
- **5. Layout Strategy:**
  - *Giant Wordmark*, pembagian bidang dengan garis hairline horizontal penuh, margin samping 24px.
- **6. Typography:**
  - Satu keluarga font (`PP Neue Montreal`) dari ukuran teks 16px hingga judul raksasa ~17vw.
- **7. Color Strategy:**
  - Coral red (`#ED4B44`), cream (`#F0E7D4`), near-black (`#1A1A1A`).
- **8. Interaction Strategy:**
  - Pengguliran halaman bertahap seperti membalik halaman buku panduan cetak.
- **9. Responsive Behavior:**
  - Garis hairline membentang penuh; tipografi berskala fluid dengan formula clamp terkendali.
- **10. Transferable Principles ("Steal"):**
  - Gunakan satu keluarga font dengan variasi bobot dan skala dramatis untuk menciptakan kesatuan visual murni.
  - Manfaatkan garis hairline horizontal untuk menyusun ritme pembacaan yang tenang.
- **11. Anti-Patterns & Constraints:**
  - Hindari animasi mengambang yang tidak memiliki konteks cetak.
- **12. Evidence Status:**
  - `[Observasi Arsip Lokal Terverifikasi dari data/sites.json]`.

---

## 6. Kasus: Kononenko Architectural Bureau (`aww-kononenko-architectural-bureau`)

- **1. Identity:**
  - URL: `https://kononenko.bureau/` (arsip referensi Awwwards)
  - Nama Brand: Kononenko Architectural Bureau
  - Kategori / Domain: `architecture` / `cultural` (Biro Desain Arsitektur & Perencanaan Spasial)
  - Tanggal Akses / Sumber: 30 Oktober 2026 (Terverifikasi dari arsip lokal `data/sites.json#aww-kononenko-architectural-bureau`)
- **2. Context:**
  - Model Bisnis: Jasa konsultasi desain arsitektur residensial mewah dan bangunan publik budaya.
  - Target Audiens: Pengembang properti swasta, komisi kota, pemilik residensial privat.
  - Tujuan Halaman: Menunjukkan ketajaman spasial, penguasaan cahaya, dan monograf proyek arsitektur.
- **3. Visual Signature:**
  - *Fullbleed Media Overlay*, monokromatik abu-abu beton dan batu alam, tipografi arsitektural bersahaja.
- **4. Information Architecture:**
  - Header Melayang $\to$ Hero Fotografi Spasial $\to$ Monograf Proyek Terpilih $\to$ Pernyataan Filosofi Spasial $\to$ Monograf Kontak $\to$ Footer Minimal.
- **5. Layout Strategy:**
  - Bidang fotografi lebar penuh dengan overlay teks yang terpotong rapi, batas kontainer 1320px.
- **6. Typography:**
  - Sans-serif arsitektural proporsional dipadukan dengan aksen serif tegak untuk kata terakhir judul.
- **7. Color Strategy:**
  - Abu-abu batu kapur (`#E2E8F0`), abu-abu beton gelap (`#334155`), hitam granit (`#0F172A`).
- **8. Interaction Strategy:**
  - Navigasi proyek berbasis galeri horizontal dengan transisi lembut.
- **9. Responsive Behavior:**
  - Gambar bertransisi proporsional dengan aspect ratio terjaga; tidak ada pergeseran tata letak.
- **10. Transferable Principles ("Steal"):**
  - Padukan sans-serif dengan aksen serif pada kata penutup judul untuk tanda tangan visual unik.
  - Biarkan kualitas visual ruang dan material berbicara daripada memenuhi halaman dengan teks klaim berlebihan.
- **11. Anti-Patterns & Constraints:**
  - Dilarang keras menggunakan kartu harga komersial atau lencana jaminan garansi.
- **12. Evidence Status:**
  - `[Observasi Arsip Lokal Terverifikasi dari data/sites.json]`.

