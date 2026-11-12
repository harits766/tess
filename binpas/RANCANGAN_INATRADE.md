# Rancangan: distribusi + harga + stok, dan penguatan data INATRADE

Disusun di sesi 5 (10 Nov 2026) lewat diskusi dengan pengguna. **Belum ada yang dijalankan.**
Ambang lolos ujian ada di `ambang_ujian.md` (DIKUNCI 11 Nov 2026, disetujui Bu Fitria).
Spesifikasi teknis tambahan yang dikunci sebelum ujian ada di **bagian 7** (sesi 6, 12 Nov 2026); bila bertentangan
dengan bagian 3–5, bagian 7 yang berlaku.

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

## 7. Spesifikasi tambahan, DIKUNCI sebelum ujian (sesi 6, 12 Nov 2026)
Disepakati dengan pengguna lewat diskusi; belum ada yang dijalankan saat bagian ini di-commit. Butir yang ditandai
"sesudah Tahap 0" diputuskan memakai profil data saja (bukan kinerja metode), sebelum ujian pertama.

### 7.1 Tahap 0 (tambahan)
- Unduh ulang INATRADE terbaru sebelum mulai (laporan telat mengurangi lubang); catat tanggal unduhan dan hash file.
- Konsentrasi per komoditas × pulau: pangsa 5 terbesar, Herfindahl.
- Cakupan volume per komoditas × pulau × bulan: pengadaan pelapor ÷ (produksi + impor BPS), penyaluran pelapor ÷
  konsumsi BPS; BULOG dipisah. (Angka "0,03%" = jumlah usaha KBLI 46 semua barang yang melapor, bukan volume.)
- Validasi Harga Jual INATRADE: satuan, pisah kualitas (label subkomoditas), korelasi perubahan bulanan dengan PIHPS
  di provinsi yang sama.

### 7.2 Keputusan sesudah Tahap 0 (aturan ditetapkan sekarang)
- Sel hampir lengkap: ≥ 90% pelapor aktif melapor. Bila di blok penyetelan tingkat pulau ada < 30 sel-bulan per
  komoditas, ambang diturunkan ke 85% (sekali, untuk semua versi).
- Strata wajib-hitung: dipakai bila pangsa 5 terbesar ≥ 50% di mayoritas pulau untuk komoditas itu. Isinya:
  perusahaan yang kumulatif membentuk ±80% volume per komoditas × pulau (ditetapkan dari blok penyetelan), tanpa
  bobot pelapor, isian dari riwayat sendiri (R2/R3 tanpa tarikan ke kelompok).
- Urutan komoditas diuji: menurut cakupan volume dan jumlah sel hampir lengkap (beras tetap pertama).
- Varian rantai harga (harga distributor) di M3: hanya bila validasi Harga Jual lolos (satuan wajar dan korelasi
  perubahan bulanan dengan PIHPS ≥ 0,5); diputuskan sebelum U3.
- Skala INATRADE di M3: tetap per pulau (a_pulau) secara baku. Bila cakupan volume per pulau bergeser > ±30% antara
  2024 dan 2026, cakupan volume bulanan dipakai sebagai skala (seperti model kedelai).
- Angka-angka di 7.2 dan 7.5 (30 sel-bulan, pangsa 5 terbesar ≥ 50%, korelasi ≥ 0,5, γ = 0,005, revisi maks 2/tahun)
  dan aturan ±30% di atas disetujui pengguna 12 Nov 2026, sebelum Tahap 0 dijalankan.

### 7.3 Target dan skor
- Target UTAMA: indeks penyaluran/arus, tingkat pulau-bulanan. Provinsi dan stok = sekunder/eksploratif (tangga klaim
  tetap berlaku untuk pelaporan).
- CRPS dihitung dalam **skala log** (galat relatif), bobot sama per sel-bulan (tiap ulangan berbobot 1/R);
  CRPS dalam ton dilaporkan sebagai pendamping. CRPS dari kuantil = 2 × rata-rata pinball loss.
  (Definisi teknis pelengkap ambang; perlu diberitahukan ke Bu Fitria.)
