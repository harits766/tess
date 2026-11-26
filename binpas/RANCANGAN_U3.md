# Rancangan U3 versi ringkas: apakah INATRADE membantu meramal harga beras? — DIKUNCI 26 Nov 2026

**Status: DIKUNCI (26 Nov 2026, sesi 10).** Butir a (versi ringkas), b (gerbang BPS 2025 dilepas), c (beras dulu)
disetujui Bu Fitria lewat pengguna ("a gas ringkas, b c disetujui"). Rincian teknis bagian 3–7 dirapikan sebelum
dikunci; belum ada kode U3, belum ada data harga yang diunduh, belum ada yang dijalankan. Tanggal commit berkas ini =
bukti aturan ditetapkan sebelum melihat hasil; sesudah commit ini bagian 1–7 tidak diubah. Dasar: `ambang_ujian.md`
baris "Model gabungan", `RANCANGAN_INATRADE.md` 7.6, `SERAH_TERIMA.md` 15.2–15.4.

## 1. Pertanyaan
Apakah memasukkan data INATRADE membuat ramalan harga beras per provinsi 1 dan 2 bulan ke depan lebih tepat daripada
model yang sama tanpa INATRADE?

## 2. Yang diubah dari rancangan awal (disetujui Bu Fitria 26 Nov 2026)
- **a. Model diganti ke versi ringkas.** Rancangan awal (7.6) = model gabungan stok–arus–harga 38 provinsi (butuh model
  stok tiap titik awal dan perbaikan konvergensi; ±27 kali fit model besar). Diganti model harga per provinsi per bulan
  (bagian 4). Pertanyaan, pembanding, skor, dan cara simulasi waktu nyata TETAP.
- **b. Gerbang "ujian BPS 2025 disembunyikan" dilepas** untuk U3, karena Pola Distribusi BPS 2025 sudah dibuka untuk U2.
- **c. Komoditas: beras saja dulu.** Komoditas lain (daging sapi, ayam ras, telur: harga PIHPS ada; kedelai, kerbau:
  belum ada harga per provinsi; pupuk: harga diatur) dikerjakan terpisah bila diminta.

## 3. Data
- Target: harga eceran **Beras Kualitas Medium I** (PIHPS BI, pasar tradisional, `price_type_id=1`, `com_3`,
  `tipe_laporan=3` bulanan), 34 provinsi PIHPS, Jan 2024–Okt 2026. Diambil sendiri dari `www.bi.go.id/hargapangan`
  (cara di `SERAH_TERIMA.md` 15.3). Empat provinsi baru Papua digabung ke Papua / Papua Barat di sisi INATRADE.
- Peubah lain yang tersedia pada titik awal: musim (bulan), harga bulan-bulan sebelumnya, produksi padi KSA BPS
  (angka potensi untuk bulan yang diramal, karena diterbitkan lebih dulu).
- INATRADE beras (file sha256 `335c7e6e…`, s.d. Okt 2026), pedagang tanpa BULOG.

## 4. Model dan tiga versi
- Satu model, dipasang terpisah untuk h = 1 dan h = 2, dengan kuadrat terkecil biasa (OLS), dipasang ulang di tiap
  titik awal t hanya dengan pasangan (s, s+h) yang s+h ≤ t:
  log harga[p, s+h] − log harga[p, s] = efek provinsi + efek bulan kalender (bulan s+h)
  + β·(log harga[p, s] − log harga[p, s−1]) + γ·(log produksi[p, s+h] − rata-rata log produksi[p] di bulan kalender
  yang sama) + δ·sinyal INATRADE[wilayah(p), s] + galat.
  δ satu angka untuk semua wilayah. Data latih mulai s = Jan 2025 (produksi KSA bulanan BPS ada dan pelapor INATRADE
  beras ≥ 47 sejak Nov 2024).
- Produksi: padi GKG KSA BPS (angka akhir/potensi yang tersedia saat data diambil; keterbatasan: bukan angka yang
  terbit pada titik awal itu; sama untuk ketiga versi). Provinsi BPS 38 digabung ke 34 provinsi PIHPS.
- Sebaran ramalan: angka tengah model + kuantil empiris galat latih per wilayah (Jawa, Sumatera, pulau lain; provinsi
  diberi galat wilayahnya) pada 21 kuantil `adu_metode.KUANTIL`; CRPS dari kuantil (`adu_versi._crps_q`).
- Sinyal INATRADE (satu peubah): log stok akhir pedagang beras (tanpa BULOG) se-wilayah di bulan s dikurangi rata-rata
  log tiga bulan sebelumnya. Provinsi diberi sinyal wilayahnya.
- **V0 tanpa INATRADE** (δ = 0). **V1 INATRADE asli**: jumlah stok akhir dari laporan yang ada. **V2 INATRADE
  diperkuat**: laporan bolong diisi dengan isian resep beras U1 (`hasil_adu_beras/resep.json`: B = interpolasi antara
  dua laporan tetangga untuk lubang tengah, laporan terakhir untuk lubang akhir, semua lubang diisi), diterapkan ke stok
  akhir per perusahaan. Catatan: U1 menguji isian ini pada penyaluran, bukan stok akhir.
