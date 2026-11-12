# Hasil Tahap 0: profil data INATRADE (12 Nov 2026)

Skrip: `python -I binpas/tahap0.py <Non_PAW_dari_nol.xlsm> <keluaran> <keluaran ambil_bps.py>` (±10 detik).
File INATRADE: unggahan sesi 11 Nov 2026 (sha256 `c667dddba86bdfb6…`), sheet "2024-2026". Hanya memprofil data;
tidak ada metode yang dinilai. Angka per perusahaan tidak disimpan di repo.

## 1. Ukuran data
- 27.665 baris -> 9.479 laporan (perusahaan × komoditas × subkomoditas × bulan), **315 kode perusahaan**, 16 komoditas,
  Jan 2024–Sep 2026.
- Pelapor per komoditas: minyak goreng 111, beras 91, kedelai 73, daging sapi 73, gula 72, tepung terigu 68,
  daging kerbau 22, pupuk 17, bawang putih 15, lainnya ≤ 12.
- **Patahan struktur:** 209 dari 315×komoditas pelapor baru pertama muncul Okt–Des 2024. Pelapor beras per bulan:
  11–15 (Jan–Sep 2024) -> 31 (Okt 2024) -> 47–66 (Nov 2024–Sep 2026).
- 441 laporan (4,7%) memuat beberapa "kepala laporan" berbeda untuk kunci yang sama (bukan beda kab/kota). Di skrip
  dijumlah; kode lama (`beras_stok/inatrade_panel.py`) mengambil yang terbesar. Selisih total penyaluran 2%.
  **Perlu konfirmasi pengguna: satu kode bisa memuat beberapa unit usaha?**
- Tanggal Lapor selalu tanggal 15 bulan berikutnya -> keterlambatan lapor tidak bisa diukur dari data.

## 2. Kehadiran
- Median kehadiran pelapor saat aktif 93–97%; porsi perusahaan-bulan bolong saat aktif: beras 15%, minyak goreng 15%,
  gula 15%, tepung 19%, daging sapi 20%, kedelai 23%.
- Lubang di tengah kebanyakan 1 bulan (beras: 83 lubang 1 bulan, 16 dua bulan, 17 lebih panjang).
- Lapor di Sep 2026: beras 62%, minyak goreng 66%, daging sapi 75%, kedelai 36%. Diam > 3 bulan: beras 22%, kedelai 56%,
  pupuk 77% (53% pelapor pupuk dan 37% pelapor kedelai hanya lapor 1 bulan).
- Beras per pulau (rata-rata pelapor per bulan, 2026): Sumatera ±29, Jawa ±22, Maluku & Papua ±4, Kalimantan ±2,
  Bali & Nusa Tenggara ≤ 1, Sulawesi < 1. **Tingkat pulau hanya bermakna untuk Jawa dan Sumatera.**

## 3. Sel hampir lengkap (aktif ≥ 3)
Jumlah sel-bulan dengan pelapor ≥ 90% (≥ 85%) dari aktif. aktif0 = bulan pertama..terakhir lapor; aktif3 = + tenggang 3 bulan.

| Komoditas | Tingkat | Penyetelan aktif0 | Penyetelan aktif3 | Kalibrasi aktif0 | Ujian aktif0 | Ujian aktif3 |
| --- | --- | --- | --- | --- | --- | --- |
| Beras | pulau | 10 (16) dari 35 | 10 (14) | 5 (7) dari 18 | 18 (21) dari 32 | 8 (10) |
| Beras | provinsi | 28 (31) dari 74 | 26 (29) | 17 (27) dari 42 | 34 (46) dari 63 | 18 (30) |
| Beras | nasional | 3 (7) dari 18 | 2 (6) | 0 (3) dari 6 | 4 (5) dari 9 | 0 (1) |
| Minyak goreng | pulau | 19 (25) dari 50 | 14 (16) | 10 (12) dari 24 | 20 (23) dari 39 | 13 (17) |
| Gula | pulau | 18 (22) dari 36 | 14 (18) | 4 (6) dari 12 | 12 (16) dari 25 | 6 (10) |
| Daging sapi | pulau | 19 (20) dari 44 | 18 (20) | 6 (6) dari 18 | 15 (17) dari 27 | 12 (13) |
| Tepung terigu | pulau | 10 (13) dari 45 | 7 (10) | 4 (6) dari 18 | 17 (19) dari 31 | 13 (16) |
| Kedelai | pulau | 7 (17) dari 28 | 7 (10) | 1 (1) dari 12 | 2 (5) dari 18 | 1 (1) |

- Aturan 7.2 terpicu untuk semua komoditas: < 30 sel-bulan di tingkat pulau -> **ambang 85%**. Sesudah diturunkan pun
  jumlahnya tetap kecil (beras 16 sel-bulan penyetelan, 7 kalibrasi).
- Definisi aktif sangat berpengaruh di blok ujian (beras pulau 18 vs 8): dengan aktif0, perusahaan yang berhenti lapor
  di bulan-bulan terakhir dianggap "berhenti", sehingga bulan terakhir tampak lengkap padahal belum tentu.

