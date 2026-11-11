# Rancangan: distribusi + harga + stok, dan penguatan data INATRADE

Disusun di sesi 5 (10 Nov 2026) lewat diskusi dengan pengguna. **Belum ada yang dijalankan.**
Ambang lolos ujian ada di `ambang_ujian.md` (DIKUNCI 11 Nov 2026, disetujui Bu Fitria).

## 1. Keputusan arah
- **Fokus kajian: distribusi.** Alasannya: data milik Binpas sendiri (INATRADE), sesuai mandat, langsung jadi produk
  (kartu dashboard), dan bisa divalidasi dengan BPS.
- **Harga = sensor utama, pendamping distribusi.** Satu-satunya data yang lengkap, sering, dan mewakili
  (PIHPS BI, SP2KP). Dipakai sebagai hasil yang diukur (disparitas harga) dan sebagai alat baca stok/arus.
- **Stok dibekukan.** Model beras yang ada tetap dipakai untuk tren dan sinyal rawan; tanpa SSBAT 2024–2025 dan
  stok BULOG per kanwil, level 2024–2026 tidak bisa divalidasi. Kerja lanjutan stok dibuka lagi kalau data datang.
- **Bayesian** masih relevan untuk stok (menggabungkan sumber berbias, rentang jujur, prakiraan berupa peluang),
  tapi tidak menyelesaikan masalah keterwakilan INATRADE (±0,03% = jumlah usaha KBLI 46 yang melapor, dari pengguna; cakupan menurut volume belum dihitung).
  Pembaruan posterior memperbaiki galat acak, bukan galat sistematis. Yang menyelesaikan adalah patokan luar (BPS).
- Shrinkage (provinsi -> pulau) hanya untuk meredam noise. Untuk struktur arus, tarik ke matriks BPS, bukan ke pulau.

## 2. Data (publik, tanpa surat)
- Neraca (BPS WebAPI): produksi bulanan var 2506 (2025–2026) dan 1498 (tahunan ≤2024), Susenas var 2094 (beras) /
  2101 (kedelai), penduduk var 2790, impor per pelabuhan (dataexim; HS 1006, 12019000, ...). USDA PSD hanya pembanding.
- Distribusi: Pola Distribusi Perdagangan BPS 2024/2025 (PDF lewat WebAPI; id 2025 f7bd40cb4779162e89bf2eda,
  2024 a688dbac2f627b8b2f5b3b87; berisi provinsi asal pembelian, rantai, MPP), Perdagangan Antar Wilayah BPS (cek
  edisi terbaru), INATRADE (internal), jarak antar ibu kota provinsi.
- Harga: PIHPS BI (harian per provinsi), SP2KP Kemendag, harga penggilingan BPS (var 500/2277), Info Pangan Jakarta
  (Cipinang). Akses otomatis PIHPS/SP2KP belum dicek; cadangan: pengguna mengunggah file.
- Kebijakan/jangkar: HET (Perbadan, Permendag Minyakita), realisasi SPHP (rilis), stok BULOG publik
  (`beras_stok/jangkar_publik.csv`) + INATRADE 00372, SCBN Jun 2022, SSBAT Des 2022/2023.
- Untuk memperluas INATRADE: jumlah usaha perdagangan besar per provinsi (Sensus Ekonomi BPS 2016; 2026 bila terbit).
- Tidak dipakai (perlu surat): SSBAT 2024–2025, stok BULOG per kanwil, stok pelaku usaha Bapanas (SAPA).
- Persiapan: harmonisasi 38 provinsi (pemekaran Papua 2022 dibagi pangsa penduduk), koreksi satuan INATRADE,
  harga harian -> median bulanan.

