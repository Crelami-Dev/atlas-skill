---
title: Panduan Kontribusi
description: Cara menjalankan suite pengujian repositori, validate-package.mjs, serta menambah scene atau kode temuan baru dengan aman.
---

Kontribusi pada Atlas-skill harus mempertahankan prinsip utama repositori: **nol dependensi npm runtime pada paket inti**, **konsistensi lintas manifes**, dan **dokumentasi situs yang tersinkron dengan kode sumber**.

## 1. Menjalankan Validasi & Tes Bawaan

Sebelum mengajukan perubahan apa pun pada skill, templat, atau dokumentasi, jalankan seluruh rangkaian verifikasi dari direktori akar repo:

```sh
# 1. Memeriksa konsistensi versi, frontmatter SKILL.md, JSON, sintaks .mjs, dan 189+ link internal
node scripts/validate-package.mjs

# 2. Menjalankan unit test Node bawaan (termasuk parser dokumentasi & katalog)
node --test tests/*.test.mjs

# 3. Menjalankan 33 kasus regresi checker untuk quick-check.mjs / slop-scan
node skills/atlas-checker/scripts/self-test.mjs

# 4. Memastikan arsip distribusi hanya berisi file resmi (tanpa site/ atau site/dist/)
npm pack --dry-run
```

Jika Anda juga mengubah isi `site/` atau sumber data dokumentasi, jalankan generator serta penjaga sinkronisasi dan build situs:

```sh
node scripts/gen-docs.mjs
node scripts/check-docs.mjs
cd site && npm run build
```

## 2. Cara Menambah atau Mengubah Scene Baru

1. Tambahkan definisi scene pada array `scenes` di `templates/scene-catalog.json` dengan lengkap (`id`, `mode`, `family`, `fits`, `look`, `needs`, `never`, `rest`, `cost`).
2. Tambahkan gaya CSS, implementasi gerak pada `templates/atlas-scenes.mjs`, contoh di `templates/atlas-scenes-demo.html`, serta panduan penggunaannya di `references/scenes.md` agar `tests/scenes-and-copy.test.mjs` (bila tersedia) tetap sinkron.
3. Jalankan `node scripts/gen-docs.mjs && node scripts/check-docs.mjs` — daftar dan halaman detail scene baru pada situs `/id/scenes/<id>/` serta `/en/scenes/<id>/` akan terbit secara otomatis tanpa penyuntingan manual file situs.

## 3. Cara Menambah Kode Temuan Baru ke `quick-check.mjs`

1. Tambahkan pemeriksaan dan panggilan `fails.push("kode-baru: ...")` atau `warns.push("kode-baru: ...")` di `skills/atlas-checker/scripts/quick-check.mjs` beserta kasus regresinya di `skills/atlas-checker/scripts/self-test.mjs`.
2. Tambahkan entri baru dengan `code: kode-baru` pada `site/content-src/findings.yml` (lengkapi `severity`, `meaning_id`, `cause_id`, `fix_id`, `meaning_en`, `cause_en`, dan `fix_en`).
3. Jalankan `node scripts/gen-docs.mjs && node scripts/check-docs.mjs` untuk memverifikasi bahwa kamus temuan sinkron 1-ke-1 dengan kode sumber `quick-check.mjs`.

## 4. Menjaga Kebersihan Paket Distribusi

- Jangan memasukkan `site/`, `site/dist/`, `tests/`, `maintenance/`, atau berkas kerja lokal ke `"files"` dalam `package.json` maupun `"include"` dalam `package-manifest.json`.
- Jangan menambahkan `dependencies` atau `devDependencies` ke `package.json` di akar repo; semua dependensi generator Astro Starlight harus terisolasi di dalam `site/package.json`.
- Setiap klaim metrik atau evaluasi empiris wajib merujuk berkas fakta di `evals/` bersama seluruh konteks dan batasannya.