## 4. Identitas stok
- Dalam bulan (Stok Akhir = Stok Awal + Pengadaan − Penyaluran): **100% tepat** di semua komoditas (dipaksa sistem).
- Antarbulan (Stok Awal[t] vs Stok Akhir[t−1]), laporan berurutan:

| Komoditas | Pasangan | Tepat | ≤ 5% | 5–25% | > 25% | Awal lebih kecil | Awal lebih besar |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Minyak goreng | 1.551 | 85% | 4% | 3% | 8% | 9% | 7% |
| Kedelai | 374 | 81% | 6% | 9% | 4% | 10% | 9% |
| Tepung terigu | 728 | 80% | 8% | 5% | 8% | 14% | 7% |
| Gula | 776 | 77% | 8% | 6% | 9% | 13% | 10% |
| Beras | 1.187 | 76% | 8% | 4% | 12% | 15% | 9% |
| Daging sapi | 865 | 35% | 19% | 16% | 30% | 37% | 28% |
| Daging kerbau | 302 | 25% | 17% | 28% | 31% | 47% | 28% |
| Ikan segar | 213 | 15% | 10% | 13% | 62% | 41% | 45% |

## 5. Konsentrasi (penyaluran, blok penyetelan)
- Beras: Jawa 24 perusahaan, 5 terbesar 92%; Sumatera 40 perusahaan, 5 terbesar 70%; pulau lain ≤ 3 perusahaan.
  Nasional 73 perusahaan, 5 terbesar 68%, 9 perusahaan membentuk 80%.
- Komoditas lain serupa atau lebih terkonsentrasi (daging sapi: 1 perusahaan 82% nasional; gula: 1 perusahaan 73%).
- Aturan 7.2 terpicu: pangsa 5 terbesar ≥ 50% di semua pulau -> **strata wajib-hitung dipakai**.

## 6. Cakupan volume beras terhadap BPS
| Tahun | Pelapor pedagang | Pengadaan ÷ (produksi + impor) | Penyaluran ÷ konsumsi RT Susenas |
| --- | --- | --- | --- |
| 2024 | 65 | 0,6% | 0,8% |
| 2025 | 69 | 1,9% | 2,8% |
| 2026 (Jan–Sep) | 76 | 1,5% | 2,5% |

- Per pulau (penyaluran ÷ konsumsi RT): Jawa 0,9% -> 3,5%; Sumatera 1,6% -> 3,9% -> 2,5%; pulau lain < 1,5%.
- **Cakupan volume pedagang beras ±1,5–3%** (terhadap konsumsi total ±2,6 juta ton/bulan lebih kecil lagi: ±1–2%).
- Aturan 7.2 terpicu: cakupan bergeser > ±30% antara 2024 dan 2026 -> **cakupan bulanan dipakai sebagai skala di M3**.
- BULOG (00372): 8 bulan, angka tidak teratur (penyaluran Jun 2026 1,55 juta ton, Sep 2026 3,12 juta ton; dua kepala
  laporan di Agu–Sep 2026) -> tidak dipakai untuk cakupan; perlu dicek sebelum dipakai di model.
- Komoditas lain belum dihitung (penyebut BPS belum disiapkan).

## 7. Satuan dan Harga Jual
- Koreksi kg->ton (≥ 100× median sendiri): beras 58 laporan, daging sapi 111, ikan 56, minyak goreng 44, kerbau 36.
- Total penyaluran yang masih tidak wajar sesudah koreksi: pupuk (15,8 juta ton 2025 dari 17 pelapor), daging sapi
  (451 ribu ton 2025), elpiji (satuan tabung/ton campur). Minyak goreng dalam liter.
- Harga Jual wajar (≥ 94% dalam ½–2× median): beras premium (median Rp14.900/kg), beras medium (Rp13.500), gula
  (Rp16.800), minyak goreng (curah Rp17.000, Minyakita Rp14.500, premium Rp19.329), kedelai impor (Rp9.000),
  daging kerbau, bawang putih.
- Tidak wajar: tepung terigu (36% dalam Rp/ton), daging sapi (campur potongan/satuan), "Beras BULOG" (14% bernilai ±1),
  bawang merah (18% < 1/100 median).
- Median beras premium = HET premium (Rp14.900): banyak pelapor menulis harga tepat di HET.
- Korelasi dengan PIHPS belum dihitung (data PIHPS belum diambil).

## 8. Implikasi (belum diputuskan pengguna, kecuali yang otomatis dari aturan 7.2)
1. Daya uji di tingkat pulau kecil bila kunci jawaban = sel hampir lengkap. Usul: kunci jawaban = laporan yang memang
   ada (nilai yang dihapus diketahui, tidak perlu sel lengkap); sel hampir lengkap hanya untuk menilai bobot pelapor.
2. Definisi aktif: usul pakai tenggang 3 bulan (aktif3) supaya bulan-bulan terakhir tidak tampak lengkap semu.
3. Wilayah: usul Jawa, Sumatera, dan "pulau lain" digabung (pulau lain ≤ 4 pelapor beras per bulan).
4. Blok penyetelan efektif hanya Okt 2024–Jun 2025 (sebelum itu pelapor beras 11–15).
5. Cakupan volume beras rendah (±1,5–3%): harapan realistis = sinyal tren Jawa/Sumatera; level tidak.
