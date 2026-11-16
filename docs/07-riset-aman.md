# 07. Riset Referensi yang Aman dan Terbatas

## Tujuan
Riset tetap mendalam tapi terkendali: jumlah referensi dibatasi, yang diambil adalah prinsip (bukan aset/kode), dan kegagalan capture diperlakukan jujur.

## Prompt

```
Baca skills/atlas-research/SKILL.md, skills/atlas-research/scripts/capture-references.mjs, dan research/2026-11-13/README.md.

Perbarui aturan riset:
1. Batasi 3-5 referensi per proyek. Tiap referensi dicatat di `research-notes.md` dengan: URL, tanggal akses, tingkat bukti (dilihat langsung / hanya deskripsi), prinsip yang DIADAPTASI (struktur, ritme, hierarki, tipografi), dan yang DITOLAK beserta alasannya.
2. Larangan eksplisit: menyalin aset, kode, copy teks, atau tanda tangan visual khas sebuah situs. Yang boleh diambil hanya prinsip yang diadaptasi ke subjek proyek.
3. Referensi harus beragam: tidak boleh semuanya dari kategori produk yang sama; minimal satu dari luar industri subjek untuk menghindari desain generik.
4. capture-references.mjs: jika terdeteksi cookie gate, halaman tantangan keamanan, atau halaman kosong, tandai referensi sebagai TIDAK TERVERIFIKASI dan jangan hitung sebagai riset selesai. Hormati robots/ToS dasar (jangan crawl; satu halaman per URL), dan tambahkan catatan bahwa capture hanya untuk analisis internal.
5. Jika tool tidak punya akses browsing/jaringan, agen menulis "riset tidak dapat dilakukan" dan meminta pengguna menyediakan referensi, bukan mengarang referensi.
6. Contoh riset bertanggal di research/2026-11-13 diberi label jelas sebagai contoh penanganan bukti, bukan daftar tren.

Tambahkan tes untuk deteksi halaman kosong/gate, dan jalankan npm test.
```

## Task

- [ ] Format `research-notes.md` (adaptasi vs tolak, tingkat bukti)
- [ ] Larangan menyalin aset/kode/copy
- [ ] Aturan keberagaman referensi
- [ ] Deteksi cookie gate/kosong -> TIDAK TERVERIFIKASI
- [ ] Aturan jika tidak ada akses jaringan
- [ ] Tes

## Kriteria selesai

- Referensi dibatasi 3-5 dan tiap satu punya catatan adaptasi/tolak.
- Halaman gate atau kosong tidak dihitung sebagai riset selesai.
