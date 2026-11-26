# Serah terima sesi: stok & distribusi bapokting (Dit. Binpas, Kemendag)

Baca file ini dulu di setiap sesi baru. Rincian per bagian ada di `beras_stok/CATATAN_SESI.md`,
`beras_stok/README.md`, `stok_komoditas/README.md`, `binpas/RANCANGAN_INATRADE.md`, `binpas/ambang_ujian.md`.

## STATUS TERKINI (per 26 Nov 2026, akhir sesi 9) — BACA INI DULU
Bagian 5–8 di bawah adalah riwayat; sebagian kalimat "belum" di sana sudah usang. Yang berlaku adalah blok ini,
bagian 9–14, bagian 15 (sesi 8: arah U3, data harga, laporan magang), dan **bagian 16 (sesi 9: bahan bimbingan dosen,
penjelasan bergambar beras, kemungkinan tugas akhir)**.

**Sesi 9 (23–26 Nov 2026) singkatnya:** tidak ada ujian/penyetelan/model yang dijalankan. Yang dibuat: (1) Google Doc
bahan bimbingan dosen khusus beras (6 halaman, diagram alir metodologi); (2) teks presentasi + daftar pertanyaan untuk
dosen (di chat, tidak disimpan sebagai file; ringkasannya di 16.3); (3) Google Doc penjelasan bergambar beras untuk
pengguna sendiri (15 halaman, 19 grafik). Pengguna mengatakan pekerjaan ini juga bahan **bimbingan dengan dosen** dan
bertanya apakah bisa jadi **tugas akhir** (jawaban di 16.4). U3 belum disentuh lagi sejak sesi 8.

**Yang sedang dibahas saat sesi 8 berakhir (belum ada keputusan "gas", belum ada yang dijalankan):** pengguna ingin
**U3 TETAP ADA** dan condong ke **semua komoditas dijalankan lalu dilaporkan apa adanya**. Usul saya: U3 versi ringkas
(model harga per provinsi per bulan, tiga versi diadu). Sumber harga sudah dicari sendiri: **PIHPS BI bisa diambil**
untuk beras, daging sapi, daging ayam ras, telur ayam ras; kedelai, daging kerbau, pupuk belum ada sumber harga per
provinsi. Rincian, keputusan yang masih perlu, dan cara ambil data: bagian 15.

**Peta ujian per komoditas (17 Nov 2026):**
| Komoditas | U1 | U2 | U3 |
| --- | --- | --- | --- |
| Beras | sudah: wilayah lolos | sudah: "lebih dekat" lolos, korelasi asal gagal | belum; harga PIHPS ada |
| Daging sapi | sudah: wilayah lolos | belum (publikasi BPS 2025, 2018 ada; ditawarkan, belum dijawab) | belum; harga PIHPS ada |
| Kedelai | sudah: wilayah gagal bias, provinsi lolos | belum (publikasi BPS belum dicek) | belum; harga per provinsi belum ada |
| Daging kerbau | sudah: gagal bias | tidak ada publikasi BPS | belum; harga belum ada |
| Telur ayam ras | sudah: gagal | belum (publikasi BPS 2023, 2021, 2019 ada) | belum; harga PIHPS ada |
| Daging ayam ras | tidak dijalankan (tidak bisa diuji: tidak ada data 2024) | belum (publikasi BPS 2019, 2018) | belum; harga PIHPS ada |
| Pupuk | tidak dijalankan (gagal bias di penyetelan; pelapor tinggal 4) | tidak ada publikasi BPS | tidak bermakna (harga diatur/HET) |

**Hasil yang sudah final (semua ujian SEKALI JALAN dan SUDAH TERPAKAI; jangan dijalankan lagi):**
| Komoditas | Status | Rincian |
| --- | --- | --- |
| Beras | LOLOS U1 di wilayah; provinsi lolos dengan catatan; nasional cakupan belum bisa diputuskan | `binpas/HASIL_ADU_BERAS.md` |
| Daging sapi | LOLOS U1 di wilayah (sesudah koreksi satuan, resep hasil turun peringkat); provinsi dan nasional gagal bias | `binpas/HASIL_ADU_KOMODITAS.md` |
| Kedelai | lolos U1 di provinsi saja; wilayah gagal bias -> "tercatat" | idem |
| Daging kerbau, telur ayam ras | gagal U1 -> "tercatat" | idem |
| Daging ayam ras, pupuk | "tercatat" (tidak bisa diuji / gagal bias di penyetelan; data terlalu tipis) | idem |
| Keterwakilan beras (U2) | gerbang "lebih dekat" LOLOS; gerbang korelasi asal GAGAL -> INATRADE = penguat peta jalur BPS, bukan gambaran pola asal | `binpas/RANCANGAN_U2.md` |

**Yang dikunci dan menunggu data baru:** resep versi 2 kedelai, daging kerbau, telur ayam ras
(`binpas/RANCANGAN_V2.md`, `binpas/hasil_v2_*/`). Hanya boleh diuji di bulan sesudah Sep 2026 (perkiraan butuh
Okt 2026–Mar 2027, ±April 2027). Jangan ubah `resep.json`.

**Notebook tunggal (sesi 8, 16 Nov 2026): SELESAI** — `binpas/colab/05_inatrade_tujuh_komoditas.ipynb` (dengan
output dari awal sampai akhir, termasuk log proses resmi dan enam grafik; dibangun dan dijalankan oleh `binpas/colab/buat_notebook.py`). Sudah dikirim ke
pengguna. Replikasi di dalamnya: daging sapi, kedelai, daging kerbau, telur, dan U2 beras SAMA PERSIS dengan hasil
resmi; beras berbeda tipis seperti diperkirakan (status gerbang sama). **Jalur Colab belum pernah dicoba** (hanya
dijalankan lokal); bila pengguna melaporkan galat di Colab, lihat bagian 14.0.

**Tawaran yang belum dijawab pengguna:** ujian keterwakilan (U2) daging sapi dengan Pola Distribusi BPS (rekomendasi
saya; ±30–60 menit, tebakan); 79 kombinasi + peubah luar impor bulanan untuk kedelai/daging sapi (hasilnya hanya calon
resep); pembaruan Claude Doc laporan ringkas; tenggat dan kerangka laporan magang (ditanyakan, belum dijawab).

## Pengguna dan cara kerja
- Harits, Dit. Bina Pasar Dalam Negeri (Binpas) Kemendag; atasan yang sering dibalas lewat WA: Bu Fitria.
- Bahasa Indonesia santai; jawaban ringkas; kalau diminta "chat WA", tulis teks siap tempel.
- **Konteks (disebut pengguna 17 Nov 2026): pekerjaan ini juga bahan LAPORAN MAGANG pengguna.** Tenggat, format, dan
  kerangka bab belum diketahui (sudah ditanyakan). Saat memilah pekerjaan, bedakan: hasil final yang bisa dilaporkan,
  keputusan yang masih terbuka, yang masih bisa dijalankan sebelum tenggat, dan yang masuk "saran lanjutan".
