# Serah terima sesi: stok & distribusi bapokting (Dit. Binpas, Kemendag)

Baca file ini dulu di setiap sesi baru. Rincian per bagian ada di `beras_stok/CATATAN_SESI.md`,
`beras_stok/README.md`, `stok_komoditas/README.md`, `binpas/RANCANGAN_INATRADE.md`, `binpas/ambang_ujian.md`.

## Pengguna dan cara kerja
- Harits, Dit. Bina Pasar Dalam Negeri (Binpas) Kemendag; atasan yang sering dibalas lewat WA: Bu Fitria.
- Bahasa Indonesia santai; jawaban ringkas; kalau diminta "chat WA", tulis teks siap tempel.
- Hemat kredit: beri tahu dulu sebelum run panjang (> ±10 menit). Jangan bikin mockup kalau tidak diminta.
- Kunci BPS hanya dari env var `BPS_API_KEY` (jangan ditulis ke file/chat). Pengguna menolak memberi kunci USDA:
  jangan diminta lagi (unduhan bulk CSV USDA tidak butuh kunci). Jangan akali bot-check (tidak boleh spoof
  User-Agent); bps.go.id dan satudata.pertanian.go.id memblokir akses otomatis -> pakai WebAPI BPS.
- Data mentah tidak disimpan di repo. Commit hanya ke branch `claude/bayesian-rice-stock-model-qmunfn`,
  tanpa PR kecuali diminta.
- **Jangan menjalankan atau mengulang run tanpa diminta** (termasuk uji coba kecil). Kalau diminta mengirim sesuatu,
  langsung kirim; jangan diselingi run. Pengguna sempat menghentikan run dan pengiriman file di sesi 6.
- Pengguna ingin bisa menjalankan sendiri di Google Colab (unggah folder ke Drive).
- Bahasa: Indonesia (pengguna kadang menulis Inggris; tetap jawab Indonesia kecuali diminta lain).

## File yang harus diunggah ulang di sesi baru
- `Non_PAW_dari_nol.xlsm` (INATRADE, sheet "2024-2026", semua komoditas, PAW + Non PAW) — wajib.
- `Non_PAW_Gabungan_2024-2026_sd_Sep2026_2.xlsx`, `PAW_September_1.xlsx` (subset, opsional).
- Data BPS/USDA bisa diambil ulang otomatis (perintah di README masing-masing folder).

## Artefak (claude.ai)
| Artefak | Link | Isi |
| --- | --- | --- |
| Monitor Stok Beras (dashboard, 8 halaman) | https://claude.ai/artifact/6Fc8KdEq6vKPtz7feBpEz6 | stok beras, PAW vs Non PAW, uji, prakiraan, metode, kode |
| Monitor Harga Non PAW (dashboard lama) | https://claude.ai/artifact/6Gz4r55DxMahU9KiAp8Nn7 | tab Stok beras + Metodologi |
| Estimasi Stok & Faktor Harga Beras (doc) | https://claude.ai/artifact/SVxGikX6P5haRF9QLhZwur | bagian model Bayesian stok |
| Model Stok Beras: Gambaran Lengkap (doc) | https://claude.ai/artifact/AZFmtTpEQPN8Z4QVrVJahR | penjelasan detail + rujukan |
| Rencana Model Stok 7 Komoditas (doc) | https://claude.ai/artifact/4GD99BQKeAv95DRAfUTKXR | rencana beras, kedelai, pupuk, sapi, kerbau, ayam, telur |
| Tautan Data Stok dan Distribusi 7 Komoditas (doc, dibuat pengguna) | https://claude.ai/artifact/6WTegJt8gPHDsNwzLZBdUX | daftar sumber Bapanas, BPS, BULOG, Kementan |
| Rancangan Metodologi Pelaporan Stok dan Distribusi Beras (doc) | https://claude.ai/artifact/WjvkAe8JC9xDFVG9EwDGvR | rancangan terbaru (lihat bagian 4) |

## 1. Model stok beras (`beras_stok/`) — selesai
- State-space Bayesian per provinsi per bulan, Jul 2022–Sep 2026 (ditampilkan mulai Jan 2024), PyMC + nutpie.
- Stok nasional akhir Sep 2026: 14,2 juta ton (11,3–18,6); BULOG 4,65; susut 7,1% (4,3–9,3); pengali konsumsi 1,41.
- Validasi: holdout SSBAT Des 2022 -> 4,40 (3,43–5,59) vs 4,06. Sensitivitas kendala swasta >= 0: pulau 14,2,
  nasional 14,2, provinsi 16,8. Varian INATRADE: keduanya 14,2; Non PAW 13,4; PAW 16,4; tanpa 15,1.
