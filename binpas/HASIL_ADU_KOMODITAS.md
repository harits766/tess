# Hasil adu versi komoditas selain beras (14 Nov 2026)

Daftar komoditas dari pengguna (14 Nov 2026): daging sapi, daging kerbau, daging ayam ras, telur ayam ras, beras,
kedelai, pupuk. Beras sudah selesai sampai U1 (`HASIL_ADU_BERAS.md`). Berkas ini untuk enam lainnya.
Bagian atas = hasil penyetelan; keputusan lanjutan dan hasil U1 kedelai dan telur ada di bagian paling bawah.

Perintah: `python -I binpas/adu_versi.py penyetelan <xlsm> <keluaran> - "<NAMA KOMODITAS>"`, kode pada commit `fc81529`,
13.30–13.38 UTC (±8 menit total, 4 CPU), skala ulangan 50 / 200 / 500. File INATRADE sama dengan beras.
Semua angka = skor di blok PENYETELAN (gerbang dinilai di Jan–Jun 2025), bukan skor ujian akhir.

## Perubahan kode dibanding run beras (di-commit sebelum run ini)
- 58 kombinasi (tanpa R5, R6, R7, juri RF), sesuai rancangan bagian 4. Semua metode yang tersisa satu keluarga, jadi
  tidak ada penggabung (syarat "anggota dari keluarga berbeda" tidak terpenuhi).
- Seed turunan per metode tetap antarjalan (crc32, bukan `hash()`).
- Sel di luar blok tidak dinilai (di U1 beras sel Nov–Des 2025 ikut dinilai).
- Tahap 5: gerbang tiap opsi koreksi dihitung pada pijakan yang sama (Jan–Jun 2025); bila peringkat 1 gagal gerbang di
  tingkat wilayah, otomatis turun ke opsi koreksi peringkat berikutnya yang lolos (aturan yang sama dengan keputusan
  beras). Turun peringkat hanya antaropsi koreksi, belum antarversi tahap 1–3.
- Tambahan "luar" (peubah luar) tidak punya data untuk komoditas selain beras, jadi tidak berpengaruh.

## Data
| Komoditas | Perusahaan (Jawa / Sumatera / lain) | Strata besar | Pelapor per bulan, 2026 | Catatan data (Tahap 0) |
| --- | --- | --- | --- | --- |
| Kedelai | 73 (42 / 24 / 7) | 9 | 20–26 | satuan wajar |
| Daging sapi | 73 (61 / 5 / 7) | 5 | 40–55 | total volume tidak wajar; 1 perusahaan 82% nasional; identitas antarbulan hanya 35% tepat |
| Daging kerbau | 22 (13 / 4 / 5) | 7 | 12–18 | identitas antarbulan 25% tepat |
| Daging ayam ras | 12 (10 / 2 / 0) | 4 | 3–5 | tidak ada laporan sebelum Okt 2024 |
| Telur ayam ras | 11 (5 / 5 / 1) | 3 | 4–8 | |
| Pupuk | 17 (13 / 2 / 2) | 7 | 2–4 | tidak ada laporan sebelum Okt 2024; total volume tidak wajar |

## Resep dan gerbang di tingkat wilayah (target utama)
| Komoditas | Resep | P\* | Sel-bulan | CRPS resep / P\* | Perbaikan | Bias resep / P\* | Arah | Cakupan 90% (Wilson) | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kedelai | I0, B semua lubang, tdist, ragam 1×, konformal | A3 | 25 | 0,081 / 0,154 | 47% | +3,0% / −5,8% | 96% | 88,6% (74,2–95,5) | lolos; cakupan belum bisa diputuskan |
| Daging sapi | I0, B batas 3, tdist, ragam 0,5×, tanpa koreksi | A3 | 33 | 0,162 / 0,343 | 53% | −5,2% / −17,7% | 88% | 62,8% (48,2–75,4) | **gagal** (bias; cakupan) |
| Daging kerbau | I0, R3, ciri + pola, ragam 0,5×, tanpa koreksi | A5 | 25 | 0,125 / 0,509 | 75% | −7,9% / −28,8% | 92% | 81,5% (65,9–91,0) | **gagal** (bias) |
| Daging ayam ras | (tahap 1–4: I1, B, tdist, ragam titik) | A3 | – | – | – | – | – | – | **tidak bisa diuji** |
| Telur ayam ras | I1, B semua lubang, tdist, ragam 1×, tanpa koreksi | A3 | 6 | 0,028 / 0,370 | 92% | +2,2% / −12,8% | 97% | 89,4% (56,1–98,2) | lolos; cakupan belum bisa diputuskan |
| Pupuk | I0, B semua lubang, ragam 1×, konformal | A3 | 7 | 0,131 / 0,601 | 78% | +4,4% / −40,3% | 88% | 86,8% (46,9–98,0) | **gagal** (bias) |