- Hemat kredit: beri tahu dulu sebelum run panjang (> ±10 menit). Jangan bikin mockup kalau tidak diminta.
- **Pelajaran sesi 9 (ikuti):**
  - Pengguna **tidak paham teknis** pekerjaan beras ("gua bener2 gak paham lu ngapain sama beras itu dan hasilnya kenapa
    begitu"). Saat menjelaskan: bahasa sederhana, analogi (soal latihan/try out/ujian, saldo rekening untuk neraca),
    gambar, dan paragraf "cara membaca" untuk tiap grafik; selalu jelaskan KENAPA hasilnya begitu, bukan hanya angkanya.
  - Pengguna sering meminta "jelasin detail bagian X" dari dokumen yang sudah dibuat: jelaskan per butir/per baris tabel,
    apa artinya, dari mana angkanya, dan batasnya.
  - Dokumen untuk dosen/pengguna dibuat sebagai **Google Doc** (Drive `create_file` dari .docx berisi gambar, lalu
    dirapikan dengan Docs `update_doc`: lebar tabel dan letak gambar tidak terbawa dari .docx; perlu
    `updateTableColumnProperties`). Batas halaman yang disebut pengguna = batas keras.
  - Jangan menulis "P\\*" di python-docx (tercetak dengan garis miring); tulis "P*".
- **Pelajaran sesi 8 (ikuti):**
  - **Jangan minta pengguna menyediakan/mengekspor data.** "pake data yg ada aja", "lu cari2 sendiri di internet":
    cari dan coba sendiri sumber terbuka dulu; baru laporkan yang benar-benar tidak bisa diambil.
  - **Jangan menutup tiap jawaban dengan pertanyaan balik**; pengguna kesal ditanya terus. Beri rekomendasi, lanjutkan
    yang tidak bergantung pada jawabannya.
  - **Jangan menawarkan/menjajarkan hal yang belum bisa dikerjakan seolah tinggal dijalankan** (kasus U3: pengguna
    marah karena U3 ada di rancangan padahal modelnya belum ada). Sebut jelas dari awal: sudah ada / tinggal run /
    harus dibangun dulu.
  - Tetapi **jangan memangkas cakupan tanpa diminta**: saat ditawari U3 ditandai "di luar cakupan", jawabannya
    "gak lah U3 ttep ada". Pengguna juga ingin semua komoditas diperlakukan setara dan hasilnya dilaporkan apa adanya.
  - Keluaran yang terlalu ringkas ditolak ("ko pendek banget isinya"): notebook harus memuat log proses dan grafik.
  - Izin run lewat kotak pilihan (AskUserQuestion) berjalan baik: sebut lama run dan apa yang ikut dijalankan.
  - Pengguna menulis sangat singkat dan kasar saat kesal; jawab langsung ke isi, tanpa basa-basi, tanpa membela diri.
- Kunci BPS hanya dari env var `BPS_API_KEY` (jangan ditulis ke file/chat). Pengguna menolak memberi kunci USDA:
  jangan diminta lagi (unduhan bulk CSV USDA tidak butuh kunci). Jangan akali bot-check (tidak boleh spoof
  User-Agent); bps.go.id dan satudata.pertanian.go.id memblokir akses otomatis -> pakai WebAPI BPS.
- Data mentah tidak disimpan di repo. Commit hanya ke branch `claude/bayesian-rice-stock-model-qmunfn`,
  tanpa PR kecuali diminta.
- **Jangan menjalankan atau mengulang run tanpa diminta** (termasuk uji coba kecil). Kalau diminta mengirim sesuatu,
  langsung kirim; jangan diselingi run. Pengguna sempat menghentikan run dan pengiriman file di sesi 6.
- Pengguna ingin bisa menjalankan sendiri di Google Colab (unggah folder ke Drive).
- Bahasa: Indonesia (pengguna kadang menulis Inggris; tetap jawab Indonesia kecuali diminta lain).
- **Pola kerja sesi 7 (ikuti):** tiap ada hasil atau keputusan, pengguna meminta "bikinin chat WA buat Bu Fitria soal
  ini (dan rekom lu)". Tulis teks siap tempel dalam blok kode, format WA (*tebal* satu bintang), sapaan "Selamat siang
  Bu Fitria, izin lapor ...", penutup "Terima kasih, Bu.", butir rekomendasi diberi huruf/angka (a–c, 1–3) supaya
  jawaban beliau bisa "di iyain a–c". Jawaban beliau diteruskan pengguna sebagai "di iyain ...", "gas", atau
  "jawabannya b" -> itu persetujuan untuk butir yang disebut SAJA.
- **Selalu TANYA DULU sebelum ujian sekali jalan** (U1 per komoditas, U2). Urutan wajib: kunci resep/definisi ->
  commit + push -> baru jalankan. Turun peringkat di blok penyetelan boleh langsung (aturan `ambang_ujian.md`).
- Laporkan hasil apa adanya, termasuk yang gagal dan perkiraan saya yang meleset; sebut kalau suatu angka adalah hasil
  penyetelan (bukan ujian) atau temuan sesudah hasil dilihat.
- Daftar komoditas dari pengguna: **daging sapi, daging kerbau, daging ayam ras, telur ayam ras, beras, kedelai,
  pupuk SAJA** (minyak goreng, gula, tepung terigu dibatalkan).
- **Jangan usulkan lagi konfirmasi satuan ke perusahaan/pengelola INATRADE** (ditolak 14 Nov 2026); perkiraan dari
  data dipakai.
- Kode perusahaan (mis. `00267`) boleh disebut ke pengguna dan di WA untuk Bu Fitria, tetapi tidak dimasukkan ke
  dokumen/laporan yang dibagikan. Berkas per perusahaan tidak di-commit.
- Dokumen untuk Bu Fitria dibuat sebagai Claude Doc (artefak), bukan file.

## File yang harus diunggah ulang di sesi baru
- `Non_PAW_dari_nol.xlsm` (INATRADE, sheet "2024-2026", semua komoditas, PAW + Non PAW) — wajib.
- `Non_PAW_Gabungan_2024-2026_sd_Sep2026_2.xlsx`, `PAW_September_1.xlsx` (subset, opsional).
- Data BPS/USDA bisa diambil ulang otomatis (perintah di README masing-masing folder).
- **Semua isi folder scratchpad sesi 7 hilang saat sesi berakhir** (xlsm, cache BPS, PDF BPS, keluaran penuh per tahap,
  CSV per perusahaan). Yang dibutuhkan untuk melanjutkan sudah ada di repo (lihat "Menyiapkan lingkungan" di bagian 14).
- Hash file INATRADE yang dipakai semua hasil sesi 7: sha256 `c667dddba86bdfb624b441f7a10b5b29cd548cc9bd98fcbecd2c687faf5adac2`.
  Bila pengguna mengunggah file baru (hash beda), itu DATA BARU: catat hash dan tanggalnya, jangan dipakai untuk
  mengulang ujian yang sudah terpakai.
- **DATA BARU (sesi 10, 26 Nov 2026): `Cleaning_Lengkap.xlsm`**, sha256
  `335c7e6e804c758a4fc70cb21cf089b813ebe43444b37dfe1c8c17b6f46b401e`, Jan 2024–**Okt 2026**, sheet "2024-2026" berkolom
  sama (28.945 baris; Okt 2026 = 1.280 baris; sheet lain: PAW/Non PAW Gabungan, Data Mentah Okt, cek anomali harga).
  Dicek baca-saja dengan fungsi `tahap0.baca/laporan/identitas/konsentrasi/harga` (tanpa model): **Jan 2024–Sep 2026
  identik dengan Tahap 0 resmi** (27.665 baris, 9.479 laporan, 315 kode, 441 multi-kepala, 58 koreksi kg beras,
  pelapor beras per tahun 65/69/76 dan per bulan sama, tabel identitas stok dan konsentrasi sama persis, BULOG sama).
  Okt 2026 beras: 57 pelapor non-BULOG (Sep 55; Jawa 19, Sumatera 30), 52 dari 74 pelapor aktif Apr–Sep lapor, 5 baru,
  0 koreksi kg, satuan semua ton; BULOG Okt stok awal 4,49 / akhir 4,43 juta ton (Sep stok akhir 2,18 tetap janggal,
  perlakuan khusus Sep di `model_stok.py` tetap perlu). Belum ada yang dijalankan dengan file ini.

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
| Laporan Ringkas: Penguatan Data INATRADE Tujuh Komoditas (doc) | https://claude.ai/artifact/GTjBbAhSw52RP2Kszwqm6o | hasil ujian tujuh komoditas + keterwakilan beras, untuk Bu Fitria (14 Nov 2026) |
| Estimasi Stok dan Penguatan Data Distribusi Beras (Google Doc, bahan bimbingan dosen, 23 Nov 2026) | https://docs.google.com/document/d/17JMV-rw9R_suBzrOpngQ1x485XmDJL1LqJjlwJm942U/edit | beras saja: permasalahan, sumber data, diagram alir metodologi, evaluasi, hasil U1/stok/U2; 6 halaman (batas pengguna 7). Dibuat dari `binpas/bimbingan/buat_docx.py` + `diagram.py`, lalu dirapikan langsung di Google Docs (lebar tabel, 3.1–3.3 dipindah sebelum diagram) |
| Beras: apa yang dikerjakan, datanya, caranya, dan hasilnya (Google Doc, penjelasan bergambar untuk pengguna sendiri, 25 Nov 2026) | https://docs.google.com/document/d/1z9B4ncCgNmemr3s6w3kCf2nW--09F2iZ_y6ho7wGBzU/edit | bahasa sederhana, 19 grafik/diagram, 15 halaman; dibuat dari `binpas/penjelasan_beras/` (angka.py: angka agregat dari xlsm + tahap0; grafik.py; dok.py). Pengguna bilang "gua bener2 gak paham lu ngapain sama beras": jelaskan dengan gambar dan "cara membaca" |

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
  `tahap4_penuh.pkl.xz`).
- Resep: I0, isian B (interpolasi/laporan terakhir, semua lubang diisi), tambahan tdist, tanpa bobot pelapor,
  ragam 0,5×, tanpa rekonsiliasi, tanpa penggabung; P\* = A5. Koreksi akhir: peringkat 1 CRPS "tanpa" gagal gerbang
  cakupan (Jan–Jun 2025: wilayah 76%), **Bu Fitria memutuskan turun ke konformal** (12 Nov 2026); `resep.json` sudah diubah.
- Gerbang penyetelan, wilayah (target utama): CRPS 0,019 vs 0,236 (−92%), konsisten, bias +0,1%, arah 94% -> lolos;
  cakupan 81,0% (Wilson 65,7–90,5%) -> "belum bisa diputuskan". Provinsi: cakupan 77,4% -> gagal. Nasional: cakupan
  80,6% -> belum bisa diputuskan.
- Konformal di blok penyetelan (Jan–Jun 2025): wilayah dan provinsi lolos semua gerbang (cakupan 92,8% dan 91,0%);
  nasional cakupan "belum bisa diputuskan". Rincian: `hasil_adu_beras/gerbang_opsi5.csv`, skrip `binpas/gerbang_opsi5.py`.
- Catatan: seed turunan memakai `hash()` teks (tidak persis terulang antarjalan); `kalibrasi`/`ujian` ikut menjalankan
  R5 dan R7 yang tidak dipakai resep (±0,5 jam per langkah).

## 10. Kalibrasi dan U1 beras SUDAH DIJALANKAN (12 Nov 2026, sesi 7) — U1 SUDAH TERPAKAI, jangan dijalankan lagi
- Resep dikunci di commit `f6544a0` (anggota dipangkas ke B saja, koreksi konformal), lalu `kalibrasi` (7,5 detik) dan
  `ujian` (18 detik). Rincian di `binpas/HASIL_ADU_BERAS.md`, berkas di `binpas/hasil_adu_beras/`.
- **Wilayah-bulanan (target utama) LOLOS semua gerbang U1:** CRPS 0,016 vs P\* 0,116 (−86%), bias +0,04%, arah 96%,
  cakupan 97,8% (Wilson 88,1–99,6%), CRPS −3% dibanding penyetelan.
- Provinsi (7 provinsi ber-pelapor ≥ 3): lolos semua; CRPS +13% dibanding resep yang sama di penyetelan (+28% bila
  acuannya angka seluruh blok tanpa koreksi; acuan tidak dirinci di ambang). **Bu Fitria memutuskan acuan = resep
  yang sama (14 Nov 2026, sesudah hasil U1 dilihat) -> provinsi "lolos dengan catatan"**; angka +28% tetap dilaporkan.
  Nasional: cakupan "belum bisa diputuskan".
- Catatan: 6 dari 57 sel-bulan wilayah di U1 jatuh di Nov–Des 2025 (lubang akhir mundur ke blok kalibrasi); uji
  kepekaan hanya 2026 memberi status gerbang yang sama (`binpas/peka_u1.py`). Rentang cenderung terlalu lebar.
- Belum: skor tingkat perusahaan, triwulanan, CRPS ton, U2 (keterwakilan, Poldis 2025), U3 (model gabungan), komoditas
  lain. Hasil U1 sudah dilaporkan ke Bu Fitria lewat WA (14 Nov 2026); arahan beliau soal tahap berikutnya belum ada.

## 11. Adu versi komoditas lain: PENYETELAN sudah (14 Nov 2026, sesi 7) — rincian di `binpas/HASIL_ADU_KOMODITAS.md`
- Bu Fitria: lanjut ("gas"). Pengguna membatasi komoditas: **daging sapi, daging kerbau, daging ayam ras, telur ayam
  ras, beras, kedelai, pupuk SAJA** (minyak goreng, gula, tepung terigu dibatalkan).
- Kode diubah dulu (commit `fc81529`): argumen ke-5 = nama komoditas, 58 kombinasi untuk selain beras, seed tetap
  (crc32), sel di luar blok tidak dinilai, turun peringkat otomatis antaropsi koreksi di tahap 5.