- Prakiraan (`prakiraan.py`): Okt 13,6 / Nov 12,5 / Des 11,1 juta ton; rawan Des: Papua Tengah, Kepri, Riau, Babel.
- Prediksi model untuk survei SSBAT berikutnya (bila terbit): Des 2024 5,79 (4,89–6,88), Des 2025 6,14 (4,97–7,66).
- Notebook Colab: `beras_stok/colab/01_gabung_data.ipynb` (data mentah -> panel gabungan) dan
  `02_model_stok_beras.ipynb` (model dari panel); masukannya identik dengan `model_stok.py`.
- Temuan penting sesudah model jadi:
  - Publikasi BPS "Distribusi Perdagangan Komoditas Beras" 2024/2025 menyebut produksi beras BPS SUDAH
    memperhitungkan susut/tercecer. Parameter "susut" di model sebaiknya dinamai "selisih tak tercatat"
    (belum diganti di kode/dokumen/dashboard).
  - Konsumsi total BPS 2024 (Susenas + Survei Konsumsi Bahan Pokok 2017) 29,80 juta ton ≈ model 29,79.
  - Tidak ada survei stok total yang terbit untuk 2024–2026; level 2024–2026 belum tervalidasi langsung.
  - INATRADE beras hanya masuk sebagai indeks naik-turun stok pedagang per pulau + stok BULOG (00372).

## 2. Kedelai, fase 1 (`stok_komoditas/`) — model jalan, belum selesai
- Data: impor BPS per pelabuhan (HS 12019000, 2023+), Susenas tahu/tempe (faktor 0,30/0,60), produksi USDA
  (BPS tidak menerbitkan produksi kedelai per provinsi; pangsa provinsi = asumsi), INATRADE kedelai.
- Hasil dasar: stok nasional akhir Sep 2026 ±592 ribu ton (438–815), ±2,4 bulan konsumsi; bias USDA −0,91.
  Holdout USDA Sep 2025: amatan 165, prediksi 100 (67–156) -> sedikit di luar rentang.
  Varian: Non PAW 639, PAW 662 (tidak konvergen, r-hat 1,59), tanpa INATRADE 789, prior psi lebar 674,
  kendala per provinsi 1.923 (tidak konvergen).
- Belum: prakiraan (`stok_komoditas/prakiraan.py` belum dijalankan), perbaikan varian PAW, ekspor dashboard.

## 3. Pelaporan distribusi untuk Dashboard Monitoring Perdagangan Antarwilayah (`binpas/`)
- Konteks: dashboard kolaborasi (BPS, Sardaglog, Dinas, KAD); kartu "Pelaporan Distribusi Bapokting"
  (sumber Dit. Binpas) masih placeholder. Keputusan dengan pengguna:
  - isi HANYA data Binpas (INATRADE), fokus PAW saja (antarprovinsi), tanpa model, tanpa stok,
    tanpa tren bulanan/pola musiman;
  - kartu: masuk (distributor · provinsi asal · komoditas) dan keluar (distributor · provinsi tujuan · komoditas),
    per bulan; klik -> jendela detail per komoditas, filter periode, tab masuk/keluar, volume "XX.XXX Ton";
  - volume (ton) belum ditampilkan: satuan beberapa komoditas tidak wajar (minyak goreng, pupuk Riau jutaan ton);
  - "asal" = provinsi kedudukan perusahaan pengirim, belum tentu asal fisik barang.
- Contoh Riau Sep 2026: masuk 12 distributor, 4 provinsi, 7 komoditas; keluar 1 distributor, 1 provinsi (gula).
  Hitung ulang: `python -I binpas/paw_provinsi.py Non_PAW_dari_nol.xlsm 2026-09 2026-09 RIAU hasil_binpas`.
- Mockup HTML (render jadi PNG dengan Playwright) di `binpas/mockup/`; skor peringkat (nomor 4) memakai angka dummy.
- Usulan skor peringkat: persentil 0–100 dari jumlah distributor, provinsi mitra, komoditas (volume menyusul),
  rata-rata 3 bulan, label "rentan" bila > 60% dari satu asal; peringkat keluar bias ke provinsi kantor pusat (DKI).