- Selain per komoditas, keputusan "metode bekerja" boleh memakai skor gabungan antarkomoditas bila sel per komoditas
  kurang; hasil per komoditas tetap dilaporkan.
- Bobot presisi tidak dipakai untuk menjumlah ton (lihat bagian 4).

### 7.4 Blok penyetelan (cara adu versi)
- Pola hapus dibuat dari profil kehadiran blok penyetelan saja (peluang mulai lubang dan sebaran panjang lubang per
  ukuran × PAW/Non PAW × bulan).
- Dua jenis lubang buatan: tengah (laporan sesudah lubang terlihat) dan akhir (data dipotong di bulan t).
- Setiap ulangan: semua versi + pembanding menerima data yang sama tanpa nilai yang dihapus; model dilatih ulang
  hanya dari data tersisa.
- Penyaringan per tahap: semua pilihan × 50 ulangan → 10 teratas × 200 → 5 teratas × 500; tahap dengan ≤ 5 pilihan
  langsung 500.
- "Selisih tipis" = rentang 90% bootstrap per blok bulan dari selisih CRPS mencakup 0 → pilih versi lebih sederhana.
- Penggabung (bobot CRPS, juri RF): bobot dipelajari out-of-fold per blok bulan.
- Konformal mini untuk memilih koreksi di tahap 5: Q dan bias dari Jan–Des 2024, dinilai di Jan–Jun 2025.
- R6 CatBoost, 3 set dikunci: (kedalaman 4, laju 0,05, 500 pohon), (6; 0,05; 1.000), (8; 0,03; 1.500); keluaran
  MultiQuantile; fitur lubang akhir tidak memakai laporan sesudah lubang.
- Seed acak dan versi pustaka dicatat.

### 7.5 Pemenang, kalibrasi, dan ujian akhir
- Yang dikunci adalah RESEP (identitas, isian, tambahan, bobot, ragam, rekonsiliasi, penggabung, jenis koreksi);
  parameter diestimasi ulang tiap bulan dengan data sampai bulan itu (nilai yang dihapus tetap tidak terlihat).
- Konformal resmi: skor s = max(log q_lo − log y, log y − log q_hi); n = jumlah sel-bulan; Q = kuantil
  ⌈(n+1)·tingkat⌉/n; rentang [q_lo·e^(−Q), q_hi·e^(Q)]; dihitung per tingkat (provinsi/pulau/nasional) × jenis lubang
  (tengah/akhir), kelompok < 20 sel-bulan memakai Q kelompok induk; di 4 tingkat rentang (50/80/90/95%), kuantil yang
  tumpang-tindih diurutkan ulang.
- Koreksi bias = median(log ŷ − log y), diterapkan sebelum skor konformal. Penghalusan = rata-rata bergerak 3 bulan
  pada lebar rentang (log), titik tengah tidak diubah.
- Awal Q dan bias dari blok kalibrasi Jul–Des 2025; selama U1 diperbarui bergulir tiap bulan (adaptive conformal,
  Gibbs & Candès 2021) dengan aturan tetap: γ = 0,005, memakai sel-bulan yang sudah selesai dinilai.
- Sel U1/U2/U3 dijalankan sekali; waktu jalan dan hasil dicatat.

### 7.6 Model gabungan (M3)
- Konvergensi: r-hat ≤ 1,01, ESS ≥ 400, tanpa divergensi (model beras sekarang r-hat 1,06 -> diperbaiki).
- Selisih harga antarprovinsi TIDAK diberi likelihood terpisah (data eceran terhitung dua kali); pengaruh arus masuk
  ke persamaan harga level: − θ_masuk·(arus masuk di atas biasa) + θ_keluar·(arus keluar di atas biasa); τ dari MPP
  Poldis sebagai prior untuk (α_b − α_a).
- Harga distributor (Harga Jual INATRADE) tidak masuk likelihood utama (tingkat berbeda, kualitas belum tervalidasi);
  dipakai untuk margin = log PIHPS eceran − log Harga Jual (sinyal; > persentil 95 = "perlu dicek").