- Penyetelan enam komoditas ±8 menit total. Hasil di tingkat wilayah (blok penyetelan, Jan–Jun 2025):
  kedelai LOLOS (B + tdist + konformal; perbaikan 47%); telur ayam ras LOLOS tapi hanya 6 sel-bulan; daging sapi,
  daging kerbau, pupuk GAGAL gerbang bias (−5,2%, −7,9%, +4,4%; batas 3%); daging ayam ras TIDAK BISA DIUJI (tidak ada
  data 2024 untuk konformal mini, tahap 5 berhenti).
- Bu Fitria menyetujui (14 Nov 2026): kedelai dan telur lanjut U1; daging kerbau dicoba turun peringkat; daging sapi,
  pupuk, daging ayam ras berlabel "tercatat".
- **U1 kedelai SUDAH (terpakai):** wilayah GAGAL gerbang bias (+5,0%, batas 3%; berasal dari "Pulau lain", 4 sel-bulan),
  gerbang lain lolos (perbaikan 84%, cakupan 95%); provinsi lolos semua; nasional cakupan belum bisa diputuskan.
- **U1 telur ayam ras SUDAH (terpakai):** gagal (CRPS wilayah 5× lebih besar daripada penyetelan) -> "tercatat".
- **Daging kerbau:** turun peringkat (`binpas/turun_peringkat.py`, aturan di-commit sebelum dijalankan) -> resep R4
  (regresi panel musiman) lolos gerbang penyetelan di wilayah (bias +2,4%, perbaikan 71%). **U1 kerbau SUDAH
  (terpakai, disetujui Bu Fitria): wilayah GAGAL gerbang bias (+5,7%; berasal dari Sumatera)** -> "tercatat".
- **Status akhir tujuh komoditas (14 Nov 2026):** beras lolos di wilayah; kedelai lolos di provinsi saja (wilayah
  "tercatat"; disetujui Bu Fitria); daging kerbau, telur ayam ras, daging sapi, pupuk, daging ayam ras "tercatat".
  Semua U1 yang ada sudah terpakai; jangan dijalankan lagi. Perbaikan resep hanya boleh diuji di data bulan baru.
- Hasil U1 kerbau dan status akhir sudah dilaporkan ke Bu Fitria (14 Nov 2026).
- Berkas: `binpas/hasil_adu_<komoditas>/`.

## 12. Lanjutan sesudah tujuh komoditas (14 Nov 2026, sesi 7) — disetujui Bu Fitria (butir a–c)
- **a. Validasi satuan daging sapi dan pupuk: SUDAH** — `binpas/HASIL_VALIDASI_SATUAN.md`, skrip
  `binpas/validasi_satuan.py`. Semua baris berlabel TON tetapi sebagian diisi kg. Dua pola: lonjakan sesaat (bisa
  dikoreksi otomatis) dan skala konsisten besar (3 perusahaan: 2 daging sapi, 1 pupuk; harus dikonfirmasi ke
  pengelola INATRADE). Bila ketiganya kg: daging sapi 2025 turun dari 451 ribu ke ±63 ribu ton, pupuk 2025 dari 15,8
  juta ke ±0,3 juta ton. Kode perusahaan ada di berkas internal (tidak di repo). Sesudah konfirmasi: perbaiki koreksi
  satuan di `tahap0.py`, ulang penyetelan daging sapi dan pupuk (U1 keduanya belum pernah jalan).
- **b. Uji ulang resep kedelai dan daging kerbau:** menunggu data bulan baru (sesudah Sep 2026). Belum bisa dikerjakan.
- **c. Ujian keterwakilan (U2) beras: SUDAH DIJALANKAN (sekali jalan, terpakai)** — `binpas/RANCANGAN_U2.md` bagian 6
  (definisi dikunci) dan 7 (hasil), `binpas/hasil_u2_beras/`. Publikasi BPS hanya memuat DAFTAR provinsi mitra (bukan
  pangsa); "Perdagangan Antar Wilayah" BPS juga tidak memuat rincian beras; Bu Fitria menyetujui gerbang diganti
  perbandingan jalur. Hasil: gabungan BPS 2024 + INATRADE lebih tepat menebak jalur BPS 2025 (AP 0,563) daripada BPS
  2024 saja (0,480; selisih +0,083, selang 0,041–0,133) dan INATRADE mentah (0,329) -> gerbang "lebih dekat" LOLOS;
  korelasi volume asal INATRADE vs BPS 2025 = 0,20 (batas 0,6) -> gerbang keterwakilan GAGAL. INATRADE = penguat peta
  jalur, bukan wakil pola asal. Ekstraksi: `poldis_mitra.py` (2024, diagram), `poldis_mitra_narasi.py` (2025, kalimat),
  hasilnya di `binpas/data_publik/`.
- **Satuan (perkiraan sendiri, diminta pengguna):** ketiga perusahaan berskala besar hampir pasti kg. Pupuk: laporan
  beralih dari ton ke kg mulai Jun 2025 (stok awal Jun = 1.000 × stok akhir sebelumnya, di 4 jenis pupuk). Daging sapi:
  satu perusahaan omzetnya Rp31,8 triliun sebulan bila ton; satu lagi rincian per tujuan 1–16 ribu "ton" (perusahaan
  lain median 5,8 ton). Peralihan ton <-> kg yang terlihat dari stok juga ada di komoditas lain (beras 8 pasangan
  laporan). **Diterapkan (disetujui Bu Fitria):** `tahap0.KOREKSI_KG` (commit `b1f1171`); data komoditas lain dicek
  tidak berubah.
- **Daging sapi diulang dengan satuan terkoreksi** (`binpas/hasil_adu_daging_sapi_v2/`, rincian di
  `HASIL_ADU_KOMODITAS.md`): pemenang masih gagal bias (−4,8%) -> turun peringkat -> resep B dengan semua lubang diisi
  + konformal LOLOS semua gerbang wilayah di blok penyetelan (perbaikan 61%, bias +0,1%, cakupan 92%). **U1 daging
  sapi SUDAH (terpakai, disetujui Bu Fitria): wilayah LOLOS semua gerbang** (CRPS 0,061 vs 0,168, −64%; bias +1,1%;
  arah 86%; cakupan 96,6%); provinsi dan nasional gagal bias (+4,6%, +3,4%). Pupuk tetap "tercatat".
- **Status akhir (14 Nov 2026):** lolos di wilayah: beras, daging sapi; lolos di provinsi saja: kedelai; "tercatat":
  daging kerbau, telur ayam ras, daging ayam ras, pupuk. Semua U1 dan U2 beras sudah terpakai.
- **Keputusan redaksi (Bu Fitria, 14 Nov 2026):** di laporan, INATRADE disebut PENGUAT peta jalur BPS, bukan gambaran
  pola asal perdagangan.

- **Keputusan penutup (Bu Fitria lewat pengguna, 14 Nov 2026):** (1) koreksi satuan tiga perusahaan TIDAK dikonfirmasi
  ke perusahaan; perkiraan dari data tetap dipakai (jangan diusulkan lagi). (2) Kedelai, daging kerbau, telur ayam ras
  diuji ulang bila data sesudah Sep 2026 masuk (belum bisa dikerjakan). (3) Laporan ringkas tujuh komoditas sudah
  dibuat sebagai doc (lihat tabel artefak).

## 13. Resep versi 2 dan cakupan volume komoditas lain (14 Nov 2026, sesi 7)
- **Resep versi 2 kedelai, daging kerbau, telur ayam ras: DIKUNCI, BELUM DIUJI** — `binpas/RANCANGAN_V2.md`,
  `binpas/hasil_v2_<komoditas>/`. Blok penyetelan versi 2 = Jan 2024–Sep 2026 (opsi `v2`); ujiannya HANYA boleh di
  bulan sesudah Sep 2026 (perkiraan butuh Okt 2026–Mar 2027, ±April 2027). Resep: kedelai C, daging kerbau B, telur
  R1; ketiganya lolos gerbang wilayah di data penyetelan (bukan hasil ujian). Jangan ubah `resep.json`.
- Telusur bias U1 (eksploratif): kedelai dari "Pulau lain" (1 perusahaan 91%), kerbau dari Sumatera (2 perusahaan 91%).
- **Cakupan volume enam komoditas lain terhadap BPS: SUDAH** — `binpas/HASIL_CAKUPAN_KOMODITAS.md`,
  `binpas/cakupan_komoditas.py` (Susenas, produksi per provinsi, impor dataexim). Penyaluran ÷ pasokan 2025: kedelai
  62%, daging sapi 12%, daging ayam ras 2,7%, pupuk ±1%, telur 0,08% (beras ±2–3%).
- Belum (tawaran ke pengguna, belum diminta): peubah luar di adu versi untuk kedelai/daging sapi; ujian keterwakilan
  daging sapi/telur/ayam dengan Pola Distribusi BPS (sekali jalan, definisi dikunci dulu).

## 14. Notebook tunggal (SELESAI di sesi 8) + cara melanjutkan apa pun di sesi baru

### 14.0 Status sesi 8 (16 Nov 2026) — notebook SELESAI dan sudah dijalankan (lokal)
- Pengguna meminta "lanjutkan notebook tunggal di bagian 14", lalu mengizinkan run penuh ("Jalankan penuh": termasuk
  replikasi U1 lima komoditas dan U2 beras). File INATRADE sesi 8 ber-hash sama dengan sesi 7 (`c667dddb…`): bukan
  data baru.
- Berkas: `binpas/colab/buat_notebook.py` (pembangun) dan `binpas/colab/05_inatrade_tujuh_komoditas.ipynb` (55 sel,
  DENGAN output, ±1,1 MB: ±2.400 baris output teks + 6 grafik). `python binpas/colab/buat_notebook.py` saja akan MENIMPA notebook dengan versi tanpa output;
  untuk output pakai `--jalankan <folder berisi xlsm>` (±2,5 menit, 4 CPU; butuh `pip install nbclient nbformat
  ipykernel matplotlib`).
- **Versi pertama dinilai pengguna "pendek banget isinya"**; pengguna memilih tambahan "output proses lengkap" dan
  "grafik" (bukan "kode tampil di sel" dan bukan "penyetelan dijalankan ulang"). Versi sekarang: log proses RESMI apa
  adanya per komoditas (`log_penyetelan.txt`, `log_turun_peringkat.txt`, untuk beras juga log kalibrasi dan ujian;
  resep versi 2 juga), output mentah replikasi kalibrasi/ujian/U2, dan enam grafik matplotlib (pelapor per bulan,
  cakupan volume, CRPS resep vs P\*, gerbang bias + cakupan, CRPS per bulan dari replikasi, AP U2). Kode skrip tetap
  di sel paket (base64). Notebook dijalankan tiga kali di sesi 8 (dua kali versi pertama, sekali versi ini); angka
  replikasi sama di ketiganya.
