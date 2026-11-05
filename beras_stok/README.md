# Model stok beras total bulanan per provinsi

Estimasi stok beras total (rumah tangga, penggilingan, pedagang, BULOG, horeka) per provinsi per bulan,
Jan 2024 – Sep 2026, dengan model Bayesian state-space (PyMC). Hasil per provinsi dijumlah per pulau.

## Langkah
1. `inatrade_panel.py` — panel laporan distribusi INATRADE per provinsi per bulan dan matriks arus antar provinsi
   (koreksi kg→ton, BULOG dipisah).
2. Data resmi (menunggu akses): produksi KSA per provinsi per bulan, penduduk & konsumsi per kapita, stok BULOG per
   kanwil, harga per provinsi, titik Survei Cadangan Beras.
3. Model: neraca (stok_t = stok_{t-1} + produksi + masuk − keluar − konsumsi − susut) sebagai persamaan keadaan;
   tiap sumber dihubungkan lewat persamaan pengukuran dengan bias dan noise sendiri.

## Menjalankan
```bash
python -I beras_stok/inatrade_panel.py <Non_PAW_dari_nol.xlsm> <folder keluaran>
```
File data mentah tidak disimpan di repo.