Semua resep: tanpa bobot pelapor, tanpa rekonsiliasi, tanpa penggabung. B = interpolasi antara dua laporan tetangga
(lubang tengah) / laporan terakhir (lubang akhir); R3 = regresi panel dengan efek perusahaan yang ditarik ke kelompok.
Gerbang "lebih baik" dan "konsisten" lolos di semua komoditas yang bisa diuji.

Rincian:
- **Kedelai.** Koreksi peringkat 1 ("tanpa") gagal cakupan (80,0%, selang tidak memuat 90%) -> turun ke konformal.
  Bias +2,97% tipis di bawah batas 3%. Provinsi (24 sel-bulan): perbaikan 88%, cakupan 95,7%, lolos semua. Nasional
  (11): perbaikan 84%, cakupan belum bisa diputuskan.
- **Daging sapi.** Bias −5,2% (batas 3%) di semua opsi koreksi; dengan konformal cakupan 91% tetapi bias tetap −4,6
  s.d. −5,2%. Provinsi −10,4%, nasional −6,3%. Resep memakai batas lubang 3 tanpa bobot, jadi lubang panjang perusahaan
  kecil tidak tertutup.
- **Daging kerbau.** Bias −7,9% di semua opsi. Tidak ada sel provinsi (tidak ada provinsi dengan ≥ 3 pelapor).
- **Daging ayam ras.** Tidak ada laporan di Jan–Des 2024, sehingga konformal mini tahap 5 tidak punya data setel dan
  langkah itu berhenti (`hasil_adu_daging_ayam/galat_tahap5.txt`). Tidak ada resep dan gerbang.
- **Telur ayam ras.** Lolos semua gerbang, tetapi hanya 6 sel-bulan di wilayah (3 di provinsi, 11 nasional): daya uji
  sangat kecil.
- **Pupuk.** Bias +4,4% di semua opsi; 7 sel-bulan di wilayah; tidak ada sel provinsi.

## Status menurut `ambang_ujian.md`
- Lolos di blok penyetelan -> boleh lanjut ke kalibrasi dan U1: **kedelai, telur ayam ras** (telur dengan daya uji kecil).
- Gagal di blok penyetelan: **daging sapi, daging kerbau, pupuk**. Aturan: turun ke peringkat berikutnya di blok
  penyetelan; bila tidak ada yang lolos, pakai A berlabel "tercatat". Turun peringkat antarversi tahap 1–3 (mis. dengan
  bobot pelapor atau semua lubang diisi) belum dicoba.
- Tidak bisa diuji: **daging ayam ras** -> A "tercatat".

## Berkas
`binpas/hasil_adu_<komoditas>/`: `resep.json`, `status.json`, `log_penyetelan.txt`, `gerbang_penyetelan.csv`,
`gerbang_opsi5.csv`, `komoditas.txt`; untuk kedelai dan telur juga `tahap4_penuh.pkl.xz` (dibutuhkan kalibrasi/ujian;
pulihkan dengan `xz -dk`). Tidak disimpan: data per perusahaan dan CSV per tahap.

## Keputusan Bu Fitria (14 Nov 2026) dan pelaksanaannya
a. kedelai lanjut ke kalibrasi dan U1; b. telur ayam ras ikut diuji; c. daging kerbau dicoba peringkat berikutnya;
d. daging sapi dan pupuk berlabel "tercatat" sampai satuan divalidasi; e. daging ayam ras "tercatat".

### U1 kedelai (13.42 UTC, sekali jalan, sudah terpakai) — resep commit `96f4de9`, kode `fc81529`
| Ukuran | Provinsi | Wilayah (target utama) | Nasional |
| --- | --- | --- | --- |
| Sel-bulan | 43 | 38 | 17 |
| CRPS log (resep / P\*) | 0,037 / 0,275 | 0,052 / 0,318 | 0,010 / 0,093 |
| Perbaikan CRPS | 87% | 84% | 89% |
| Bias (resep / P\*) | −0,4% / −11,6% | **+5,0%** / −19,6% | −0,2% / −1,7% |
| Arah perubahan sama | 91% | 97% | 92% |
| Cakupan 90% (Wilson) | 96,7% (88,5–99,1) | 95,2% (82,4–98,8) | 96,4% (59,4–99,8) |
| CRPS vs penyetelan | −3% | −36% | −29% |
| Status | lolos semua | **gagal gerbang bias** (batas 3%) | lolos; cakupan belum bisa diputuskan |

- Wilayah gagal gerbang bias. Menurut `ambang_ujian.md`: gagal di ujian akhir -> A "tercatat" (tidak turun peringkat
  memakai data ujian).