- Isi mengikuti rancangan 14.2, dengan penyesuaian:
  1. pandas 3.0.5 di Colab dipasang ke folder terpisah (`pip install --target /content/pustaka_inatrade`) dan dipakai
     skrip lewat `PYTHONPATH`, bukan menimpa pandas kernel; bila gagal dipasang, skrip memakai pandas bawaan dengan
     peringatan. Di luar Colab skrip dijalankan dengan `-I`.
  2. Skrip dijalankan lewat peluncur kecil (`runpy` + `multiprocessing.set_start_method('fork')`) supaya tetap jalan
     bila Python Colab memakai cara mulai proses selain fork; isi skrip tidak diubah.
  3. Bila sha256 xlsm berbeda dari hash resmi, sel replikasi U1/U2 dilewati otomatis (data baru).
  4. Data BPS: sel opsional (mati); tabel cakupan resmi ditampilkan dari paket. Penyetelan ulang: sel opsional (mati).
  5. Gerbang "memburuk ≤ 20%" dihitung di notebook (acuan = resep yang sama di penyetelan; beras = baris `konformal`
     di `gerbang_opsi5.csv`). Tabel resmi yang ditampilkan cocok dengan `HASIL_*.md`.
- **Hasil replikasi (16 Nov 2026, 13.46 UTC; REPLIKASI, bukan ujian baru, status resmi tidak berubah):**
  - Daging sapi (satuan terkoreksi), kedelai, daging kerbau, telur ayam ras: `gerbang_U1.csv` replikasi SAMA PERSIS
    dengan resmi (semua kolom angka identik). U2 beras: `hasil_U2.json` SAMA PERSIS.
  - Beras: tidak sama persis, seperti diperkirakan (U1 resmi memakai seed `hash()` dan ikut menilai sel Nov–Des 2025).
    Terhadap U1 resmi: CRPS berselisih paling besar 7,9%, status gerbang sama. Terhadap tabel kepekaan "hanya sel 2026":
    jumlah sel dan CRPS pembanding P\* sama, CRPS resep berselisih paling besar 0,8% (wilayah 0,0167 vs 0,0168), status
    gerbang sama. Di replikasi, CRPS wilayah terhadap penyetelan +3% (resmi −3%); provinsi +14% (resmi +13%).
  - Output dicek: tidak ada kode perusahaan (0 dari 315) dan kunci BPS tidak tercetak.
- **Belum pernah dicoba:** seluruh jalur Colab (mount Drive, `pip --target`, pandas 3.0.5 di Python Colab), sel
  opsional BPS, dan sel opsional penyetelan ulang. Tidak bisa dicoba dari sesi ini; tunggu laporan pengguna.
- Folder kerja run (scratchpad, hilang saat sesi berakhir) tidak di-commit; `hasil_ulang/` berisi data per perusahaan.

### 14.1 Permintaan pengguna (16 Nov 2026)
"kirimin 1 ipynb yg udah kluarin output dari awal sampai akhir yg bisa di re run pas di up ke drive". Pengerjaan
dihentikan pengguna sebelum notebook ditulis, lalu pengguna meminta catatan serah terima ini. **Tanyakan dulu apakah
notebook masih diinginkan sebelum mengerjakannya.**

Yang sudah dikerjakan untuk itu (sudah di-commit): `binpas/cakupan_komoditas.py` dibuat mandiri (fungsi impor dataexim
disalin ke dalamnya, tidak lagi mengimpor `stok_komoditas/siapkan_data.py`; keluaran dicek identik);
`binpas/hasil_cakupan/cakupan_komoditas.csv` (tabel cakupan agregat). `pip install nbclient nbformat ipykernel` perlu
diulang di sesi baru.

### 14.2 Rancangan notebook (sudah dilaksanakan; lihat 14.0 untuk penyesuaiannya)
- Nama: `binpas/colab/05_inatrade_tujuh_komoditas.ipynb`, dibuat oleh skrip `binpas/colab/buat_notebook.py` supaya bisa
  dibangun ulang. Notebook lama `03_tahap0.ipynb` dan `04_adu_versi_beras.ipynb` hanya beras dan tanpa output.
- **Mandiri:** kode (`binpas/*.py`, `beras_stok/util.py`, `beras_stok/ambil_bps.py`) dan hasil resmi berukuran kecil
  (`resep.json`, `gerbang_*.csv`, log, `hasil_U2.json`, `data_publik/*.csv`, `hasil_cakupan/*.csv`, resep versi 2)
  ditanam di satu sel sebagai arsip base64, diekstrak ke `BASE/paket/`. Pengguna cukup mengunggah notebook + xlsm ke
  `MyDrive/inatrade_colab/`. Berkas `.xz` besar tidak ditanam.
- **Sel konfigurasi** meniru notebook lama: `DI_COLAB = 'google.colab' in sys.modules`, `drive.mount`, `BASE`, cari
  `Non_PAW_dari_nol.xlsm` di `BASE/` atau `BASE/data/inatrade/`.
- **Versi pustaka:** kode ditulis dan diuji dengan pandas 3.0.5 (Python 3.13); Colab bawaan pandas 2.x dan BELUM pernah
  dicoba. Rencana: di Colab `pip install "pandas==3.0.5" openpyxl`, dan semua skrip dijalankan lewat `subprocess`
  (bukan di kernel) supaya memakai pandas baru tanpa restart. catboost/quantile-forest/statsmodels hanya perlu bila
  penyetelan beras diulang penuh. Jangan impor pandas di kernel sebelum sel pip.
- **Isi sel, berurutan:** (1) Tahap 0 (`tahap0.py`); (2) validasi satuan (`validasi_satuan.py "DAGING SAPI" "PUPUK"`);
  (3) cakupan volume: tampilkan tabel resmi, ambil ulang dari BPS hanya bila `BPS_API_KEY` ada (env atau Colab
  Secrets), nilai kunci disamarkan dari output; (4) per komoditas yang diuji (beras, daging sapi, kedelai, daging
  kerbau, telur): tampilkan resep + gerbang penyetelan resmi, lalu REPLIKASI kalibrasi + ujian ke
  `BASE/hasil_ulang/<komoditas>/` dan bandingkan dengan `gerbang_U1.csv` resmi; (5) replikasi U2 beras (`u2_beras.py`
  dengan `data_publik/*.csv`); (6) resep versi 2 (tampilkan saja; belum boleh diuji); (7) tabel ringkasan status.
- **Cara replikasi tanpa penyetelan ulang:** salin `resep.json` (+ `komoditas.txt`) resmi ke folder baru, buat
  `tahap4_penuh.pkl` pengganti berisi DataFrame kosong (berkas itu hanya dibaca bila resep memakai penggabung `G:`;
  semua resep sekarang versi tunggal), lalu `adu_versi.py kalibrasi` dan `ujian`. Hapus folder replikasi di awal sel
  supaya penjaga `U1_SUDAH_JALAN.json` tidak menolak. **Beri label "REPLIKASI, bukan ujian baru; hasil resmi = yang
  tercatat di repo".**
- **Yang diharapkan:** daging sapi (satuan terkoreksi), kedelai, daging kerbau, telur -> angka replikasi sama persis
  dengan resmi (seed crc32, kode sama). **Beras TIDAK akan sama persis**: U1 resmi beras dijalankan sebelum commit
  `fc81529` (seed masih `hash()` teks, dan sel Nov–Des 2025 ikut dinilai); replikasi akan mendekati tabel kepekaan
  `gerbang_U1_peka_2026saja.csv`. Tulis penjelasan ini di notebook.
- Penyetelan penuh disediakan sebagai sel opsional yang dimatikan secara baku (beras ±1,3 jam; komoditas lain ±3
  menit + turun peringkat ±3–7 menit).
- Sesudah ditulis: jalankan sekali dari awal sampai akhir dengan `nbclient` di folder tiruan Drive yang berisi xlsm
  (perkiraan 3–5 menit; tiap skrip membaca xlsm ±10 detik), periksa output tidak memuat data per perusahaan, commit,
  lalu kirim ke pengguna dengan `SendUserFile` (berkas harus di dalam repo atau scratchpad).

### 14.3 Menyiapkan lingkungan di sesi baru
```bash
git fetch origin claude/bayesian-rice-stock-model-qmunfn && git checkout claude/bayesian-rice-stock-model-qmunfn
pip install catboost quantile-forest statsmodels pdfplumber        # pdfplumber hanya untuk ekstraksi PDF BPS
# xlsm unggahan pengguna: salin ke folder kosong sendiri di scratchpad; jalankan Python dengan -I
BPS_API_KEY=... python -I beras_stok/ambil_bps.py <cache json> <bps_out>      # ±1 menit; kunci hanya dari env var
```
Melanjutkan suatu komoditas dari hasil resmi: salin `binpas/hasil_adu_<kom>/` (atau `hasil_v2_<kom>/`) ke folder
keluaran di scratchpad, `xz -dk tahap4_penuh.pkl.xz`; `data_komoditas.pkl` / `data_beras.pkl` dibuat ulang otomatis
dari xlsm.

### 14.4 Perintah yang dipakai (semua dengan `python -I`)
```bash
python -I binpas/tahap0.py <xlsm> <keluaran> [bps_out]
python -I binpas/adu_versi.py penyetelan|kalibrasi|ujian <xlsm> <keluaran> <bps_out atau -> ["<KOMODITAS>"] [v2]
python -I binpas/turun_peringkat.py <keluaran penyetelan>          # bila pemenang gagal gerbang wilayah
python -I binpas/gerbang_opsi5.py binpas <keluaran>                # beras saja (kode lama); komoditas lain otomatis
python -I binpas/validasi_satuan.py <xlsm> <keluaran> "DAGING SAPI" "PUPUK"
BPS_API_KEY=... python -I binpas/cakupan_komoditas.py <xlsm> <cache json> <keluaran>
python -I binpas/poldis_mitra.py <pdf edisi 2024> <csv>            # daftar mitra dari diagram
python -I binpas/poldis_mitra_narasi.py <pdf edisi 2025> <csv>     # daftar mitra dari kalimat
python -I binpas/u2_beras.py <xlsm> <mitra_2024.csv> <mitra_2025.csv> <keluaran>   # SUDAH TERPAKAI
```
Nama komoditas persis: `BERAS`, `DAGING SAPI`, `DAGING KERBAU`, `DAGING AYAM RAS`, `TELUR AYAM RAS`,
`KEDELAI BAHAN BAKU TEMPE DAN TAHU`, `PUPUK`. Indeks bulan: 0 = Jan 2024, 24 = Jan 2026, 32 = Sep 2026.

