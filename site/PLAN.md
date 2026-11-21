# Rencana Arsitektur & Perawatan Situs Dokumentasi Atlas-skill

Dokumen ini menjadi rencana dan catatan arsitektur situs dokumentasi **Atlas-skill** yang dipublikasikan melalui GitHub Pages pada `https://crelami-dev.github.io/atlas-skill/`.

## 1. Tujuan & Prinsip Keterhubungan ke Repo

Situs dokumentasi ini bukan salinan statis yang terpisah dari kode sumber. Setiap informasi faktual yang dimiliki oleh repositori dihasilkan langsung dari sumber kebenarannya saat proses build:

1. **Satu sumber kebenaran per fakta:** Versi paket berasal dari `package.json`, daftar modul dari `package-manifest.json` dan `suites/project-qa/package-manifest.json`, tabel agen dan flag CLI dari `bin/atlas-skill.mjs`, daftar scene dari `templates/scene-catalog.json`, kode temuan dari `skills/atlas-checker/scripts/quick-check.mjs`, dan riwayat perubahan dari `CHANGELOG.md`.
2. **Paket pengguna tetap ramping:** Seluruh aset dokumentasi berada di `site/` dan dikecualikan dari `"files"` pada `package.json` serta `"include"` pada `package-manifest.json`. Root `package.json` tidak memiliki dependensi runtime atau dev apa pun.
3. **Etalase gaya Atlas Register:** Tampilan situs memakai token visual yang sama dengan [DESIGN-SYSTEM.md](../atlas-landing/DESIGN-SYSTEM.md) / `design-tokens.css` (palet terang netral hangat-dingin `#f7f8f5`, aksen tunggal petrol `#006654`, padanan gelap berkonsep terminal `#172522`, font lokal `Manrope` + `IBM Plex Sans` + `Fira Code`, target sentuh `>= 44px`, dan garis registrasi khas tanpa gradasi dekoratif).

## 2. Pilihan Generator & Alasannya

Generator yang dipilih adalah **Astro Starlight** (`astro` + `@astrojs/starlight`, dependensi terisolasi di `site/package.json`).

**Alasan memilih Astro Starlight dibandingkan VitePress atau site kustom polos:**
- **Pencarian statis bawaan (Pagefind):** Langsung mengindeks seluruh halaman ID/EN saat `npm run build` termasuk kode temuan `quick-check.mjs` (mis. `cta-width-mismatch`, `loop-no-pause`) dan nama scene (`pull-back`, `split-wipe`) tanpa layanan backend eksternal.
- **Dukungan i18n native (`id` dan `en`):** Rute `/atlas-skill/id/` dan `/atlas-skill/en/` terhubung otomatis oleh Starlight sehingga tombol pengubah bahasa menjaga pengguna tetap pada padanan halaman di bahasa sebelahnya.
- **Navigasi & utilitas dokumentasi out-of-the-box:** Sidebar multi-level, daftar isi kanan (*On this page*), tombol salin pada blok kode, serta tema terang/gelap yang dapat dioverride sepenuhnya menggunakan token CSS Atlas.
- **Mengapa bukan VitePress:** VitePress sangat baik untuk proyek berbasis ekosistem Vue, tetapi kustomisasi mendalam pada i18n berbasis direktori + integrasi Pagefind multi-bahasa serta kontrol penuh atas komponen head/CSS tanpa konfigurasi runtime Vue lebih langsung dan zero-client-framework di Astro Starlight (karena HTML statis Astro mengirim JS minimal dan sangat cocok dengan standar `atlas-lean-code`).

## 3. Peta Konten: Manual vs Dibuat Otomatis

