# 02. SKILL.md Menjadi Router Pendek dengan Gerbang Fase

## Tujuan
Mengurangi beban konteks tanpa mengurangi kedalaman: `SKILL.md` hanya berisi urutan fase, aturan gerbang, dan petunjuk "baca modul X saat fase Y". Modul dibaca saat fasenya tiba.

## Prompt

```
Baca SKILL.md, semua skills/*/SKILL.md, dan folder references/ di repo ini. Tugasmu: tulis ulang SKILL.md menjadi "router" sekitar 100-150 baris, tanpa menghapus isi modul (isi modul tetap di tempatnya).

Struktur SKILL.md baru:
1. Frontmatter (name, description sempit untuk desain frontend).
2. Satu paragraf: tujuan skill dan prinsip utama (kualitas dipaksa lewat gerbang dan bukti, bukan niat baik).
3. Pilih mode di awal: MODE PENUH (halaman/desain baru, redesign) atau MODE RINGAN (perubahan kecil). Kriteria tiap mode ditulis jelas. Default: PENUH jika ragu.
4. Fase berurutan, tiap fase berisi: tujuan, modul yang wajib dibaca SAAT fase itu, artefak keluaran, dan syarat lolos gerbang.
   - Fase 1 Plan -> artefak `design-brief.md`
   - Fase 2 Research -> artefak `research-notes.md` (referensi, apa yang diambil, apa yang ditolak)
   - Fase 3 Tokens -> artefak `design-tokens.*`
   - Fase 4 Build -> kode memakai token saja
   - Fase 5 Verify -> hasil checker dan screenshot
   - Fase 6 Critique -> laporan critic
5. Aturan berhenti: jangan lanjut ke fase berikutnya sebelum artefak fase sekarang ada dan memenuhi syarat. Jika checker gagal, perbaiki dan jalankan ulang; dilarang mengklaim selesai.
6. Format laporan akhir yang tetap: apa yang diverifikasi (dengan bukti), apa yang belum diverifikasi, keputusan desain dan alasannya.

Gaya penulisan: tiap aturan disertai alasan satu kalimat ("karena X"). Hindari huruf kapital berlebihan dan kata CRITICAL. Pastikan semua modul tetap terjangkau dari router (tidak ada modul yatim).

Setelah selesai, jalankan npm run validate dan perbarui evals/scenarios.md bila ada skenario yang terpengaruh. Laporkan jumlah baris SKILL.md sebelum dan sesudah.
```

## Task

- [ ] Backup isi SKILL.md lama (mis. `docs/archive/SKILL-v4.0.0.md`)
- [ ] Tulis router 100-150 baris
- [ ] Tiap fase punya: modul wajib, artefak, syarat lolos
- [ ] Definisikan MODE PENUH vs RINGAN
- [ ] Pastikan tidak ada modul yatim
- [ ] Validate lulus

## Kriteria selesai

- SKILL.md maksimal sekitar 150 baris.
- Setiap modul dirujuk dari minimal satu fase.
- Ada aturan berhenti dan format laporan akhir.
