# Laporan Audit Keamanan Projek: <Nama Projek>

**Tanggal Audit:** <YYYY-MM-DD>
**Postur Risiko Saat Ini:** Critical / High / Medium / Low
**Status Kode Saat Ini:** Read-Only (Belum ada perubahan kode yang diterapkan - menunggu instruksi perbaikan)

## 1. Ringkasan Eksekutif Keamanan

| Tingkat Keparahan | Jumlah Celah | Ringkasan Risiko Serangan |
| :--- | :---: | :--- |
| Critical | 0 | Pengambilalihan sistem/akun penuh, kebocoran data sensitif, RCE, atau SQLi |
| High | 0 | Bypass otorisasi (IDOR), XSS tersimpan, kebocoran kredensial, atau SSRF |
| Medium | 0 | Konfigurasi CORS/CSRF lemah, ketiadaan rate limit, atau validasi input parsial |
| Low | 0 | Hardening header HTTP, informasi versi terekspos, atau praktik best-practice |
| **Total** | **0** | |

## 2. Peta Permukaan Serangan (Attack Surface) yang Dianalisis

- **Autentikasi & Sesi:** <ringkasan mekanisme yang diperiksa>
- **Endpoint / Input Publik & Privat:** <daftar modul/route yang diaudit>
- **Penyimpanan Data & Kredensial:** <database, file upload, environment variables>
- **Integrasi Eksternal & Dependensi:** <paket pihak ketiga / webhook / API luar>

## 3. Detail Celah Keamanan dan Cara Mengatasinya

### [SEC-01] <Judul Celah Keamanan>

- **Tingkat Keparahan:** Critical / High / Medium / Low
- **Kategori:** <Contoh: OWASP A01 - Broken Access Control / IDOR>
- **Lokasi File:** `path/to/file.ext:baris`
- **Skenario Serangan (Bagaimana Celah Bisa Dieksploitasi):**
  Penjelasan konkret alur serangan dari input penyerang hingga dampak yang ditimbulkan.
- **Akar Kerentanan:** Mengapa kode saat ini rentan.
- **Cara Mengatasi (Remediasi & Hardening):**
  Langkah perbaikan konkret beserta contoh pola kode yang aman.
- **Analisis Kesiapan Patch & Dampak ke Fitur Lain:**
  - Konfigurasi / environment variable / fitur lain yang perlu disesuaikan saat patch dipasang: <penjelasan>
  - Cara memastikan fitur asli tetap berjalan normal setelah diamankan: <penjelasan>

## 4. Menunggu Instruksi Perbaikan

Laporan keamanan dan rencana patch di atas telah disiapkan tanpa memodifikasi kode projek Anda. Balas jika Anda ingin perbaikan keamanan dikerjakan sekarang, maka proses patching, pengujian 100% seluruh fitur projek, dan audit keamanan ulang menyeluruh akan dijalankan.