| Bagian / Halaman | Jalur Situs (`{lang}`) | Sifat Sumber | File Sumber di Repo |
|---|---|---|---|
| Beranda & Mulai Cepat | `index.mdx` | **Manual** + blok `--help` otomatis | `site/content-src/manual/{id,en}/index.mdx` + `bin/atlas-skill.mjs` |
| Mulai Cepat 5 Menit | `getting-started/quick-start.md` | **Manual** (ID/EN) + versi & CLI otomatis | `site/content-src/manual/{id,en}/getting-started/quick-start.md` |
| Pasang per Agen | `getting-started/install-by-agent.md` | **Manual** (ID/EN) + tabel agen otomatis | `site/content-src/manual/{id,en}/getting-started/install-by-agent.md` + `bin/atlas-skill.mjs` |
| Konsep & Arsitektur Modul | `concepts/architecture.md` | **Otomatis** | `package-manifest.json`, `suites/project-qa/package-manifest.json`, `SKILL.md`, `skills/*/SKILL.md` |
| Alur Kerja per Fase (0–7) | `workflow/phase-workflow.md` | **Otomatis** (salin saat build + banner) | `references/phase-workflow.md` |
| Ikhtisar Scene & Gerak | `scenes/index.md` | **Otomatis** | `templates/scene-catalog.json`, `references/scenes.md` |
| 10 Halaman Detail Scene | `scenes/<id>.md` (10 file) | **Otomatis** | `templates/scene-catalog.json`, `references/scenes.md` |
| Loop Otomatis | `guides/loops.md` | **Otomatis** (salin saat build + banner) | `references/loops.md` |
| Komponen & Komposisi | `guides/components-and-composition.md` | **Otomatis** (salin saat build + banner) | `references/composition.md`, `references/composition-selection.md` |
| Tipografi | `guides/typography.md` | **Otomatis** (salin saat build + banner) | `references/typography.md` |
| Teks Ringkas (`check-copy`) | `guides/concise-copy.md` | **Otomatis** (salin saat build + banner) | `references/copy-concise.md` |
| Citra & Foto Berlisensi | `guides/imagery.md` | **Otomatis** (salin saat build + banner) | `references/imagery.md` |
| Mobile & Tablet | `guides/mobile-and-tablet.md` | **Otomatis** (salin saat build + banner) | `references/mobile-and-tablet.md` |
| Referensi Lanjutan (`references/*.md`) | `guides/references.md` / dokumen lain | **Otomatis** (tautan & ringkasan) | `references/*.md` |
| Anti-Slop (18 Pola) | `anti-slop/patterns.md` | **Otomatis** (salin saat build + banner) | `references/slop-patterns.md` |
| Gate & Pemeriksa | `checks/gates-and-checkers.md` | **Manual** (ID/EN) | `site/content-src/manual/{id,en}/checks/gates-and-checkers.md` |
| Kamus Kode Temuan (`quick-check`) | `checks/findings-dictionary.md` | **Otomatis** (ekstraksi kode + kamus YAML) | `skills/atlas-checker/scripts/quick-check.mjs` + `site/content-src/findings.yml` |
| Suite QA & Keamanan (`--with-qa`) | `qa/project-qa-suite.md` | **Otomatis** | `suites/project-qa/package-manifest.json`, `suites/project-qa/rules/qa-security-gate.md`, `suites/project-qa/skills/*/SKILL.md` |
| Evaluasi Empiris (Blind A/B) | `evaluation/blind-ab.md` | **Otomatis** (kutip asli + batasan) | `evals/independent-eval-2026-11-18.md`, `evals/independent-eval-2026-11-18.json`, `evals/run-protocol.md`, `evals/rubric.md` |
| Pemecahan Masalah | `guides/troubleshooting.md` | **Manual** (ID/EN) | `site/content-src/manual/{id,en}/guides/troubleshooting.md` |
| Riwayat Versi | `changelog/index.md` | **Otomatis** | `CHANGELOG.md` |
| Panduan Kontribusi | `guides/contributing.md` | **Manual** (ID/EN) | `site/content-src/manual/{id,en}/guides/contributing.md` |

## 4. Batasan Klaim Empiris (Evaluasi Blind A/B)

Setiap penyebutan skor evaluasi dari `evals/independent-eval-2026-11-18.md` harus selalu tampil bersama seluruh batasannya:
- Pembanding adalah **Baseline A yang dibangun secara bersih tanpa skill Atlas** (bukan dibandingkan dengan skill atau framework pihak ketiga lain).
- Diuji pada versi **`6.1.0`** (`Round 3`: rata-rata Baseline A `2.99 / 5.00` vs Atlas B `4.04 / 5.00`, Atlas B menang `10/10` kasus).
- Pada `6.1.0`, juri independen menandai **1 pola cacat kritis terbuka**: lencana placeholder `"GANTI DENGAN FOTO ASLI"` terlihat di UI pengunjung pada 5/10 kasus domain visual. Instruksi lencana ini telah dihapus dan diblokir otomatis pada **`7.0.0`**, namun **belum dievaluasi ulang secara independen**.

