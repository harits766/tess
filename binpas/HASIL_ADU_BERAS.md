# Hasil adu versi beras, blok penyetelan (12 Nov 2026)

Perintah: `python -I binpas/adu_versi.py penyetelan <xlsm> <keluaran> <bps_out>`; 08.01–09.22 UTC (±1 jam 21 menit,
4 CPU), keluar 0. Skala ulangan 50 / 200 / 500. Kode pada commit `6733e12`. File INATRADE sha256 `c667dddba86bdfb6…`
(sama dengan Tahap 0). **Blok kalibrasi (Jul–Des 2025) dan ujian (Jan–Sep 2026) belum disentuh.**
Semua angka di bawah = skor di blok PENYETELAN, bukan skor ujian akhir.

Pustaka: Python 3.13.18, numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, scikit-learn 1.9.1, catboost 1.2.10,
quantile-forest 1.5.0, statsmodels 0.15.0.

## Resep (`hasil_adu_beras/resep.json`)
| Tahap | Pilihan | Catatan |
| --- | --- | --- |
| 1a identitas | I0 (tanpa identitas stok) | CRPS 0,0438; I2 0,0479; I1 0,0500 |
| pembanding P\* | A5 (A + bobot pelapor batas 5) | A5 0,2237; A3 0,2237; A 0,2350 |
| 1b isian | B, semua lubang diisi (batas 99) | B = interpolasi antara dua laporan tetangga (lubang tengah) / laporan terakhir (lubang akhir) |
| 1c tambahan | tdist (galat ekor tebal) | 0,0201 vs tanpa 0,0260; tambahan lain tidak menyumbang |
| 2 bobot × ragam | tanpa bobot pelapor, ragam 0,5× | 0,0192; ragam 1× 0,0204; bobot tidak berpengaruh (semua lubang sudah diisi) |
| 3 rekonsiliasi | tanpa | nasional 0,0133 vs dengan 0,0151 |
| 4 penggabung | tidak dipakai (versi tunggal B) | B 0,0189; juri RF 0,0196; R5 0,0217; pool 0,0277; rata/CRPS 0,0370; R7 0,0911 |
| 5 koreksi akhir | konformal (peringkat 2; peringkat 1 "tanpa" gagal cakupan) | lihat bagian keputusan koreksi |

Di tahap 1b (500 ulangan) R5/QRF sedikit lebih kecil daripada B (0,0230 vs 0,0254); selisihnya tipis (rentang
bootstrap mencakup 0) sehingga aturan "pilih yang lebih sederhana" memilih B. Dengan pengaturan pemenang (tahap 4)
B lebih kecil daripada R5.

## Gerbang di blok penyetelan (`hasil_adu_beras/gerbang_penyetelan.csv`), pembanding P\* = A5
| Ukuran | Provinsi | Wilayah (target utama) | Nasional |
| --- | --- | --- | --- |
| Sel-bulan | 128 | 75 | 33 |
| CRPS log (resep / P\*) | 0,034 / 0,367 | 0,019 / 0,236 | 0,013 / 0,094 |
| Perbaikan CRPS | 91% | 92% | 86% |
| MAE median (resep / P\*) | 0,045 / 0,449 | 0,026 / 0,264 | 0,018 / 0,111 |
| Selisih CRPS, rentang 90% bootstrap | −0,405 … −0,285 | −0,256 … −0,183 | −0,098 … −0,067 |
| Bias (resep / P\*) | −0,1% / −11,9% | +0,1% / −11,9% | −0,1% / −2,1% |
| Arah perubahan sama | 91% | 94% | 93% |
| Cakupan rentang 90% | 77,4% | 81,0% | 80,6% |
| Selang Wilson 90% (n efektif) | 69,8–83,5% (100) | 65,7–90,5% (26) | 59,3–92,2% (14) |
| Lebih baik / konsisten / bias / arah | lolos | lolos | lolos |
| **Cakupan** | **gagal** | **belum bisa diputuskan** | **belum bisa diputuskan** |

"Belum bisa diputuskan" = 0,90 ada di dalam selang dan cakupan ≥ 80%, tetapi setengah lebar selang > 10 poin persen.

## Keputusan koreksi akhir (12 Nov 2026, sebelum kalibrasi dan ujian): KONFORMAL
Gerbang tiap opsi tahap 5 dihitung ulang pada pijakan yang sama (Q dari Jan–Des 2024, dinilai Jan–Jun 2025) dari tabel
tahap 4 yang sudah ada, tanpa isian baru: `python -I binpas/gerbang_opsi5.py binpas <keluaran>` ->
`hasil_adu_beras/gerbang_opsi5.csv`.