- Prior (lemah): log F̄[a,b] ~ N(log gravitasi-naif, 1,5) (F_naif ∝ surplus_a × defisit_b ÷ jarak); σ_ω ~ HN(0,2);
  musim ~ N(κ·musim panen asal, σ_m), κ ~ N(1; 0,3), σ_m ~ HN(0,1); η: ρ ~ Beta(4,2), σ_η ~ HN(0,2);
  α hierarki prov→pulau→nas, α_nas ~ N(log median harga; 0,3), τ ~ HN(0,1); γ jalan acak σ_γ ~ HN(0,02);
  β_nas ~ N(−0,1; 0,1), β_pulau ~ N(β_nas, 0,05); δ ~ N(0; 0,1) (SPHP distandarkan); u: ρ_u ~ Beta(5,2),
  σ_u ~ HN(0,03); θ ~ HN(0,5); bias SP2KP ~ N(0; 0,05), PIHPS jangkar; σ_obs ~ HN(0,02); bulan persediaan
  c ~ N(0,1), λ ~ N(1; 0,3), σ_c ~ HN(0,3); INATRADE arus σ_I ~ HN(0,5); BPS arus jangkar tanpa bias,
  σ_BPS ~ HN(0,3). Prior model beras yang ada dipertahankan.
- Prior predictive wajar bila: stok nasional 95% di ±3–40 juta ton; harga 0,5–2× teramati; arus koridor ≤ produksi;
  stok +10% → harga 0 s.d. −3%.
- Komponen Bayesian lain (untuk pemenang): R3/R7 penuh, 20 isian = tarikan posterior predictive; I2 = campuran
  tepat/wajar/ekstrem, logit v ~ N(μ_v, τ_v), μ_v ~ N(logit 0,02; 1), τ_v ~ HN(0,5), σ_ε ~ HN(0,1),
  σ_besar ~ HN(1), π ~ Dirichlet(1,1,1).
- Harga: target beras medium eceran per provinsi (median bulanan dari harian); prakiraan h = 1, 2 dengan simulasi
  maju dari posterior (produksi = angka potensi KSA, impor rata-rata/rencana, SPHP rencana atau 0).
- Peluang lonjakan = P(harga t+h naik > 5%) dan P(harga t+h > HET). Status ketat bila P(bulan persediaan <
  persentil 25 historis provinsi) ≥ 60%, longgar bila P(> persentil 75) ≥ 60%, selain itu normal.
- U3 simulasi waktu nyata: titik awal bergulir Des 2025–Agu 2026, hanya data sampai titik awal, laporan INATRADE
  bulan titik awal dibuat tak lengkap meniru keterlambatan (pola lubang akhir); CRPS log harga. Pembanding tambahan
  (dilaporkan, bukan gerbang): harga bulan lalu, musiman naif. Gagal U3 -> model tanpa INATRADE; INATRADE cukup
  jadi kartu tercatat.

### 7.7 Keluaran, jejak, dan revisi
- Setiap angka keluaran menyimpan: komposisi asli/isian/bobot, metode isian, status sementara/final, Q konformal,
  versi data (tanggal unduh, hash), commit kode, seed. Tabel internal kontribusi per perusahaan (volume, ragam);
  publik: kelompok < 3 perusahaan digabung.
- Label rekomendasi: "sinyal untuk prioritas pemantauan, bukan ukuran dampak kebijakan"; tidak ada klaim sebab-akibat
  SPHP, dosis, atau tindakan ke perusahaan berdasar angka isian.
- Revisi sesudah hasil keluar: hasil versi 1 tetap dilaporkan; versi 2 di-commit sebelum data barunya dilihat dan diuji
  di bulan-bulan baru (atau komoditas yang hasil ujiannya belum dilihat, bukti lebih lemah); ambang tidak ikut diubah;
  maksimal 2 revisi per tahun; perbaikan bug objektif boleh dijalankan ulang dengan hasil sebelum/sesudah dilaporkan.

