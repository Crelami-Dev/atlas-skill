# Pemilihan Arketipe Struktural & Komposisi (Atlas v6.0)

Gunakan panduan ini sebelum menulis kode UI. Mengganti palet warna, jenis huruf, atau radius sudut di atas kerangka yang sama tidak dihitung sebagai desain yang berbeda. Setiap domain wajib memakai arketipe struktural yang sesuai dengan cara pengunjung mengevaluasi kontennya.

## Aturan Keras Pembatasan Pola Workbench

Pola **"hero 2 kolom + kartu workbench (search/filter/Reset)"** HANYA boleh digunakan untuk domain **aplikasi interaktif atau dashboard operasional** (`split-screen` aplikasi SaaS atau `dashboard-shell`). Pola tersebut dilarang dipakai pada halaman restoran, portofolio fotografer/arsitek, acara/festival, undangan pernikahan, firma hukum, klinik, travel, fashion, maupun halaman donasi/NGO.

## 10 Arketipe Struktural Resmi

| ID Arketipe | Struktur Utama | Kapan Dipakai (`whenToUse`) | Kapan Dilarang (`whenForbidden`) |
|---|---|---|---|
| `editorial-index-rail` | Rail indeks bernomor di kiri + matriks area praktik/layanan (`01–04`) + direktori mitra & meja konsultasi | Firma hukum, konsultan manajemen/pajak, company profile korporat, lembaga kebijakan | Dilarang untuk toko ritel produk tunggal, dashboard real-time, atau undangan perayaan |
| `poster-full-bleed` | Masthead poster tipografis selebar penuh (tanggal/lokasi raksasa atau panggung suasana ruang) + jadwal atau buku besar menu 2 kolom | Festival, konferensi, konser, acara publik, serta restoran/roastery/kafe | Dilarang untuk dashboard analitik, dokumentasi API, atau firma hukum/audit |
| `split-screen` | Layar terbelah asimetris (`42/58`) yang menyandingkan proposisi produk dengan kalkulator/simulator aplikasi langsung | Aplikasi web SaaS, alat produktivitas/otomasi, simulator finansial B2B | Dilarang untuk restoran, portofolio foto, pernikahan, hukum, travel, atau halaman naratif |
| `dashboard-shell` | App shell penuh viewport (`sidebar kiri + pita KPI + tabel operasional padat dengan filter + drawer detail`) tanpa hero promosi | Aplikasi operasional, logistik/armada, POS/kasir, CRM/ERP, konsol telemetri | Dilarang untuk landing page publik, restoran, portofolio, acara, atau company profile |
| `ledger-table-first` | Header triase layanan langsung + matriks jadwal praktisi/tarif/suku bunga berbentuk tabel + protokol persiapan | Klinik kesehatan, rumah sakit, laboratorium, layanan keuangan/akuntansi, jadwal kursus | Dilarang untuk lookbook fashion, undangan pernikahan, atau galeri fotografi |
| `narrative-long-scroll` | Kolom baca tunggal terpusat (`65ch–68ch`) + catatan margin + grafik alokasi inline + tabel audit distribusi & lembar komitmen | Yayasan/NGO, kampanye donasi, laporan tahunan, riset publik, jurnalisme data | Dilarang untuk e-commerce multi-varian, dashboard operasional, atau dokumentasi SDK |
| `gallery-masonry` | Kolofon tipis + grid pelat karya asimetris multi-rasio (`16:9`, `4:5`, `1:1`) bernomor kuratorial (`01–06`) + lembar komisi | Portofolio fotografer, arsitektur, agensi kreatif, galeri seni, lookbook fashion | Dilarang memasang search bar/filter/Reset; dilarang untuk aplikasi B2B atau klinik |
| `docs-three-pane` | 3 panel dokumentasi (`navigasi pohon kiri + referensi teknis & tab kode tengah + daftar isi kanan`) dimulai dari perintah instalasi | Dokumentasi SDK/API, CLI developer tools, library open-source, panduan infrastruktur | Dilarang untuk situs konsumen, restoran, acara, properti, atau portofolio visual |
| `catalogue-grid` | Panggung produk/properti multi-sudut (`60/40`) atau grid unit terkurasi + pemilih varian/unit + tabel spesifikasi terukur | E-commerce produk fisik, katalog properti/real estate, katalog program pendidikan | Dilarang memakai timer kelangkaan palsu; halaman produk tunggal dilarang memakai toolbar filter katalog |
| `timeline-story` | Sampul/lambang seremonial terpusat + alur waktu kronologis (rundown acara atau itinerary hari demi hari) + peta & RSVP/booking | Undangan pernikahan, perayaan, ekspedisi travel/tur wisata, linimasa sejarah brand | Dilarang memakai kartu harga SaaS, widget dashboard korporat, atau toolbar filter data |

## Menuliskan Tiga Alternatif di `design-brief.md`

1. Di bagian `## Tiga alternatif komposisi`, pilih **3 arketipe struktural yang berbeda** dari tabel di atas dan jelaskan apa yang dilihat pengunjung pada layar pertama untuk masing-masing alternatif.
2. Di bagian `## Pilihan akhir dan alasan`, nyatakan `ID Arketipe` yang dipilih (sesuai keluaran `selectedArchetype.id` dari `scripts/deal-direction.mjs`) beserta alasan mengapa dua arketipe lainnya ditolak.
3. Di bagian `## Hal yang sengaja ditolak dan kenapa`, catat pola yang dilarang oleh `selectedArchetype.whenForbidden` agar tidak bocor saat implementasi.

## Variasi Penutup Halaman (Hindari Pola Seragam)

- Jangan mengakhiri seluruh domain dengan pita gelap 2-kolom (informasi di kiri, formulir kartu putih di kanan). Untuk hospitality/restoran (`linen-espresso-craft`), akhiri dengan pita terang/permukaan yang memisahkan jadwal sangrai dan meja reservasi dari gaya undangan pernikahan atau simposium.
