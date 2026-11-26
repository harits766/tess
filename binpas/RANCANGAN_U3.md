# Rancangan U3 versi ringkas: apakah INATRADE membantu meramal harga beras? — USULAN, BELUM DISETUJUI, BELUM DIKUNCI

Status: draf 26 Nov 2026 (sesi 10), dikirim ke Bu Fitria lewat WA (butir a–c). Belum ada kode U3, belum ada data harga
yang diunduh, belum ada yang dijalankan. Sesudah disetujui: berkas ini diberi status DIKUNCI, di-commit + push, baru
kode ditulis. Dasar: `ambang_ujian.md` baris "Model gabungan", `RANCANGAN_INATRADE.md` 7.6, `SERAH_TERIMA.md` 15.2–15.4.

## 1. Pertanyaan
Apakah memasukkan data INATRADE membuat ramalan harga beras per provinsi 1 dan 2 bulan ke depan lebih tepat daripada
model yang sama tanpa INATRADE?

## 2. Yang diubah dari rancangan awal (perlu persetujuan)
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
- Model (sama untuk ketiga versi): untuk tiap provinsi p, titik awal t, jarak h ∈ {1, 2}:
  log harga[p, t+h] − log harga[p, t] = efek provinsi + efek bulan kalender + β·(log harga[p, t] − log harga[p, t−1])
  + γ·(log produksi[p, t+h] − rata-rata log produksi bulan yang sama) + δ·sinyal INATRADE[wilayah(p), t] + galat.
  Galat Student-t dengan skala per wilayah; rentang dari sebaran galat. Dipasang ulang di tiap titik awal hanya dengan
  data sampai t.
- Sinyal INATRADE (satu peubah, dikunci di sini): perubahan log stok akhir pedagang per wilayah (Jawa, Sumatera, pulau
  lain) bulan t dibanding rata-rata 3 bulan sebelumnya. Provinsi diberi sinyal wilayahnya.
- **V0 tanpa INATRADE** (δ = 0). **V1 INATRADE asli** (jumlah laporan yang ada). **V2 INATRADE diperkuat** (laporan bolong
  ditambal dengan resep beras yang lolos U1, `hasil_adu_beras/resep.json`).
- Laporan INATRADE bulan t dibuat tak lengkap meniru keterlambatan (pola lubang akhir dari blok penyetelan: ±20%
  perusahaan kecil, ±9% perusahaan besar belum lapor), sama untuk V1 dan V2.

## 5. Simulasi waktu nyata dan skor
- Titik awal ujian: **Des 2025 s.d. Agu 2026 (9 titik)**, seperti rancangan awal; h = 2 dari Agu 2026 = Okt 2026.
- Titik awal untuk mencoba kode dan menyetel (boleh dilihat berulang): Jun–Nov 2025.
- Skor: CRPS log harga, dirata-rata atas provinsi × titik awal × h. Juga dilaporkan per h, MAE median, cakupan
  rentang 90%.
- Pembanding tambahan (dilaporkan, bukan gerbang): harga bulan lalu; musiman naif.

## 6. Gerbang
- **INATRADE menyumbang** bila V2 (dan dilaporkan juga V1) mengalahkan V0 **dan** V1: CRPS lebih kecil, dan rentang 90%
  bootstrap per titik awal (2.000 resampel, satu blok = satu titik awal beserta semua provinsi dan h) dari selisih CRPS
  seluruhnya < 0.
- Menang tetapi rentang mencakup 0 -> "belum bisa diputuskan". Kalah -> "tidak menyumbang": INATRADE tetap kartu
  tercatat untuk harga, model harga memakai V0.
- Selisih tipis -> pilih versi yang lebih sederhana. Semua hasil dilaporkan, termasuk yang gagal.

## 7. Aturan jalan
- Urutan: berkas ini disetujui -> DIKUNCI + commit + push -> ambil PIHPS -> tulis kode -> coba hanya di titik awal
  Jun–Nov 2025 -> tanya dulu -> U3 sekali jalan (penjaga `U3_SUDAH_JALAN.json`) -> lapor apa adanya.
- Dilarang: ubah model, sinyal, titik awal, atau gerbang sesudah melihat hasil titik awal ujian.
- Daya uji kecil (9 titik awal, harga antarprovinsi bergerak bersama); hasil yang paling mungkin "tidak menyumbang"
  atau "belum bisa diputuskan" (cakupan volume INATRADE beras ±1,5–3%).
