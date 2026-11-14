# Cakupan volume INATRADE terhadap sumber BPS, komoditas selain beras (14 Nov 2026)

Padanan HASIL_TAHAP0 bagian 6 (beras) untuk enam komoditas lain. Skrip:
`BPS_API_KEY=... python -I binpas/cakupan_komoditas.py <xlsm> <cache json> <keluaran>` (±2 menit; WebAPI BPS).
INATRADE: pedagang tanpa BULOG, satuan sesudah koreksi `tahap0` (termasuk tiga perusahaan yang dikoreksi ke kg).
Hanya profil data; tidak ada metode yang dinilai dan hasil ujian tidak tersentuh.

## Sumber BPS yang dipakai (semua lewat WebAPI, tanpa surat)
| Komoditas | Konsumsi rumah tangga (Susenas × penduduk) | Produksi per provinsi | Impor (dataexim) |
| --- | --- | --- | --- |
| Daging sapi | var 2097 (2024), 2552 (2025) | var 480 | HS 0201 + 0202 (termasuk daging kerbau beku) |
| Daging kerbau | var 2552 (baru ada 2025) | var 481 | tidak bisa dipisah dari HS 0202 |
| Daging ayam ras | var 2097, 2552 | var 488 | – |
| Telur ayam ras | var 2099, 2554 (dalam butir; asumsi 16 butir/kg) | var 491 | – |
| Kedelai | var 2101 (kedelai + tahu × 0,30 + tempe × 0,60) | tidak ada per provinsi | HS 12019000 |
| Pupuk | tidak ada | tidak ada di WebAPI | HS 31021000, 31022100, 31042000, 31052000 |

## Hasil: penyaluran INATRADE dibanding pasokan dan konsumsi (ribu ton)
Pasokan = produksi + impor. Untuk 2026, INATRADE dan impor Jan–Sep; produksi dan konsumsi disetarakan 9 bulan.

| Komoditas | Tahun | Pelapor | Penyaluran INATRADE | Konsumsi RT setahun | Produksi setahun | Impor | Penyaluran ÷ pasokan | Penyaluran ÷ konsumsi RT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kedelai | 2025 | 60 | 1.578 | 1.965 | – | 2.558 | 62% | 80% |
| Kedelai | 2026 | 38 | 1.328 | 1.965 | – | 2.150 | 62% | 90% |
| Daging kerbau | 2025 | 17 | 6,6 | 14,8 | 16,4 | (tak terpisah) | 40%* | 44% |
| Daging kerbau | 2026 | 20 | 7,6 | 14,8 | 16,4 | (tak terpisah) | 62%* | 68% |
| Daging sapi | 2025 | 64 | 87 | 129 | 499 | 231 | 12% | 68% |
| Daging sapi | 2026 | 64 | 27 | 129 | 499 | 136 | 5% | 28% |
| Daging ayam ras | 2025 | 11 | 108 | 2.111 | 4.061 | – | 2,7% | 5,1% |
| Daging ayam ras | 2026 | 5 | 62 | 2.111 | 4.061 | – | 2,0% | 3,9% |
| Pupuk | 2025 | 6 | 78 | – | – | 5.993 | 1,3%** | – |
| Pupuk | 2026 | 4 | 54 | – | – | 4.929 | 1,1%** | – |
| Telur ayam ras | 2025 | 8 | 5,4 | 2.121 | 6.314 | – | 0,08% | 0,25% |
| Telur ayam ras | 2026 | 9 | 4,4 | 2.121 | 6.314 | – | 0,09% | 0,28% |
| Beras (pembanding, Tahap 0) | 2025 | 69 | – | – | – | – | 1,9% (pengadaan) | 2,8% |

\\* Penyebut daging kerbau hanya produksi dalam negeri; impor daging kerbau beku tercatat di HS yang sama dengan daging
sapi, jadi cakupan sebenarnya lebih kecil.
\\** Penyebut pupuk hanya impor empat kode HS; produksi dalam negeri tidak termasuk, jadi cakupan sebenarnya lebih kecil.

2024 tidak ditabelkan: pelapor baru ramai sejak Okt–Nov 2024 (kedelai 2024: 11% pasokan; daging sapi 4%).

## Cara membaca
- **Kedelai paling terwakili menurut volume:** pelapor INATRADE menyalurkan ±62% dari impor kedelai. Ini jauh di atas
  beras (±2–3%).
- **Daging sapi menengah:** ±12% pasokan pada 2025, turun ke ±5% pada 2026 (Jan–Sep). Angkanya bergantung pada koreksi
  satuan; pengadaan daging sapi 2024 masih memuat angka yang tampak salah satuan (312 ribu ton vs penyaluran 26 ribu).
- **Daging ayam ras, pupuk, dan telur sangat kecil** (≤ 3%, ≤ 1%, < 0,1%): INATRADE bukan gambaran pasar untuk tiga
  komoditas ini, berapa pun baiknya isian.
- Konsumsi RT hanya rumah tangga (tanpa hotel, restoran, industri), jadi rasio terhadap konsumsi RT lebih tinggi
  daripada rasio terhadap pasokan.
- Faktor konversi (tahu 0,30; tempe 0,60; telur 16 butir/kg) adalah asumsi.

## Yang masih bisa ditambahkan supaya setara beras
| Bahan | Beras | Komoditas lain |
| --- | --- | --- |
| Cakupan volume | ada | **sekarang ada** (berkas ini) |
| Peubah luar di adu versi (mis. produksi/impor bulanan) | ada, tidak menyumbang | bisa untuk kedelai dan daging sapi (impor bulanan BPS); belum dicoba |
| Ujian keterwakilan (Pola Distribusi BPS) | sudah (U2) | publikasi ada untuk daging sapi (2025, 2018), telur ayam ras (2023, 2021, 2019), daging ayam ras (2019, 2018); kedelai belum dicek; belum dicoba |
| Model stok | ada | kedelai fase 1 ada; lainnya belum |