## 5. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Kode temuan baru ditambah di `quick-check.mjs` tanpa dokumentasi | Kamus temuan kedaluwarsa | `scripts/check-docs.mjs` membandingkan set kode regex dari `quick-check.mjs` dengan `site/content-src/findings.yml` dan keluar `exit 1` jika ada selisih atau entri yatim. |
| Scene baru ditambah di `scene-catalog.json` tapi lupa dibuat halamannya | Daftar scene tidak sinkron | `scripts/gen-docs.mjs` membangkitkan halaman per scene secara otomatis; `check-docs.mjs` menggagalkan build jika ada ID scene di katalog yang tidak ada di output `docs/`. |
| Tautan relatif di `references/*.md` atau `README.md` rusak saat dipindah ke base `/atlas-skill/` | Error 404 saat klik tautan di Pages | `gen-docs.mjs` menulis ulang link internal ke rute `/atlas-skill/<locale>/...`, dan `check-docs.mjs` memverifikasi setiap target link internal ada pada peta rute hasil generate. |
| `site/` atau `site/dist/` ikut masuk ke paket `npm pack` pengguna | Paket npm membengkak | Root `package.json` `"files"` dan `package-manifest.json` `"include"` memakai allowlist eksplisit; `npm pack --dry-run` diverifikasi pada Langkah 7. |
| Terjemahan halaman manual ID dan EN menyimpang | Halaman ID atau EN tertinggal | `check-docs.mjs` memverifikasi kesamaan daftar file serta jumlah heading/struktur frontmatter antara `site/content-src/manual/id/` dan `en/`. |
| Klaim angka tanpa sumber masuk lewat suntingan manual | Melanggar prinsip jujur faktual repo | `check-docs.mjs` memindai pola klaim terlarang (`bintang GitHub`, `pengguna aktif`, angka skor tanpa konteks `6.1.0`). |

## 6. Catatan Akhir & Status Implementasi

- **Generator & Penjaga (`scripts/gen-docs.mjs`, `scripts/check-docs.mjs`):** Menghasilkan `62` berkas dokumentasi (31 halaman per bahasa `id`/`en` termasuk `10` halaman detail scene dari `templates/scene-catalog.json` dan `26` entri kamus temuan dari `skills/atlas-checker/scripts/quick-check.mjs` + `site/content-src/findings.yml`), idempotent pada dua eksekusi beruntun.
- **Validasi & Tes:**
  - `node scripts/validate-package.mjs` => `PASS` (`122` file tercakup di manifest, `0` error).
  - `node --test tests/gen-docs.test.mjs` => `4/4 PASS`.
  - `node skills/atlas-checker/scripts/self-test.mjs` => `PASS 33 checker regression cases`.
  - `node scripts/check-tokens.mjs site/src --tokens site/src/styles/tokens.css` => `PASS`.
  - Uji negatif `scripts/check-docs.mjs`: menghapus entri `loop-no-pause` di salinan `findings.yml` dan menambah `fake-scene-xyz` di salinan `scene-catalog.json` keduanya gagal (`exit 1`) dengan pesan menyebut kode & berkas target.
  - `npm pack --dry-run` => `123` file (termasuk root `package.json`), **tanpa `site/` maupun `site/dist/`**.
- **Build & Browser QA (`site/`):**
  - `astro build` berhasil membangun `63` halaman (termasuk `/index.html` pengalihan ke `/atlas-skill/id/`), dan Pagefind mengindeks `2` bahasa (`11200` kata).
  - Verifikasi Playwright pada `1440x900`, `768x1024`, dan `375x812`: `0` horizontal overflow, `0` broken links (`31` tautan internal teruji), `0` console error, tombol bahasa `/atlas-skill/id/` <-> `/atlas-skill/en/` berfungsi, menu mobile terbuka penuh (`44x44px`), dan pencarian Pagefind menemukan `cta-width-mismatch`.
- Panduan operasional perawatan berkala tersedia di [MAINTAINING.md](./MAINTAINING.md).
