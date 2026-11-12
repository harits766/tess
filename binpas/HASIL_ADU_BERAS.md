# Hasil adu versi beras: penyetelan, kalibrasi, dan ujian akhir U1 (12 Nov 2026)

Perintah: `python -I binpas/adu_versi.py penyetelan <xlsm> <keluaran> <bps_out>`; 08.01–09.22 UTC (±1 jam 21 menit,
4 CPU), keluar 0. Skala ulangan 50 / 200 / 500. Kode pada commit `6733e12`. File INATRADE sha256 `c667dddba86bdfb6…`
(sama dengan Tahap 0). Kalibrasi dan U1 dijalankan sesudah resep dikunci (commit `f6544a0`); hasil U1 ada di bagian
paling bawah. Angka di bagian resep, gerbang penyetelan, dan keputusan koreksi = skor di blok PENYETELAN.

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

## Catatan (ditulis sebelum U1)
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
- Sesudah U1: `gerbang_U1.csv`, `log_kalibrasi.txt`, `log_ujian.txt`, `U1_SUDAH_JALAN.json`, `U1_sel.csv.xz` (skor per sel ×
  ulangan), `kalibrasi.pkl.xz`, `gerbang_U1_peka_2026saja.csv` (uji kepekaan, bukan hasil resmi).

## Kalibrasi dan ujian akhir U1 (12 Nov 2026, 13.09 UTC; SEKALI JALAN, sudah terpakai)
Resep terkunci pada commit `f6544a0`: I0, isian B, tdist, tanpa bobot, ragam 0,5×, tanpa rekonsiliasi, koreksi konformal
adaptif (γ = 0,005). Kalibrasi 7,5 detik (500 ulangan, Jul–Des 2025), U1 18 detik (500 ulangan), keduanya keluar 0.
Pelebar Q90 dari kalibrasi: wilayah 0,011 (lubang tengah) dan 0,028 (lubang akhir); provinsi 0,046 dan 0,021.

| Ukuran | Provinsi | Wilayah (target utama) | Nasional |
| --- | --- | --- | --- |
| Sel-bulan | 133 (7 provinsi) | 57 | 19 |
| CRPS log (resep / P\*) | 0,043 / 0,244 | 0,016 / 0,116 | 0,011 / 0,048 |
| Perbaikan CRPS | 82% | 86% | 78% |
| MAE median (resep / P\*) | 0,058 / 0,301 | 0,021 / 0,135 | 0,015 / 0,055 |
| Selisih CRPS, rentang 90% bootstrap | −0,228 … −0,178 | −0,134 … −0,075 | −0,043 … −0,031 |
| Bias (resep / P\*) | +0,9% / −11,0% | +0,04% / −4,3% | +0,3% / −1,3% |
| Arah perubahan sama | 93% | 96% | 98% |
| Cakupan rentang 90% | 93,3% | 97,8% | 96,9% |
| Selang Wilson 90% (n efektif) | 87,3–96,6% (82) | 88,1–99,6% (30) | 69,3–99,8% (8) |
| CRPS vs penyetelan (konformal, Jan–Jun 2025) | +13% (0,038 -> 0,043) | −3% (0,0163 -> 0,0158) | −4% (0,0111 -> 0,0107) |
| Lebih baik / konsisten / bias / arah | lolos | lolos | lolos |
| Cakupan | lolos | lolos | belum bisa diputuskan |
| CRPS memburuk ≤ 20% | lolos (lihat catatan) | lolos | lolos |

**Status:** wilayah-bulanan (target utama) LOLOS semua gerbang U1. Provinsi lolos dengan catatan. Nasional: semua lolos
kecuali cakupan "belum bisa diputuskan" (19 sel-bulan). Resep menang atas P\* di 100% ulangan (hanya dilaporkan).

Catatan hasil U1:
- **Acuan "memburuk ≤ 20%" untuk provinsi.** Terhadap resep yang sama di blok penyetelan (konformal, Jan–Jun 2025)
  CRPS provinsi +13%. Terhadap angka seluruh blok penyetelan tanpa koreksi (0,034) selisihnya +28%. `ambang_ujian.md`
  tidak merinci acuannya; yang dipakai di tabel = resep yang sama. Wilayah dan nasional lolos dengan kedua acuan.
- **Sel Nov–Des 2025 ikut dinilai.** Lubang akhir bisa mundur sampai 3 bulan sebelum bulan potong, sehingga soal dengan
  bulan potong Jan–Feb 2026 memuat sel Nov–Des 2025 (blok kalibrasi): 6 dari 57 sel-bulan wilayah, 14 dari 133
  provinsi, 2 dari 19 nasional. Uji kepekaan sesudah hasil (bukan hasil resmi), hanya sel Jan–Sep 2026
  (`python -I binpas/peka_u1.py binpas <keluaran>`): wilayah CRPS 0,0167 vs 0,123 (−86%), cakupan 97,6%
  (87,2–99,6%); provinsi 0,043 vs 0,244, cakupan 94,3%; semua status gerbang sama.
- **Rentang cenderung terlalu lebar** di wilayah (cakupan 97,8% untuk sasaran 90%); masih lolos karena 90% ada di dalam
  selang Wilson.
- Tingkat provinsi hanya mencakup 7 provinsi yang punya ≥ 3 pelapor; "Pulau lain" paling lemah (CRPS 0,021 vs
  Jawa 0,014 dan Sumatera 0,013).
- Arti hasil tidak berubah: yang lolos adalah kemampuan menutup laporan yang bolong secara konsisten, bukan bukti
  mewakili pasar (cakupan volume pedagang beras ±1,5–3%).
- Belum dihitung: skor tingkat perusahaan, agregasi triwulanan, CRPS dalam ton (pendamping).
