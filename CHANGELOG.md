# Changelog

## 7.0.0 — Unified Atlas Universal + Antigravity QA & Security Suite + `npx` CLI (2026-11-19)

### Penggabungan Suite & Ekosistem `npx`
- **Penggabungan `atlas-skill` v6.1.0 Universal + `antigravity-qa-security-suite`:** Menyatukan seluruh 11 modul frontend/motion (`atlas-frontend-design` + 10 sub-skill) dengan suite QA & Security (`project-bug-hunter`, `project-security-auditor`, `project-fix-and-verify`) dalam satu repositori terpadu `atlas-skill`.
- **Integrasi Penuh QA & Security Governance (`suites/project-qa/`):**
  - Menambahkan aturan gerbang wajib `suites/project-qa/rules/qa-security-gate.md` (`trigger: always_on`) yang otomatis terpasang ke `.agents/rules/qa-security-gate.md` (atau `~/.gemini/config/rules/qa-security-gate.md`) saat instalasi dengan `--with-qa --with-rules`.
  - Menambahkan skrip `verify_feature_coverage.py` ke `project-fix-and-verify`, Decision Tree read-only vs gated remediation, 3-layer live CVE intelligence (OSV.dev / NIST NVD / CISA KEV + native audit + live web search), serta protokol uji 100% seluruh fitur + Zero-Defect Loop.
- **Installer `bin/atlas-skill.mjs` Siap `npx`:**
  - Mendukung `npx --yes github:Crelami-Dev/atlas-skill` maupun `npx atlas-skill` dan `node bin/atlas-skill.mjs`.
  - Mendukung penuh `--agent <codex|antigravity|claude|cursor|windsurf|cline|copilot|agents|all>`, `--dir <PATH>`, `--global`, `--with-rules`, `--expose-subskills`, `--with-qa`, `--dry-run`, `update` (dengan backup atomik), `doctor` (verifikasi SHA-256), dan `list`.
- **Konsistensi Versi `7.0.0`:** Menyelaraskan `package.json` (`"name": "atlas-skill"`, `"version": "7.0.0"`), `package-manifest.json`, `plugin.json`, `suites/project-qa/package-manifest.json`, `adapters/`, `README.md`, dan `docs/INSTALLATION.md`.

## 6.1.0 — Pembaruan Arsitektur Gambar, Komponen Form, 10 Arketipe, & Evaluasi Buta 3 Putaran (2026-11-18)

### Perbaikan Sumber Skill & Gate Deterministik
- **Strategi Gambar & Placeholder (`references/imagery.md`):** Menambahkan alur keputusan aset foto, bagian `Rencana gambar` pada brief, aturan SVG non-overlap dan badge `nowrap`, serta larangan siluet bukit+matahari.
- **Komponen Form & Isolasi Panel (`templates/design-tokens.css`, `scripts/deal-direction.mjs`):** Menambahkan styling lengkap untuk `input`, `select` (`appearance: none` + panah kustom + `text-overflow: ellipsis`), `textarea`, tombol (`text-decoration: none`), `checkbox`/`radio`, segmented control, serta isolasi warna heading di `.panel` / `.band-dark .panel`.
- **10 Arketipe Layout & 16 Direction Domain (`references/composition-selection.md`, `scripts/deal-direction.mjs`):** Memperluas cakupan ke 10 arketipe makro dan 16 direction (termasuk diferensiasi aksen `#9a3b1e` untuk `terracotta-artisan-store` dan variasi penutup hospitality) serta fallback nada yang terukur.
- **Penguatan Gate & Inspeksi DOM (`skills/atlas-checker/scripts/slop-scan.mjs`, `skills/atlas-checker/scripts/visual_dom_inspector.py`, `tests/gates.test.mjs`):** Memblokir jargon skill bocor (`leaked-skill-jargon`) dan meta string placeholder di UI, menambahkan pengecekan kontras full-page tanpa batas 40-node, `svg-text-overlap` (termasuk `<line>`), `mobile-squeezed-grid`, dan `desktop-broken-split-grid`.

### Evaluasi Buta Juri Independen (10 Kasus A/B, Baseline A Non-Stub Dibekukan)
- **Putaran 1:** A `3.11` vs B `4.16` (B menang `10/10`, 2 cacat KRITIS pada B, 3 pasangan B serupa).
- **Putaran 2:** A `3.00` vs B `4.26` (B menang `10/10`, 1 cacat KRITIS pada B, 1 pasangan B serupa).
- **Putaran 3 (Final):** A `2.99` (`209/70`) vs B `4.04` (`283/70`), B menang `10/10`, keberagaman layout terpenuhi (`<= 2` pasang serupa), namun juri independen Putaran 3 mencatat 1 pola cacat KRITIS terbuka: badge `"GANTI DENGAN FOTO ASLI"` yang tampak langsung di UI pada 5/10 kasus domain visual. Ringkasan lengkap tersimpan di `evals/independent-eval-2026-11-18.md` dan `evals/independent-eval-2026-11-18.json`.

