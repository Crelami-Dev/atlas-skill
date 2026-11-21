---
title: Pemecahan Masalah
description: Solusi kendala umum Atlas-skill termasuk lingkungan tanpa Python 3, jaringan tanpa CDN, laporan drift dari doctor, dan penggunaan di Windows.
---

Bagian ini merangkum cara menangani kendala lingkungan nyata sesuai mekanisme yang tersedia langsung di skrip Atlas-skill.

## 1. Tidak Ada Python 3 di Mesin

- **Gejala:** Gate 1–5 (statis) berhasil dijalankan, tetapi Gate 6 (`--visual` pada `run-gates.mjs`) atau skrip `suites/project-qa/` gagal atau melaporkan Python tidak tersedia.
- **Penyebab & Fakta:** Penginstal CLI (`bin/atlas-skill.mjs`) dan seluruh gate statis (`check-brief`, `check-tokens`, `check-motion-v4`, `slop-scan`, `check-copy`, `check-visual-proof`) maupun `quick-check.mjs` murni memakai **Node.js 18+**. Sebaliknya, `visual_dom_inspector.py` dan Suite QA (`suites/project-qa/`) membutuhkan **Python 3**.
- **Solusi:**
  1. Untuk audit browser multi-viewport tanpa Python, jalankan pemeriksa Node.js secara langsung:
     ```sh
     node skills/atlas-checker/scripts/quick-check.mjs http://127.0.0.1:3000 --shots ./maintenance/browser --click-test
     ```
  2. Jika Python 3 tidak dapat dipasang, jalankan `node scripts/run-gates.mjs <proyek> --mode full --strict` (tanpa `--visual`) lalu catat dengan jujur pada laporan audit bahwa Gate 6 Python & skrip Suite QA berstatus *tidak dijalankan*.

## 2. Jaringan Terbatas / CDN Tidak Terjangkau (`--offline`)

- **Gejala:** Pencarian foto Wikimedia di `fetch-photos.mjs` gagal timeout, CDN `cdn.jsdelivr.net/npm/animejs@4/+esm` tidak dimuat di browser target, atau audit kerentanan CVE di Suite QA tidak dapat menghubungi OSV.dev / NIST NVD / CISA KEV.
- **Solusi yang Didukung Repo:**
  - **Anime.js v4 & Font:** Gunakan berkas lokal/bundle di proyek target alih-alih CDN eksternal (seperti pola font `.woff2` lokal dan paket npm lokal), serta pastikan konten statis terbaca meski skrip gerak tidak berjalan (status fallback `rest`).
  - **Wikimedia Photos (`fetch-photos.mjs`):** Skrip memiliki batas waktu keras per permintaan (`--request-timeout`, bawaan `30` detik) dan total anggaran (`--timeout`, bawaan `120` detik), serta tidak menimpa atribut kredit bila berjalan parsial. Di lingkungan luring penuh (`--offline` pada `references/imagery.md`), gunakan aset lokal milik pengguna atau pelat spesifikasi tipografis (`data-atlas-proof="editorial-plate"`).
  - **Audit CVE Suite QA (`live_cve_osv_check.py`):** Tambahkan flag `--offline-parse-only` untuk memindai manifes ketergantungan secara lokal tanpa mengirim nama/versi paket ke OSV.dev, NVD, atau CISA.

## 3. `atlas-skill doctor` Melaporkan Perubahan Berkas

- **Gejala:** Menjalankan `node bin/atlas-skill.mjs doctor --agent <nama>` melaporkan perbedaan checksum **SHA-256** atau berkas hilang dibandingkan `.atlas-install.json`.
- **Penyebab:** Salah satu berkas skill, referensi, atau skrip di folder `.agents/skills/atlas-skill/` (atau folder agen terkait) pernah disunting secara manual atau terputus saat pembaruan.
- **Solusi:**
  1. Tinjau berkas yang berbeda tersebut; jangan simpan perubahan kustom di folder paket terkelola.
  2. Jalankan pembaruan atomik agar pemasangan dikembalikan ke kondisi bersih sambil tetap mengamankan cadangan lama di `.atlas-skill-backups/`:
     ```sh
     node bin/atlas-skill.mjs update --agent <nama> --with-rules
     ```
  3. Jalankan ulang `node bin/atlas-skill.mjs doctor --agent <nama>` untuk memverifikasi seluruh hash kembali utuh.

## 4. Kendala Khusus Windows (PowerShell & Playwright)

- **Python di `AppData\Local\Programs\Python\...`:** Jika `python` tidak dikenali di shell Node/PowerShell meski Python sudah terpasang, tambahkan folder biner Python ke `$env:PATH` sebelum menjalankan `--visual`, misalnya:
  ```powershell
  $env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python310;$env:PATH"
  node scripts/run-gates.mjs <proyek> --mode full --strict --visual <url>
  ```
- **Chromium / `file://` Blokir atau Playwright Tidak Ditemukan:** `quick-check.mjs` otomatis menyalakan peladen HTTP statis lokal bila diberi path file HTML sehingga terhindar dari pemblokiran `file://`. Apabila Playwright atau browser tidak terdeteksi otomatis di jalur default Windows, setel variabel lingkungan `ATLAS_PLAYWRIGHT_PACKAGE` atau `ATLAS_BROWSER_PATH` ke lokasi `chrome.exe` / `msedge.exe` yang tersedia di mesin.
- **Eksekusi Berkas `.mjs`:** Selalu jalankan skrip lewat `node scripts/...mjs` dan hindari pemotongan argumen kutipan di PowerShell 5.1 ketika menjalankan pengujian satu-baris.