- Rincian sesudah hasil (bukan dasar keputusan): bias wilayah berasal dari "Pulau lain" (4 sel-bulan, bias +58%,
  CRPS 0,317, cakupan 60%); Jawa −0,2% dan Sumatera +0,3% (masing-masing 17 sel-bulan, CRPS 0,014 dan 0,028).

### U1 telur ayam ras (13.42 UTC, sekali jalan, sudah terpakai)
| Ukuran | Provinsi | Wilayah (target utama) | Nasional |
| --- | --- | --- | --- |
| Sel-bulan | 4 | 17 | 17 |
| CRPS log (resep / P\*) | 0,148 / 0,792 | 0,139 / 0,421 | 0,140 / 0,274 |
| Perbaikan CRPS | 81% | 67% | 49% |
| Bias | +6,4% | +2,5% | −4,9% |
| Arah perubahan sama | 98% | 96% | 95% |
| Cakupan 90% (Wilson) | 58,4% (23,5–86,5) | 80,5% (61,0–91,6) | 76,3% (53,0–90,2) |
| CRPS vs penyetelan | +629% | **+397%** | +52% |
| Status | gagal | **gagal** (memburuk > 20%) | gagal |

- Di wilayah gerbang lebih baik, konsisten, bias, arah lolos dan cakupan "belum bisa diputuskan", tetapi CRPS 5× lebih
  besar daripada di penyetelan (0,139 vs 0,028; penyetelan hanya 6 sel-bulan) -> gagal -> A "tercatat".

### Turun peringkat daging kerbau (blok penyetelan saja) — aturan di `binpas/turun_peringkat.py`, commit `8c65bb5`
- 43 kandidat (beda satu tahap dari pemenang), 500 ulangan, ±3 menit. 9 kandidat lolos semua gerbang wilayah.
- Terpilih: **I0, R4 (regresi panel dengan musim), semua lubang diisi, ciri + pola, tanpa bobot, ragam 0,5×, tanpa
  koreksi.** Wilayah (25 sel-bulan): CRPS 0,147 vs P\* 0,509 (−71%), bias +2,4%, arah 88%, cakupan 80,7%
  (Wilson 65,1–90,4%) -> lolos; cakupan "belum bisa diputuskan". Nasional (11): −59%, bias +0,2%.
- Pemenang semula (R3) CRPS 0,125 tetapi bias −7,9%. Resep semula disimpan di `resep_peringkat1.json`.

### U1 daging kerbau (14 Nov 2026, 13.49 UTC, sekali jalan, sudah terpakai) — disetujui Bu Fitria; resep commit `4ce0f69`
| Ukuran | Provinsi | Wilayah (target utama) | Nasional |
| --- | --- | --- | --- |
| Sel-bulan | 9 | 49 | 17 |
| CRPS log (resep / P\*) | 0,218 / 0,837 | 0,138 / 0,276 | 0,094 / 0,162 |
| Perbaikan CRPS | 74% | 50% | 42% |
| Bias (resep / P\*) | −17,4% / −37,7% | **+5,7%** / −12,3% | +3,0% / −4,8% |
| Arah perubahan sama | 79% | 80% | 88% |
| Cakupan 90% (Wilson) | 96,6% (71,9–99,7) | 85,5% (75,4–91,9) | 82,4% (61,1–93,3) |
| CRPS vs penyetelan | – | −6% | +29% |
| Status | gagal (bias, arah) | **gagal gerbang bias** (batas 3%) | gagal (bias 3,002%; memburuk > 20%) |

- Wilayah: lebih baik, konsisten, cakupan, arah lolos; bias +5,7% gagal -> A "tercatat".
- Rincian sesudah hasil (bukan dasar keputusan): bias berasal dari Sumatera (15 sel-bulan, +18,7%); Jawa +0,7% dan
  Pulau lain +0,1%.

### Keputusan lanjutan Bu Fitria (14 Nov 2026)
1. U1 daging kerbau dijalankan (hasil di atas). 2. Kedelai: wilayah berlabel "tercatat"; provinsi yang lolos tetap
dilaporkan dengan catatan (tangga klaim); perbaikan "Pulau lain" hanya boleh diuji di data bulan berikutnya.
3. Telur ayam ras "tercatat", ditinjau lagi bila pelapor bertambah.

### Status akhir per komoditas (14 Nov 2026)
| Komoditas | Status |
| --- | --- |
| Beras | wilayah lolos U1; provinsi lolos dengan catatan; nasional cakupan belum bisa diputuskan |
| Kedelai | wilayah gagal U1 (bias) -> "tercatat"; provinsi lolos U1, dilaporkan dengan catatan |
| Daging kerbau | gagal U1 (bias) -> "tercatat" |
| Telur ayam ras | gagal U1 -> "tercatat" |
| Daging sapi, pupuk | "tercatat" sampai satuan divalidasi (gagal bias di penyetelan) |
| Daging ayam ras | "tercatat" (tidak bisa diuji) |
