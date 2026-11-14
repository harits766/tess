# Validasi satuan laporan INATRADE: daging sapi dan pupuk (14 Nov 2026)

Skrip: `python -I binpas/validasi_satuan.py <xlsm> <keluaran> "DAGING SAPI" "PUPUK"` (±15 detik). Hanya memeriksa dan
mengelompokkan; data tidak diubah dan hasil adu versi tidak tersentuh. Daftar kode perusahaan ada di berkas keluaran
(`satuan_<komoditas>_perusahaan.csv`, `_laporan.csv`; INTERNAL, tidak disimpan di repo).

## Temuan umum
- Semua baris berlabel satuan "TON", tetapi sebagian diisi dalam kg (atau lebih kecil lagi). Label satuan tidak bisa
  dipakai untuk memilah.
- Ada dua pola salah satuan:
  1. **Lonjakan sesaat:** perusahaan yang biasanya mengisi dalam ton sesekali mengisi dalam kg (nilai ≥ 100× median
     sendiri). Bisa dikoreksi otomatis.
  2. **Skala konsisten besar:** perusahaan yang SELALU mengisi dalam skala ribuan kali perusahaan lain. Tidak tertangkap
     aturan lonjakan (mediannya sendiri sudah besar). Tidak bisa diputuskan dari data saja: bisa kg, bisa memang pelaku
     sangat besar (di beras, satu-satunya yang tertangkap adalah BULOG, yang memang besar).
- Aturan Tahap 0 yang sekarang dipakai (÷1.000 bila nilai terbesar dari empat besaran ≥ 100× median semua besaran) punya
  tiga kelemahan: tidak menangkap pola 2; beberapa laporan butuh ÷1.000.000; dan satuan bisa berbeda antarkolom dalam
  satu laporan (stok dan penyaluran tidak selalu salah bersama), sehingga hasil koreksi bergeser bila aturannya diubah
  sedikit.

## Daging sapi (1.347 kepala laporan, 73 perusahaan)
- Lonjakan: 50 laporan dari 18 perusahaan (48 butuh ÷1.000, 2 butuh ÷1.000.000). Ragu (10–100× median sendiri): 38
  laporan dari 19 perusahaan.
- Skala konsisten ≥ 1.000×: **2 perusahaan** (2 dan 6 laporan; semua angkanya bulat). Salah satunya melaporkan 265 ribu
  "ton" dalam satu bulan, kira-kira setara impor daging nasional setahun, sehingga hampir pasti kg.

| Penyaluran per tahun ("ton") | 2024 | 2025 | 2026 (Jan–Sep) |
| --- | --- | --- | --- |
| Mentah | 1,71 juta | 27,1 juta | 133 ribu |
| Aturan Tahap 0 (dipakai adu versi) | 26 ribu | 451 ribu | 94 ribu |
| Koreksi lonjakan (usul) | 41 ribu | 427 ribu | 94 ribu |
| + bila 2 perusahaan berskala besar ternyata kg | 41 ribu | 63 ribu | 28 ribu |

- Dua perusahaan itu membentuk 85% total 2025 dan 70% total 2026 sesudah koreksi lonjakan. Pangsa perusahaan terbesar
  turun dari 65% ke 21% (5 terbesar 88% -> 64%) bila keduanya kg. Temuan Tahap 0 "1 perusahaan 82% nasional" dan "451
  ribu ton" kemungkinan besar akibat salah satuan.
- Laporan "ragu" masih memuat ±23% total sesudah koreksi: tetap sumber ketidakpastian.
- Harga Jual: median Rp120.000/kg; 45 laporan < Rp1.000 dan 3 laporan > Rp1 juta (satuan harga juga tidak seragam).

## Pupuk (271 kepala laporan, 17 perusahaan)
- Lonjakan: 22 laporan, semuanya dari 1 perusahaan (÷1.000). Ragu: 3 laporan.
- Skala konsisten ≥ 1.000×: **1 perusahaan** (56 laporan, 4 jenis pupuk, Nov 2024–Sep 2026). Bila angkanya ton, satu
  perusahaan ini menyalurkan ±1,8 juta ton per bulan (±22 juta ton per tahun), lebih besar daripada perkiraan pasar
  pupuk nasional. Kemungkinan besar kg, tetapi perlu dikonfirmasi (bisa juga produsen besar dengan satuan lain).

| Penyaluran per tahun ("ton") | 2024 | 2025 | 2026 (Jan–Sep) |
| --- | --- | --- | --- |
| Mentah | 12,5 juta | 31,6 juta | 9,9 juta |
| Aturan Tahap 0 (dipakai adu versi) | 22 ribu | 15,8 juta | 9,9 juta |
| Koreksi lonjakan (usul) | 133 ribu | 16,0 juta | 9,9 juta |
| + bila 1 perusahaan berskala besar ternyata kg | 132 ribu | 297 ribu | 54 ribu |

- Perusahaan itu membentuk 98–100% total 2025–2026. Angka 2024 berbeda jauh antara aturan Tahap 0 dan usul (22 vs 133
  ribu): hasil koreksi otomatis belum stabil.
- Di luar soal satuan, pelapor pupuk menyusut: 16 perusahaan (2024), 6 (2025), 4 (2026). Sesudah satuan beres pun
  pupuk tetap terlalu tipis untuk diuji.

## Komoditas lain (pemeriksaan cepat dengan skrip yang sama)
- Beras: yang berskala ≥ 1.000× hanya BULOG (sudah dikeluarkan dari adu versi); 4 perusahaan berskala 100–1.000×
  (bisa pedagang besar). 9 laporan dari 1 perusahaan (2024) mediannya tercemar angka sangat kecil, sehingga aturan
  Tahap 0 kemungkinan salah mengoreksinya; dampaknya kecil (blok penyetelan saja).
- Kedelai: 1 perusahaan berskala ≥ 1.000× (hanya 1 laporan) dan 6 perusahaan 100–1.000×. Daging kerbau dan telur ayam
  ras: tidak ada yang tertangkap. Daging ayam ras: 1 perusahaan 100–1.000×.

## Yang perlu dikonfirmasi ke pengelola INATRADE / perusahaan
1. Tiga perusahaan berskala konsisten besar (2 daging sapi, 1 pupuk): satuan yang sebenarnya dipakai.
2. Apakah formulir INATRADE mengizinkan satuan selain ton, dan apakah kolom "Satuan" memang selalu terisi "TON".
3. Untuk laporan "ragu": cukup contoh beberapa perusahaan, untuk menentukan batas koreksi otomatis.

## Sesudah konfirmasi
- Perbaiki aturan koreksi di `tahap0.py` (faktor per kolom, ÷1.000.000, daftar perusahaan berskala kg), lalu ulang
  penyetelan daging sapi dan pupuk. Ujian akhir keduanya belum pernah dijalankan, jadi tidak ada yang "terpakai".
- Angka patokan nasional di atas (impor daging, pasar pupuk) dari ingatan dan belum dicek ulang.
