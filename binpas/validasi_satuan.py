"""Validasi satuan laporan INATRADE per komoditas (semua baris berlabel TON, tetapi sebagian diisi dalam kg).

Pakai:  python -I binpas/validasi_satuan.py <Non_PAW_dari_nol.xlsm> <folder keluaran> "<KOMODITAS>" ["<KOMODITAS>" ...]

Hanya memeriksa dan mengelompokkan; tidak mengubah data dan tidak dipakai oleh adu versi.
Satuan pemeriksaan = kepala laporan (perusahaan x subkomoditas x bulan), peubah = Penyaluran.
Patokan sendiri = median penyaluran positif perusahaan x subkomoditas itu.

Kelompok laporan:
  wajar          penyaluran < 10x patokan sendiri
  ragu           10x-100x patokan sendiri (bisa lonjakan nyata, bisa salah satuan)
  lonjakan       >= 100x patokan sendiri -> usul faktor 1/1.000 atau 1/1.000.000 (yang paling dekat ke patokan sendiri)
  patokan kecil  >= 100x patokan sendiri tetapi patokannya < 0,1 (median tercemar angka sangat kecil) -> tidak dikoreksi
                 otomatis, perlu dicek
Kelompok perusahaan (skala konsisten, tidak tertangkap aturan lonjakan):
  skala >= 1.000x   median penyaluran perusahaan >= 1.000x median antarperusahaan komoditas itu: kemungkinan diisi dalam
                    kg, ATAU memang pelaku sangat besar (contoh: BULOG di beras) -> harus dikonfirmasi
  skala 100x-1.000x perlu dicek
Aturan Tahap 0 yang sekarang dipakai (pembanding): faktor 1/1.000 bila nilai terbesar dari empat besaran >= 100x median
semua besaran positif perusahaan x subkomoditas.
Keluaran: ringkasan (agregat) ke layar; <keluaran>/satuan_<komoditas>_laporan.csv dan _perusahaan.csv memuat kode
perusahaan (INTERNAL, tidak disimpan di repo).
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tahap0 as T0  # noqa: E402

Q = T0.Q


def periksa(S, kom, out):
    R = S[S.kom == kom]
    K = R.drop_duplicates(['kode', 'sub', 'per'] + Q)[['kode', 'sub', 'per', 'prov', 'Harga Jual'] + Q].copy()
    K['maks'] = K[Q].max(axis=1)
    kunci = pd.MultiIndex.from_arrays([K.kode, K['sub']])
    st = K[Q].replace(0, np.nan).stack()
    ks = [K.kode.loc[st.index.get_level_values(0)].values, K['sub'].loc[st.index.get_level_values(0)].values]
    K['patokan_t0'] = st.groupby(ks).median().reindex(kunci).values
    K['peny_t0'] = K.Penyaluran * np.where(K.maks / K.patokan_t0 >= T0.AMBANG_KG, 1 / 1000, 1.0)   # aturan Tahap 0 sekarang
    K['patokan'] = K.Penyaluran.where(K.Penyaluran > 0).groupby([K.kode, K['sub']]).median().reindex(kunci).values
    K['rasio'] = K.Penyaluran / K.patokan
    K['kelompok'] = np.where(K.rasio >= 100, np.where(K.patokan < 0.1, 'patokan kecil', 'lonjakan'),
                             np.where(K.rasio >= 10, 'ragu', 'wajar'))
    k = np.clip(np.round(np.log10(K.rasio.where(K.rasio >= 100, 1.0)) / 3), 1, 2)
    K['faktor_usul'] = np.where(K.kelompok == 'lonjakan', 1000.0 ** -k, 1.0)
    K['peny_usul'] = K.Penyaluran * K.faktor_usul
    g = K[K.Penyaluran > 0].groupby('kode')
    P = pd.DataFrame(dict(laporan=K.groupby('kode').size(), peny_median=g.peny_usul.median(), peny_total_mentah=K.groupby('kode').Penyaluran.sum(),
                          peny_total_usul=K.groupby('kode').peny_usul.sum(), lonjakan=(K.kelompok == 'lonjakan').groupby(K.kode).sum(),
                          ragu=(K.kelompok == 'ragu').groupby(K.kode).sum(),
                          porsi_desimal=g.Penyaluran.apply(lambda x: float(((x % 1) != 0).mean()))))
    med = P.peny_median[P.peny_median > 0].median()
    P['skala'] = P.peny_median / med
    P['kelompok'] = np.where(P.skala >= 1000, 'skala >= 1000x', np.where(P.skala >= 100, 'skala 100-1000x', 'wajar'))
    kg = set(P.index[P.kelompok == 'skala >= 1000x'])
    K['peny_usul2'] = K.peny_usul * np.where(K.kode.isin(kg), 1 / 1000, 1.0)
    P['peny_total_usul2'] = K.groupby('kode').peny_usul2.sum()
    slug = kom.lower().replace(' ', '_')
    K.to_csv(os.path.join(out, f'satuan_{slug}_laporan.csv'), index=False)
    P.sort_values('peny_total_usul', ascending=False).to_csv(os.path.join(out, f'satuan_{slug}_perusahaan.csv'))
    print(f'\n===== {kom}: {len(K)} kepala laporan, {K.kode.nunique()} perusahaan; median penyaluran antarperusahaan {med:,.1f}')
    print('laporan per kelompok:', K.kelompok.value_counts().to_dict(),
          '| faktor usul:', K[K.kelompok == 'lonjakan'].faktor_usul.value_counts().to_dict(),
          '| perusahaan dengan lonjakan:', int((P.lonjakan > 0).sum()), '| dengan laporan ragu:', int((P.ragu > 0).sum()))
    print('perusahaan per kelompok skala:', P.kelompok.value_counts().to_dict())
    K['thn'] = K.per.str[:4]
    T = K.groupby('thn').agg(pelapor=('kode', 'nunique'), mentah=('Penyaluran', 'sum'), aturan_tahap0=('peny_t0', 'sum'),
                             usul_lonjakan=('peny_usul', 'sum'), bila_skala_1000x_ternyata_kg=('peny_usul2', 'sum'))
    print('total penyaluran per tahun (satuan laporan = "ton"):')
    print(T.round(0).to_string())
    for kol, nm in [('Penyaluran', 'mentah'), ('peny_t0', 'aturan Tahap 0'), ('peny_usul', 'usul lonjakan'), ('peny_usul2', 'bila skala >= 1000x ternyata kg')]:
        t = K.groupby('kode')[kol].sum().sort_values(ascending=False)
        print(f'  pangsa terbesar / 5 terbesar ({nm}): {t.iloc[0] / t.sum():.0%} / {t.iloc[:5].sum() / t.sum():.0%}')
    h = K['Harga Jual'][K['Harga Jual'] > 0]
    print('Harga Jual > 0:', len(h), 'kepala laporan; median', f'{h.median():,.0f}', '| < 1.000:', int((h < 1000).sum()), '| > 1.000.000:', int((h > 1e6).sum()))


def main(xlsm, out, koms):
    os.makedirs(out, exist_ok=True)
    S = T0.baca(xlsm)
    for kom in koms:
        periksa(S, kom.upper(), out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
