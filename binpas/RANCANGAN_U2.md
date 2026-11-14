# Ujian keterwakilan (U2) beras terhadap Pola Distribusi BPS: kelayakan, definisi, dan HASIL (14 Nov 2026)

**Status: bagian 6 DIKUNCI (14 Nov 2026, disetujui Bu Fitria lewat pengguna) sebelum isi edisi BPS 2025 dibuka**
(saat dikunci baru metadata dan tautan unduhnya yang diambil). Yang diperiksa di sini hanya edisi 2024 (yang memang tidak disembunyikan) dan data INATRADE.

## 1. Apa isi publikasi BPS sebenarnya
- "Distribusi Perdagangan Komoditas Beras Indonesia 2024" (188 halaman, 34 provinsi) diambil lewat WebAPI BPS.
- Per provinsi tersedia: (a) DAFTAR provinsi asal pembelian dari luar provinsi dan DAFTAR provinsi tujuan penjualan ke
  luar provinsi; (b) persentase arus antarjenis pelaku (produsen, distributor, grosir, eceran, ...); (c) pola utama dan
  MPP. **Tidak ada pangsa per provinsi asal** (berapa persen pembelian datang dari provinsi X).
- Ekstraksi: `python -I binpas/poldis_mitra.py <pdf> <csv>` -> `binpas/data_publik/poldis_beras_2024_mitra.csv`
  (150 tautan berarah asal -> tujuan; 144 di antaranya disebut dari dua sisi). Dicek dengan jumlah mitra yang tercetak
  di halaman peta: cocok kecuali 3 provinsi (selisih 1–2 tautan: Kalimantan Barat, Kalimantan Tengah, NTB).

## 2. Akibatnya untuk ambang yang dikunci
- Gerbang "korelasi peringkat pangsa asal vs Pola Distribusi BPS ≥ 0,6" **tidak bisa dihitung seperti tertulis**, karena
  BPS tidak menerbitkan pangsa asal. Yang bisa dibandingkan hanya ADA/TIDAKNYA tautan antarprovinsi.
- Gerbang "lebih dekat daripada INATRADE mentah dan BPS 2024 apa adanya" masih bisa dijalankan, tetapi "dekat" harus
  didefinisikan untuk data tautan (ada/tidak), bukan pangsa.
- Mengganti definisi gerbang = perubahan ambang. Belum ada hasil 2025 yang dilihat, jadi masih bisa ditetapkan dengan
  sah, tetapi perlu persetujuan Bu Fitria dan di-commit sebelum edisi 2025 dibuka.

## 3. Gambaran INATRADE terhadap edisi 2024 (bukan ujian; `binpas/paw_vs_bps.py`)
| Tahun INATRADE | Perusahaan PAW | Tautan | Provinsi asal | Ada di BPS 2024 (presisi) | Tertimbang volume | Tautan BPS yang tertangkap |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 | 10 | 41 | 6 | 73% | 99% | 20% |
| 2025 | 14 | 54 | 7 | 57% | 93% | 21% |
| 2026 (Jan–Sep) | 20 | 71 | 8 | 54% | 91% | 25% |

- Peluang acak (kepadatan graf BPS) 13%. Jadi tautan INATRADE jauh lebih sering benar daripada acak, dan hampir semua
  volumenya ada di jalur yang juga dicatat BPS.
- Tetapi INATRADE hanya menangkap seperlima sampai seperempat tautan BPS. Arus PAW beras berasal dari 26 perusahaan
  saja, di 6–8 provinsi asal; Jawa Timur, DKI Jakarta, dan Jawa Tengah membentuk ±95% volume 2025–2026. "Asal" di
  INATRADE = provinsi kedudukan perusahaan pengirim, belum tentu asal fisik barang.
- Hanya 5–7 tautan per tahun yang diisi ≥ 3 perusahaan (syarat tampil publik).
- Volume PAW 2024 didominasi satu provinsi asal (72%) yang hampir hilang di 2025: perlu dicek satuannya.

## 4. Usulan definisi U2 (untuk diputuskan; bisa diubah sebelum dikunci)
- **Satuan:** pasangan provinsi berarah asal -> tujuan di antara 34 provinsi cakupan BPS (1.122 pasangan).
- **Jawaban:** daftar tautan edisi BPS 2025 (disembunyikan sampai spesifikasi dikunci).
- **Yang diadu** (masing-masing memberi skor tiap pasangan):
  1. INATRADE mentah: tautan tercatat di INATRADE pada tahun acuan (volume sebagai skor).
  2. BPS 2024 apa adanya: tautan ada di edisi 2024.
  3. INATRADE diperkuat: gabungan BPS 2024 + INATRADE (rekonstruksi jaringan: gravitasi surplus–defisit–jarak, diperbarui
     dengan tautan INATRADE); bobot semu dan kalibrasi pangsa tidak relevan lagi karena tidak ada pangsa BPS.
