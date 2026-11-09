"""Model Bayesian state-space stok komoditas tingkat B (impor dominan) per provinsi per bulan (PyMC).

Pakai:
  python -I model_neraca.py <komoditas> <folder data> <folder hasil> [--holdout 2025-09] [--tanpa inatrade]
         [--psi a,b] [--positif pulau|provinsi] [--draws 1000] [--tune 1000] [--chains 4] [--label nama]

<folder data> = keluaran siapkan_data.py. Persamaan keadaan, provinsi p, bulan t (t=0 = akhir bulan sebelum awal):
  X[p,t] = X[p,t-1] + produksi[p,t] + impor[p,t] - (1+nu_y)·konsumsi_RT[p,t] + masuk[p] - keluar[p] + e[p,t]
  impor      = impor BPS per pelabuhan, dicatat di provinsi pelabuhan (data, dianggap tepat)
  produksi   = produksi nasional USDA / 12 x pangsa provinsi (asumsi konfigurasi)
  konsumsi   = Susenas setara biji (tahu, tempe, kedelai) x penduduk; (1+nu) = pengali konsumsi di luar
               rumah tangga (kecap, tauco, susu kedelai, industri makanan, pakan, tercecer), simpangan per tahun
  masuk/keluar = provinsi defisit struktural menerima sebesar defisitnya x theta; provinsi surplus (pelabuhan)
               mengirim sebanding surplusnya; jumlah masuk = jumlah keluar; tidak ada musim
  e          = guncangan provinsi berjumlah nol + guncangan nasional (beda waktu catat impor vs datang, dll.)
Pengukuran:
  stok akhir USDA (akhir tahun pemasaran): log y = log X_nas + bias_usda + galat
  stok tercatat INATRADE (importir/distributor pelapor): log S_t = log(c_t·psi) + log X_nas,t + galat Student-t
      c_t = pangsa pengadaan pelapor terhadap impor (6 bulan bergulir), psi = porsi stok nasional yang
      berada di tahap importir/distributor (sisanya di perajin, industri)
  kendala lunak: X_nas,t >= S_t, stok total tiap pulau >= 0
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

AKAR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AKAR)
sys.path.insert(0, os.path.join(AKAR, '..', 'beras_stok'))
from konfigurasi import KOMODITAS  # noqa: E402
from model_stok import PROV, PULAU, PULAU_DARI  # noqa: E402
from siapkan_data import bulan_list  # noqa: E402


def siapkan(K, data, holdout=None, tanpa=()):
    per = bulan_list(K['awal'], K['akhir'])
    N, T = len(PROV), len(per)
    ip = {p: i for i, p in enumerate(PROV)}
    it = {b: i for i, b in enumerate(per)}

    def mat(df, kol='ton'):
        M = np.zeros((N, T))
        for r in df.itertuples():
            if r.periode in it:
                M[ip[r.prov], it[r.periode]] += getattr(r, kol)
        return M

    imp = mat(pd.read_csv(os.path.join(data, 'impor_bulanan.csv')))
    prod = mat(pd.read_csv(os.path.join(data, 'produksi_bulanan.csv')))
    C = pd.read_csv(os.path.join(data, 'konsumsi_provinsi.csv'))
    tahun = sorted({int(b[:4]) for b in per})
    ck = {(r.prov, r.tahun): r.konsumsi_rt_ton_bulan for r in C.itertuples()}
    tmax = C.tahun.max()
    cons = np.array([[ck[(p, min(int(b[:4]), tmax))] for b in per] for p in PROV])
    U = pd.read_csv(os.path.join(data, 'usda_neraca.csv'))
    jangkar = []
    for my in K['jangkar_usda_my']:
        r = U[U.tahun_pemasaran == my].iloc[0]
        if r.periode_akhir in it and r.periode_akhir != holdout:
            jangkar.append((it[r.periode_akhir] + 1, float(r.stok_akhir), 0.25 if my == max(K['jangkar_usda_my']) else 0.15))
    inat = None
    if 'inatrade' not in tanpa:
        n = pd.read_csv(os.path.join(data, 'inatrade_nasional.csv'))
        L = pd.read_csv(os.path.join(data, 'inatrade_laporan.csv'))
        peng = L.groupby('periode').peng.sum().reindex(per).fillna(0).values
        impn = imp.sum(axis=0)
        cov = np.array([peng[max(0, t - 5):t + 1].sum() / impn[max(0, t - 5):t + 1].sum() for t in range(T)])
        S = n.set_index('periode').stok_tercatat_ton.reindex(per).values
        ok = np.isfinite(S) & (S > 0) & (cov > 0)
        inat = (np.where(ok)[0] + 1, S[ok], np.clip(cov[ok], 0.02, 1.0))
    sup = (prod + imp).mean(axis=1)
    kpr = np.log(K['prior_konsumsi_total_ton_tahun'] / 12 / cons.sum(axis=0).mean())
    return dict(per=per, N=N, T=T, imp=imp, prod=prod, cons=cons, cbar=cons.mean(axis=1), sbar=sup,
                tahun=tahun, idx_tahun=np.array([tahun.index(int(b[:4])) for b in per]),
                jangkar=jangkar, inat=inat, nu_mu=kpr, K=K, tanpa=tanpa)


def bangun(D, psi_ab=(6.0, 2.0), positif='pulau'):
    import pymc as pm
    import pytensor.tensor as pt

    K, N, T = D['K'], D['N'], D['T']
    cons, cbar = D['cons'], D['cbar']
    with pm.Model() as m:
        lognu = pm.Normal('log_1_plus_nu', D['nu_mu'], 0.3)
        dnu = pm.Normal('dev_tahunan_nu', 0, 0.05, shape=len(D['tahun']))
        fnu_t = pt.exp(lognu + dnu[D['idx_tahun']])
        fnu = pt.exp(lognu)
        X0n = pm.LogNormal('stok_awal_nasional', np.log(K['prior_stok_awal_ton']), 0.7)
        a0 = 0.5 * cbar / cbar.sum() + 0.5 * D['sbar'] / D['sbar'].sum()
        X0 = X0n * pm.Dirichlet('pangsa_awal', 20 * N * a0)
        tau_th = pm.HalfNormal('tau_theta', 0.1)
        theta = pt.exp(tau_th * pm.Normal('eta_theta', 0, 1, shape=N))
        neto = D['sbar'] - cbar * fnu
        k = 0.05 * cbar
        masuk = theta * k * pt.softplus(-neto / k)
        surplus = k * pt.softplus(neto / k)
        keluar = masuk.sum() * surplus / surplus.sum()
        sigma = pm.HalfNormal('sigma_proses', 0.05)
        e = sigma * cbar[:, None] * pm.Normal('z', 0, 1, shape=(N, T))
        e = e - (cbar / cbar.sum())[:, None] * e.sum(axis=0)[None, :]
        sn = pm.HalfNormal('sigma_nasional', 0.05)
        en = sn * cbar.sum() * pm.Normal('zn', 0, 1, shape=T)
        e = e + (cbar / cbar.sum())[:, None] * en[None, :]
        d = D['prod'] + D['imp'] - cons * fnu_t[None, :] + (masuk - keluar)[:, None] + e
        X = pt.concatenate([X0[:, None], X0[:, None] + pt.cumsum(d, axis=1)], axis=1)
        X = pm.Deterministic('stok', X)
        Xn = X.sum(axis=0)
        # stok >= 0 per pulau (bukan per provinsi): impor masuk bergelombang di provinsi pelabuhan dan arus
        # antar provinsi dimodelkan rata, sehingga kendala per provinsi memaksa level nasional naik (sama seperti beras)
        G = np.eye(N) if positif == 'provinsi' else np.array([[1.0 if PULAU_DARI[p] == g else 0.0 for p in PROV] for g in PULAU])
        negp = pt.maximum(-pt.dot(G, X), 0) / (0.3 * (G @ cbar)[:, None])
        pm.Potential('total_pulau_positif', -0.5 * pt.sum(negp ** 2))
        if D['jangkar']:
            jt, jv, js = map(np.array, zip(*D['jangkar']))
            b_u = pm.Normal('bias_usda', 0, K['sd_bias_usda'])
            pm.Normal('obs_usda', pt.log(pt.maximum(Xn[jt], 1.0)) + b_u, js, observed=np.log(jv))
        if D['inat'] is not None:
            ti, S, cov = D['inat']
            psi = pm.Beta('psi_importir', *psi_ab)
            sd_i = pm.HalfNormal('sd_inatrade', 0.5)
            pm.StudentT('obs_inatrade', nu=4, mu=pt.log(cov * psi) + pt.log(pt.maximum(Xn[ti], 1.0)), sigma=sd_i,
                        observed=np.log(S))
            neg = pt.maximum(S - Xn[ti], 0) / (0.1 * S)
            pm.Potential('nasional_di_atas_tercatat', -0.5 * pt.sum(neg ** 2))
    return m


def ringkas(D, post, out, label):
    T = D['T']
    pr = [str(pd.Period(D['per'][0], 'M') - 1)] + D['per']
    X = np.asarray(post['stok']).reshape(-1, D['N'], T + 1)
    fnu = np.exp(np.asarray(post['log_1_plus_nu']).reshape(-1))
    rows = []
    lv = {'provinsi': [(p, [i]) for i, p in enumerate(PROV)],
          'pulau': [(g, [PROV.index(p) for p in ps]) for g, ps in PULAU.items()],
          'nasional': [('INDONESIA', list(range(D['N'])))]}
    for tk, items in lv.items():
        for w, ix in items:
            a = X[:, ix, :].sum(axis=1) / 1e3
            q = np.percentile(a, [5, 50, 95], axis=0)
            ck = D['cons'][ix].sum(axis=0)
            for t, b in enumerate(pr):
                c = ck[max(0, t - 1)] * np.median(fnu) / 1e3
                rows.append((tk, w, PULAU_DARI.get(w, w if tk == 'pulau' else ''), b, q[1, t], q[0, t], q[2, t], q[1, t] / c))
    R = pd.DataFrame(rows, columns=['tingkat', 'wilayah', 'pulau', 'periode', 'median_ribu_ton', 'p05', 'p95', 'cukup_bulan'])
    R.to_csv(os.path.join(out, f'posterior_{label}.csv'), index=False)
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('komoditas')
    ap.add_argument('data')
    ap.add_argument('out')
    ap.add_argument('--holdout', default=None, help='sembunyikan jangkar USDA pada bulan ini, mis. 2025-09')
    ap.add_argument('--tanpa', default='', help='inatrade')
    ap.add_argument('--psi', default='6,2', help='prior Beta porsi stok di tahap importir/distributor')
    ap.add_argument('--positif', default='pulau', choices=['pulau', 'provinsi'], help='tingkat kendala stok >= 0')
    ap.add_argument('--draws', type=int, default=1000)
    ap.add_argument('--tune', type=int, default=1000)
    ap.add_argument('--chains', type=int, default=4)
    ap.add_argument('--seed', type=int, default=11)
    ap.add_argument('--label', default='dasar')
    A = ap.parse_args()
    import arviz as az
    import pymc as pm

    K = KOMODITAS[A.komoditas]
    os.makedirs(A.out, exist_ok=True)
    tanpa = tuple(x for x in A.tanpa.split(',') if x)
    D = siapkan(K, A.data, A.holdout, tanpa)
    m = bangun(D, tuple(float(x) for x in A.psi.split(',')), A.positif)
    with m:
        try:
            import nutpie  # noqa: F401
            kw = dict(nuts_sampler='nutpie', nuts_sampler_kwargs={'low_rank_modified_mass_matrix': True, 'target_accept': 0.95})
        except ImportError:
            kw = dict(target_accept=0.95)
        idata = pm.sample(A.draws, tune=A.tune, chains=A.chains, cores=A.chains, random_seed=A.seed, progressbar=False, **kw)
    simpan = [v for v in ['stok', 'log_1_plus_nu', 'dev_tahunan_nu', 'bias_usda', 'psi_importir', 'sigma_proses',
                          'sigma_nasional', 'sd_inatrade', 'stok_awal_nasional'] if v in idata.posterior]
    np.savez_compressed(os.path.join(A.out, f'posterior_{A.label}.npz'), **{v: np.asarray(idata.posterior[v]) for v in simpan})
    par = [v for v in simpan if v != 'stok']
    S = az.summary(idata, var_names=par, ci_prob=0.9)
    S.to_csv(os.path.join(A.out, f'parameter_{A.label}.csv'))
    div = int(idata.sample_stats['diverging'].sum()) if 'diverging' in idata.sample_stats else -1
    rs = az.rhat(idata, var_names=['stok'])['stok'].values
    R = ringkas(D, idata.posterior, A.out, A.label)
    print(S[['mean', 'sd', 'r_hat']].round(3).to_string())
    print(f'divergensi {div}; r-hat maks stok {np.nanmax(rs):.3f}')
    n = R[R.tingkat == 'nasional'].set_index('periode')
    print(n.loc[[p for p in n.index if p.endswith(('-03', '-09', '-12'))], ['median_ribu_ton', 'p05', 'p95', 'cukup_bulan']].round(1).to_string())
    if A.holdout:
        U = pd.read_csv(os.path.join(A.data, 'usda_neraca.csv'))
        y = float(U.loc[U.periode_akhir == A.holdout, 'stok_akhir'].iloc[0])
        t = D['per'].index(A.holdout) + 1
        Xn = np.asarray(idata.posterior['stok']).reshape(-1, D['N'], D['T'] + 1)[:, :, t].sum(axis=1)
        pred = Xn * np.exp(np.asarray(idata.posterior['bias_usda']).reshape(-1) + np.random.default_rng(1).normal(0, 0.15, Xn.size))
        q = np.percentile(pred, [5, 50, 95])
        pd.DataFrame([dict(jangkar='USDA stok akhir', periode=A.holdout, amatan=y, median=q[1], p05=q[0], p95=q[2])]).to_csv(
            os.path.join(A.out, f'validasi_{A.label}.csv'), index=False)
        print(f'holdout {A.holdout}: amatan {y / 1e3:.0f} ribu ton; prediksi {q[1] / 1e3:.0f} ({q[0] / 1e3:.0f}-{q[2] / 1e3:.0f})')


if __name__ == '__main__':
    main()
