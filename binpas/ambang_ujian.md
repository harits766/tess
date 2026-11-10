# Ambang lolos ujian (penguatan INATRADE dan model gabungan)

**Status: BELUM DIKUNCI.** Usulan dikirim ke Bu Fitria lewat WA (sesi 5, 10 Nov 2026); menunggu tanggapan.
Perubahan hanya boleh dilakukan SEBELUM ujian pertama dijalankan; setelah itu file ini tidak diubah.
Tanggal commit yang mengunci file ini = bukti ambang ditetapkan sebelum melihat hasil.

Peringkat versi ditentukan CRPS (makin kecil makin baik). Pemenang peringkat dipakai hanya jika lolos semua gerbang;
kalau tidak, turun ke peringkat berikutnya; kalau tidak ada yang lolos, pakai A (data asli).

| Gerbang | Ambang | Berlaku untuk |
| --- | --- | --- |
| CRPS lebih baik dari pembanding (A asli; di tingkat perusahaan: "sama seperti bulan lalu") | ≥ 10% | Tahap 1 dan 2 |
| Konsisten (berpasangan, pola hapus sama) | menang di ≥ 80% ulangan **dan** rentang 90% bootstrap selisih CRPS tidak mencakup 0 | Tahap 1 dan 2 |
| Cakupan rentang 90% | 85–95% | versi yang punya rentang |
| Bias (rata-rata galat log) | ≤ 3%, dan tidak lebih buruk dari A | Tahap 1 dan 2 |
| Arah perubahan bulanan sama dengan jawaban benar | ≥ 80% bulan | Tahap 2 (agregat) |
| Korelasi peringkat pangsa asal vs Pola Distribusi BPS | ≥ 0,6 | gerbang keterwakilan; ujian BPS 2025 disembunyikan |
| Ujian akhir Jan–Sep 2026 vs penyetelan | masih mengalahkan A; CRPS memburuk ≤ 20%; cakupan 85–95% | pemenang |
| Ujian BPS 2025 disembunyikan | lebih dekat daripada INATRADE mentah **dan** "BPS 2024 apa adanya" | bobot semu, kalibrasi pangsa, rekonstruksi jaringan |
| Model gabungan | mengalahkan "tanpa INATRADE" dan "INATRADE asli" (CRPS prakiraan harga 1–2 bulan, ujian BPS 2025) | model |

Penyesuaian yang dibolehkan sebelum dikunci (bila disepakati):
- INATRADE terutama untuk peringatan dini: arah perubahan ≥ 85%, cakupan diperketat; bias boleh lebih longgar.
- Bila volume ton akan ditampilkan: bias ≤ 2%.

Aturan tambahan: selisih tipis -> pilih versi yang lebih sederhana; semua hasil dilaporkan; menang tipis di ujian BPS
(hanya satu tahun pembanding) -> "belum bisa diputuskan"; daya uji kurang -> "belum bisa diputuskan".