### 14.5 Hal teknis yang mudah terlupa
- `adu_versi.py`: komoditas selain beras memakai 58 kombinasi (tanpa R5, R6, R7, juri RF) sehingga tidak ada
  penggabung; tambahan "luar" tidak berpengaruh di luar beras (kalau ikut terpilih itu derau).
- Turun peringkat otomatis hanya antaropsi koreksi (tahap 5); antarversi lewat `turun_peringkat.py` (kandidat beda
  satu tahap dari pemenang; aturan tertulis di docstring-nya).
- Gerbang "memburuk ≤ 20%" TIDAK dihitung kode: bandingkan `crps` di `gerbang_U1.csv` dengan `gerbang_penyetelan.csv`
  secara manual (acuan = resep yang sama; diputuskan Bu Fitria).
- `L_cakupan` False = gagal; `cakupan_belum_bisa` True dengan `L_cakupan` True = "belum bisa diputuskan".
- `tahap0.KOREKSI_KG`: tiga perusahaan dikoreksi ke kg (daging sapi 2, pupuk 1 sejak Jun 2025). Data beras, kedelai,
  daging kerbau dicek tidak berubah.
- Blok versi 2 (`v2`) disimpan di `<keluaran>/blok.json`; `tahap0.PER` masih berhenti di 2026-09 dan harus
  diperpanjang saat data baru datang.
- PDF BPS diambil lewat WebAPI: `.../v1/api/view/domain/0000/model/publication/lang/ind/id/<pub_id>/key/<KEY>/` ->
  kolom `pdf`. Beras 2024 `a688dbac2f627b8b2f5b3b87`, beras 2025 `f7bd40cb4779162e89bf2eda`, daging sapi 2025
  `3bbe93c02d8533def35a8b41`, telur ayam ras 2023 `3585f0898795b4189a71666e`, Perdagangan Antar Wilayah 2023
  `49016c4556ea47b96d62e9bf` (tidak memuat rincian komoditas). Pencarian: `.../list/model/publication/.../keyword/<kata>/`
  dan `.../list/model/var/.../keyword/<kata>/`.
- Variabel BPS yang dipakai: Susenas daging 2097 (2024) / 2552 (2025), telur 2099 / 2554, kacang-kacangan 2101,
  penduduk 2790; produksi daging sapi 480, kerbau 481, ayam ras pedaging 488, telur ayam petelur 491; impor lewat
  dataexim (`.../dataexim/sumber/2/kodehs/<hs>/jenishs/2/tahun/<y>/periode/1/key/<KEY>/`).
- Dokumen laporan untuk Bu Fitria (Claude Doc `GTjBbAhSw52RP2Kszwqm6o`) dibuat sebelum resep versi 2 dan cakupan
  volume komoditas lain; belum diperbarui dengan dua hal itu.

## 15. Sesi 8 lanjutan (16–17 Nov 2026): cakupan "semua kayak beras", U3, data harga, laporan magang
Semua di bagian ini DISKUSI dan PENCARIAN DATA; tidak ada ujian, penyetelan, atau model yang dijalankan.

### 15.1 Urutan percakapan dan sikap pengguna
1. "bisa ga treat semua komoditi kayak beras? jan run duls" -> saya jelaskan lima perlakuan beras yang belum dimiliki
   komoditas lain: 79 kombinasi (lain 58), peubah luar, U2, model stok + prakiraan, (cakupan volume sudah setara).
2. "kenapa sebelumnya ga di-treat sama?" -> dari `RANCANGAN_INATRADE.md` baris 96: "R5, R6, R7 dan juri RF dicoba di
   beras dulu; kalau tidak menyumbang, komoditas lain cukup 58 kombinasi" (dikunci 12 Nov, terpicu karena di beras
   tidak menyumbang); peubah luar hanya ada untuk beras; U2 yang disetujui Bu Fitria hanya beras; model stok = proyek
   awal beras, lalu stok dibekukan (sesi 5). Catatan saya: "tidak menyumbang di beras" adalah asumsi untuk komoditas
   lain, bukan temuan.
3. "U1 U2 U3 ke semua komoditi udah running semua?" -> belum (tabel peta ujian di STATUS TERKINI).
4. "Kalau gas jalanin semuanya amankah?" -> tidak semuanya bisa: U1 ulang tidak boleh; U1 versi 2 belum ada datanya;
   U1 ayam/pupuk tidak ada resep lolos; U2 hanya untuk komoditas ber-publikasi BPS; U3 belum ada modelnya.
5. Pengguna menyebut ini untuk **laporan magang** -> saya pilah: sudah final / belum diputuskan / masih bisa di-run /
   masuk saran lanjutan (ringkasnya di 15.5).
6. Pengguna marah U3 ditawarkan padahal modelnya belum ada. Penyebab yang saya akui: U3 masuk rancangan sesi 5 sebagai
   tahap ketiga, lalu di sesi yang sama stok dibekukan tetapi U3 tidak ditandai di luar cakupan; rancangan ditulis
   untuk kajian penuh, bukan skala magang. U1 dan U2 tidak bergantung pada U3.
