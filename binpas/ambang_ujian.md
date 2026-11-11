# Ambang lolos ujian (penguatan INATRADE dan model gabungan)

**Status: DIKUNCI (11 Nov 2026).** Usulan awal dikirim ke Bu Fitria lewat WA (sesi 5, 10 Nov 2026). Empat perbaikan
(pembanding, sebaran pembanding, cakupan berbasis n efektif, bootstrap per blok bulan) dikirim di sesi 6 dan
**disetujui Bu Fitria**. Belum ada ujian yang dijalankan saat file ini dikunci. Setelah commit ini file tidak diubah;
tanggal commit = bukti ambang ditetapkan sebelum melihat hasil.

## Pembanding
- **P\*** = pembanding dengan CRPS terkecil di blok penyetelan (Jan 2024–Jun 2025) di antara A (asli), A + bobot
  pelapor batas 3, dan A + bobot pelapor batas 5. Di tingkat perusahaan: "sama seperti bulan lalu".
- Semua pembanding diberi sebaran: titik + kuantil galat log empiris per kelompok dari 6 bulan sebelumnya (bergulir,
  tidak memakai bulan yang dinilai). Bila kelompok punya < 6 bulan galat, pakai galat kelompok induk
  (provinsi -> pulau -> nasional).

## Peringkat dan gerbang
Peringkat versi ditentukan CRPS (makin kecil makin baik). Pemenang peringkat dipakai hanya jika lolos semua gerbang;
kalau tidak, turun ke peringkat berikutnya (hanya di blok penyetelan); kalau tidak ada yang lolos, pakai A berlabel
"tercatat". Gagal di ujian akhir -> A "tercatat" (tidak turun ke peringkat 2 memakai data ujian akhir); bila yang
gagal hanya cakupan, skala ragam disesuaikan dan diuji di bulan berikutnya.

| Gerbang | Ambang | Berlaku untuk |
| --- | --- | --- |
| Lebih baik dari pembanding | CRPS ≥ 10% lebih kecil dari P\* bersebaran **dan** MAE angka tengah (median) tidak lebih buruk dari P\* | Tahap 1 dan 2 |
| Konsisten | rentang 90% bootstrap per blok bulan dari selisih CRPS (versi − P\*) seluruhnya < 0; "% ulangan menang" hanya dilaporkan | Tahap 1 dan 2 |
| Cakupan rentang 90% | 0,90 berada di dalam selang keyakinan 90% (Wilson, n efektif) dari cakupan teramati **dan** cakupan teramati ≥ 80%; bila setengah lebar selang > 10 poin persen -> "belum bisa diputuskan" | versi yang punya rentang |
| Bias (rata-rata galat log) | ≤ 3%, dan tidak lebih buruk dari P\* | Tahap 1 dan 2 |
| Arah perubahan bulanan sama dengan jawaban benar | ≥ 80% bulan | Tahap 2 (agregat) |
| Korelasi peringkat pangsa asal vs Pola Distribusi BPS | ≥ 0,6 | gerbang keterwakilan; ujian BPS 2025 disembunyikan |
| Ujian akhir Jan–Sep 2026 vs penyetelan | masih mengalahkan P\* (gerbang "lebih baik" di atas); CRPS memburuk ≤ 20%; cakupan dengan aturan di atas | pemenang |
| Ujian BPS 2025 disembunyikan | lebih dekat daripada INATRADE mentah **dan** "BPS 2024 apa adanya" | bobot semu, kalibrasi pangsa, rekonstruksi jaringan |
| Model gabungan | mengalahkan "tanpa INATRADE" dan "INATRADE asli" (CRPS prakiraan harga 1–2 bulan, ujian BPS 2025) | model |

## Definisi teknis (ikut dikunci)
- **Bootstrap per blok bulan:** satu blok = satu bulan kalender beserta semua sel dan ulangannya; 2.000 resampel
  dengan pengembalian; selang persentil 5–95%.
- **n efektif cakupan:** n_eff = n × (1 − ρ) / (1 + ρ), ρ = autokorelasi lag-1 indikator "masuk rentang" antarbulan
  (dirata-rata antarsel), dibatasi 0 ≤ ρ ≤ 0,9.
- **Bias:** rata-rata (log ŷ − log y); dinyatakan dalam persen sebagai exp(·) − 1.
- **Arah perubahan:** proporsi bulan dengan tanda Δŷ[t] = tanda Δy[t].
- **Kemulusan** (dilaporkan, bukan gerbang): rata-rata |Δ² log ŷ[t]|.

## Aturan tambahan
- Selisih tipis -> pilih versi yang lebih sederhana; semua hasil dilaporkan.
- Menang tipis di ujian BPS (hanya satu tahun pembanding) -> "belum bisa diputuskan".
- Daya uji kurang -> "belum bisa diputuskan" (tidak dihitung sebagai gagal atau lolos).
- Tangga klaim: provinsi-bulanan -> pulau-bulanan -> nasional-bulanan -> triwulanan; laporkan tingkat terhalus
  yang lolos.
- Dilarang: ubah ambang setelah lihat hasil, pilih bulan/perusahaan yang mudah, setel di data ujian akhir, pola hapus
  berbeda antarversi, tambah versi terus sampai ada yang lolos.