### Kebersihan Paket Rilis
- Menaikkan versi ke `6.1.0` di `package.json`, `package-manifest.json`, `plugin.json`, `suites/project-qa/package-manifest.json`, `README.md`, dan `docs/INSTALLATION.md`.
- Mengecualikan `.git`, `evals/results/`, dan `evals/archive-invalid/` dari paket dan zip rilis, serta menghapus seluruh klaim skor mandiri dari `README.md`.

## 6.0.0 — Konsistensi Paket, Perbaikan Gate Deterministik, Pemisahan Suite QA, & Kerangka Evaluasi Buta (2026-11-18)

### Perbaikan & Perubahan Utama (Tahap 1 - Tahap 7)
- **Tahap 1 (Konsistensi & Pengujian):** Menjadikan `package.json` (`6.0.0`) sebagai sumber kebenaran versi tunggal untuk `bin/atlas-skill.mjs`, `scripts/validate-package.mjs`, `README.md`, `docs/INSTALLATION.md`, `plugin.json`, `package-manifest.json`, dan `tests/installer.test.mjs`. Menghitung jumlah skill secara dinamis dari `package-manifest.json`, memperbarui fixture `run-gates.mjs` agar menyertakan bukti visual nyata (`<img>` + 3 token permukaan), serta menambah pengujian halaman teks-saja pada Gate 5.
- **Tahap 2 (Perbaikan Gate 5 `scripts/check-visual-proof.mjs`):** Menghapus pencocokan kata kunci teks/kelas/komentar palsu (`chart`, `workbench`, `specimen`, `telemetry`) dan hanya menerima elemen DOM visual nyata (`<img>`, `<picture>`, `<canvas>`, `<video>`, `<svg>` data-viz yang bukan wireframe kaku, atau atribut `[data-atlas-proof]`) setelah mengabaikan komentar HTML/JSX serta blok `<style>`/`<script>`. Menjadikan `missing-visual-proof` dan `flat-surface-monotony` sebagai `warn` secara default dan `error` saat flag `--strict` diberikan (sementara `leaked-markdown-backticks` dan `crude-wireframe-svg` tetap `error`). Menambahkan dukungan opt-out `<!-- atlas-proof: not-applicable -->`.
- **Tahap 3 (Perbaikan `scripts/deal-direction.mjs`):** Mengganti pencocokan substring dengan pencocokan kata utuh (*Unicode word-boundary*) dan sistem skoring per direction sehingga kata pendek (`ai`, `dev`, `data`) tidak cocok di dalam kata lain (`ramai`, `develop`, `update`). Menghapus fallback berbasis hash path folder dan menggantinya dengan fallback deterministik tetap (`alabaster-botanical-studio`). Memperluas koleksi menjadi 8 direction dengan 8 pasangan font berbeda dan kategori non-netral-hangat (termasuk *dark mode* `obsidian-terminal-noir`, kontras tinggi `bauhaus-signal-poster`, dan klinis dingin `clinical-emerald-trust`), seluruhnya diverifikasi lulus kontras WCAG AA (`>= 4.5:1`) secara otomatis.
- **Tahap 4 (Dukungan Dwibahasa Indonesia & Inggris):** Memperbarui `scripts/check-brief.mjs` agar menerima heading Bahasa Indonesia maupun Bahasa Inggris beserta `### Alternative N` / `### Alternatif N`. Menambahkan `templates/design-brief.en.md`, menyertakan padanan verdict `PASS`/`FIX` untuk `LOLOS`/`PERBAIKI`, dan menghapus instruksi `deal-direction.js` yang tidak memiliki file fisik.
- **Tahap 5 (Perapian `SKILL.md` & Sub-skill):** Meringkas `SKILL.md` utama menjadi di bawah 60 baris dan memindahkan rincian fase ke `references/phase-workflow.md`. Menulis ulang seluruh deskripsi frontmatter menjadi aturan pemicu yang jelas (`"Gunakan saat... Jangan gunakan untuk..."`) tanpa klaim promosi, mengurangi pemakaian huruf kapital penuh/tanda seru, menyertakan alasan satu kalimat pada setiap aturan keras, serta menyediakan Jalur Ringan (*Compact Track*, `<!-- atlas-brief: light -->` / `--light`, tanpa `research-notes.md` kecuali diminta atau domain belum dikenal).
- **Tahap 6 (Pemisahan Suite Bug & Security):** Memindahkan `project-bug-hunter`, `project-security-auditor`, dan `project-fix-and-verify` ke `suites/project-qa/` dengan `suites/project-qa/package-manifest.json` tersendiri serta menambahkan flag opsional `--with-qa` pada `bin/atlas-skill.mjs` (keputusan konservatif: tetap menyertakan `suites/project-qa` di dalam paket distribusi sehingga baik pemisahan manifest maupun flag `--with-qa` berfungsi bersamaan tanpa memutus alur distribusi). Mendokumentasikan secara eksplisit di `project-security-auditor/SKILL.md` bahwa `live_cve_osv_check.py` mengirim nama dan versi dependency ke OSV.dev/NVD/CISA serta menyediakan flag `--offline-parse-only`.
- **Tahap 7 (Kerangka Evaluasi Buta & Transparansi Bukti):** Menambahkan `evals/prepare-blind-eval.mjs` untuk menyiapkan struktur `evals/results/YYYY-MM-DD/<prompt>/{A,B}` dan mengacak label kandidat A/B secara buta sesuai `evals/run-protocol.md` tanpa mengarang skor. Memberi label eksplisit pada `evals/review-2026-11-13.md` sebagai *"penilaian mandiri oleh agent penulis, bukan benchmark independen"* dan mencatat secara jujur di `README.md` bahwa belum ada bukti empiris A/B independen.