## 4. Rancangan pelaporan stok + distribusi beras (doc WjvkAe8JC9xDFVG9EwDGvR)
- Enam perubahan: distribusi jadi keluaran; arus antar provinsi diestimasi (INATRADE PAW + Survei Pola Distribusi
  BPS + Perdagangan Antar Wilayah BPS); konsumsi per provinsi dari BPS; impor bulanan HS 1006; "susut" -> "selisih
  tak tercatat"; target evaluasi baru.
- Data yang perlu diminta (surat dinas/SAPA/PPID): SSBAT 2024–2025 (Bapanas/BPS), stok pelaku usaha Bapanas
  (SAPA), stok BULOG per kanwil, panel harga Bapanas (pengganti terbuka: PIHPS BI hargapangan.id),
  stok Cipinang (Info Pangan Jakarta). Tanpa data itu: bab distribusi jadi tulang punggung, stok untuk tren.
- PDF Poldis beras 2024/2025 bisa diunduh lewat WebAPI BPS (endpoint `view/.../model/publication/.../id/<pub_id>`;
  id 2025 f7bd40cb4779162e89bf2eda, 2024 a688dbac2f627b8b2f5b3b87).

## 5. Sesi 5 (10 Nov 2026): arah kajian + rancangan penguatan INATRADE — diskusi saja, BELUM ADA YANG DIJALANKAN
- Rincian lengkap: `binpas/RANCANGAN_INATRADE.md`; ambang lolos ujian: `binpas/ambang_ujian.md` (dikunci di sesi 6).
- Keputusan: fokus kajian **distribusi**; **harga** jadi sensor utama (PIHPS/SP2KP, data lengkap); **stok dibekukan**
  (model beras tetap untuk tren). Bayesian masih relevan untuk stok, tapi tidak menyelesaikan keterwakilan INATRADE.
- Rancangan model gabungan stok–arus–harga (perluasan `beras_stok/model_stok.py`) dan penguatan INATRADE: identitas
  stok lunak (Stok Awal ≠ Stok Akhir bulan lalu dimodelkan dengan laju susut v), isian lubang (regresi panel, QRF,
  CatBoost, MRP), ragam, bobot pelapor, rekonsiliasi, penggabung, kalibrasi konformal; 79 kombinasi per komoditas,
  penyaringan bertahap 50 -> 200 -> 500 ulangan; blok penyetelan Jan 2024–Jun 2025, kalibrasi Jul–Des 2025,
  ujian akhir Jan–Sep 2026.
- Pengguna diminta mengirim WA usulan ambang ke Bu Fitria; tanggapan beliau dicatat di `binpas/ambang_ujian.md`
  dan file itu di-commit (dikunci) SEBELUM ujian pertama.
- Fakta dari data di sesi ini:
  - BULOG (00372) di INATRADE: rincian penyaluran/pengadaan per provinsi (38 provinsi) sejak Sep 2025, hanya 8 bulan
    (2025-09..12, 2026-05, -06, -08, -09). Stok akhir hanya nasional (perusahaan tercatat di DKI).
  - Stok akhir BULOG Sep 2026 di INATRADE 2,18 juta ton vs publik 4,6 -> laporan Sep kemungkinan belum lengkap.
  - Tidak ada data INATRADE sebelum Jan 2024 (konfirmasi pengguna).
  - Cakupan INATRADE "±0,03%" = jumlah usaha KBLI 46 (perdagangan besar, semua barang) yang melapor (dari pengguna).
    Ini cakupan menurut JUMLAH usaha, bukan volume; cakupan volume per komoditas belum dihitung (usul: Tahap 0).
- Pertanyaan terbuka: ada kolom ciri perusahaan di INATRADE? (79 vs 78 kombinasi); PIHPS/SP2KP bisa diambil
  otomatis?; rujukan jurnal di rancangan belum dicek ulang.
- Lingkungan: `BPS_API_KEY` ada sebagai env var; PyMC/nutpie mungkin perlu dipasang ulang; catboost dan quantile
  forest baru perlu kalau R5/R6 dijalankan.

