# Catatan serah-terima: model stok beras

## Target (sudah disepakati)
- Stok beras **total** (rumah tangga + penggilingan + pedagang + BULOG + horeka), **bulanan**, Jan 2024 – Sep 2026.
- Level **provinsi** (model hierarkis), dilaporkan juga **per pulau**.
- Output: (1) bagian baru di dokumen "Estimasi Stok & Faktor Harga Beras"
  https://claude.ai/artifact/SVxGikX6P5haRF9QLhZwur, (2) kode PyMC di folder ini, (3) tabel Excel posterior
  per provinsi per bulan (median, interval 90%, per komponen), (4) tab baru di dashboard "Monitor Harga Non PAW"
  https://claude.ai/artifact/6Gz4r55DxMahU9KiAp8Nn7.

## Status (sesi 2, 5 Nov 2026) — keempat output sudah dibuat
- Kode: `ambil_bps.py`, `jangkar_publik.csv`, `model_stok.py`, `tabel_excel.py`, `ekspor_dashboard.py`,
  `diagnostik.py` (urutan menjalankan di README).
- Dokumen: bagian "Model Bayesian stok per provinsi" (grafik bulanan, tabel pulau, cara kerja, uji, keterbatasan)
  + satu butir di ringkasan atas.
- Dashboard: tab "Stok beras" (dataset `stok_beras` dan `stok_ringkas`, file JSON dari `ekspor_dashboard.py`).
- Excel: `stok_beras_posterior.xlsx` dikirim ke pengguna (tidak disimpan di repo).

## Hasil skenario dasar
- Stok nasional akhir Sep 2026: **14,2 juta ton (11,3–18,6)**; BULOG 4,65 (4,29–5,04); swasta 9,6 (6,7–14,0).
- Setara Sep 2025 (14,4), tetapi bergeser ke BULOG. Terendah tiap Jan–Feb, naik setelah panen Mar–Apr.
- Susut 7,1% (4,3–9,9%); konsumsi total ≈ 1,41 × konsumsi RT Susenas (≈ 2,6 juta ton/bulan).
- Survei SSBAT ≈ separuh level model (bias log −0,68); SCBN BPS Jun 2022 hampir tanpa bias.
- Validasi: SSBAT Des 2022 disembunyikan → prediksi 4,40 (3,43–5,59) vs amatan 4,06.
- Sensitivitas kendala "swasta ≥ 0": per pulau (dasar) 14,2 (11,3–18,6); nasional saja 14,2 (11,4–19,1);
  per provinsi 16,8 (14,0–21,3). **Ini pilihan model yang paling menentukan level.**
- Konvergensi dasar: nutpie, 4 rantai × 1.000, 0 divergensi, r-hat maks sel stok 1,06.

## Keputusan model yang penting (dan alasannya)
- Model mulai akhir Jun 2022 agar tiga survei stok bisa dipakai (SCBN Jun 2022 9,71; SSBAT Des 2022 4,06,
  Des 2023 4,13). Tiap sumber punya bias sendiri.
- Kendala swasta ≥ 0 per **provinsi** menggelembungkan level (model arus terlalu kasar) → dipakai per **pulau**,
  plus stok total provinsi ≥ 0.
- Guncangan proses provinsi dibuat berjumlah nol (arus tak termodel), σ prior HalfNormal(0,05).
- INATRADE pedagang diagregasi per pulau; per provinsi membuat posterior bimodal (pelapor berganti-ganti).
- Pengaruh INATRADE (stok nasional akhir Sep 2026; dasar 14,2): tanpa INATRADE 15,1; baris Non PAW saja 13,4;
  baris PAW saja 16,4. Non PAW = Provinsi Perusahaan = Provinsi Penyaluran; PAW = beda provinsi (antar provinsi).
  BULOG tidak berubah (4,62–4,65). Opsi: `inatrade_panel.py ... nonpaw|paw`, `model_stok.py --tanpa inatrade,bulog_inatrade`.
- max(·,0) di defisit/surplus dihaluskan (softplus); noise BULOG tetap 5% — keduanya untuk menghilangkan divergensi.

## Akses data
- BPS: WebAPI dengan env var `BPS_API_KEY`. Var: 2506 (produksi bulanan 2025–2026), 1498 (tahunan ≤2024),
  2094 (Susenas kab/kota), 2790 (penduduk kab/kota), 500/2277 (harga penggilingan ≤2025; 2026 belum ada).
- Panel harga Bapanas (`api-panelhargav2.badanpangan.go.id`): koneksi diputus dari lingkungan ini → harga per
  provinsi belum masuk model.
- File input dari pengguna (unggah ulang di session baru): `Non_PAW_dari_nol.xlsm`,
  `Non_PAW_Gabungan_2024-2026_Sep2026.xlsx`.

## Langkah lanjut yang paling berguna
1. Hasil SSBAT akhir 2024/2025 (bila ada) → jangkar level baru; akan mempersempit interval paling banyak.
2. Produksi KSA bulanan 2022–2024 per provinsi dan impor bulanan (BPS) menggantikan pola 2025/pembagian rata.
3. Stok BULOG per kanwil → komponen BULOG per provinsi tidak lagi alokasi.
4. Harga per provinsi (panel Bapanas) sebagai sinyal ketatnya pasar per provinsi.
