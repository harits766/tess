"""Prakiraan stok beras 1-3 bulan ke depan (Okt-Des 2026) dari posterior model, tanpa fit ulang.

Pakai:  python -I prakiraan.py <folder data> <folder hasil>

Setiap draw posterior stok akhir September 2026 diteruskan dengan neraca yang sama seperti model:
  X[m] = X[m-1] + (1-s) P[m] - (1+nu) C + masuk - keluar + e
- s, nu: draw posterior (nu 2026 diberi simpangan tahunan ~ N(0; 0,03)).
- P: angka potensi KSA BPS Okt-Nov 2026; Desember = produksi Des 2025 x faktor acak lognormal(0; 0,15).
- Impor 0 (tidak ada impor beras konsumsi 2025-2026).
- Arus antar provinsi: rumus model dengan theta ~ lognormal(0; 0,04) per provinsi; guncangan sigma 0,042.
- BULOG: acak berjalan log dengan sigma 0,24 per bulan (posterior), tanpa tren (tidak ada data rencana BULOG).
Keluaran: prakiraan.csv (median, p05, p95 per wilayah/bulan/komponen) dan risiko_provinsi.csv
(berapa bulan stok cukup untuk konsumsi dan peluang stok < 1 bulan konsumsi).
Prakiraan belum di-backtest.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_stok as M  # noqa: E402

BULAN = ['2026-10', '2026-11', '2026-12']
SIGMA_PROSES, SIGMA_BULOG, TAU_THETA, SD_DEV, SD_DES = 0.042, 0.24, 0.04, 0.03, 0.15


def main(data, hasil, seed=7):
    rng = np.random.default_rng(seed)
    D = M.siapkan(data)
    z = np.load(os.path.join(hasil, 'posterior_penuh.npz'))
    N = D['N']
    X = z['stok'].reshape(-1, N, D['T'] + 1)[:, :, -1].astype(float)  # stok akhir Sep 2026
    S = X.shape[0]
    B = z['bulog'].reshape(-1, D['T'] + 1)[:, -1]
    wB = z['pangsa_bulog'].reshape(-1, N)
    s = z['susut'].reshape(-1)
    lognu = z['log_1_plus_nu'].reshape(-1)
    fnu = np.exp(lognu + rng.normal(0.0036, SD_DEV, S))

    ksa = pd.read_csv(os.path.join(data, 'produksi_bulanan_ksa.csv'))
    km = {(r.prov, r.periode): r.padi_gkg_ton * M.KONV for r in ksa.itertuples()}
    prod_f = np.array([[km.get((p, b), np.nan) for b in ['2026-10', '2026-11', '2025-12']] for p in M.PROV])
    cbar, pbar = D['cbar'], D['pbar']
    pmean = D['prod'].mean(axis=1)
    cons26 = D['cons'][:, -1]

    rows_x, rows_b = [], []
    Xm, lB = X.copy(), np.log(B)
    for j, b in enumerate(BULAN):
        P = np.tile(prod_f[:, j], (S, 1))
        if b == '2026-12':
            P = P * np.exp(rng.normal(0, SD_DES, (S, 1)))
        neto = pbar[None, :] * (1 - s[:, None]) + D['imp'].mean() * D['wcons'][None, :] - cbar[None, :] * fnu[:, None]
        k = 0.05 * cbar[None, :]
        theta = np.exp(rng.normal(0, TAU_THETA, (S, N)))
        masuk = theta * k * np.logaddexp(0, -neto / k)
        surplus = k * np.logaddexp(0, neto / k)
        shs = surplus / surplus.sum(axis=1, keepdims=True)
        keluar = masuk.sum(axis=1, keepdims=True) * shs
        ma = 0.5 + 0.5 * P / pmean[None, :]
        g = (shs * ma).sum(axis=1, keepdims=True)
        e = SIGMA_PROSES * cbar[None, :] * rng.standard_normal((S, N))
        e = e - (cbar / cbar.sum())[None, :] * e.sum(axis=1, keepdims=True)
        d = P * (1 - s[:, None]) - cons26[None, :] * fnu[:, None] + masuk * g - keluar * ma + e
        Xm = np.clip(Xm + d, 0, None)
        lB = lB + rng.normal(0, SIGMA_BULOG, S)
        rows_x.append(Xm.copy())
        rows_b.append(np.exp(lB))

    out, risk = [], []
    konsumsi = cons26[None, :] * fnu[:, None]  # konsumsi total per bulan per draw
    for j, b in enumerate(BULAN):
        Xj, Bj = rows_x[j], rows_b[j]
        Bp = Bj[:, None] * wB
        comp = {'total': Xj, 'bulog': Bp, 'swasta': np.clip(Xj - Bp, 0, None)}
        for kmp, arr in comp.items():
            lv = {'provinsi': (arr, M.PROV)}
            lv['pulau'] = (np.stack([arr[:, [M.PROV.index(p) for p in v]].sum(axis=1) for v in M.PULAU.values()],
                                    axis=1), list(M.PULAU))
            lv['nasional'] = (arr.sum(axis=1, keepdims=True), ['INDONESIA'])
            for tk, (a, names) in lv.items():
                lo, me, hi = np.percentile(a / 1e6, [5, 50, 95], axis=0)
                for i, n in enumerate(names):
                    out.append((tk, n, M.PULAU_DARI.get(n, n if tk == 'pulau' else ''), b, kmp, me[i], lo[i], hi[i]))
        cover = Xj / konsumsi
        for i, p in enumerate(M.PROV):
            risk.append((p, M.PULAU_DARI[p], b, np.median(cover[:, i]), np.mean(cover[:, i] < 1.0)))
        nas = Xj.sum(axis=1) / konsumsi.sum(axis=1)
        risk.append(('INDONESIA', '', b, np.median(nas), np.mean(nas < 1.0)))
    R = pd.DataFrame(out, columns=['tingkat', 'wilayah', 'pulau', 'periode', 'komponen', 'median_juta_ton', 'p05', 'p95'])
    R.to_csv(os.path.join(hasil, 'prakiraan.csv'), index=False)
    K = pd.DataFrame(risk, columns=['wilayah', 'pulau', 'periode', 'cukup_bulan_median', 'peluang_kurang_1_bulan'])
    K.to_csv(os.path.join(hasil, 'risiko_provinsi.csv'), index=False)
    n = R[(R.tingkat == 'nasional') & (R.komponen == 'total')]
    print(n.round(2).to_string(index=False))
    print(K[K.periode == '2026-12'].sort_values('peluang_kurang_1_bulan', ascending=False).head(8).round(2).to_string(index=False))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