- **Ukuran "dekat":** average precision (luas kurva presisi–recall) atas 1.122 pasangan; pendamping: F1, presisi,
  recall. Selang 90% lewat bootstrap per provinsi tujuan.
- **Gerbang (usul pengganti):** (i) versi diperkuat lebih baik daripada INATRADE mentah DAN BPS 2024 apa adanya, dengan
  selang selisih tidak mencakup 0; menang tipis -> "belum bisa diputuskan" (aturan lama tetap); (ii) pengganti korelasi
  pangsa asal: korelasi peringkat antara volume keluar per provinsi asal di INATRADE dan jumlah provinsi yang menyebut
  provinsi itu sebagai asal di BPS ≥ 0,6.
- **Perkiraan jujur:** BPS 2024 apa adanya kemungkinan sulit dikalahkan (tautan antarprovinsi cenderung tetap dari tahun
  ke tahun), dan INATRADE hanya menangkap ±20–25% tautan. Hasil yang paling mungkin: "belum lolos" atau "belum bisa
  diputuskan". Nilai tambah INATRADE lebih mungkin di volume dan waktu (bulanan) pada jalur yang ia catat, bukan di
  peta tautan.

## 5. Yang belum diketahui
- Tahun acuan survei tiap edisi (edisi 2024 kemungkinan data 2023; edisi 2025 data 2024) -> menentukan tahun INATRADE
  yang dipakai. INATRADE baru ada sejak Jan 2024 dan pelapor PAW beras 2024 hanya 10 perusahaan.
- Apakah bagian narasi publikasi (berupa gambar, tidak terbaca mesin) menyebut pangsa asal; perlu dibaca manual/OCR.
- BPS "Perdagangan Antar Wilayah" (bila memuat volume antarprovinsi per komoditas) belum dicek sebagai sumber pangsa.

## 6. Definisi U2 beras — DIKUNCI 14 Nov 2026, sebelum edisi 2025 dibuka (skrip `binpas/u2_beras.py`)
Persetujuan Bu Fitria (lewat pengguna, 14 Nov 2026): cek dulu publikasi BPS lain; bila tidak memuat pangsa, gerbang
diganti perbandingan jalur dan dikunci sebelum edisi 2025 dibuka; ujian sekali jalan.
- **Cek sumber lain:** "Perdagangan Antar Wilayah Indonesia 2023" (tahun data 2022) hanya memuat nilai perdagangan
  SEMUA barang antarprovinsi dalam bentuk peta kelas nilai; tidak ada rincian beras. Jadi definisi pengganti dipakai.
- **Satuan:** pasangan berarah asal -> tujuan antarprovinsi yang punya bagian di kedua edisi (2024 dan 2025).
- **Jawaban:** tautan edisi 2025 = gabungan daftar "pembelian dari luar provinsi" dan "penjualan ke luar provinsi",
  diekstrak dengan `binpas/poldis_mitra.py` apa adanya. Sebelum skor dihitung hanya struktur yang dicek (jumlah
  provinsi, jumlah mitra vs angka di halaman peta); bila ekstraksi gagal secara struktur, skrip ekstraksi diperbaiki
  memakai cek struktur saja.
- **INATRADE:** beras tanpa BULOG, baris dengan provinsi tujuan ≠ provinsi perusahaan dan rincian penyaluran > 0, semua
  bulan Jan 2024–Sep 2026 digabung (tahun acuan survei BPS tidak pasti dan pelapor PAW 2024 hanya 10 perusahaan).
  Asal = provinsi kedudukan perusahaan.
- **Yang diadu (skor tiap pasangan):** (1) INATRADE mentah = jumlah perusahaan-bulan yang melaporkan tautan itu;
  (2) BPS 2024 apa adanya = 1 bila tautan ada di edisi 2024; (3) gabungan = BPS 2024 + 0,5 × [tautan ada di INATRADE]
  (urutan: ada di keduanya > BPS saja > INATRADE saja > tidak ada). Rekonstruksi gravitasi, bobot semu, dan kalibrasi
  pangsa tidak diikutkan (butuh data jarak/pangsa dan penyetelan sendiri).
- **Ukuran:** average precision (skor seri dikelompokkan); pendamping: presisi, recall, F1 himpunan tautan; INATRADE per
  tahun dilaporkan sebagai pendamping.
- **Gerbang (i) "lebih dekat":** AP gabungan > AP INATRADE mentah DAN > AP BPS 2024 apa adanya, dengan selang 90%
  bootstrap per provinsi tujuan (2.000 resampel, seed 20261114) dari selisih AP seluruhnya > 0 -> lolos; selisih positif
  tetapi selang mencakup 0 -> "belum bisa diputuskan"; selain itu gagal.
