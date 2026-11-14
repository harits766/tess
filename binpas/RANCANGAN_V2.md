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
