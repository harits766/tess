"""Diagnostik (bukan dasar keputusan): korelasi perubahan bulanan yang sudah dibuang pola musimnya.

Pakai:  python -I diagnostik.py <folder data> <folder hasil>

Membandingkan perubahan log stok per perusahaan pelapor INATRADE dengan perubahan log stok swasta posterior
(median) di provinsi yang sama. Pola musim dibuang dengan mengurangi rata-rata per bulan kalender di tiap
provinsi. Hasil: diagnostik_korelasi.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_stok as M  # noqa: E402


def main(data, hasil):
    D = M.siapkan(data)
    z = np.load(os.path.join(hasil, 'posterior_penuh.npz'))
    X = z['stok'].reshape(-1, D['N'], D['T'] + 1)
    B = z['bulog'].reshape(-1, D['T'] + 1)
    wB = z['pangsa_bulog'].reshape(-1, D['N'])
    sw = np.median(np.clip(X - B[:, None, :] * wB[:, :, None], 1, None), axis=0)
    per = ['2022-06'] + D['per']
    P = pd.read_csv(os.path.join(data, 'panel_provinsi.csv'))
    P = P[(P.stok_akhir_ton > 0) & P.prov.isin(M.PROV) & P.periode.isin(per)].copy()
    P['y'] = np.log(P.stok_akhir_ton / P.perusahaan)
    P['m'] = [np.log(sw[M.PROV.index(p), per.index(b)]) for p, b in zip(P.prov, P.periode)]
    rows = []
    for p, g in P.sort_values('periode').groupby('prov'):
        g = g.set_index('periode')
        idx = pd.period_range(g.index.min(), g.index.max(), freq='M').astype(str)
        g = g.reindex(idx)
        d = g[['y', 'm']].diff().dropna()
        if len(d) < 6:
            continue
        d['bln'] = d.index.str[5:]
        d = d - d.groupby('bln')[['y', 'm']].transform('mean')
        d = d[['y', 'm']]
        rows.append((p, len(d), d.y.corr(d.m)))
    R = pd.DataFrame(rows, columns=['provinsi', 'pasang_bulan', 'korelasi'])
    R.to_csv(os.path.join(hasil, 'diagnostik_korelasi.csv'), index=False)
    print(R.to_string(index=False))
    print(f'median korelasi antar provinsi: {R.korelasi.median():.2f} ({len(R)} provinsi)')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
