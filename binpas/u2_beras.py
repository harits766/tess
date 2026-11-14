"""U2 beras: ujian keterwakilan terhadap daftar mitra Pola Distribusi BPS edisi 2025 (SEKALI JALAN).

Pakai:  python -I binpas/u2_beras.py <Non_PAW_dari_nol.xlsm> <mitra_2024.csv> <mitra_2025.csv> <folder keluaran>

Definisi dikunci di RANCANGAN_U2.md bagian 6 sebelum edisi 2025 dibuka. Keluaran agregat saja.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tahap0 as T0  # noqa: E402

N_BOOT, SEED = 2000, 20261114


def tautan_bps(path):
    B = pd.read_csv(path)
    prov = sorted(B.prov.dropna().unique())
    B = B[B.mitra.notna()]
    L = set((r.mitra, r.prov) for r in B[B.arah == 'beli'].itertuples()) | set((r.prov, r.mitra) for r in B[B.arah == 'jual'].itertuples())
    return prov, L


def inatrade(xlsm):
    """Tautan PAW beras (tanpa BULOG): asal = provinsi perusahaan, tujuan = provinsi penyaluran."""
    S = T0.baca(xlsm)
    S = S[(S.kom == 'BERAS') & (S.kode != T0.KODE_BULOG)].copy()
    kunci = ['kode', 'kom', 'sub', 'per']
    K = S.drop_duplicates(kunci + T0.Q)[kunci + T0.Q].copy()
    st = K[T0.Q].replace(0, np.nan).stack()
    idx = st.index.get_level_values(0)
    K['basis'] = st.groupby([K.kode.loc[idx].values, K['sub'].loc[idx].values]).median() \
        .reindex(pd.MultiIndex.from_arrays([K.kode, K['sub']])).values
    K['faktor'] = np.where((K.basis > 0) & (K[T0.Q].max(axis=1) / K.basis >= T0.AMBANG_KG), 1 / 1000, 1.0)   # aturan Tahap 0
    S = S.merge(K[kunci + T0.Q + ['faktor']], on=kunci + T0.Q, how='left')
    R = S[(S.tuj != '') & S.tuj.notna() & (S.tuj != S.prov) & (S['Rincian Penyaluran'] > 0)].copy()
    R['vol'] = R['Rincian Penyaluran'] * R.faktor.fillna(1.0)
    R['thn'] = R.per.str[:4]
    return R[['kode', 'per', 'thn', 'prov', 'tuj', 'vol']]


def ap(skor, benar):
    """Average precision dengan skor seri dikelompokkan (ambang = nilai skor yang berbeda)."""
    if benar.sum() == 0:
        return np.nan
    o = np.argsort(-skor, kind='stable')
    s, y = skor[o], benar[o]
    tp, n = np.cumsum(y), np.arange(1, len(y) + 1)
    akhir = np.r_[s[1:] != s[:-1], True]
    P, Rc = tp[akhir] / n[akhir], tp[akhir] / y.sum()
    return float(np.sum(np.diff(np.r_[0.0, Rc]) * P))


def prf(pred, benar):
    tp = float((pred & benar).sum())
    p, r = tp / max(pred.sum(), 1), tp / max(benar.sum(), 1)
    return dict(tautan=int(pred.sum()), presisi=p, recall=r, f1=2 * p * r / (p + r) if p + r else 0.0)


def spearman(a, b):
    ra, rb = pd.Series(a).rank().values, pd.Series(b).rank().values
    return float(np.corrcoef(ra, rb)[0, 1])


def main(xlsm, f24, f25, out):
    os.makedirs(out, exist_ok=True)
    kunci = os.path.join(out, 'U2_SUDAH_JALAN.json')
    if os.path.exists(kunci):
        sys.exit('U2 sudah pernah dijalankan; hanya sekali jalan.')
    p24, L24 = tautan_bps(f24)
    p25, L25 = tautan_bps(f25)
    prov = sorted(set(p24) & set(p25))
    json.dump(dict(mulai=time.strftime('%Y-%m-%d %H:%M:%S'), provinsi=len(prov)), open(kunci, 'w'))
    R = inatrade(xlsm)
    pasangan = [(a, b) for a in prov for b in prov if a != b]
    ix = {pb: i for i, pb in enumerate(pasangan)}
    tuj = np.array([prov.index(b) for _, b in pasangan])
    y = np.array([pb in L25 for pb in pasangan])
    b24 = np.array([pb in L24 for pb in pasangan], float)

    def skor_ina(g):
        n = g.drop_duplicates(['kode', 'per', 'prov', 'tuj']).groupby(['prov', 'tuj']).size()
        v = np.zeros(len(pasangan))
        for (a, b), k in n.items():
            if (a, b) in ix:
                v[ix[(a, b)]] = k
        return v
    ina = skor_ina(R)
    versi = {'INATRADE mentah': ina, 'BPS 2024 apa adanya': b24, 'gabungan (BPS 2024 + INATRADE)': b24 + 0.5 * (ina > 0)}
    hasil = {k: dict(ap=ap(v, y), **prf(v > 0, y)) for k, v in versi.items()}
    hasil['acak (kepadatan)'] = dict(ap=float(y.mean()), tautan=int(len(y)), presisi=float(y.mean()), recall=1.0, f1=float(2 * y.mean() / (1 + y.mean())))
    rng = np.random.default_rng(SEED)
    G, sel = 'gabungan (BPS 2024 + INATRADE)', {}
    D = {k: [] for k in versi if k != G}
    for _ in range(N_BOOT):
        s = rng.integers(0, len(prov), len(prov))
        m = np.concatenate([np.where(tuj == t)[0] for t in s])
        ag = ap(versi[G][m], y[m])
        for k in D:
            D[k].append(ag - ap(versi[k][m], y[m]))
    for k in D:
        d = np.array(D[k]); d = d[np.isfinite(d)]
        sel[k] = dict(selisih=hasil[G]['ap'] - hasil[k]['ap'], lo=float(np.quantile(d, 0.05)), hi=float(np.quantile(d, 0.95)))
    # gerbang (ii): korelasi peringkat volume keluar INATRADE per provinsi asal vs jumlah provinsi yang menyebutnya asal (BPS 2025)
    Rr = R[R.prov.isin(prov) & R.tuj.isin(prov)]
    vol = Rr.groupby('prov').vol.sum().reindex(prov).fillna(0).values
    ntuj = Rr.groupby('prov').tuj.nunique().reindex(prov).fillna(0).values
    deg25 = np.array([sum(1 for (a, b) in L25 if a == p and b in prov) for p in prov])
    deg24 = np.array([sum(1 for (a, b) in L24 if a == p and b in prov) for p in prov])
    kor = dict(volume_vs_bps2025=spearman(vol, deg25), jumlah_tujuan_vs_bps2025=spearman(ntuj, deg25), bps2024_vs_bps2025=spearman(deg24, deg25),
               provinsi_asal_inatrade=int((vol > 0).sum()))
    lolos_i = all(sel[k]['selisih'] > 0 and sel[k]['lo'] > 0 for k in sel)
    belum_i = (not lolos_i) and all(sel[k]['selisih'] > 0 for k in sel)
    gerbang = dict(lebih_dekat='lolos' if lolos_i else 'belum bisa diputuskan' if belum_i else 'gagal',
                   korelasi_asal='lolos' if kor['volume_vs_bps2025'] >= 0.6 else 'gagal')
    per_thn = {t: dict(ap=ap(skor_ina(g), y), perusahaan=int(g.kode.nunique()), **prf(skor_ina(g) > 0, y)) for t, g in R.groupby('thn')}
    ringkas = dict(provinsi=len(prov), pasangan=len(pasangan), tautan_bps2025=int(y.sum()), tautan_bps2024=int(b24.sum()),
                   tetap_2024_ke_2025=int((y & (b24 > 0)).sum()), perusahaan_paw=int(R.kode.nunique()), versi=hasil, selisih_gabungan=sel,
                   korelasi=kor, gerbang=gerbang, inatrade_per_tahun=per_thn, selesai=time.strftime('%Y-%m-%d %H:%M:%S'))
    json.dump(ringkas, open(os.path.join(out, 'hasil_U2.json'), 'w'), indent=1)
    print(json.dumps(ringkas, indent=1))


if __name__ == '__main__':
    main(*sys.argv[1:5])
