# 01. Repo Hygiene

## Tujuan
Menutup kelemahan dasar repo: lisensi tidak jelas, nama bentrok dengan skill Atlas (schema migration), README membingungkan, tanpa deskripsi/release, dan install dari `main` yang bergerak.

## Prompt

```
Kamu mengerjakan repo skill agen AI "atlas-skill". Baca dulu README.md, package.json, plugin.json, package-manifest.json, SKILL.md, dan docs/INSTALLATION.md sebelum mengubah apa pun.

Tugas: rapikan "repo hygiene" tanpa mengubah isi desain/instruksi skill.

1. Nama: nama "atlas" bentrok dengan skill Atlas (atlasgo.io) yang memakai folder `atlas`. Ganti nama skill menjadi `atlas-frontend-design` di: field `name` pada frontmatter SKILL.md, folder tujuan installer (.agents/skills/... dan .claude/skills/...), package.json, plugin.json, README, dan docs. Cari semua kemunculan lama dengan grep dan pastikan tidak ada yang tertinggal.
2. Description pemicu: tulis ulang `description` di frontmatter SKILL.md supaya sempit dan spesifik: aktif hanya untuk tugas desain/UI frontend (landing page, halaman web, komponen visual), dan tidak aktif untuk database, migrasi, atau backend.
3. Lisensi: tambahkan file LICENSE (MIT) dan ubah package.json dari UNLICENSED ke MIT. Jangan ubah `private:true` kecuali aku minta; tulis di ringkasan bahwa itu keputusan terpisah.
4. README: hapus kalimat "This repository may be private". Tambahkan bagian "Install yang direkomendasikan" memakai tag atau commit SHA (`github:Crelami-Dev/atlas-skill#<tag-atau-sha>`), dan beri peringatan bahwa install dari `main` bisa berubah kapan saja. Perbaiki juga bagian Limitations yang menyebut lisensi.
5. Metadata: siapkan teks deskripsi singkat repo (1 kalimat) dan daftar topic yang disarankan, simpan di docs/REPO-METADATA.md (aku yang akan mengisinya di GitHub).
6. Release: tambahkan CHANGELOG.md dengan entri v4.0.0 dan catatan perubahan nama. Jangan membuat tag git sendiri; berikan perintahnya di ringkasan.
7. Jalankan `npm run validate` dan `npm test`, perbaiki yang rusak karena rename.

Keluaran akhir: ringkasan perubahan, daftar file yang berubah, hasil validate/test, dan perintah tag/release yang harus kujalankan sendiri.
```

## Task

- [ ] Rename ke `atlas-frontend-design` di semua file dan path
- [ ] Tulis ulang `description` frontmatter agar sempit
- [ ] Tambah LICENSE (MIT), ubah package.json
- [ ] Bersihkan README (hapus "may be private", tambah install pin)
- [ ] Buat `docs/REPO-METADATA.md`
- [ ] Buat `CHANGELOG.md`
- [ ] `npm run validate` dan `npm test` lulus

## Kriteria selesai

- `grep -ri "skills/atlas\b"` tidak menemukan path lama.
- Installer memasang ke `.../skills/atlas-frontend-design`.
- README tidak menyebut repo private dan menyarankan install dengan tag/SHA.
- Validate dan test lulus.