### Perbaikan Pasca-Review Desain & Kebersihan Paket (2026-11-18)
- **Kebersihan Paket & Eksklusi Artefak Eval:** Mengecualikan `evals/results` dan `__pycache__` dari `package-manifest.json`, `package.json` (`files`), `scripts/package-files.mjs`, `scripts/verify-export.mjs`, dan `.gitignore` sehingga ukuran paket terinstal/terekspor turun kembali ke 91 file inti tanpa membawa screenshot hasil evaluasi atau folder `.git`.
- **Larangan Dropdown Debug di UI Produksi:** Menambahkan aturan `leaked-debug-state-switcher` (`error`) di `slop-scan.mjs` dan memperbarui `atlas-ui-architecture/SKILL.md` agar dropdown pengujian state (`Populated / Loading / Empty / Error`) tidak pernah bocor ke pengunjung akhir.
- **Keberagaman Struktur Layout Makro (Anti-Uniformity):** Memperbarui `deal-direction.mjs` dan `atlas-design/SKILL.md` untuk melarang penyeragaman *"hero 2-kolom + kartu workbench berisi Search/Filter/Reset"* di semua domain; mendefinisikan 8 arketipe struktur makro berbeda (mis. *Full-Bleed Atmospheric Cover + Two-Column Print Menu* untuk restoran, *Full-Width Swiss Poster + Chronological Timetable* untuk event, *Exhibition Plate Masonry* untuk fotografer, *Single-Column 68ch Editorial Dossier* untuk donasi, *60/40 Multi-Angle Studio Stage* untuk produk fisik, *3-Pane DevDocs* untuk dokumentasi, dan *Full-Viewport App Shell* untuk dashboard).
- **Perluasan Cakupan Domain `deal-direction.mjs` (12 Direction):** Menambahkan 4 direction baru beserta kata kunci Indonesia & Inggris untuk domain pernikahan (`velvet-champagne-atelier`), konsultan hukum/korporat (`savile-navy-counsel`), toko produk fisik/e-commerce (`terracotta-artisan-store`), dan pendidikan/kursus (`campus-amber-academy`), seluruhnya terverifikasi lolos kontras WCAG AA (`>= 4.5:1`).
- **Rekonstruksi Baseline A Setara & Penghapusan Klaim Skor Mandiri:** Membangun ulang 8 halaman Baseline A sebagai halaman multi-seksi lengkap (bukan stub) dan menghapus klaim skor mandiri (`2.16 vs 4.93`) dari `README.md` agar evaluasi tetap objektif untuk penilai independen.