## 3. Model gabungan stok–arus–harga (state-space Bayesian, perluasan `beras_stok/model_stok.py`)
Indeks: provinsi i, pulau a/b, bulan t. Model sekarang sudah memakai harga penggilingan nasional (`beta_harga`).
```
Neraca      : X[i,t] = X[i,t-1] + Prod + Imp + N[i,t] − k·Kons − r·Prod + ε     (r = "selisih tak tercatat")
              N[i,t] = masuk − keluar (dari F, dibagi ke provinsi dengan pangsa BPS);  Σ_i N[i,t] = 0
Arus pulau  : log F[a,b,t] = log F̄[a,b,tahun] + musim[a,b,bulan] + η[a,b,t],  η ~ AR(1)   (±7×7 koridor)
Alat ukur   : survei stok & BULOG (bias per sumber, seperti sekarang)
              BPS arus     : log BPS[a,b,thn] = log Σ_t F[a,b,t] + e
              INATRADE arus: log Indeks[a,b,t] = log F[a,b,t] − log F[a,b,t−1] + e,  var(e) ∝ 1/jumlah pelapor
              Stok pedagang: log StokINATRADE[pulau,t] = log Swasta[pulau,t] + bias + e  (indeks)
              Bulan persediaan: log Cover[pulau,t] = c + λ·log(X/Kons) + e
              Harga level  : log P[i,t] = α_i + γ_t + β_pulau·log(X[i,t]/Kons[i,t]) + δ·SPHP + u,  u ~ AR(1);
                             harga ≥ HET diperlakukan tersensor
              Selisih harga: log P[b,t] − log P[a,t] − τ_ab = −θ·η[a,b,t] + v   (τ dari MPP Pola Distribusi BPS)
Hierarki    : α, β provinsi -> pulau -> nasional; β prior negatif lemah; pola arus ditarik ke matriks BPS
```
Tahapan: (1) beras nasional/pulau + harga per provinsi; (2) + arus antarpulau dan selisih harga; (3) label per
provinsi; (4) komoditas lain lewat `stok_komoditas/konfigurasi.py` (komoditas mudah rusak: bagian stok dimatikan).
Jalur deskriptif sebelum model: gerbang keterwakilan INATRADE vs BPS; matriks BPS + gravitasi PPML + RAS;
indeks INATRADE berantai dari pelapor yang sama.

## 4. Penguatan data INATRADE
Batas: membuat INATRADE konsisten dengan dirinya sendiri dan patokan BPS; tidak membuktikan pelapor mewakili pasar.
Pembukti langsung hanya survei kecil acak (opsional, di luar analisis).

- **Tahap 0 — persiapan:** koreksi satuan; satukan kode perusahaan/cabang; samakan label subkomoditas; populasi =
  semua yang pernah melapor Jan 2024–Sep 2026 (catat bulan mulai/akhir aktif); **profil kehadiran** (pelapor per
  bulan × komoditas × pulau, panjang lubang, bulan "hampir lengkap" = pelapor ≥ 90% dari yang aktif). Ini langkah
  pertama yang akan dijalankan.
- **Identitas stok (lunak):** Stok Awal[t] tidak dianggap pasti = Stok Akhir[t−1] (bisa ada susut/hilang, pindah
  gudang, opname, salah input). Ukur dulu `selisih = Stok Awal[t] − Stok Akhir[t−1]` (persen nol, besar, tanda,
  ekstrem); pilah tepat / wajar / ekstrem; model `Stok Awal[t] = Stok Akhir[t−1]·(1−v) + gangguan`, v = laju susut
  per komoditas × ukuran. Sama untuk identitas dalam bulan. Laju v dicatat sebagai pembanding "selisih tak tercatat".
- **Isian lubang:** perusahaan yang sudah berhenti tidak diisi; bulan terakhir ditandai "sementara" (revisi).
  Regresi panel: `log vol[i,t] = efek perusahaan + efek kelompok-bulan (= indeks) + sisa AR(1)`; nol -> model dua
  bagian; balik dari log pakai smearing.
- **Ragam:** dari simpangan terhadap perusahaan sejenis / ragam prediksi regresi; lubang tengah σ²·k(h−k)/h, lubang
  akhir σ²·k. Dipakai sebagai bobot presisi, interpolasi berganda (±20 isian, aturan Rubin) untuk hasil turunan tak
  lurus, dan galat tambahan di model. **Angka isian tidak pernah dianggap data asli.**
- **Bobot:** bobot pelapor (aktif ÷ melapor per komoditas × pulau × ukuran, dibatasi 3 atau 5) × (bobot semu dari
  jumlah usaha BPS atau kalibrasi ke pangsa Pola Distribusi, bila lolos). Kalibrasi ke total BPS tidak dipakai
  (bobot ekstrem). **Koreksi sesi 6:** bobot presisi (1/ragam) TIDAK dipakai saat menjumlah ton (membuat total
  kekecilan); hanya untuk mengestimasi indeks/pertumbuhan kelompok, menggabungkan sumber/metode, dan di model.
  Total = Σ laporan asli + Σ isian + (bobot pelapor − 1) × bagian tak terisi; ketidakpastian masuk ke rentang.
  Usulan terbuka (belum diputuskan pengguna): strata wajib-hitung untuk perusahaan besar (kumulatif ±80% volume per
  komoditas × pulau, ditetapkan dari blok penyetelan) tanpa bobot pelapor.
- **Memeras informasi:** panel per perusahaan, rasio (bulan persediaan, pangsa tujuan, margin Harga Jual vs PIHPS),
  pinjam antarkomoditas/antarwaktu, rekonstruksi jaringan, INATRADE sebagai sensor dini, kunci neraca.

