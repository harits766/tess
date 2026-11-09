# Model stok komoditas (generik) — fase 1: kedelai

Kerangka yang sama dengan model beras (`beras_stok/`): neraca bulanan per provinsi sebagai persamaan keadaan,
setiap sumber data sebagai pengukuran dengan bias dan galat sendiri, diestimasi bersama dengan PyMC (nutpie).
Perbedaan antar komoditas ditulis di `konfigurasi.py`, bukan di kode model. Beras tetap memakai `beras_stok/`
(tingkat A: survei stok dan BULOG) supaya hasil yang sudah divalidasi tidak berubah.

## Langkah (kedelai)

```bash
BPS_API_KEY=... python -I stok_komoditas/siapkan_data.py kedelai Non_PAW_dari_nol.xlsm cache psd_oilseeds.csv data          # semua baris INATRADE
BPS_API_KEY=... python -I stok_komoditas/siapkan_data.py kedelai Non_PAW_dari_nol.xlsm cache psd_oilseeds.csv data_np nonpaw
BPS_API_KEY=... python -I stok_komoditas/siapkan_data.py kedelai Non_PAW_dari_nol.xlsm cache psd_oilseeds.csv data_paw paw
python -I stok_komoditas/model_neraca.py kedelai data hasil                                   # dasar
python -I stok_komoditas/model_neraca.py kedelai data hasil --holdout 2025-09 --label holdout_2025-09
python -I stok_komoditas/model_neraca.py kedelai data_np hasil --label nonpaw
python -I stok_komoditas/model_neraca.py kedelai data_paw hasil --label paw
python -I stok_komoditas/model_neraca.py kedelai data hasil --tanpa inatrade --label tanpa_inatrade
python -I stok_komoditas/model_neraca.py kedelai data hasil --psi 2,2 --label psi_2_2          # sensitivitas prior
python -I stok_komoditas/model_neraca.py kedelai data hasil --positif provinsi --label positif_provinsi
python -I stok_komoditas/prakiraan.py kedelai data hasil                                      # Okt-Des 2026
```
`psd_oilseeds.csv` dari unduhan publik USDA PSD (`psd_oilseeds_csv.zip`, tanpa kunci). Data mentah dan hasil
tidak disimpan di repo.

## Berkas
- `konfigurasi.py` — satu kamus per komoditas: kode HS, peta pelabuhan → provinsi, item Susenas dan faktor setara
  biji, pangsa produksi provinsi (asumsi), jangkar USDA, prior.
- `siapkan_data.py` — panel satu komoditas: impor BPS per pelabuhan (dataexim), konsumsi Susenas per kab/kota
  dibobot penduduk, produksi USDA, laporan INATRADE (koreksi kg→ton, subkomoditas tanpa label diisi dari label
  dominan perusahaan, pilihan baris semua / Non PAW / PAW), indeks dan arus.
- `model_neraca.py` — model tingkat B (lihat docstring untuk persamaannya), ringkasan posterior, holdout.
- `prakiraan.py` — prakiraan 3 bulan dan peluang stok < 1 bulan konsumsi.

## Kedelai: data dan asumsi
- **Impor**: BPS dataexim HS 12019000 per pelabuhan, bulanan sejak Jan 2023 (sebelum 2023 tidak tersedia di
  WebAPI), dicatat di provinsi pelabuhan. Total Okt–Sep sama persis dengan impor USDA per tahun pemasaran.
- **Konsumsi rumah tangga**: Susenas var 2101 (tahu, tempe, kedelai mentah; kg/kapita/minggu per kab/kota)
  × penduduk, dikonversi ke biji dengan faktor tahu 0,30 dan tempe 0,60 (asumsi). Pengali (1+ν) untuk konsumsi
  di luar rumah tangga diestimasi; hanya hasil kali faktor × pengali yang teridentifikasi.
- **Produksi**: BPS tidak lagi menerbitkan produksi kedelai per provinsi dan Satu Data Kementan tidak dapat
  diakses otomatis; dipakai produksi nasional USDA dibagi rata per bulan dan dibagi ke provinsi dengan pangsa
  asumsi di `konfigurasi.py` (±11% pasokan; hanya memengaruhi angka provinsi).
- **Jangkar level**: stok akhir USDA (akhir September) dengan bias diestimasi, dan stok tercatat importir/distributor
  INATRADE yang disesuaikan dengan cakupan pelapor (pangsa pengadaan pelapor terhadap impor, 6 bulan bergulir) dan
  porsi stok di tahap importir ψ. Stok nasional tidak boleh di bawah stok tercatat INATRADE.
- **Kendala**: stok ≥ 0 per pulau. Kendala per provinsi menggelembungkan level (impor bergelombang di provinsi
  pelabuhan, arus antar provinsi dimodelkan rata); diuji sebagai sensitivitas.
- Tingkat B: angka nasional dan pulau bisa dipakai dengan rentangnya; provinsi hanya indikasi.
