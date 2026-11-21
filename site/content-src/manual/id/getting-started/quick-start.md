---
title: Mulai Cepat (5 Menit)
description: Pasang Atlas-skill v{{VERSION}}, jalankan prompt pertama, dan periksa keluaran gate deterministik dalam lima menit.
---

Panduan ini membawa proyek Anda dari nol hingga menghasilkan halaman web yang lolos pemeriksaan statis dan verifikasi viewport browser.

## Prasyarat

- **Node.js 18+** (disarankan Node 20/22 LTS) — dibutuhkan untuk penginstal CLI dan seluruh gate statis (`1–5` + `4b`).
- **Python 3** *(opsional, tetapi wajib untuk Gate 6 `--visual` dan Suite QA)* beserta Playwright/Chromium jika Anda menjalankan pemeriksaan tangkapan layar penuh di browser headless.

## Langkah 1: Pasang Skill ke Proyek

Jalankan salah satu perintah berikut di akar direktori proyek target:

```sh
# Pasang ke semua folder agen proyek (.agents, .claude, .cursor) beserta rule adaptif
npx --yes github:Crelami-Dev/atlas-skill install --agent all --with-rules

# Atau pasang lokal langsung dari salinan repo Atlas-skill:
node bin/atlas-skill.mjs install --agent antigravity --with-rules
```

Untuk menyertakan Suite QA & Keamanan Python (`project-bug-hunter`, `project-security-auditor`, `project-fix-and-verify`), tambahkan `--with-qa`:

```sh
npx --yes github:Crelami-Dev/atlas-skill install --agent codex --with-rules --with-qa
```

Ingin menguji terlebih dahulu tanpa menulis berkas? Tambahkan `--dry-run`:

```sh
npx --yes github:Crelami-Dev/atlas-skill install --agent claude --dry-run
```

## Langkah 2: Berikan Perintah Pertama ke Agen

Buka folder proyek Anda di agen AI coding pilihan, lalu jalankan perintah slash (atau rujuk `SKILL.md`):

```text
/atlas-frontend Bangun halaman profil studio arsitektur bergaya terang dengan token CSS lengkap, animasi masuk 15% viewport memakai Anime.js v4, dan verifikasi di 375/768/1440 px.
```

Untuk proyek end-to-end yang sekaligus menjalankan audit bug/keamanan (Fase 7) secara otomatis setelah pembangunan UI, gunakan `/atlas-skill`:

```text
/atlas-skill Bangun aplikasi manajemen jadwal berbasis web lengkap dengan 5-State UI Contract dan perbaikan otomatis seluruh temuan QA/CVE.
```

## Langkah 3: Hasil yang Diharapkan

Setelah agen menjalankan alur [Fase 0–6](/atlas-skill/id/workflow/phase-workflow/), proyek Anda akan memiliki artefak terverifikasi berikut:

| Berkas / Keluaran | Asal Fase | Fungsi |
|---|---|---|
| `design-brief.md` | Fase 1 (`atlas-plan`) | Tujuan pengunjung, konten nyata, 3 kandidat tata letak (atau track ringan), dan rencana gambar. |
| `design-tokens.css` | Fase 0 & 3 (`deal-direction.mjs`) | Sistem token palet WCAG AA, skala tipografi 2 keluarga (+1 mono opsional), spasi, dan durasi gerak. |
| `.atlas-direction.json` / `.atlas-scenes.json` | Fase 0 & 4 | Catatan pilihan arah desain dan scene agar tidak berulang secara mekanis antarhalaman. |
| HTML / CSS / JS terstruktur | Fase 4 (`atlas-lean-code`, `atlas-scenes`) | Tata letak responsif dengan kontrol `>= 44 px`, 0 `opacity: 0` statis, dan animasi Anime.js v4. |
| Laporan Gate 1–6 & tangkapan layar | Fase 5 (`run-gates.mjs` & `quick-check.mjs`) | Hasil PASS pada `check-brief`, `check-tokens`, `check-motion-v4`, `slop-scan`, `check-copy`, `check-visual-proof`, dan tangkapan layar `1440/820/375`. |

## Langkah Selanjutnya

- Lihat rute folder dan flag tiap agen di [Pasang per Agen](/atlas-skill/id/getting-started/install-by-agent/).
- Pahami struktur 3 skill utama dan 10 modul internal di [Arsitektur & Konsep](/atlas-skill/id/concepts/architecture/).
- Pelajari daftar kode error/peringatan browser di [Kamus Kode Temuan](/atlas-skill/id/checks/findings-dictionary/).
