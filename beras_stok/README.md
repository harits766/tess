# Model stok beras total bulanan per provinsi

Estimasi stok beras total (rumah tangga, penggilingan, pedagang, BULOG, horeka) per provinsi per bulan,
Jan 2024 – Sep 2026, dengan model Bayesian state-space (PyMC). Hasil per provinsi dijumlah per pulau dan nasional.
Model berjalan dari akhir Juni 2022 supaya tiga titik survei stok (Jun 2022, Des 2022, Des 2023) ikut dipakai.

## Satu file
`stok_beras_satu_file.py` memuat semua kode di bawah plus hasil posterior yang sudah dihitung. `python stok_beras_satu_file.py` langsung menampilkan hasil (hanya pustaka standar, <1 detik); `--excel`, `--csv`, `--grafik` menulis tabel/grafik; `--jalankan-ulang <xlsm>` menjalankan seluruh pipeline.
`stok_beras.ipynb` berisi hal yang sama sebagai notebook, sudah dijalankan (tabel dan grafik tersimpan).

## Langkah

```bash
python -I beras_stok/inatrade_panel.py <Non_PAW_dari_nol.xlsm> <data>     # panel & arus INATRADE
BPS_API_KEY=... python -I beras_stok/ambil_bps.py <cache json> <data>      # produksi, penduduk, konsumsi, harga
python -I beras_stok/model_stok.py <data> <hasil>                          # skenario dasar (kendala per pulau)
python -I beras_stok/model_stok.py <data> <hasil> --holdout 2022-12        # validasi: survei Des 2022 disembunyikan
python -I beras_stok/model_stok.py <data> <hasil> --positif provinsi       # uji sensitivitas
python -I beras_stok/model_stok.py <data> <hasil> --positif nasional       # uji sensitivitas
python -I beras_stok/tabel_excel.py <hasil> <hasil>/stok_beras_posterior.xlsx
python -I beras_stok/diagnostik.py <data> <hasil>                          # korelasi (diagnostik saja)
```
File data mentah dan hasil tidak disimpan di repo. Kunci BPS hanya dibaca dari env var `BPS_API_KEY`.

## Berkas
- `inatrade_panel.py`, `util.py` — laporan INATRADE beras: koreksi kg→ton, BULOG (00372) dipisah, panel per
  provinsi-bulan, matriks arus asal→tujuan.
- `ambil_bps.py` — WebAPI BPS: produksi padi bulanan (var 2506, 2025–2026) dan tahunan (1498, 2022–2024),
  konsumsi beras per kapita Susenas per kab/kota (2094) dibobot penduduk kab/kota (2790), harga beras
  penggilingan (500, 2277).
- `jangkar_publik.csv` — angka publik dengan sumbernya: survei stok, stok BULOG, impor, konsumsi Bapanas, neraca
  Bapanas (neraca hanya pembanding, tidak dipakai untuk fit).
- `model_stok.py` — model (lihat docstring untuk persamaannya), ringkasan posterior, validasi.
- `tabel_excel.py` — tabel Excel posterior (nasional, pulau, provinsi; median dan interval 90% per komponen).
- `diagnostik.py` — korelasi perubahan bulanan tanpa pola musim antara INATRADE dan posterior (diagnostik).

## Inti model
- **Keadaan:** stok_t = stok_{t-1} + produksi×(1−susut) + impor − konsumsi RT×(1+ν) + masuk − keluar + guncangan.
  Produksi = padi GKG BPS × 0,5762. Susut prior 2,5–10%. ν = porsi konsumsi non rumah tangga, prior dari rasio
  konsumsi Bapanas (2,591 juta ton/bulan) terhadap konsumsi Susenas, boleh menyimpang sedikit per tahun.
- **Arus antar provinsi:** provinsi defisit struktural menerima sebesar defisitnya × θ (θ hierarkis ≈ 1); provinsi
  surplus mengirim sebanding surplusnya, mengikuti musim panennya sendiri. Jumlah masuk = jumlah keluar setiap
  bulan. Guncangan provinsi berjumlah nol (arus yang tak termodel, bukan beras baru). Peta asal→tujuan INATRADE
  dipakai untuk pangsa asal, tetapi stok provinsi hanya bergantung pada total masuk dan keluarnya.
- **Komponen:** BULOG nasional laten (acak berjalan log) dengan pangsa provinsi Dirichlet; stok swasta = total −
  BULOG, dibagi ke rumah tangga/penggilingan/pedagang/horeka dengan pangsa dari survei 2022 dan 2023.
- **Pengukuran (bias & noise per sumber):** survei stok total (SCBN BPS Jun 2022; SSBAT Bapanas-BPS Des 2022 dan
  Des 2023), stok BULOG (angka publik; laporan INATRADE 00372), INATRADE pedagang (stok per perusahaan pelapor,
  skala per provinsi diestimasi, Student-t), harga beras penggilingan (perubahan 12 bulan vs perubahan stok).
- **Kendala:** stok swasta tidak negatif, diterapkan per pulau (skenario dasar). Ini pilihan model yang paling
  menentukan level; lihat bagian sensitivitas di dokumen.