## 6. Sesi 6 (11 Nov 2026): penjelasan metodologi + AMBANG DIKUNCI — belum ada yang dijalankan
- Bu Fitria menyetujui 4 perbaikan ambang: pembanding P\* (terbaik dari A, A + bobot 3, A + bobot 5) diberi sebaran
  galat empiris; gerbang "lebih baik" juga mensyaratkan MAE median tidak lebih buruk; cakupan memakai selang Wilson
  dengan n efektif (lantai 80%); konsistensi lewat bootstrap per blok bulan. `binpas/ambang_ujian.md` DIKUNCI.
- Koreksi rancangan: bobot presisi tidak dipakai untuk menjumlah ton.
- Usulan terbuka: strata wajib-hitung perusahaan besar (belum diputuskan pengguna); Tahap 0 ditambah ukuran
  konsentrasi (pangsa 5 terbesar, Herfindahl) per komoditas × pulau.
- Perkiraan hasil (tebakan, belum diuji): isian pulau/nasional lumayan mungkin lolos; provinsi kemungkinan
  "belum bisa diputuskan"; keterwakilan (Poldis 2025) dan model gabungan kemungkinan belum lolos.
- Pengguna: **jangan jalankan apa pun dulu** sampai diminta.
- 12 Nov 2026: semua usulan teknis sesi 6 DIKUNCI di `binpas/RANCANGAN_INATRADE.md` bagian 7 (Tahap 0 tambahan:
  cakupan volume, konsentrasi, validasi Harga Jual; target utama arus pulau-bulanan; CRPS skala log; cara adu versi;
  resep dikunci + parameter diperbarui bulanan; konformal adaptif; prior M3; definisi lonjakan/status; U3 waktu nyata;
  jejak keluaran; aturan revisi). **Perlu diberitahukan ke Bu Fitria: CRPS dihitung dalam skala log (persen).**
- Kode untuk Tahap 0, adu versi, dan ujian BELUM ADA; notebook Colab yang ada hanya model stok beras lama.
- 12 Nov 2026: pengguna menyetujui lima angka bagian 7 dan aturan cakupan ±30% (skala bulanan bila cakupan volume per
  pulau bergeser > ±30%); dikunci di bagian 7.2. Pengguna meminta Tahap 0 dijalankan.

## 7. Tahap 0 SUDAH DIJALANKAN (12 Nov 2026) — rincian di `binpas/HASIL_TAHAP0.md`, skrip `binpas/tahap0.py`
- 315 kode perusahaan, 9.479 laporan, 16 komoditas; pelapor beras 91. Patahan Okt–Nov 2024 (pelapor beras 11–15 -> ±50).
- Cakupan volume pedagang beras ±1,5–3% (penyaluran ÷ konsumsi RT); bergeser > 30% antara 2024 dan 2026.
- Sel hampir lengkap sedikit (beras pulau: 10 pada 90%, 16 pada 85% di blok penyetelan); tingkat pulau hanya bermakna
  untuk Jawa dan Sumatera. Identitas dalam bulan 100% tepat; antarbulan beras 76% tepat, 12% ekstrem.
- Aturan 7.2 yang terpicu: ambang sel 85%; strata wajib-hitung; cakupan bulanan sebagai skala M3.
- Pengguna MENYETUJUI (12 Nov 2026): kunci jawaban dari laporan yang ada, definisi aktif +3 bulan, wilayah
  Jawa/Sumatera/Pulau lain, laporan berkepala ganda dijumlah. Dikunci di RANCANGAN bagian 7.8–7.9.
- Belum: korelasi Harga Jual vs PIHPS (data PIHPS belum diambil), cakupan volume komoditas selain beras, cek BULOG.

## 8. Kode adu versi beras — SUDAH DITULIS (12 Nov 2026); penyetelan penuh sudah dijalankan di sesi 7, lihat bagian 9
**Berkas:** `binpas/adu_metode.py` (data, pola hapus, metode isian B, C, R1–R4, R5 QRF, R6a/b/c CatBoost, R7 MRP),
`binpas/adu_versi.py` (soal ujian, skor, tahap 1a–5, penggabung, konformal, gerbang, kalibrasi, U1),
notebook Colab `binpas/colab/03_tahap0.ipynb`, `04_adu_versi_beras.ipynb`, `BACA_DULU.txt`, `buat_paket.sh`.