### Audit Independen, Serangan Adversarial Gate, & Evaluasi End-to-End 8 Prompt (2026-11-18)
- **Putaran 1 (Audit Regresi, Adversarial Gate, & Konsistensi):**
  - Memperbaiki false-positive `font-proliferation` di `slop-scan.mjs` yang sebelumnya menghitung jumlah deklarasi properti `font-family:` alih-alih jumlah keluarga font unik.
  - Memperbaiki crash `ENOENT` pada symlink rusak dan path berspasi di `check-tokens.mjs`, `check-motion-v4.mjs`, `slop-scan.mjs`, dan `check-visual-proof.mjs`.
  - Memperkuat `check-brief.mjs` terhadap duplikasi nomor `### Alternatif 1`, file kosong, dan baris CRLF Windows.
  - Memperkuat `check-tokens.mjs` agar mengabaikan komentar CSS/HTML, menerima shorthand campuran (`margin: 0 auto var(--space-4)`, `border-radius: 50%`), dan memeriksa atribut `style="..."` inline.
  - Memperkuat `check-motion-v4.mjs` untuk mendeteksi `import * as anime` / `anime.default()` serta jebakan SSR `[data-hero-title] { opacity: 0 }` dan `visibility: hidden`.
  - Memperkuat `check-visual-proof.mjs` agar menolak `<img src="">` kosong dan mendeteksi SVG wireframe kotak tanpa atribut `viewBox`.
  - Menyelaraskan versi `package-lock.json` (`6.0.0`), menambahkan dukungan `--with-rules` untuk `--agent copilot`, serta memperkaya kata kunci `deal-direction.mjs` agar 8 domain uji memetakan 1-ke-1 ke 8 direction unik.
- **Putaran 2 (Uji End-to-End 8 Prompt A/B & Tangkapan Layar Chromium):**
  - Menemukan melalui inspeksi PNG (`view_file`) bahwa kebijakan Chromium memblokir navigasi `file://*` (`This page is blocked`); memperbaiki `visual_dom_inspector.py`, `ui_visual_bug_probe.py`, dan `e2e_visual_regression.py` dengan melakukan inlining stylesheet dan gambar lokal ke dalam `Page.setDocumentContent` serta menambahkan tangkapan layar tablet `820x1180`.
  - Memperbaiki pelanggaran token hex mentah pada `02-photographer/B`, jumlah keluarga font pada `07-donation/B`, ukuran judul rail `320px` pada `02-photographer/B`, urutan tata letak mobile `375x667` pada `05-product/B` dan `07-donation/B` agar CTA utama berada di atas lipatan `667px`, serta target anchor `#retry-semantics` pada `08-docs/B`.
- **Putaran 3 & Putaran 4 (Verifikasi Dua Putaran Bersih Berturut-turut):**
  - Seluruh 39 unit & adversarial test lulus (`39/39`), `npm run validate` dan `npm run test:export` lulus, serta seluruh 8 proyek B lulus `run-gates.mjs --mode full --strict` dan audit browser multi-viewport (`1440`, `820`, `375`, zoom 200%, 5-state UI, keyboard focus, dan 0 error konsol) selama 2 putaran berturut-turut tanpa temuan KRITIS/SEDANG baru.

## 5.0.0 - 2026-11-18

- Added dedicated `atlas-motion-animejs` module, `references/animejs-v4-playbook.md`, `templates/animejs-v4-scope.ts`, and `scripts/check-motion-v4.mjs` enforcing authentic Anime.js v4 APIs (`animate`, `createTimeline`, `createScope`, `onScroll`, `spring`, `splitText`, `createLayout`, `svg`, `waapi`) while blocking v3 hallucinations and SSR invisibility traps.
- Added `atlas-ui-architecture` (5-state view contract, responsive app shells, accessible forms/tables/filters) and `atlas-fullstack-contracts` (typed API/mock adapters, auth state boundaries, SEO/OpenGraph readiness) for complete project delivery.
- Upgraded `bin/atlas-skill.mjs` and added `adapters/` for universal compatibility across OpenAI Codex, Google Antigravity IDE, Claude Code, Cursor, Windsurf, Cline, GitHub Copilot, and any `AGENTS.md`-aware agent (including `--global`, `--with-rules`, and `--expose-subskills`).
- Upgraded `check-tokens.mjs`, `slop-scan.mjs`, `run-gates.mjs`, and all 7 existing sub-skills with concrete Bad-vs-Good code contrasts and deterministic guardrails.
- Fixed UTF-8 corruption in `SKILL.md` and replaced Node 22-only `import.meta.dirname` calls with `fileURLToPath` across all scripts and tests for full Node 18-24+ compatibility.

## 4.0.0 - 2026-11-13

- Replaced legacy Python preset runtime with a dependency-free Node.js installer, modular instruction set, phase gates, and Playwright verification tools.
