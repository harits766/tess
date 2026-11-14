# Ujian keterwakilan (U2) beras terhadap Pola Distribusi BPS: temuan kelayakan dan USULAN (14 Nov 2026)

**Status: USULAN, BELUM DIKUNCI. U2 belum dijalankan. Isi edisi BPS 2025 BELUM dibuka** (baru metadata dan tautan
unduhnya). Yang diperiksa di sini hanya edisi 2024 (yang memang tidak disembunyikan) dan data INATRADE.

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
