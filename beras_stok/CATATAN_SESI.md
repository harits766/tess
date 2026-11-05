# Catatan serah-terima: model stok beras

## Target (sudah disepakati)
- Stok beras **total** (rumah tangga + penggilingan + pedagang + BULOG + horeka), **bulanan**, Jan 2024 – Sep 2026.
- Level **provinsi** (model hierarkis), dilaporkan juga **per pulau**.
- Output: (1) bagian baru di dokumen "Estimasi Stok & Faktor Harga Beras"
  https://claude.ai/artifact/SVxGikX6P5haRF9QLhZwur, (2) kode PyMC di folder ini, (3) tabel Excel posterior
  per provinsi per bulan (median, interval 90%, per komponen), (4) tab baru di dashboard "Monitor Harga Non PAW"
  https://claude.ai/artifact/6Gz4r55DxMahU9KiAp8Nn7.

## Metode
- Persamaan keadaan (neraca): stok_t = stok_{t-1} + produksi + impor + masuk antar provinsi − keluar − konsumsi − susut.
- Arus antar provinsi: arah/pangsa dari INATRADE PAW (`arus_penyaluran.csv`, `arus_pengadaan.csv`), besaran
  disesuaikan surplus/defisit provinsi, ketidakpastian lebar.
- Konsumsi: konsumsi per kapita Susenas × penduduk + porsi non rumah tangga.
- Susut: prior 2,5–10%.
- Persamaan pengukuran per sumber (bias & noise sendiri): Survei Cadangan Beras BPS (jangkar level; satu titik
  disembunyikan untuk validasi), stok BULOG (komponen BULOG), INATRADE (indeks perilaku stok pedagang, skala
  diestimasi), harga (sinyal ketatnya pasar).
- Jangan pakai ambang korelasi untuk memutuskan; Bayesian jadi kerangka utama. Korelasi hanya diagnostik, pada
  perubahan yang sudah dibuang pola musimnya.

## Temuan sejauh ini
- 58 dari 1.683 laporan beras dikoreksi kg→ton (perusahaan 00138, 00154, 00056 perlu dikonfirmasi).
- Kode 00372 = BULOG (kantor pusat DKI); stok cocok dengan angka publik, penyalurannya tidak dipakai.
- Pelapor pedagang hanya di 20 provinsi; Jawa Barat cuma 1 bulan, Sulawesi Selatan tidak ada.
- Estimasi kasar stok nasional akhir Sep 2026: 12,7 juta ton (9,9–15,7); neraca Bapanas 17,9 sebagai batas atas.

## Akses data
- BPS: situs diproteksi Cloudflare → pakai WebAPI dengan env var `BPS_API_KEY` (key ditaruh di URL `/key/<KEY>/`).
- Panel harga Bapanas: data dari `api-panelhargav2.badanpangan.go.id` (endpoint `/front/harga-pangan-table-province`,
  `/front/harga-pangan-bulanan-v2`, dll.).
- File input dari pengguna (unggah ulang di session baru): `Non_PAW_dari_nol.xlsm`,
  `Non_PAW_Gabungan_2024-2026_Sep2026.xlsx`.