- **Gerbang (ii) pengganti korelasi pangsa asal:** korelasi peringkat (Spearman) antarprovinsi antara volume keluar
  INATRADE per provinsi asal (rincian penyaluran, koreksi satuan aturan Tahap 0) dan jumlah provinsi yang menyebut
  provinsi itu sebagai asal di BPS 2025, ≥ 0,6. Pendamping: versi jumlah provinsi tujuan, dan korelasi BPS 2024 vs 2025.
- Aturan lama tetap: hanya satu tahun pembanding, menang tipis -> "belum bisa diputuskan". U2 menulis
  `U2_SUDAH_JALAN.json` dan menolak jalan kedua.

## 7. HASIL U2 beras (14 Nov 2026, 15.03 UTC; SEKALI JALAN, sudah terpakai) — `hasil_u2_beras/hasil_U2.json`
Definisi commit `4bd139b`; ekstraksi edisi 2025 commit `438c907` (sebelum skor dihitung hanya struktur yang dicek).
- **Ekstraksi edisi 2025:** diagram di separuh provinsi tidak terbaca mesin, tetapi daftar mitra ditulis sebagai kalimat
  ("... pembelian beras dari N provinsi lain yaitu ..."), jadi dipakai `binpas/poldis_mitra_narasi.py`. 38 provinsi,
  226 tautan; 64 dari 64 jumlah mitra cocok dengan angka N yang tertulis; di 16 provinsi yang diagramnya terbaca, 107
  dari 107 tautan diagram juga ada di kalimat. Ditambahkan singkatan (Jabar, Kalsel, ...) dan satu salah ketik
  publikasi ("Jawa Tiimur"); ekstraksi edisi 2024 tidak berubah.
- **Cakupan:** 34 provinsi yang ada di kedua edisi, 1.122 pasangan. Tautan BPS 2024: 150; BPS 2025: 104; yang tetap
  dari 2024 ke 2025: 85. INATRADE: 26 perusahaan, 77 tautan, 9 provinsi asal.

| Versi | Average precision | Tautan | Presisi | Recall | F1 |
| --- | --- | --- | --- | --- | --- |
| Acak (kepadatan) | 0,093 | – | 9% | – | – |
| INATRADE mentah | 0,329 | 77 | 51% | 38% | 0,43 |
| BPS 2024 apa adanya | 0,480 | 150 | 57% | 82% | 0,67 |
| Gabungan (BPS 2024 + INATRADE) | **0,563** | 185 | 50% | 89% | 0,64 |

- **Gerbang (i) "lebih dekat": LOLOS.** Gabungan − BPS 2024 = +0,083 (selang 90% 0,041 … 0,133); gabungan − INATRADE
  mentah = +0,234 (0,167 … 0,300). Kedua selang tidak mencakup 0.
- **Gerbang (ii) pengganti korelasi pangsa asal: GAGAL.** Korelasi peringkat volume keluar INATRADE per provinsi asal vs
  jumlah provinsi yang menyebutnya asal di BPS 2025 = 0,20 (batas 0,6); versi jumlah tujuan 0,20. Pembanding: BPS 2024
  vs BPS 2025 = 0,89.
- INATRADE per tahun (pendamping): AP 0,25 (2024, 10 perusahaan), 0,31 (2025, 14), 0,30 (2026, 20).

Cara membaca:
- Keunggulan gabungan datang dari URUTAN, bukan dari himpunan tautan: tautan BPS 2024 yang juga tercatat di INATRADE
  lebih sering muncul lagi di 2025. Sebagai himpunan, gabungan justru sedikit lebih buruk daripada BPS 2024 saja (F1 0,64
  vs 0,67) karena tautan INATRADE yang tidak ada di BPS menambah tebakan salah.
- INATRADE TIDAK mewakili struktur asal: hanya 9 provinsi asal (kedudukan perusahaan), korelasi 0,20. Gerbang
  keterwakilan tidak lolos.
- Kesimpulan menurut ambang: INATRADE berguna sebagai PENGUAT/penegas peta jalur BPS (gerbang i), tetapi tidak boleh
  diklaim mewakili pola asal perdagangan beras (gerbang ii). Hanya satu tahun pembanding.
- Keterbatasan: edisi 2024 diekstrak dari diagram dan edisi 2025 dari kalimat (cara berbeda; edisi 2024 meleset 1–2
  tautan di 3 provinsi); jumlah tautan BPS turun 150 -> 104 antara edisi, bisa karena perubahan survei/penyajian; empat
  provinsi baru Papua tidak ikut; "asal" INATRADE = kedudukan perusahaan.