7. **Pengguna: "gak lah U3 ttep ada gimana kira2?"** -> usul U3 ringkas (15.2).
8. Pengguna soal komoditas U3: "kalau semuanya di run kenapa? dan dilaporin sebegitu hasilnya" -> boleh (15.2).
9. Saya meminta pengguna mengekspor harga dari SP2KP -> ditolak keras ("lu cari2 sendiri di internet... dah gua
   bilang pake data yg ada aja") -> saya cari sendiri (15.3). Pengguna lalu memotong dan meminta serah terima ini.

### 15.2 Usul U3 versi ringkas (BELUM disetujui, BELUM dikunci, BELUM ada kode)
- Pertanyaan U3 dan gerbangnya TETAP seperti `ambang_ujian.md`: model harus mengalahkan "tanpa INATRADE" dan "INATRADE
  asli" pada CRPS prakiraan harga 1–2 bulan. Simulasi waktu nyata: titik awal bergulir Des 2025–Agu 2026, hanya data
  sampai titik awal, laporan INATRADE bulan terakhir dibuat tak lengkap (pola lubang akhir); CRPS log harga; pembanding
  tambahan yang hanya dilaporkan: harga bulan lalu, musiman naif (`RANCANGAN_INATRADE.md` 7.6).
- Yang diganti hanya MODEL: bukan model gabungan stok–arus–harga 38 provinsi (rancangan 7.6; butuh model stok, data
  arus, konvergensi model beras diperbaiki dulu; perkiraan 27 kali fit model besar), melainkan **model harga per
  provinsi per bulan**: musim, harga bulan lalu, produksi/impor bila ada, ditambah sinyal INATRADE (arus/stok pedagang
  per wilayah). Tiga versi berbeda hanya di masukan INATRADE: tanpa / asli / diperkuat (resep U1). Tidak butuh model
  stok, jadi tidak menabrak "stok dibekukan". Run perkiraan hitungan menit (tebakan).
- **Keputusan yang masih perlu dari Bu Fitria (belum dikirim; pengguna belum minta teks WA):**
  a. model diganti ke versi ringkas (perubahan rancangan; sah bila dikunci dan di-commit sebelum dijalankan, seperti
     penggantian gerbang U2);
  b. gerbang "ujian BPS 2025" di U3 dilepas, karena edisi beras 2025 sudah dibuka untuk U2 (tidak buta lagi);
  c. komoditas: pengguna condong **semua komoditas yang punya data harga**, hasil dilaporkan apa adanya.
- Konsekuensi butir c yang sudah saya sampaikan: versi "diperkuat" hanya ada untuk beras dan daging sapi (lolos U1);
  kedelai, kerbau, telur, ayam, pupuk hanya dua versi (tanpa vs asli) karena aturan "gagal U1 -> data apa adanya";
  daya uji kecil (9 titik awal; ayam/telur/pupuk 3–9 pelapor); makin banyak komoditas makin besar peluang satu lolos
  kebetulan -> lolos tipis dilaporkan "belum bisa diputuskan". Tebakan saya: kebanyakan "tidak menyumbang".
- Urutan kerja bila disetujui: (1) ambil harga PIHPS (15.3); (2) tulis definisi U3 ringkas sebagai berkas
  `binpas/RANCANGAN_U3.md` (target, tiga versi, titik awal, gerbang, sekali jalan, penjaga `U3_SUDAH_JALAN.json`),
  minta persetujuan, commit + push; (3) tulis kode, coba HANYA di titik awal sebelum Des 2025; (4) tanya dulu, lalu U3
  sekali jalan; (5) laporkan apa adanya. Yang belum dirancang: bentuk persis sinyal INATRADE, pemetaan kualitas PIHPS
  ke subkomoditas INATRADE, perlakuan provinsi tanpa pelapor.

### 15.3 Sumber harga: hasil pencarian 17 Nov 2026 (dicoba dari lingkungan sesi; UA bawaan curl/urllib, tanpa akal-akalan)
| Sumber | Hasil | Isi |
| --- | --- | --- |
| **PIHPS BI** (`www.bi.go.id/hargapangan`) | **BISA** | harga per provinsi, harian/mingguan/bulanan; 34 provinsi (Papua dan Papua Barat saja; empat provinsi baru tidak ada) |
| SP2KP Kemendag (`sp2kp.kemendag.go.id`) | halaman terbuka; data lewat `api-sp2kp.kemendag.go.id` dengan auth + reCAPTCHA -> TIDAK dicoba lebih jauh (aturan: jangan akali bot-check) | belum tahu apakah memuat kedelai/kerbau |
| Panel Harga Bapanas (`panelharga.badanpangan.go.id`, `api-panelhargav2...`) | sambungan direset; tidak tersambung | diduga memuat kedelai impor dan daging kerbau beku (belum terbukti) |
| `data.go.id` (dataset "rata-rata harga pangan bulanan tingkat konsumen provinsi", Bapanas) | DITOLAK kebijakan jaringan lingkungan (proxy 403) | perlu host diizinkan di pengaturan lingkungan, atau diunduh pengguna |
| WebAPI BPS | var 254 "Rata-rata Harga Eceran Nasional Beberapa Jenis Barang" hanya NASIONAL TAHUNAN (ayam, sapi, telur, dll.; tanpa kedelai/kerbau); var 79 harga eceran beras 33 kota; tidak ada harga kedelai/kerbau per provinsi | – |
| Belum dicoba (ide) | nilai satuan impor kedelai (dataexim HS 12019000: nilai ÷ berat, bulanan, NASIONAL) sebagai harga pengganti kedelai | – |

**Cara ambil PIHPS (sudah dicoba, berhasil):**
```bash
curl -sS -m 90 -G "https://www.bi.go.id/hargapangan/WebSite/TabelHarga/GetGridDataDaerah" \
  --data-urlencode "price_type_id=1" --data-urlencode "comcat_id=com_3,com_4,com_7,com_8,com_9,com_10" \
  --data-urlencode "province_id=13" --data-urlencode "regency_id=" --data-urlencode "market_id=" \
  --data-urlencode "tipe_laporan=3" --data-urlencode "start_date=2024-01-01" --data-urlencode "end_date=2026-09-30"
```
- `price_type_id`: 1 pasar tradisional, 2 pasar modern, 3 pedagang besar, 4 produsen. `tipe_laporan`: 3 = bulanan.
  `province_id` kosong = rata-rata semua provinsi; satu id = satu provinsi (panggil per provinsi; beri jeda).
- Komoditas: `com_3` Beras Kualitas Medium I, `com_4` Medium II (`com_1`–`com_2` bawah, `com_5`–`com_6` super),
  `com_7` Daging Ayam Ras Segar, `com_8` Daging Sapi Kualitas 1, `com_9` Daging Sapi Kualitas 2, `com_10` Telur Ayam
  Ras Segar; kategori `cat_1` Beras, `cat_2` Daging Ayam, `cat_3` Daging Sapi, `cat_4` Telur Ayam. Lainnya: bawang,
  cabai, minyak goreng, gula. **Tidak ada kedelai, daging kerbau, pupuk.**
- Id provinsi: 1 Aceh, 2 Sumut, 3 Sumbar, 4 Riau, 5 Kepri, 6 Jambi, 7 Bengkulu, 8 Sumsel, 9 Babel, 10 Lampung,
  11 Banten, 12 Jabar, 13 DKI, 14 Jateng, 15 DIY, 16 Jatim, 17 Bali, 18 NTB, 19 NTT, 20 Kalbar, 21 Kalsel, 22 Kalteng,
  23 Kaltim, 24 Kaltara, 25 Gorontalo, 26 Sulsel, 27 Sultra, 28 Sulteng, 29 Sulut, 30 Sulbar, 31 Maluku, 32 Malut,
  33 Papua, 34 Papua Barat. Rujukan: `.../WebSite/TabelHarga/GetRefProvince`, `GetRefCommodityAndCategory`,
  `GetRefPriceType`.
- Jawaban JSON `{"data": [...]}` berbentuk lebar: tiap baris = kategori (`level` 1) atau komoditas (`level` 2), kolom
  `"Jan 2024"` … `"Sep 2026"` (33 bulan, nama bulan Inggris), nilai teks dengan koma ribuan (`"15,750"`).
  Contoh DKI: beras medium I Jan 2024 15.600 -> Sep 2026 17.050; daging sapi kualitas 1 146.650 -> 154.300.
- Panggilan pertama dengan `comcat_id=cat_1` sekali kena "connection reset"; panggilan berikutnya (pakai `com_...`)
  lancar. Bila reset lagi, ulang dengan jeda.
- Yang diambil di sesi 8 hanya uji coba (rata-rata nasional beras, dan DKI enam komoditas); panel 34 provinsi BELUM
  diunduh. Berkas uji coba ada di scratchpad (hilang). Data mentah tidak di-commit.

### 15.4 Akibat untuk U3 bila jadi dijalankan
- Bisa dengan data yang ada: **beras, daging sapi, daging ayam ras, telur ayam ras** (harga PIHPS per provinsi).
- Belum bisa: **kedelai, daging kerbau** (belum ada harga per provinsi; pilihan: Panel Harga Bapanas bila bisa
  tersambung, `data.go.id` bila host diizinkan, atau untuk kedelai nilai satuan impor nasional). **Pupuk** tidak
  bermakna diuji (harga diatur). Bila tetap tidak ada sumber: tulis "tidak bisa diuji" beserta alasannya; itu sesuai
  keinginan pengguna "dilaporkan apa adanya".
- Daging ayam ras: laporan INATRADE baru ada sejak Okt 2024, jadi data latih pendek.

### 15.5 Pilahan untuk laporan magang (sudah disampaikan ke pengguna 17 Nov 2026)
- **Sudah final, bisa dilaporkan:** Tahap 0; validasi satuan (tanpa kode perusahaan); cakupan volume tujuh komoditas;
  adu versi + U1 (termasuk yang gagal); U2 beras; model stok beras + prakiraan (level 2024–2026 belum tervalidasi);
  cara kerja (ambang dikunci dulu, ujian sekali jalan); notebook tunggal sebagai lampiran.
- **Belum diputuskan:** U2 daging sapi; 79 kombinasi + peubah luar; pembaruan Claude Doc laporan ringkas; bentuk dan
  cakupan U3 (15.2 butir a–c).
- **Masih bisa di-run:** U2 daging sapi (±30–60 menit); 79 kombinasi + impor kedelai/daging sapi (±1–2 jam, calon
  resep saja); lanjutan model stok kedelai; U3 ringkas bila disetujui. Semua perkiraan waktu = tebakan.
- **Masuk keterbatasan/saran lanjutan bila tidak sempat:** ujian resep versi 2 (butuh data s.d. ±Mar 2027); U3 penuh;
  U2 komoditas tanpa publikasi BPS.
- **Harus ditulis apa adanya:** "lolos" = menutup laporan bolong secara konsisten, bukan bukti mewakili pasar; acuan
  "memburuk ≤ 20%" provinsi beras diputuskan sesudah hasil dilihat (+13% dan +28% sama-sama dilaporkan); koreksi satuan
  tiga perusahaan = perkiraan dari data; resep daging sapi dan kerbau hasil turun peringkat.
- Belum diketahui: tenggat, format, kerangka bab laporan magang.

### 15.6 Lingkungan sesi 8 (untuk sesi baru)
- Terpasang di sesi 8 dan perlu diulang: `pip install nbclient nbformat ipykernel matplotlib`. Sudah ada: Python
  3.13.18, numpy 2.5.3, pandas 3.0.5, openpyxl 3.1.5. Belum ada: scipy, scikit-learn, catboost, quantile-forest,
  statsmodels, pdfplumber (hanya perlu untuk penyetelan beras penuh / ekstraksi PDF).
- `BPS_API_KEY` ada sebagai env var. WebSearch dan WebFetch tersedia (muat lewat ToolSearch). Jaringan lewat proxy
  berkebijakan: `data.go.id` ditolak; `bi.go.id`, `sp2kp.kemendag.go.id`, `webapi.bps.go.id` terbuka.
- Branch kerja: `claude/bayesian-rice-stock-model-qmunfn` (sesi 8 mendorong langsung ke sana atas perintah pengguna,
  walau lingkungan menunjuk branch lain sebagai bawaan). Tanpa PR.
- Pedoman grafik yang dipakai notebook: palet biru `#2a78d6`, oranye `#eb6834`, aqua `#1baf7a`, permukaan `#fcfcfb`;
  satu sumbu, batang tipis, label seperlunya (fungsi di sel "fungsi grafik" `buat_notebook.py`).

## 16. Sesi 9 (23–26 Nov 2026): bahan bimbingan dosen, penjelasan beras, kemungkinan tugas akhir
Tidak ada ujian, penyetelan, atau model yang dijalankan. Yang dijalankan hanya: pembuatan gambar/dokumen, pembacaan ulang
xlsm untuk angka agregat, dan pengambilan ulang data BPS (`ambil_bps.py`) untuk grafik produksi vs konsumsi.

### 16.1 Google Doc bahan bimbingan dosen (23 Nov 2026)
- [Estimasi Stok dan Penguatan Data Distribusi Beras (bahan bimbingan)](https://docs.google.com/document/d/17JMV-rw9R_suBzrOpngQ1x485XmDJL1LqJjlwJm942U/edit),
  6 halaman (batas pengguna 7), beras saja. Isi: permasalahan (5 masalah INATRADE + 3 rumusan masalah), tabel sumber
  data, diagram alir metodologi (gaya contoh pengguna: Mulai → Pengumpulan → Eksplorasi → Preprocessing → Blok waktu →
  Pengembangan Model → 3 cabang → Evaluasi → Gerbang → Interpretasi → Selesai), evaluasi (tabel gerbang), hasil (U1
  tabel per tingkat, stok, U2 tabel), keterbatasan + U3 sebagai langkah berikut.
- Dibuat dari `binpas/bimbingan/buat_docx.py` + `diagram.py` (`diagram_alir.png`), lalu diedit langsung di Google Docs
  (lebar tabel; 3.1–3.3 dipindah sebelum diagram supaya tidak ada halaman setengah kosong).
- Atas permintaan pengguna, kalimat "Validasi" di 5.2 diganti (24 Nov) menjadi: "...model memprediksi bacaan survei 4,40
  juta ton (3,43–5,59), dan angka survei 4,06 juta ton masih di dalam interval. Uji ini memeriksa konsistensi perubahan
  stok selama 2023, bukan level absolut, karena bias survei diestimasi model. Konsumsi total 2024 menurut model (29,79
  juta ton) sesuai dengan angka konsumsi total BPS 2024 (29,80 juta ton) yang tidak dipakai saat estimasi." Skrip di repo
  sudah disamakan.
- Nama Bu Fitria dan kode perusahaan tidak dicantumkan; nama pengguna (Harits) dan instansi ada di baris pembuka.

### 16.2 Penjelasan yang sudah diberikan ke pengguna (di chat; ringkas di sini supaya konsisten bila ditanya lagi)
- **Validasi model stok (holdout SSBAT Des 2022):** model dijalankan dua kali; run holdout membuang SSBAT Des 2022;
  survei dimodelkan `log(survei) = log(stok model) + bias_sumber + galat 5%`, bias SSBAT dipakai bersama oleh dua SSBAT.
  Tanpa Des 2022, bias SSBAT disetel dari Des 2023 saja, sehingga uji ini menguji perubahan stok selama 2023 (neraca),
  bukan level. Prediksi 4,40 = prediksi BACAAN survei, bukan stok sebenarnya. Konsumsi 29,79 vs 29,80: angka BPS tidak
  dipakai saat estimasi, tetapi prior porsi non-RT dari neraca Bapanas (2,591 juta ton/bulan, ±10%) sudah mengarahkan.
- **Temuan penting (baru dijelaskan di sesi 9):** SCBN BPS Jun 2022 (9,71) dan SSBAT Des 2022 (4,06) saling bertentangan
  (stok tidak mungkin turun separuh dalam 6 bulan menurut neraca). Posterior: bias SCBN −0,06 (≈ tanpa bias), bias SSBAT
  −0,68 (survei ≈ 0,51 × stok model). Model memilih level yang cocok dengan SCBN + neraca; mana yang benar belum bisa
  dipastikan. Ini alasan utama level 14,2 juta ton belum tervalidasi.
- **U2 fundamental:** U1 menguji INATRADE terhadap dirinya sendiri; U2 terhadap patokan luar (Pola Distribusi BPS).
  Gerbang diganti ke perbandingan jalur karena BPS tidak menerbitkan pangsa; dikunci sebelum edisi 2025 dibuka.
  Pertanyaan yang adil: apakah INATRADE menambah informasi di atas BPS tahun lalu (jalur cenderung tetap: 85 dari 104).
  AP dipakai karena jalur jarang (9%). Bootstrap per provinsi tujuan.
- **Rincian U2 (dihitung sesi 9 dari data yang sama, `binpas/penjelasan_beras/angka.py`):** pasangan yang ada di BPS 2024
  DAN INATRADE: 31/42 = 74% muncul di BPS 2025; hanya BPS 2024: 54/108 = 50%; hanya INATRADE: 8/35 = 23%; tidak di
  keduanya: 11/937 = 1%. Ini yang membuat AP gabungan naik. Volume asal INATRADE: Jawa Timur 67%, DKI 18%, Jawa Tengah
  13%; BPS 2025 asal terbanyak: Jawa Timur 19, Jawa Tengah 16, Sulawesi Selatan 13 (tidak ada di INATRADE). Spearman 0,20.
- **5.1 (U1 beras):** dijelaskan per baris tabel: sel-bulan, CRPS (≈ galat persen skala log), perbaikan, bias (P\*
  kekurangan karena yang hilang tidak diisi), arah, cakupan + Wilson n efektif, "memburuk ≤ 20%" (+13% vs +28% menurut
  acuan), gerbang konsisten (bootstrap per bulan, wilayah −0,134…−0,075). Pola hapus: lubang tengah ±7–8% per
  perusahaan-bulan; lubang akhir 20% kecil / 9% besar.
- **Bagian 3 (metodologi):** dijelaskan tiap langkah: Tahap 0, preprocessing, blok waktu (= train/validation/test),
  7 tahap adu 79 kombinasi dengan daftar 11 metode isian (B, C, R1–R4, R5 QRF, R6 CatBoost 3 varian, R7 MRP), tambahan
  1c (kalender Lebaran+panen, ragam per kelompok, tdist, pola, ciri perusahaan, peubah luar), model stok (persamaan,
  prior, pengukuran, kenapa Bayesian, kenapa mulai Jun 2022, r-hat 1,06).
- **Kenapa interpolasi menang (angka baru sesi 9):** laporan satu perusahaan berubah median ±27% per bulan; tebakan
  interpolasi per perusahaan meleset median ±20% (laporan terakhir ±25%); tetapi total wilayah hanya ±2,1% (P\* ±14,5%)
  karena hanya sedikit perusahaan bolong sekaligus, sebagian besar total adalah laporan yang ada, dan galat saling
  menutup. P\* buruk karena ukuran perusahaan timpang (Jawa: 5 terbesar 92%).

### 16.3 Teks presentasi dan pertanyaan untuk dosen (diberikan di chat 24 Nov 2026, tidak disimpan sebagai file)
- Teks presentasi ±8–10 menit mengikuti doc bimbingan: pembuka → permasalahan → data → metodologi (sambil menunjuk
  diagram) → evaluasi → hasil → keterbatasan dan U3.
- Pertanyaan untuk dosen (10, saran prioritas 1, 3, 6, 9, 5): (1) beras saja cukup atau semua komoditas setara;
  (2) tiga cabang jadi satu kajian atau satu fokus; (3) apakah simulasi hapus-tebak cukup kuat; (4) CRPS cukup atau
  perlu MAPE/RMSE; (5) cara menulis acuan "memburuk" yang diputuskan sesudah hasil; (6) level stok tak tervalidasi:
  cukup keterbatasan atau fokus ke tren; (7) skenario kepekaan cukup; (8) penggantian gerbang U2 diterima;
  (9) U3 realistis dalam waktu magang atau saran lanjutan; (10) temuan "interpolasi menang atas ML" ditonjolkan.
- Hasil bimbingan belum diketahui (pengguna belum melapor).

### 16.4 Kemungkinan tugas akhir (dijawab 24 Nov 2026)
- Jawaban: layak untuk S1. Rekomendasi bingkai: **A = perbandingan metode imputasi laporan distribusi yang tidak lengkap
  (studi kasus INATRADE beras) sebagai inti**, C = keterwakilan terhadap survei BPS sebagai bab pendukung, B = model stok
  Bayesian sebagai bab tambahan/saran (levelnya sulit dipertahankan di sidang). Komoditas lain = satu bab penerapan.
- Tiga syarat yang disampaikan: (1) izin tertulis Kemendag memakai data INATRADE (hanya agregat, tanpa kode/nama
  perusahaan; tanya soal publikasi di repositori kampus); (2) cek aturan kampus soal bantuan AI dan pastikan pengguna bisa
  menjelaskan setiap pilihan metode tanpa catatan; (3) yang kurang untuk standar TA: tinjauan pustaka (imputasi data
  survei usaha, proper scoring rule/CRPS, prediksi konformal, state-space Bayesian), bab metodologi formal dengan notasi,
  pembahasan kebijakan. Jurusan pengguna belum diketahui.

### 16.5 Google Doc penjelasan bergambar beras untuk pengguna (25 Nov 2026)
- [Beras: apa yang dikerjakan, datanya, caranya, dan hasilnya (penjelasan bergambar)](https://docs.google.com/document/d/1z9B4ncCgNmemr3s6w3kCf2nW--09F2iZ_y6ho7wGBzU/edit),
  15 halaman, 19 gambar, tiap gambar ada "Cara membaca". Bagian: ringkasan + peta besar; data (tabel, pelapor per bulan,
  panjang lubang, identitas stok, cakupan 2–3%); menambal laporan (ilustrasi simulasi, interpolasi vs P\*, ilustrasi
  CRPS, hasil U1, sebaran galat, kenapa); stok (diagram neraca, produksi vs konsumsi + musim, stok + prakiraan,
  komposisi + per pulau, uji survei, kepekaan); jalur (AP, 74/50/23%, provinsi asal); rangkuman; kamus istilah.
- Gambar 5, 6, 7 = ilustrasi dengan angka contoh (diberi label), lainnya data/hasil asli.
- Skrip: `binpas/penjelasan_beras/angka.py` (baca `laporan.csv` Tahap 0 + xlsm → angka agregat `angka.json`,
  `u2_asal.csv`), `grafik.py` (19 PNG; butuh data BPS dari `ambil_bps.py` dan `beras_stok/stok_beras_satu_file.py` untuk
  posterior stok), `dok.py` (docx). PNG ada di `binpas/penjelasan_beras/grafik/`. Sesudah upload, lebar tabel diperbaiki
  dengan `updateTableColumnProperties`.
- Hasil posterior stok bisa dibaca tanpa menjalankan model: `muat_hasil()` di `beras_stok/stok_beras_satu_file.py`
  (11.088 baris: skenario dasar / swasta>=0 nasional / per provinsi / validasi; tingkat provinsi/pulau/nasional;
  komponen total/bulog/swasta/rumah_tangga/penggilingan/pedagang/horeka; Jan 2024–Sep 2026; median, p05, p95). Daftar
  `VALIDASI` dan `PARAMETER` (bias survei, susut, dll.) ada di file yang sama.

### 16.6 Lingkungan sesi 9
- Perlu dipasang ulang bila diperlukan: `pip install matplotlib nbclient nbformat ipykernel` (python-docx sudah ada).
  `BPS_API_KEY` ada di env. Google Drive dan Google Docs connector aktif (create_file dengan file reference
  `sha256:<hash>:<path>`; read_doc besar tersimpan ke file → pakai `docs_index.py` dari skill google-workspace).
- Folder scratchpad sesi 9 (data BPS, render PDF, keluaran Tahap 0) hilang saat sesi berakhir; semua yang perlu sudah
  di repo atau bisa dibuat ulang.

## 17. Sesi 10 (26 Nov 2026): rencana prakiraan stok beras Nov–Des 2026, dijalankan LIVE di Google Colab
Belum ada yang dijalankan. File data baru: `Cleaning_Lengkap.xlsm` s.d. Okt 2026 (hash dan hasil cek di bagian
"File yang harus diunggah ulang").

### 17.1 Permintaan pengguna
- Tugas: **beras saja**, "semua dimulai dari awal" dengan data INATRADE s.d. Okt 2026, **meramal stok sampai Nov dan
  Des 2026**. Yang diramal = stok beras total (model stok Bayesian + `prakiraan.py`). Ramalan angka laporan INATRADE
  dan harga (U3) BELUM punya model; jangan disajikan seolah tinggal run.
- Cara kerja yang diminta: agen menjalankan semuanya **langsung di Google Colab** (lewat ekstensi Claude in Chrome) supaya
  pengguna melihat kode yang dijalankan secara real time. Pola tiap langkah: **teks rencana singkat → tulis kode →
  jalankan → tampilkan output → interpretasi bahasa sederhana (kenapa hasilnya begitu) → alasan langkah berikut**. Di
  titik keputusan, berhenti, beri pertanyaan + rekomendasi, tunggu jawaban, baru lanjut.
- Notebook itu sendiri = catatan kerja: interpretasi dan keputusan ditulis di sel teks (markdown) di notebook, bukan
  hanya di panel chat.

### 17.2 Susunan di Drive dan Colab
- Drive: `MyDrive/beras_live/` berisi `data/Cleaning_Lengkap.xlsm` (diunggah pengguna) dan notebook baru
  `prakiraan_beras_live.ipynb` (dibuat agen). Keluaran ke `MyDrive/beras_live/keluaran/`.
- Kode: repo publik, jadi di Colab `!git clone -b claude/bayesian-rice-stock-model-qmunfn https://github.com/harits766/tess`
  (tanpa token). Data publik (`jangkar_publik.csv`, `binpas/data_publik/`) ikut dari repo.
- Pustaka: kode diuji dengan pandas 3.0.5; model stok butuh `pymc>=5.20` dan `nutpie`, ditambah `openpyxl`. Lihat cara
  notebook 05 (`pip --target` + subprocess) atau pasang lalu restart runtime sekali di awal.
- Kunci BPS: **Colab Secrets** bernama `BPS_API_KEY` (diisi pengguna sendiri, akses notebook dinyalakan);
  `os.environ['BPS_API_KEY'] = userdata.get('BPS_API_KEY')`; jangan pernah dicetak.
- Cek sha256 xlsm di awal (harus `335c7e6e…`).

### 17.3 Langkah dan titik berhenti (usulan)
1. Persiapan: mount Drive, clone, pasang pustaka, cek hash. **Berhenti:** konfirmasi lingkungan siap.
2. Perpanjang periode ke Okt 2026 (sel kode yang memperlihatkan perubahan): `binpas/tahap0.py` `PER`,
   `beras_stok/model_stok.py` `AKHIR`, `beras_stok/ambil_bps.py` (bulan potensi), `beras_stok/prakiraan.py` `BULAN`
   = Nov–Des dan sumber produksi Des. Perlakuan khusus BULOG Sep 2026 tetap; cek Okt (stok awal 4,49 / akhir 4,43).
3. Tahap 0 dengan data baru → interpretasi (pelapor Okt, lubang akhir). Laporan bolong Okt ditambal dengan resep beras
   yang DIKUNCI (`hasil_adu_beras/resep.json`, tidak disetel ulang); hasil di Okt hanya "cek bulan baru", bukan ujian.
4. Panel INATRADE (`inatrade_panel.py`) + data BPS (`ambil_bps.py`): cek apakah KSA Okt–Des 2026 (angka potensi) sudah
   ada. **Berhenti:** bila Des belum ada, pakai Des 2025 × faktor acak (cara lama) atau tunggu.
5. Stok BULOG publik Okt/Nov 2026 dicari di web (berita BULOG/Bapanas) → baris baru `jangkar_publik.csv` dengan sumber.
   **Berhenti:** tunjukkan angka + sumber.
6. Model stok dipasang ulang Jun 2022 → Okt 2026 (±20–40 menit di Colab 2 CPU). Cek konvergensi (r-hat, divergensi).
   **Berhenti sebelum run** (sebut lama), lalu interpretasi sesudahnya; bandingkan dengan hasil lama (Sep 14,2;
   prakiraan lama Okt 13,6 / Nov 12,5 / Des 11,1).
7. Prakiraan Nov–Des + provinsi rawan → interpretasi + grafik. **Berhenti:** tawarkan kepekaan (swasta ≥ 0 per
   provinsi/nasional, tanpa INATRADE; ±13 menit per skenario) dan holdout.
8. Ringkasan akhir di notebook (angka, rentang, batas: level belum tervalidasi, prakiraan belum di-backtest). Ramalan
   Nov–Des bisa dicek nanti dengan BULOG/INATRADE Nov–Des (ujian ramalan sungguhan; catat tanggal dibuat).
- Perubahan kode dibuat di Colab; agar masuk repo, simpan patch/berkas ke Drive dan commit dari sesi Claude Code
  (agen ekstensi Chrome tidak punya akses push).

### 17.4 Varian "semua ulang dari nol" (ditanyakan pengguna 26 Nov 2026) — **PENGGUNA MEMILIH A** ("A aja")
- Pengumpulan data dari nol di Colab bisa, kecuali INATRADE (sistem internal: satu-satunya file dari pengguna) dan kunci
  BPS (Colab Secrets). BPS lewat WebAPI dari Colab (`ambil_bps.py`); angka publik `jangkar_publik.csv` (survei stok
  2022/2023, stok BULOG, impor, konsumsi Bapanas) dibangun ulang dengan membuka tiap sumber di browser dan dicocokkan,
  ditambah stok BULOG Okt/Nov 2026; Poldis BPS dan PIHPS tidak perlu untuk prakiraan stok.
- Tingkat yang ditawarkan: **A (rekomendasi)** data dari nol + Tahap 0 + tambal dengan resep terkunci + model stok +
  prakiraan (±1,5–2,5 jam termasuk mengetik live, tebakan); **B** = A + penyetelan adu versi beras dari nol (79
  kombinasi; butuh catboost, quantile-forest, statsmodels, scikit-learn; resmi ±1 jam 21 menit di 4 CPU, di Colab 2 CPU
  diperkirakan ±2,5–3 jam) sebagai PERAGAAN/REPLIKASI: blok penyetelan sama (Jan 2024–Jun 2025) sehingga resep
  diharapkan sama; bila berbeda, dilaporkan, resep resmi tidak diganti; **U1/U2 tidak dijalankan sebagai ujian**
  (boleh ditampilkan sebagai replikasi berlabel, seperti notebook 05). Ujian baru hanya sah di bulan sesudah data yang
  dipakai menyetel.

### 17.5 Pertanyaan pengguna: U1+U2 cukup atau lanjut U3? (26 Nov 2026) — pengguna: "lanjut U3"; draf
`binpas/RANCANGAN_U3.md` (USULAN, belum dikunci) + teks WA Bu Fitria butir a–c dibuat; tunggu jawaban beliau
- Jawaban: U1+U2 menjawab "datanya bisa dipercaya sampai mana" (cukup untuk laporan magang dan bingkai TA A);
  U3 menjawab "datanya berguna untuk meramal harga atau tidak" (nilai guna; tambahan). Prakiraan stok Nov–Des (sesi
  live A) BUKAN U3.
- U3 beras-saja bisa, tetapi HARUS DIBANGUN DULU. Usulan urutan: (1) selesaikan sesi live A; (2) di sesi Claude Code:
  tulis `binpas/RANCANGAN_U3.md` versi ringkas beras saja (15.2; tiga versi tanpa/asli/diperkuat karena beras lolos
  U1), teks WA Bu Fitria butir a–b (model ringkas; gerbang BPS 2025 dilepas), kunci + push; (3) sesi live Colab kedua:
  ambil PIHPS beras 34 provinsi, bangun model, coba hanya di titik awal sebelum Des 2025, tanya dulu, U3 sekali jalan.
- Dengan data s.d. Okt 2026 dan PIHPS s.d. Okt/Nov, titik awal bisa diperpanjang sampai ±Sep 2026 (putuskan SEBELUM
  dikunci). Perkiraan yang disampaikan: hasil paling mungkin "tidak menyumbang" atau "belum bisa diputuskan"
  (cakupan volume 1,5–3%, daya uji kecil); tetap layak dilaporkan apa adanya. Waktu: ±setengah hari kerja (tebakan).

## Langkah berikut yang masih terbuka
Urutan menurut yang paling dekat dengan permintaan terakhir pengguna:
0. **Bimbingan dosen / tugas akhir (sesi 9):** tunggu laporan pengguna soal hasil bimbingan (jawaban dosen atas
   pertanyaan 16.3, apakah bingkai TA 16.4 diterima). Bila diminta: perbarui doc bimbingan atau doc penjelasan (keduanya
   bisa diedit di tempat; link tetap), siapkan bab TA (tinjauan pustaka, metodologi formal), atau jelaskan bagian lain
   dengan gaya sesi 9 (bahasa sederhana + gambar).
1. **U3 tetap ada** (bagian 15.2–15.4). Langkah berikut yang paling dekat: unduh panel harga PIHPS 34 provinsi untuk
   beras, daging sapi, daging ayam ras, telur ayam ras (bagian 15.3; itu pengambilan data, tetap bilang dulu sebelum
   jalan); tulis `binpas/RANCANGAN_U3.md` (definisi U3 ringkas) untuk disetujui dan dikunci; siapkan teks WA Bu Fitria
   butir a–c bila diminta. Jangan menulis/menjalankan kode U3 sebelum definisinya dikunci.
2. Cari lagi harga kedelai dan daging kerbau per provinsi (Panel Harga Bapanas, `data.go.id`) tanpa meminta pengguna
   mengekspor data; bila tetap tidak ada, catat "tidak bisa diuji".
3. Tawaran yang belum dijawab: U2 daging sapi (rekomendasi saya; definisi dikunci dulu, sekali jalan; edisi BPS 2025
   dan 2018); 79 kombinasi + peubah luar impor untuk kedelai/daging sapi.
4. Laporan magang: tenggat dan kerangka bab belum diketahui; pilahan isi di bagian 15.5.
5. Notebook tunggal (bagian 14.0): selesai dan terkirim; menunggu laporan pengguna sesudah dicoba di Colab.
6. Ujian versi 2 kedelai, daging kerbau, telur ayam ras — menunggu data sesudah Sep 2026 (`RANCANGAN_V2.md` bagian 4).
7. Perbarui Claude Doc laporan ringkas dengan resep versi 2 dan cakupan volume (bila diminta).
8. Belum dikerjakan dari rancangan: skor tingkat perusahaan, agregasi triwulanan, CRPS dalam ton, korelasi Harga Jual
   vs PIHPS (sekarang bisa, karena PIHPS bisa diambil).
9. Pekerjaan lama yang masih terbuka: ganti nama "susut" -> "selisih tak tercatat"; `beras_stok/inatrade_panel.py`
   masih mengambil nilai terbesar untuk laporan berkepala ganda (keputusan: dijumlah); backtest bergulir model beras
   (±3–4 jam, tanya dulu); kedelai: prakiraan, varian PAW, holdout USDA.

## Pesan pembuka sesi baru (unggah juga file INATRADE)
```
Lanjutkan pekerjaan di repo harits766/tess, branch claude/bayesian-rice-stock-model-qmunfn.
Baca dulu SERAH_TERIMA.md dari atas: "STATUS TERKINI", "Pengguna dan cara kerja" (termasuk "Pelajaran sesi 9" dan
"Pelajaran sesi 8"), lalu bagian 9–16. Bagian 16 = sesi terakhir (doc bimbingan dosen, penjelasan bergambar beras,
kemungkinan tugas akhir); bagian 15 = U3 dan data harga PIHPS.
Baca juga binpas/ambang_ujian.md, binpas/HASIL_ADU_BERAS.md, binpas/RANCANGAN_U2.md, binpas/HASIL_ADU_KOMODITAS.md,
binpas/RANCANGAN_V2.md, binpas/HASIL_CAKUPAN_KOMODITAS.md, binpas/HASIL_VALIDASI_SATUAN.md,
binpas/RANCANGAN_INATRADE.md bagian 7.6, beras_stok/CATATAN_SESI.md.
File INATRADE terlampir (Non_PAW_dari_nol.xlsm). Ikuti aturan di "Pengguna dan cara kerja".
Semua ujian akhir (U1) dan U2 beras sudah terpakai: jangan dijalankan lagi. Jangan menjalankan apa pun tanpa diminta.
Jangan minta saya menyediakan data: cari sendiri sumber terbuka dulu. Jelaskan dengan bahasa sederhana dan gambar.
Tugas sekarang: <isi tugas, mis. "hasil bimbingan dosen: ...">.
```
