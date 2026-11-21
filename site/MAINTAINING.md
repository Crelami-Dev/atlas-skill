# Panduan Perawatan Situs Dokumentasi Atlas-skill

Dokumen ini menjelaskan bagian mana yang otomatis terbarui oleh repositori dan langkah tepat yang perlu dilakukan saat menambah fitur atau merilis versi baru.

## Aturan Singkat: Otomatis vs Manual

- **Jangan pernah mengedit file di `site/src/content/docs/**`.** Direktori tersebut masuk `.gitignore` dan sepenuhnya ditimpa ulang oleh `node scripts/gen-docs.mjs`.
- **Untuk mengubah narasi manual**, edit berkas di `site/content-src/manual/id/` dan padanannya di `site/content-src/manual/en/`. Keduanya harus selalu sejajar.
- **Setelah setiap perubahan**, jalankan:
  ```sh
  node scripts/gen-docs.mjs && node scripts/check-docs.mjs
  ```

---

## Skenario Perubahan & Tindakan yang Diperlukan

### 1. Menambah atau Mengubah Scene di `templates/scene-catalog.json`
- **Otomatis:** Jalankan `node scripts/gen-docs.mjs`. Skrip membaca `templates/scene-catalog.json` dan `references/scenes.md`, membuat/memperbarui `scenes/index.md` serta 1 halaman per scene (`scenes/<id>.md`) dalam versi `/id/` dan `/en/`.
- **Manual:** Tidak ada, kecuali Anda ingin menautkan halaman scene tersebut secara khusus dari teks manual. Jika hanya memperbarui `templates/scene-catalog.json`, `scripts/check-docs.mjs` memverifikasi bahwa hasil generate sudah memuat scene baru tersebut.

### 2. Menambah atau Menghapus Kode Temuan di `skills/atlas-checker/scripts/quick-check.mjs`
- **Otomatis:** `scripts/gen-docs.mjs` mengekstrak seluruh kode temuan (`fails.push("kode: ...")`, `warns.push("kode: ...")`, `sweepWarns.push("kode: ...")`) langsung dari `skills/atlas-checker/scripts/quick-check.mjs`.
- **Manual Wajib:** Tambahkan (atau hapus) entri dengan `code` yang sama di `site/content-src/findings.yml`, berisi:
  - `severity` (`FAIL`, `WARN`, atau `FAIL/WARN`)
  - `meaning_id`, `cause_id`, `fix_id`
  - `meaning_en`, `cause_en`, `fix_en`
- Jika lupa mengisi atau menyisakan entri yatim di `findings.yml`, `node scripts/check-docs.mjs` akan gagal (`exit 1`) dan menyebutkan nama kode serta file yang harus diperbarui.

### 3. Menambah Modul atau Skill Baru di `package-manifest.json` / `suites/project-qa/package-manifest.json`
- **Otomatis:** Pastikan `SKILL.md` modul baru memiliki frontmatter YAML `name` dan `description` berpetik yang valid (`validate-package.mjs` memeriksa ini). Lalu jalankan `node scripts/gen-docs.mjs`: halaman `concepts/architecture.md` dan `qa/project-qa-suite.md` otomatis memunculkan modul beserta deskripsinya.

### 4. Memperbarui Panduan Referensi di `references/*.md` atau `evals/` atau `CHANGELOG.md`
- **Otomatis:** Tidak perlu menyalin ke `site/`. Saat `gen-docs.mjs` dijalankan (lokal maupun otomatis di CI GitHub Actions), isi terbaru dari `references/*.md`, `evals/`, dan `CHANGELOG.md` langsung disalin ke `site/src/content/docs/` lengkap dengan frontmatter Starlight, penulisan ulang tautan internal `/atlas-skill/`, dan banner catatan sumber.

### 5. Mengubah Agen atau Flag CLI di `bin/atlas-skill.mjs`
- **Otomatis:** `scripts/gen-docs.mjs` membaca objek `PROJECT_TARGETS` dan `GLOBAL_TARGETS` dari `bin/atlas-skill.mjs` serta mengeksekusi `node bin/atlas-skill.mjs --help` untuk memperbarui tabel jalur agen pada halaman *Pasang per Agen* dan blok bantuan CLI pada halaman *Beranda / Mulai Cepat*.
- **Manual (bila perlu):** Jika ada konsep flag baru yang memerlukan penjelasan panjang, tambahkan penjelasannya di `site/content-src/manual/{id,en}/getting-started/install-by-agent.md`.

### 6. Rilis Versi Baru (`package.json`)
- Pastikan versi diperbarui secara konsisten pada `package.json`, `package-manifest.json`, `plugin.json`, `suites/project-qa/package-manifest.json`, `README.md`, `CHANGELOG.md`, dan jalankan `node scripts/validate-package.mjs`.
- Jalankan `node scripts/gen-docs.mjs && node scripts/check-docs.mjs`. Semua badge versi dan catatan otomatis pada situs akan ikut berubah mengikuti `package.json`.

---

## Pemeriksaan Lengkap Sebelum Push

```sh
node scripts/validate-package.mjs
node --test tests/*.test.mjs
node skills/atlas-checker/scripts/self-test.mjs
node scripts/gen-docs.mjs && node scripts/check-docs.mjs
cd site && npm run build
```
