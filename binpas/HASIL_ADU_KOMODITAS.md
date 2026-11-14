# Hasil adu versi komoditas selain beras, blok penyetelan (14 Nov 2026)

Daftar komoditas dari pengguna (14 Nov 2026): daging sapi, daging kerbau, daging ayam ras, telur ayam ras, beras,
kedelai, pupuk. Beras sudah selesai sampai U1 (`HASIL_ADU_BERAS.md`). Berkas ini untuk enam lainnya.
**Kalibrasi dan ujian akhir BELUM dijalankan untuk satu pun dari enam komoditas ini.**

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