### Daftar adu versi (per komoditas, bertahap) — 79 kombinasi
| Tahap | Isi | Kombinasi |
| --- | --- | --- |
| 1a | Identitas: I0 tanpa, I1 keras, I2 lunak | 3 |
| 1b | Isian × panjang lubang (2, 3, 6, semua): B garis lurus, C pertumbuhan sejenis, R1 efek perusahaan + kelompok-bulan, R2 + sisa AR(1), R3 + efek perusahaan ditarik ke kelompok, R4 + musiman (6×4); R5 quantile regression forest (1×4); R6 CatBoost, 3 set pengaturan dikunci (3×4); R7 MRP (1×4) | 44 |
| 1c | Tambahan satu per satu + gabungan: kalender Lebaran + panen, ragam per kelompok, sebaran t, pembanding menurut pola, ciri perusahaan (bila kolomnya ada), prior luar | 7 |
| 2 | Bobot (tanpa, batas 3, batas 5) × ragam (titik, 0,5×, 1×, 2×) | 12 |
| 3 | Rekonsiliasi provinsi–pulau–nasional (tanpa, dengan) | 2 |
| 4 | Penggabung: rata-rata kuantil bobot sama, bobot optimal CRPS (out-of-fold), linear pool, juri RF; anggota dari keluarga berbeda | 4 |
| 5 | Koreksi akhir: tanpa, konformal, konformal + bias, konformal + bias + penghalusan | 4 |
| — | Pembanding: A asli, A + bobot batas 3, A + bobot batas 5 | 3 |

- R5, R6, R7 dan juri RF dicoba di **beras dulu**; kalau tidak menyumbang, komoditas lain cukup 58 kombinasi.
- R7 saat adu versi pakai regresi bertingkat cepat (REML); PyMC penuh hanya untuk pemenang.
- Penyaringan bertahap: semua 50 ulangan -> 10 teratas 200 -> 5 teratas 500 (±6.950 jalan untuk beras).
- Perkiraan kasar: beras ±2–4 jam; komoditas lain ±20–40 menit/komoditas; 7 komoditas ±4–8 jam. **Tanya dulu.**
- Daftar dibekukan di 79. Ide baru setelah melihat hasil diuji di data bulan berikutnya.

### Cara menguji
- Jawaban benar: bulan/kelompok hampir lengkap; laporan dihapus meniru pola bolong nyata; semua versi memakai pola
  hapus yang sama (berpasangan). A (asli) selalu ikut; di tingkat perusahaan pembandingnya "sama seperti bulan lalu".
- Blok waktu: penyetelan Jan 2024–Jun 2025, kalibrasi Jul–Des 2025 (konformal, koreksi bias), ujian akhir
  Jan–Sep 2026 (sekali jalan).
- Ukuran: CRPS (penentu peringkat), MAE, cakupan 90%, bias, arah perubahan, kemulusan. Gerbang di `ambang_ujian.md`;
  pembanding = P\* (terbaik dari A, A + bobot 3, A + bobot 5), diberi sebaran galat empiris.
- Tangga klaim (ditetapkan di awal): provinsi -> pulau -> nasional; bulanan -> triwulanan. Laporkan tingkat terhalus
  yang lolos. Hitung daya uji dulu; kalau kurang, status "belum bisa diputuskan".
- Ujian tambahan bobot semu / kalibrasi pangsa / rekonstruksi jaringan: sembunyikan Pola Distribusi BPS 2025, harus
  lebih dekat daripada INATRADE mentah dan "BPS 2024 apa adanya".
- Model gabungan: INATRADE diperkuat harus mengalahkan "tanpa INATRADE" dan "INATRADE asli".
- Dilarang: ubah ambang setelah lihat hasil, pilih bulan/perusahaan yang mudah, setel di data ujian akhir, pola hapus
  berbeda antarversi, tambah versi terus sampai ada yang lolos.

### Kalau gagal
Semua versi kalah dari A -> pakai A berlabel "tercatat". Bobot semu gagal -> bobot pelapor saja. Cakupan gagal ->
skala ragam disesuaikan, uji di bulan berikutnya. Paket minimum: kartu arus tercatat, matriks BPS tahunan,
harga/disparitas apa adanya, laporan ujian.