- Keterlambatan lapor ditiru: di tiap titik awal t, laporan bulan t dihapus acak per perusahaan dengan pola lubang
  akhir dari adu versi beras (±20% perusahaan kecil, ±9% perusahaan besar), pola sama untuk V1 dan V2; interpolasi V2
  tidak memakai laporan sesudah t. 20 ulangan pola hapus, seed tetap (crc32 nama titik awal); skor = rata-rata ulangan.

## 5. Simulasi waktu nyata dan skor
- Titik awal ujian: **Des 2025 s.d. Agu 2026 (9 titik)**, seperti rancangan awal; h = 2 dari Agu 2026 = Okt 2026.
- Titik awal untuk mencoba kode (boleh dilihat berulang, tidak untuk memilih model/sinyal): Jun–Nov 2025.
- Skor utama: CRPS log harga, rata-rata atas provinsi × titik awal × h × ulangan. Juga dilaporkan per h, MAE median,
  cakupan rentang 90%, dan δ per titik awal.
- Pembanding tambahan (dilaporkan, bukan gerbang): harga bulan lalu; musiman naif (harga bulan lalu × rata-rata
  perubahan bulan kalender yang sama di data latih); keduanya dengan sebaran dari galat latih per wilayah.

## 6. Gerbang
- **INATRADE menyumbang** bila V2 mengalahkan V0 **dan** V1: CRPS lebih kecil, dan rentang 90% bootstrap per titik awal
  (2.000 resampel dengan pengembalian; satu blok = satu titik awal beserta semua provinsi, h, dan ulangan; persentil
  5–95%) dari selisih CRPS (V2 − pembanding) seluruhnya < 0.
- V2 menang tetapi salah satu rentang mencakup 0 -> "belum bisa diputuskan". V2 kalah dari V0 -> "tidak menyumbang":
  INATRADE tetap kartu tercatat untuk harga, model harga memakai V0.
- V1 vs V0 dilaporkan dengan aturan yang sama (apakah INATRADE apa adanya menyumbang), bukan gerbang.
- Selisih tipis -> pilih versi yang lebih sederhana. Semua hasil dilaporkan, termasuk yang gagal.

## 7. Aturan jalan
- Urutan: berkas ini DIKUNCI + commit + push -> ambil PIHPS -> tulis kode -> coba hanya di titik awal Jun–Nov 2025
  -> tanya dulu -> U3 sekali jalan (penjaga `U3_SUDAH_JALAN.json`) -> lapor apa adanya.
- Dilarang: ubah model, sinyal, data latih, titik awal, atau gerbang sesudah melihat hasil titik awal ujian.
- Bila kode tidak bisa mengikuti suatu rincian di atas (mis. data tidak tersedia), perubahan dicatat dan di-commit
  SEBELUM titik awal ujian dijalankan.
- Daya uji kecil (9 titik awal, harga antarprovinsi bergerak bersama); hasil yang paling mungkin "tidak menyumbang"
  atau "belum bisa diputuskan" (cakupan volume INATRADE beras ±1,5–3%).

## 8. Model gabungan 7.6 = saran lanjutan (tidak dipilih; penjelasan ke pengguna 26 Nov 2026, tidak ikut dikunci)
- Bisa, tetapi model gabungan **harus dibangun dari awal**; yang sudah ada hanya model stok (bagian dari 7.6).
- Yang dibutuhkan: (1) model stok diperbaiki sampai r-hat ≤ 1,01, ESS ≥ 400, tanpa divergensi (syarat 7.6; sekarang
  r-hat 1,06) — belum tentu tercapai; (2) bagian arus koridor asal→tujuan (INATRADE + BPS Poldis 2024 sebagai jangkar,
  prior gravitasi) dan persamaan harga level (bulan persediaan, AR(1), SPHP, HET) dalam satu model; (3) data: PIHPS
  (ada), Poldis 2024/MPP (ada), realisasi SPHP per provinsi per bulan (belum dicari; mungkin hanya nasional dari berita),
  SP2KP (tidak bisa diakses: auth + reCAPTCHA -> PIHPS saja sebagai jangkar).
- Komputasi U3: 9 titik awal × 3 versi = 27 kali fit model besar. Model stok saja ±13 menit (4 CPU); model gabungan
  diperkirakan beberapa kali lebih lama (tebakan ±1–3 jam per fit) -> ±1–3 hari komputasi. Tidak cocok di Colab gratis
  (batas ±12 jam, putus); perlu sesi Claude Code (seperti sesi ini) atau mesin sendiri. Perkiraan membangun + menyetel:
  ±1–3 minggu kerja (tebakan).
- Risiko: bila konvergensi tidak tercapai, U3 gabungan "tidak bisa diuji" (dilaporkan apa adanya).
- Jalan tengah yang ditawarkan: (i) U3 ringkas dulu (bagian 1–7), model gabungan jadi saran lanjutan / bahan TA;
  (ii) "semi-gabungan": model stok yang ada dijalankan per titik awal × versi INATRADE (27 × ±13 menit ≈ ±6 jam di
  4 CPU), lalu bulan persediaan dari posteriornya menjadi peubah di model harga bagian 4 (jalur stok -> harga ikut,
  arus dan harga tidak dimodelkan bersama). Konvergensi model stok tetap catatan.