### 7.8 Keputusan sesudah Tahap 0 (disetujui pengguna 12 Nov 2026, sebelum adu versi dijalankan)
Berdasarkan profil data di `HASIL_TAHAP0.md`, bukan kinerja metode.
- **Kunci jawaban ujian = laporan yang memang ada.** Populasi sel pada bulan t = perusahaan yang melapor di bulan t;
  sebagian dihapus; target = total laporan asli sel itu. Sel hampir lengkap tidak lagi menjadi syarat (hanya dilaporkan).
  Sel yang dinilai: sel-bulan dengan ≥ 1 laporan terhapus dan ≥ 3 perusahaan dalam populasi.
- **Definisi aktif:** bulan pertama lapor s.d. 3 bulan sesudah laporan terakhir (dibatasi akhir data).
- **Wilayah:** Jawa, Sumatera, dan "Pulau lain" (digabung). Tingkat: provinsi, wilayah, nasional.
- **Laporan berkepala ganda dijumlah** (satu kode dapat memuat beberapa unit usaha).
- Otomatis dari 7.2: ambang sel hampir lengkap 85% (hanya untuk pelaporan), strata wajib-hitung dipakai, cakupan bulanan
  sebagai skala INATRADE di M3.

### 7.9 Rincian pelaksanaan adu versi (ditetapkan sebelum dijalankan)
- Peubah sasaran: penyaluran per perusahaan-bulan (jumlah semua subkomoditas), pedagang tanpa BULOG. Pengadaan diisi
  dengan metode yang sama hanya untuk keperluan identitas stok.
- Identitas: dalam bulan selalu tepat di data (Tahap 0), jadi 1a hanya soal antarbulan. I1/I2 memakai stok tetangga:
  Σ_lubang (pengadaan − penyaluran) = Stok Akhir sebelum lubang berikutnya − Stok Awal sesudah lubang dimulai; isian
  pengadaan dan penyaluran disesuaikan sebanding ragamnya (I1 penuh; I2 sebagian, dengan peluang "ekstrem" dan laju v
  dari data latih). Lubang akhir tidak punya tetangga kanan -> identitas tidak berpengaruh.
- Strata wajib-hitung (besar): perusahaan yang kumulatif membentuk 80% penyaluran per wilayah di blok penyetelan;
  selalu diisi (berapa pun panjang lubang), tanpa bobot pelapor, efek perusahaan tidak ditarik ke kelompok; untuk R7
  (tanpa efek perusahaan) strata besar memakai R2. Perusahaan yang baru muncul sesudah blok penyetelan = kecil.
- Lubang lebih panjang dari batas (strata kecil) tidak diisi dan ditutup bobot pelapor per wilayah × strata kecil.
  Pengaturan baku selama tahap 1a–1c: bobot batas 3, skala ragam 1×, tanpa rekonsiliasi, tanpa koreksi akhir.
- Sebaran prediksi tiap sel dinyatakan pada 21 kuantil (0,025; 0,05; 0,10 … 0,90; 0,95; 0,975) dari log total;
  CRPS = 2 × rata-rata pinball loss pada kuantil itu. Satuan penilaian = (tingkat, wilayah, bulan, jenis lubang).
- Tiap ulangan memuat dua ragam soal dengan pola hapus sama untuk semua versi: lubang tengah (di dalam blok) dan lubang
  akhir (data dipotong di satu bulan acak, sebagian perusahaan belum lapor).
- R4 (musiman) dan "kalender" hanya teridentifikasi lemah (data efektif < 2 tahun); tetap diuji sesuai daftar.
- R7 memakai regresi bertingkat (efek acak ukuran, wilayah, PAW, bulan) + poststratifikasi ke jumlah perusahaan populasi.
- Rekonsiliasi: isian dibangun dari tingkat perusahaan sehingga tingkat provinsi/wilayah/nasional sudah koheren kecuali
  bagian bobot pelapor; tahap 3 membandingkan bobot per tingkat (tanpa) dengan MinT-WLS (dengan).
- B dan C (tanpa model): sebaran dari galat log metode itu sendiri pada lubang buatan di data latih.

## 6. Rujukan (sebagian dicek ulang di sesi 6; sisanya dari ingatan)
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
