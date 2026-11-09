"""Prakiraan stok 1-3 bulan setelah bulan terakhir model (komoditas tingkat B), tanpa fit ulang.

Pakai:  python -I prakiraan.py <komoditas> <folder data> <folder hasil> [label posterior, bawaan: dasar]

Setiap tarikan posterior stok bulan terakhir diteruskan dengan neraca yang sama seperti model_neraca.py:
- impor nasional per bulan: diambil acak (bootstrap) dari impor nasional 24 bulan terakhir, dibagi ke provinsi
  pelabuhan dengan pangsa 12 bulan terakhir (jadwal kapal belum diketahui);
- produksi: produksi USDA tahun pemasaran berjalan / 12 x pangsa provinsi konfigurasi;
- konsumsi: konsumsi RT tahun terakhir x (1+nu) tarikan posterior, termasuk simpangan tahun terakhir;
- arus antar provinsi: rumus model; guncangan provinsi dan nasional dengan sigma tarikan posterior.
Keluaran: prakiraan_<label>.csv dan risiko_<label>.csv (bulan cukup, peluang stok < 1 bulan konsumsi) per
pulau dan nasional, serta provinsi sebagai indikasi. Belum di-backtest.
"""
import os
import sys

import numpy as np
import pandas as pd

AKAR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AKAR)
import model_neraca as MN  # noqa: E402
from konfigurasi import KOMODITAS  # noqa: E402

H = 3


def main(nama, data, hasil, label='dasar', seed=5):
    rng = np.random.default_rng(seed)
    K = KOMODITAS[nama]
    D = MN.siapkan(K, data)
    z = np.load(os.path.join(hasil, f'posterior_{label}.npz'))
    N, T = D['N'], D['T']
    X = z['stok'].reshape(-1, N, T + 1)[:, :, -1].astype(float)
    S = X.shape[0]
    fnu = np.exp(z['log_1_plus_nu'].reshape(-1) + z['dev_tahunan_nu'].reshape(S, -1)[:, -1])
    sig = z['sigma_proses'].reshape(-1)
    sgn = z['sigma_nasional'].reshape(-1)
    imp_n = D['imp'].sum(axis=0)
    pangsa_imp = D['imp'][:, -12:].sum(axis=1) / D['imp'][:, -12:].sum()
    U = pd.read_csv(os.path.join(data, 'usda_neraca.csv'))
    akhir = pd.Period(K['akhir'], 'M')
    bulan = [str(akhir + h) for h in range(1, H + 1)]
    sh = pd.Series(K['pangsa_produksi'])
    sh = (sh / sh.sum()).reindex(MN.PROV).fillna(0).values
    cbar = D['cbar']
    c_last = D['cons'][:, -1]
    neto = D['sbar'][None, :] - cbar[None, :] * fnu[:, None]
    k = 0.05 * cbar[None, :]
    masuk = k * np.logaddexp(0, -neto / k)
    surplus = k * np.logaddexp(0, neto / k)
    keluar = masuk.sum(axis=1, keepdims=True) * surplus / surplus.sum(axis=1, keepdims=True)
    Xm = X.copy()
    hasil_x = []
    for b in bulan:
        y, m = int(b[:4]), int(b[5:])
        my = y if m >= K['usda_bulan_awal'] else y - 1
        prod = float(U.loc[U.tahun_pemasaran == my, 'produksi'].iloc[0]) / 12 * sh
        imp = rng.choice(imp_n[-24:], S)[:, None] * pangsa_imp[None, :]
        e = sig[:, None] * cbar[None, :] * rng.standard_normal((S, N))
        e = e - (cbar / cbar.sum())[None, :] * e.sum(axis=1, keepdims=True)
        e = e + (cbar / cbar.sum())[None, :] * (sgn * cbar.sum() * rng.standard_normal(S))[:, None]
        Xm = Xm + prod[None, :] + imp - c_last[None, :] * fnu[:, None] + masuk - keluar + e
        hasil_x.append(Xm.copy())
    kons = c_last[None, :] * fnu[:, None]
    rows, risk = [], []
    lv = {'provinsi': [(p, [i]) for i, p in enumerate(MN.PROV)],
          'pulau': [(g, [MN.PROV.index(p) for p in ps]) for g, ps in MN.PULAU.items()],
          'nasional': [('INDONESIA', list(range(N)))]}
    for j, b in enumerate(bulan):
        for tk, items in lv.items():
            for w, ix in items:
                a = hasil_x[j][:, ix].sum(axis=1)
                c = kons[:, ix].sum(axis=1)
                q = np.percentile(a / 1e3, [5, 50, 95])
                pul = MN.PULAU_DARI.get(w, w if tk == 'pulau' else '')
                rows.append((tk, w, pul, b, q[1], q[0], q[2]))
                risk.append((tk, w, pul, b, np.median(a / c), np.mean(a / c < 1.0)))
    R = pd.DataFrame(rows, columns=['tingkat', 'wilayah', 'pulau', 'periode', 'median_ribu_ton', 'p05', 'p95'])
    Q = pd.DataFrame(risk, columns=['tingkat', 'wilayah', 'pulau', 'periode', 'cukup_bulan_median', 'peluang_kurang_1_bulan'])
    R.to_csv(os.path.join(hasil, f'prakiraan_{label}.csv'), index=False)
    Q.to_csv(os.path.join(hasil, f'risiko_{label}.csv'), index=False)
    print(R[R.tingkat != 'provinsi'].round(1).to_string(index=False))
    print(Q[Q.tingkat != 'provinsi'].round(2).to_string(index=False))


if __name__ == '__main__':
    main(*sys.argv[1:4], *(sys.argv[4:5] or ['dasar']))
