# Revisi resep (versi 2) untuk kedelai, daging kerbau, dan telur ayam ras — aturan DIKUNCI 14 Nov 2026

Disetujui Bu Fitria lewat pengguna (14 Nov 2026): ketiga komoditas diuji ulang bila data sesudah Sep 2026 masuk; resep
versi 2 disiapkan dan dikunci sekarang, sebelum data baru dilihat. Dasar: RANCANGAN_INATRADE.md 7.7 (versi 2 di-commit
sebelum data barunya dilihat dan diuji di bulan-bulan baru; ambang tidak diubah; maksimal 2 revisi per tahun).
Ini revisi pertama untuk ketiga komoditas.

## 1. Telusur sumber bias di U1 (eksploratif, tidak mengubah status) — `python -I <skrip telusur>` atas `U1_sel.csv`
- **Kedelai:** seluruh bias wilayah (+5,0%) berasal dari "Pulau lain": 4 sel-bulan (Feb dan Jun 2026), bias +33% s.d.
  +58%. Di blok ujian wilayah itu hanya punya 1–3 pelapor per bulan dan satu perusahaan memegang 91% volumenya, jadi
  galatnya adalah galat menebak satu perusahaan. Jawa (17 sel-bulan) −0,2% dan Sumatera (17) +0,3%.
- **Daging kerbau:** bias wilayah (+5,7%) berasal dari Sumatera (15 sel-bulan, +18,7%): 2–3 pelapor per bulan, dua
  perusahaan memegang 91%. Galatnya condong ke atas di hampir semua bulan 2026 (median +3% s.d. +15%, ekor kanan
  panjang): resep R4 menebak terlalu tinggi untuk perusahaan yang volumenya turun. Jawa +0,7%, Pulau lain +0,1%.
- **Telur ayam ras:** semua wilayah bersel kecil (Jawa 1–3 pelapor, satu perusahaan 96%; Sumatera 2–5); median galat
  per sel hampir nol tetapi rata-ratanya ditarik beberapa ulangan ekstrem.
- Pola umum: yang gagal adalah sel berisi ≥ 3 pelapor tetapi dikuasai satu–dua perusahaan. Mengeluarkan sel seperti itu
  dari penilaian berarti mengubah spesifikasi ujian (7.8), jadi TIDAK dilakukan di versi 2.

## 2. Aturan versi 2 (ditetapkan sebelum dijalankan)
- Prosedur adu versi SAMA dengan versi 1 (58 kombinasi, tahap 1a–5, gerbang, turun peringkat otomatis antaropsi koreksi,
  lalu `turun_peringkat.py` bila pemenang gagal gerbang wilayah). Ambang, sel yang dinilai, dan skor tidak diubah.
- Yang berubah hanya pembagian waktu (`adu_versi.py ... "<KOMODITAS>" v2`, tersimpan di `blok.json`):
  penyetelan = Jan 2024–Sep 2026 (seluruh data yang sudah terlihat); gerbang penyetelan dinilai di Jan 2025–Sep 2026
  (tahap 5: Q dari Jan–Des 2024); kalibrasi = Jan–Sep 2026; **ujian = bulan-bulan sesudah Sep 2026**.
- Strata besar dan pola hapus dihitung ulang dari blok penyetelan versi 2.
- Yang dikunci adalah RESEP (`resep.json` tiap komoditas). Saat data baru datang: unduh ulang INATRADE, perpanjang
  `tahap0.PER`, hitung kalibrasi dengan data saat itu, lalu `ujian` sekali jalan. Perkiraan kebutuhan: 5–6 bulan baru
  (Okt 2026–Mar 2027) supaya gerbang cakupan bisa diputuskan.
- Bila tidak ada versi yang lolos gerbang wilayah di blok penyetelan versi 2: tidak ada resep versi 2; komoditas tetap
  "tercatat" di tingkat itu dan tidak diuji ulang.

## 3. Resep versi 2 — DIKUNCI 14 Nov 2026 (`binpas/hasil_v2_<komoditas>/resep.json`), belum diuji
Dijalankan dengan aturan bagian 2 (commit `1012302`), ±25 menit. Gerbang di bawah dinilai di Jan 2025–Sep 2026, yaitu
data yang SUDAH TERLIHAT (termasuk periode ujian versi 1). **Ini hasil penyetelan, bukan hasil ujian.** Ujian yang sah
baru bisa dilakukan di bulan-bulan sesudah Sep 2026. (Judul di log masih bertuliskan "Jan-Jun 2025"; untuk versi 2
periodenya Jan 2025–Sep 2026.)

| Komoditas | Resep versi 1 (gagal U1) | Resep versi 2 | Wilayah: sel-bulan | Perbaikan CRPS | Bias | Arah | Cakupan 90% (Wilson) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kedelai | B, tdist, ragam 1×, konformal | **C (pertumbuhan perusahaan sejenis)**, semua lubang, tdist, ragam 1×, tanpa koreksi | 89 | 75% | +2,5% | 97% | 83,4% (72,4–90,6) |
| Daging kerbau | R4, ciri + pola, ragam 0,5×, tanpa koreksi | **B (interpolasi)**, semua lubang, tdist, ragam 0,5×, tanpa koreksi | 113 | 67% | +0,9% | 87% | 85,2% (75,3–91,6) |
| Telur ayam ras | I1, B, tdist, ragam 1×, tanpa koreksi | **R1 (regresi panel)**, semua lubang, ragam 1×, tanpa koreksi | 45 | 84% | +0,3% | 92% | 87,2% (76,1–93,6) |

- Kedelai dan daging kerbau: pemenang adu versi (B dan R1) gagal gerbang wilayah, lalu turun peringkat memilih resep di
  atas (10 dan 11 kandidat lolos dari 42 dan 43). Telur: pemenang langsung lolos di wilayah.
- Ketiganya lolos semua gerbang di tingkat wilayah pada data penyetelan versi 2. Kedelai juga lolos di provinsi dan
  nasional (cakupan nasional belum bisa diputuskan); telur gagal cakupan di provinsi dan bias di nasional.
- Tambahan "luar" yang ikut terpilih di daging kerbau dan telur tidak berpengaruh (tidak ada peubah luar untuk
  komoditas selain beras).
- Bias kedelai +2,5% masih dekat batas 3%: masalah sel "Pulau lain" (satu perusahaan 91%) tidak hilang, hanya mengecil.

## 4. Saat data baru datang
1. Unduh ulang INATRADE (catat tanggal dan hash); perpanjang `tahap0.PER` sampai bulan terakhir.
2. Salin `binpas/hasil_v2_<komoditas>/` ke folder keluaran, pulihkan `tahap4_penuh.pkl.xz`, lalu
   `adu_versi.py kalibrasi ...` dan `adu_versi.py ujian ...` (sekali jalan) dengan argumen `"<KOMODITAS>" v2`.
3. Jangan mengubah `resep.json`. Perkiraan kebutuhan 5–6 bulan baru (Okt 2026–Mar 2027).