**Cara jalan** (pustaka: `pip install catboost quantile-forest statsmodels`; data BPS dari `beras_stok/ambil_bps.py`):
```bash
BPS_API_KEY=... python -I beras_stok/ambil_bps.py <cache json> <bps_out>            # ±1 menit
python -I binpas/tahap0.py <xlsm> <hasil_tahap0> <bps_out>                          # ±10 detik
python -I binpas/adu_versi.py coba       <xlsm> <hasil_coba> <bps_out>              # uji kode, ±3–4 menit (4 CPU)
python -I binpas/adu_versi.py penyetelan <xlsm> <hasil_adu> <bps_out>               # BELUM PERNAH; perkiraan 0,5–1,5 jam (4 CPU)
python -I binpas/adu_versi.py kalibrasi  <xlsm> <hasil_adu> <bps_out>               # BELUM PERNAH
python -I binpas/adu_versi.py ujian      <xlsm> <hasil_adu> <bps_out>               # U1, SEKALI JALAN, BELUM PERNAH
```
- `penyetelan` bisa dilanjutkan bila terputus (`status.json` di folder keluaran; tahap selesai dilewati).
- `ujian` menulis `U1_SUDAH_JALAN.json` dan menolak jalan kedua.
- Mode `coba` memakai blok PENYETELAN saja (4/6/8 ulangan; langkah kalibrasi dan ujian versi coba juga di blok
  penyetelan), jadi blok kalibrasi dan ujian belum pernah disentuh.

**Status uji kode:** `coba` dijalankan sekali penuh di sesi 6 dan selesai tanpa error (keluar 0): tahap 1a–5, gerbang,
kalibrasi, dan jalur ujian semuanya berjalan. Angka dari `coba` (8 ulangan) BUKAN hasil dan tidak boleh dikutip.
Pengguna lalu meminta run dihentikan; **yang tertunda = `penyetelan` penuh (lalu `kalibrasi`, lalu `ujian`)**.
Pengguna ingin menjalankannya ulang di sesi baru (atau sendiri di Colab).

**Yang sudah ditetapkan di kode (sesuai RANCANGAN bagian 7.8–7.9):**
- Beras, pedagang tanpa BULOG: 90 perusahaan (Jawa 32, Sumatera 43, Pulau lain 15), 14 strata besar (wajib-hitung).
- Pola hapus dari blok penyetelan: peluang mulai lubang ±7–8% per perusahaan-bulan; peluang belum lapor di bulan
  terakhir 20% (kecil) dan 9% (besar).
- Tiap ulangan: soal lubang tengah + soal lubang akhir (potong di bulan acak); sel dinilai bila populasi ≥ 3.
- Pembanding A, A3, A5 diberi sebaran galat 6 bulan sebelumnya; P* dipilih di tahap 1a.
- Pengaturan baku tahap 1a–1c: R2 (untuk 1a), bobot batas 3, ragam 1×. Tahap 3 dinilai di tingkat nasional.
- Skor: 2 × rata-rata pinball pada 21 kuantil log total; peringkat di tingkat wilayah (target utama).
- CatBoost dilatih pada 7 kuantil lalu diinterpolasi ke 21, `border_count=32` (17× lebih cepat; kedalaman, laju
  belajar, jumlah pohon tetap seperti yang dikunci). Waktu per isian: B/C/R1–R4 < 0,1 detik; R7 ±1,4; R5 ±2;
  R6a ±1; R6b ±2; R6c ±8 detik.
- R7: MixedLM (REML); bila tidak konvergen, cadangan penarikan empiris berurutan.
- Konformal adaptif di U1: kolam = kalibrasi + bulan ujian yang sudah dinilai, γ = 0,005.

**Belum dikerjakan / keterbatasan kode saat ini:**
- Skor tingkat perusahaan (pembanding "sama seperti bulan lalu") dan agregasi triwulanan belum ada.
- Fallback gerbang "turun ke peringkat berikutnya" belum otomatis: gerbang dihitung untuk resep akhir saja.
- Rekonsiliasi MinT hanya nasional–wilayah (provinsi tidak, karena banyak sel provinsi < 3 perusahaan).
- `beras_stok/inatrade_panel.py` masih mengambil nilai terbesar untuk laporan berkepala ganda (keputusan: dijumlah);
  model stok beras lama belum disesuaikan.