## 5. Keluaran
1. Kartu "arus tercatat INATRADE" + tanda cakupan (provinsi, bulanan).
2. Matriks asal–tujuan BPS + peta arus, simpul, provinsi rentan (> 60% dari satu asal) (tahunan).
3. Indeks arus koridor antarpulau dengan rentang 90% (bulanan; bila INATRADE lolos).
4. Stok nasional/pulau dengan rentang; provinsi sebagai indikasi.
5. Status ketat / normal / longgar per provinsi (bila harga lolos).
6. Peluang lonjakan harga 1–2 bulan.
7. Margin distributor (Harga Jual vs eceran).
8. Laporan ujian: semua versi, pemenang dan penyetelannya, skor ujian akhir (bukan skor penyetelan), status gerbang,
   interpretasi dengan batasan ("lebih konsisten, bukan bukti mewakili pasar").
9. Kode, tabel Excel, catatan metodologi. Data per perusahaan tidak ditampilkan; kelompok < 3 perusahaan digabung.

Tidak diklaim: ton per koridor provinsi–provinsi per bulan, ton stok per provinsi, pangsa pasar distributor.
Yang menaikkan batas atas hanya data: perluasan wajib lapor INATRADE, lokasi gudang, SSBAT, stok BULOG per kanwil,
survei kecil acak distributor (100–300, lewat Dinas, tahunan).

## 6. Rujukan (ditulis dari ingatan, BELUM dicek ulang volume/halaman)
- Bias seleksi: Meng (2018) AoAS 12(2); Elliott & Valliant (2017) Stat Sci 32(2); Chen, Li & Wu (2020) JASA 115(532);
  Kim, Park, Chen & Wu (2021) JRSS A 184(3).
- Shrinkage/SAE: Fay & Herriot (1979) JASA 74(366); Efron & Morris (1975) JASA 70(350); Rao & Molina (2015).
- Gravitasi/matriks: Anderson & van Wincoop (2003) AER 93(1); Head & Mayer (2014) Handbook Int. Econ. 4;
  Santos Silva & Tenreyro (2006) REStat 88(4); Bacharach (1970); Squartini dkk. (2018) Physics Reports 757.
- Indeks: ILO/IMF dkk. (2004) CPI Manual.
- State-space/Bayesian: Durbin & Koopman (2012); West & Harrison (1997); Gelman dkk. (2013) BDA3; Gelman & Hill (2007).
- Stok–harga: Deaton & Laroque (1992) REStud 59(1); Williams & Wright (1991); Wright (2011) AEPP 33(1).
- Harga antarwilayah: Baulch (1997) AJAE 79(2); Fackler & Goodwin (2001) Handbook Agric. Econ. 1B; Barrett & Li (2002) AJAE 84(2).
- Bobot/imputasi: Kalton & Flores-Cervantes (2003) JOS 19(2); Deville & Särndal (1992) JASA 87(418);
  de Waal, Pannekoek & Scholtus (2011); Little & Rubin (2019); Rubin (1987); Valliant, Dorfman & Royall (2000);
  Duan (1983) JASA 78(383); Wooldridge (2010).
- MRP: Gelman & Little (1997) Survey Methodology 23(2); Wang, Rothschild, Goel & Gelman (2015) IJF 31(3).
- Pohon/penggabung: Breiman (2001) ML 45(1); Breiman (1996) ML 24(1); Meinshausen (2006) JMLR 7; Stekhoven &
  Bühlmann (2012) Bioinformatics 28(1); Wolpert (1992) Neural Networks 5(2); Prokhorenkova dkk. (2018) NeurIPS;
  Duan dkk. (2020) ICML; Caruana & Niculescu-Mizil (2006) ICML; Grinsztajn dkk. (2022) NeurIPS;
  Gneiting & Ranjan (2013) EJS 7; Smith & Wallis (2009) OBES 71(3); Claeskens dkk. (2016) IJF 32(3);
  Yao dkk. (2018) Bayesian Analysis 13(3); Wickramasuriya dkk. (2019) JASA 114(526); Romano dkk. (2019) NeurIPS.
- Evaluasi: Gneiting & Raftery (2007) JASA 102(477); Hyndman & Koehler (2006) IJF 22(4); Vehtari dkk. (2017)
  Stat Comput 27(5); Vehtari dkk. (2021) Bayesian Analysis 16(2); Gabry dkk. (2019) JRSS A 182(2); Gelman dkk. (2020)
  arXiv:2011.01808; Tashman (2000) IJF 16(4); Cawley & Talbot (2010) JMLR 11; Hastie dkk. (2009); Li dkk. (2018)
  JMLR 18(185); Carroll dkk. (2006); Gelman & Loken (2014) Am. Sci. 102(6); Nosek dkk. (2018) PNAS 115(11);
  Bańbura dkk. (2013) Handbook Econ. Forecasting 2A.