| Opsi | CRPS wilayah | Cakupan prov / wil / nas | Gerbang cakupan prov / wil / nas |
| --- | --- | --- | --- |
| tanpa (peringkat 1) | 0,0149 | 75,0% / 76,0% / 78,2% | gagal / gagal / gagal |
| konformal (peringkat 2) | 0,0163 | 91,0% / 92,8% / 95,7% | lolos / lolos / belum bisa diputuskan |
| konformal + bias | 0,0163 | sama | sama |
| konformal + bias + penghalusan | 0,0170 | 88,8% / 90,5% / 91,3% | lolos / lolos / belum bisa diputuskan |

- "Tanpa" gagal gerbang cakupan (< 80%) di ketiga tingkat pada Jan–Jun 2025. Tabel gerbang di atas (81,0% wilayah)
  dinilai di seluruh blok penyetelan, pijakan yang berbeda.
- Sesuai `ambang_ujian.md` (pemenang dipakai hanya jika lolos semua gerbang; kalau tidak, turun ke peringkat
  berikutnya di blok penyetelan), resep turun ke **konformal**. Konformal dan konformal + bias sama (selisih CRPS
  ±10⁻⁸), jadi dipilih yang lebih sederhana. Diputuskan Bu Fitria (lewat pengguna) sebelum blok kalibrasi dan ujian
  dijalankan.
- Konformal, wilayah: perbaikan CRPS 91% terhadap P\*, selisih −0,205 … −0,130, bias +0,1%, arah 94%, cakupan 92,8%
  (Wilson 79,5–97,7%, n efektif 25) -> lolos semua gerbang. Provinsi lolos semua. Nasional: cakupan "belum bisa
  diputuskan" (11 sel-bulan), gerbang lain lolos.
- `resep.json`: `koreksi` = `konformal` (`koreksi_peringkat1` = `tanpa` dicatat). Bagian lain resep tidak berubah.

## Yang perlu diperhatikan sebelum U1
- **Rentang terlalu sempit.** Ragam 0,5× dan koreksi "tanpa" menang karena CRPS, tetapi cakupan di bawah 90%. Di
  Jan–Jun 2025 (periode sesudah patahan pelapor) cakupan wilayah 76,0% untuk "tanpa" dan 92,8% untuk konformal
  (CRPS 0,0149 vs 0,0163). Cakupan wilayah per periode: Jan–Sep 2024 85%, Okt–Des 2024 86%, Jan–Jun 2025 76%;
  per wilayah: Jawa 76%, Sumatera 87%, Pulau lain 81%.
- Fallback "turun ke peringkat berikutnya" belum otomatis di kode; untuk tahap 5 dihitung dengan `gerbang_opsi5.py`.
- `anggota` di `resep.json` dipangkas ke B saja (disetujui pengguna 12 Nov 2026, sebelum kalibrasi dan U1): penggabung
  tidak dipakai, dan R5/R7 hanya menambah waktu (±0,5 jam per langkah) tanpa memengaruhi hasil resep. Daftar semula
  disimpan di `anggota_tahap4`.
- Kunci jawaban = total laporan yang ada di sel; yang dinilai adalah kemampuan menutup laporan yang hilang, bukan
  keterwakilan pasar (cakupan volume pedagang beras tetap ±1,5–3%).
- Seed turunan per metode memakai `hash()` teks, yang diacak Python tiap proses (dan `-I` mengabaikan
  `PYTHONHASHSEED`): pola hapus sama antarversi dan antarjalan, tetapi tarikan acak isian tidak persis terulang.

## Berkas di `hasil_adu_beras/`
- `resep.json`, `status.json`, `log_penyetelan.txt`, `gerbang_penyetelan.csv`, `gerbang_opsi5.csv`.
- `tahap4_penuh.pkl.xz` (±50 MB; skor per sel × ulangan, sel berpopulasi ≥ 3 perusahaan). Dibutuhkan `kalibrasi`
  dan `ujian`. Pulihkan dengan `xz -dk tahap4_penuh.pkl.xz` (sha256 hasil `d49c8432643e3fcc…`).
- Tidak disimpan: `data_beras.pkl` (data per perusahaan; dibuat ulang dari xlsm) dan `tahap1a…5.csv` (±320 MB).

Melanjutkan di sesi baru: salin isi folder ini ke folder keluaran, pulihkan pkl, lalu
`python -I binpas/adu_versi.py kalibrasi <xlsm> <keluaran> <bps_out>` dan `… ujian …` (U1 sekali jalan).
