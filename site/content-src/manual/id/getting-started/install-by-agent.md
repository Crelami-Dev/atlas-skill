---
title: Pasang per Agen & Referensi CLI
description: Lokasi folder, flag --global, --with-qa, --expose-subskills, --dry-run, serta perintah update dan doctor untuk 7 agen AI coding.
---

Atlas-skill mendukung **7 agen AI coding** serta agen lain yang kompatibel dengan `AGENTS.md`. Penginstal CLI (`bin/atlas-skill.mjs` versi `v{{VERSION}}`) tidak melakukan permintaan jaringan saat menyalin file paket dan tidak memodifikasi konfigurasi pribadi agen Anda di luar direktori skill/rule yang diminta.

## Matriks Agen Proyek-Lokal (`PROJECT_TARGETS`)

Tabel ini dihasilkan langsung dari definisi `PROJECT_TARGETS` di `bin/atlas-skill.mjs`:

{{AGENT_TABLE}}

## Matriks Pemasangan Global (`--global`)

Agen berikut mendukung pemasangan global ke direktori konfigurasi pengguna (`GLOBAL_TARGETS` di `bin/atlas-skill.mjs`). Untuk agen tanpa jalur global standar (Windsurf, Cline, Copilot), gunakan flag `--dir <PATH>`:

{{GLOBAL_AGENT_TABLE}}

## Penjelasan Perintah (`install`, `update`, `doctor`, `list`)

| Perintah | Cara Kerja |
|---|---|
| `install` *(default)* | Menyalin skill utama (`atlas-skill`, `atlas-frontend`, `atlas-bug-hunter`) beserta modul dan aset yang dibutuhkan ke folder agen target, lalu menulis manifes integritas `.atlas-install.json`. |
| `update` | Mencadangkan folder pemasangan lama secara utuh ke `.atlas-skill-backups/` sebelum mengganti isi berkas secara atomik. Memungkinkan pemulihan cepat bila Anda melakukan kustomisasi lokal. |
| `doctor` | Memeriksa ketersediaan Node.js 18+, Playwright/Chromium opsional, dan memvalidasi hash **SHA-256** setiap file terhadap `.atlas-install.json` untuk mendeteksi berkas yang berubah atau hilang. |
| `list` | Menampilkan daftar skill frontend, skill QA, serta jalur tujuan agen yang tersedia. |

## Penjelasan Flag Penting

### `--with-rules`
Menulis berkas rule adaptif native (misalnya `.agents/rules/atlas-frontend-gate.md`, `.cursor/rules/atlas-frontend-gate.mdc`, atau `AGENTS.atlas.md`) tanpa menimpa `AGENTS.md` atau berkas rule Anda yang sudah ada. Sangat disarankan saat menggunakan model berbiaya hemat/cepat agar agen selalu menjalankan gate terminasi `run-gates.mjs`.

### `--with-qa`
Menyertakan Suite QA & Keamanan Python dari [suites/project-qa/](/atlas-skill/id/qa/project-qa-suite/) (`project-bug-hunter`, `project-security-auditor`, `project-fix-and-verify`). Bila digabungkan dengan `--with-rules`, file rule `qa-security-gate.md` ikut terpasang.

### `--expose-subskills`
Secara bawaan, Atlas hanya menampilkan **3 perintah teratas** (`/atlas-skill`, `/atlas-frontend`, `/atlas-bug-hunter`) agar menu perintah slash IDE Anda tetap ringkas. Flag `--expose-subskills` memaparkan ke-10 modul internal (`atlas-plan`, `atlas-design`, `atlas-motion-animejs`, dll.) sebagai folder skill sejajar jika Anda ingin memanggil modul tertentu secara manual.

### `--global` dan `--dir <PATH>`
- `--global`: Menginstal Atlas ke direktori konfigurasi home pengguna (`~/.agents`, `~/.gemini/config`, `~/.claude`, `~/.cursor`) sehingga tersedia di seluruh repositori pada mesin tersebut.
- `--dir <PATH>`: Menginstal ke folder khusus pilihan Anda (tidak dapat digabungkan dengan `--agent all`).

### `--dry-run`
Memvalidasi paket sumber dan mencetak rencana pemasangan lengkap beserta daftar berkas tujuan tanpa menulis satu pun byte ke disk.

```sh
node bin/atlas-skill.mjs install --agent antigravity --with-qa --with-rules --dry-run
```

## Referensi Output `--help` Terkini

```text
{{CLI_HELP}}
```