- Belum: korelasi Harga Jual vs PIHPS, cakupan volume komoditas selain beras, cek data BULOG, U2, U3 (model gabungan).
- Paket Colab (`inatrade_colab.zip`, ±15 MB, berisi data internal) sempat disusun di sesi 6 tetapi belum terkirim ke
  pengguna; susun ulang dengan `bash binpas/colab/buat_paket.sh <xlsm> <bps_out> <cache json> <hasil_tahap0> <tujuan>`.
- WA ke Bu Fitria soal "CRPS dihitung dalam skala log (persen)" belum dikonfirmasi terkirim.

## 9. Penyetelan penuh beras SUDAH DIJALANKAN (12 Nov 2026, sesi 7) — rincian di `binpas/HASIL_ADU_BERAS.md`
- ±1 jam 21 menit (4 CPU), keluar 0. Keluaran penting di `binpas/hasil_adu_beras/` (resep, status, log, gerbang,
  `tahap4_penuh.pkl.xz`). Blok kalibrasi dan ujian BELUM disentuh; `kalibrasi` dan `ujian` (U1) BELUM dijalankan.
- Resep: I0, isian B (interpolasi/laporan terakhir, semua lubang diisi), tambahan tdist, tanpa bobot pelapor,
  ragam 0,5×, tanpa rekonsiliasi, tanpa penggabung, koreksi "tanpa"; P\* = A5.
- Gerbang penyetelan, wilayah (target utama): CRPS 0,019 vs 0,236 (−92%), konsisten, bias +0,1%, arah 94% -> lolos;
  cakupan 81,0% (Wilson 65,7–90,5%) -> "belum bisa diputuskan". Provinsi: cakupan 77,4% -> gagal. Nasional: cakupan
  80,6% -> belum bisa diputuskan.
- Perlu keputusan pengguna sebelum U1: rentang terlalu sempit (cakupan wilayah Jan–Jun 2025 76% untuk "tanpa",
  92,8% untuk konformal dengan CRPS 0,0163 vs 0,0149); fallback gerbang belum otomatis; seed turunan memakai `hash()`
  teks (tidak persis terulang antarjalan).
- Melanjutkan: salin `binpas/hasil_adu_beras/*` ke folder keluaran, `xz -dk tahap4_penuh.pkl.xz`, lalu `kalibrasi`,
  lalu `ujian`. TANYA DULU sebelum keduanya.

## Langkah berikut yang masih terbuka
0. (SELESAI, lihat bagian 7) Tahap 0 profil kehadiran pelapor INATRADE (Jan 2024–Sep 2026, per komoditas × pulau; panjang lubang;
   bulan hampir lengkap) + ukur selisih Stok Awal vs Stok Akhir bulan lalu. Ringan (menit). Lalu adu versi beras
   (±2–4 jam; tanya dulu).
1. Ganti nama "susut" -> "selisih tak tercatat" di kode, dokumen, dashboard.
2. Validasi satuan semua komoditas INATRADE (bandingkan dengan konsumsi provinsi) sebelum tonase ditampilkan.
3. Ekstrak tabel provinsi Poldis 2024/2025; bandingkan arah PAW INATRADE dengan BPS.
4. Backtest bergulir model beras + pemeriksaan prediktif posterior (±3–4 jam komputasi; tanya dulu).
5. Kedelai: prakiraan, perbaiki varian PAW, holdout USDA.

## Pesan pembuka sesi baru (unggah juga file INATRADE)
```
Lanjutkan pekerjaan di repo harits766/tess, branch claude/bayesian-rice-stock-model-qmunfn.
Baca dulu SERAH_TERIMA.md (terutama "Pengguna dan cara kerja" dan bagian 6–8), lalu binpas/RANCANGAN_INATRADE.md
(bagian 7), binpas/ambang_ujian.md, binpas/HASIL_TAHAP0.md.
File INATRADE terlampir (Non_PAW_dari_nol.xlsm). Ikuti aturan di bagian "Pengguna dan cara kerja".
Baca juga bagian 9 dan binpas/HASIL_ADU_BERAS.md (penyetelan penuh sudah selesai; resep dan gerbang ada di sana).
Tugas sekarang: siapkan lingkungan (pip install catboost quantile-forest statsmodels; ambil data BPS dengan
beras_stok/ambil_bps.py), salin binpas/hasil_adu_beras/* ke folder keluaran dan pulihkan tahap4_penuh.pkl.xz.
TANYA DULU sebelum kalibrasi dan ujian akhir (U1 hanya sekali jalan). Jangan menjalankan hal lain tanpa diminta.
```
