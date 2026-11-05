"""Model Bayesian state-space stok beras total per provinsi per bulan (PyMC).

Pakai:
  python -I model_stok.py <folder data> <folder keluaran> [--holdout 2022-12] [--draws 1000] [--chains 4]

<folder data> berisi keluaran inatrade_panel.py dan ambil_bps.py. jangkar_publik.csv dibaca dari folder skrip ini.

Persamaan keadaan, provinsi p, bulan t (Jul 2022 - Sep 2026; t=0 = akhir Juni 2022):
  X[p,t] = X[p,t-1] + (1-s)·produksi[p,t] + impor[t]·w[p] - (1+nu)·konsumsi_RT[p,t]
           + masuk[p] - keluar[p] + e[p,t]
  e         = guncangan sigma·konsumsi_RT[p]·z[p,t], dibuat berjumlah nol antar provinsi (arus tak termodel)
  nu        boleh menyimpang per tahun: log(1+nu_y) = log(1+nu) + dev_y, dev_y ~ N(0; 0,03)
  produksi  = padi GKG BPS (KSA bulanan 2025-2026; 2022-2024 tahunan x pola bulanan 2025) x 0,5762
  s         = susut/kehilangan, prior 2,5-10% produksi
  nu        = porsi konsumsi non rumah tangga (horeka, industri, dll.) di atas konsumsi Susenas
  masuk[q]  = theta[q] x defisit struktural q (konsumsi - produksi bersih rata-rata, bila positif) x g[t]
  keluar[p] = total masuk x pangsa surplus struktural p x musim panen p[t]; g[t] = rata-rata musim asal
              tertimbang, sehingga jumlah masuk = jumlah keluar tiap bulan.
  Peta asal-tujuan O[q,p] (untuk tabel arus) = arus INATRADE dicampur gravitasi (surplus asal, bobot 3x
  bila satu pulau), lalu diseimbangkan (RAS) agar kiriman tiap asal sebanding surplusnya.
  Stok provinsi hanya bergantung pada total masuk dan keluar, jadi arah INATRADE tidak mengubah stok.
Komponen: BULOG nasional B[t] (laten, acak berjalan log) dibagi ke provinsi dengan pangsa Dirichlet
  (prior campuran pangsa produksi & konsumsi; tidak ada data kanwil);
  sisanya (swasta) dibagi ke rumah tangga / penggilingan / pedagang / horeka dengan pangsa Dirichlet dari
  survei Juni 2022 dan akhir 2023.
Persamaan pengukuran (bias & noise per sumber):
  survei stok total (BPS SCBN Jun 2022; SSBAT Bapanas-BPS Des 2022, Des 2023): log y = log X_nas + bias_sumber + e
  stok BULOG (angka publik; laporan INATRADE 00372): log y = log B + bias_sumber + e
  INATRADE pedagang: log(stok akhir per perusahaan pelapor)[pulau,t] = a[pulau] + log swasta[pulau,t] + e
                     (Student-t; diagregasi per pulau, sel dengan >= 2 perusahaan)
  harga penggilingan medium (BPS): perubahan log 12 bulan = c + beta x perubahan log 12 bulan X_nas + e
"""
import argparse
import os

import numpy as np
import pandas as pd

KONV = 0.5762  # GKG -> beras (BPS 2024: 53,14 juta ton GKG = 30,62 juta ton beras)
AWAL, AKHIR = '2022-07', '2026-09'
PULAU = {
    'Sumatera': ['ACEH', 'SUMATERA UTARA', 'SUMATERA BARAT', 'RIAU', 'JAMBI', 'SUMATERA SELATAN', 'BENGKULU',
                 'LAMPUNG', 'KEPULAUAN BANGKA BELITUNG', 'KEPULAUAN RIAU'],
    'Jawa': ['DKI JAKARTA', 'JAWA BARAT', 'JAWA TENGAH', 'DAERAH ISTIMEWA YOGYAKARTA', 'JAWA TIMUR', 'BANTEN'],
    'Bali & Nusa Tenggara': ['BALI', 'NUSA TENGGARA BARAT', 'NUSA TENGGARA TIMUR'],
    'Kalimantan': ['KALIMANTAN BARAT', 'KALIMANTAN TENGAH', 'KALIMANTAN SELATAN', 'KALIMANTAN TIMUR',
                   'KALIMANTAN UTARA'],
    'Sulawesi': ['SULAWESI UTARA', 'SULAWESI TENGAH', 'SULAWESI SELATAN', 'SULAWESI TENGGARA', 'GORONTALO',
                 'SULAWESI BARAT'],
    'Maluku & Papua': ['MALUKU', 'MALUKU UTARA', 'PAPUA BARAT', 'PAPUA BARAT DAYA', 'PAPUA', 'PAPUA SELATAN',
                       'PAPUA TENGAH', 'PAPUA PEGUNUNGAN'],
}
PROV = [p for v in PULAU.values() for p in v]
PULAU_DARI = {p: k for k, v in PULAU.items() for p in v}
KOMP = ['rumah_tangga', 'penggilingan', 'pedagang', 'horeka']
# pangsa stok swasta (di luar BULOG) dari survei: Jun 2022 (SCBN) dan akhir 2023 (SSBAT), dirata-rata
PANGSA_SURVEI = np.array([0.796, 0.062, 0.104, 0.038])


def siapkan(data, holdout=None):
    here = os.path.dirname(os.path.abspath(__file__))
    bulan = pd.period_range(AWAL, AKHIR, freq='M')
    per = [str(b) for b in bulan]
    T, N = len(per), len(PROV)
    ip = {p: i for i, p in enumerate(PROV)}
    it = {b: i + 1 for i, b in enumerate(per)}  # indeks keadaan; 0 = akhir Jun 2022

    # produksi
    ksa = pd.read_csv(os.path.join(data, 'produksi_bulanan_ksa.csv'))
    th = pd.read_csv(os.path.join(data, 'produksi_tahunan.csv'))
    k25 = ksa[ksa.periode.str.startswith('2025')].copy()
    k25['m'] = k25.periode.str[5:].astype(int)
    pola = k25.pivot(index='prov', columns='m', values='padi_gkg_ton')
    pola = pola.div(pola.sum(axis=1), axis=0)
    kmap = {(r.prov, r.periode): r.padi_gkg_ton for r in ksa.itertuples()}
    tmap = {(r.prov, r.tahun): r.padi_gkg_ton for r in th.itertuples() if not np.isnan(r.padi_gkg_ton)}
    # 2022: provinsi pemekaran Papua masih tergabung di provinsi induk -> bagi menurut pangsa 2023
    for induk, anak in [('PAPUA', ['PAPUA', 'PAPUA SELATAN', 'PAPUA TENGAH', 'PAPUA PEGUNUNGAN']),
                        ('PAPUA BARAT', ['PAPUA BARAT', 'PAPUA BARAT DAYA'])]:
        tot22, tot23 = tmap[(induk, 2022)], sum(tmap[(a, 2023)] for a in anak)
        for a in anak:
            tmap[(a, 2022)] = tot22 * tmap[(a, 2023)] / tot23
    prod = np.zeros((N, T))
    sumber_prod = np.empty((N, T), dtype=object)
    for p in PROV:
        for b in per:
            y, m = int(b[:4]), int(b[5:])
            if (p, b) in kmap:
                v, src = kmap[(p, b)], 'KSA bulanan' + (' (potensi)' if b >= '2026-09' else '')
            else:
                v, src = tmap[(p, y)] * pola.loc[p, m], 'KSA tahunan x pola 2025'
            prod[ip[p], it[b] - 1] = v * KONV
            sumber_prod[ip[p], it[b] - 1] = src

    # konsumsi rumah tangga (Susenas x penduduk); 2026 = 2025 x 1,01
    K = pd.read_csv(os.path.join(data, 'konsumsi_provinsi.csv'))
    kc = {(r.prov, r.tahun): r.konsumsi_rt_ton_bulan for r in K.itertuples()}
    cons = np.array([[kc[(p, min(int(b[:4]), 2025))] * (1.01 if b >= '2026' else 1.0) for b in per]
                     for p in PROV])
    cbar = cons.mean(axis=1)
    wcons = cbar / cbar.sum()

    # jangkar publik
    J = pd.read_csv(os.path.join(here, 'jangkar_publik.csv'))
    imp = np.zeros(T)
    for r in J[J.jenis == 'impor'].itertuples():
        if r.periode == '2022-H2':
            idx = [it[b] - 1 for b in per if '2022-07' <= b <= '2022-12']
        else:
            idx = [it[b] - 1 for b in per if b.startswith(r.periode)]
        imp[idx] = r.nilai_juta_ton * 1e6 / 12 if r.periode != '2022-H2' else r.nilai_juta_ton * 1e6 / 6
    kons_bapanas = float(J[J.jenis == 'konsumsi_bapanas'].nilai_juta_ton.iloc[0]) * 1e6

    surv = []  # (t, nilai ton, sumber, dipakai)
    t0 = {'2022-06': 0}
    for r in J[J.jenis.str.startswith('survei')].itertuples():
        t = t0.get(r.periode, it.get(r.periode))
        surv.append((t, r.nilai_juta_ton * 1e6, r.jenis, r.periode != holdout, r.periode))
    bulog = []
    for r in J[J.jenis == 'bulog_publik'].itertuples():
        if r.periode in it:
            bulog.append((it[r.periode], r.nilai_juta_ton * 1e6, 0))
    L = pd.read_csv(os.path.join(data, 'laporan.csv'), dtype={'kode': str})
    Lb = L[L.bulog].groupby('periode')['sk'].sum()
    for b, v in Lb.items():
        # Sep 2026: stok akhir turun ke 2,2 juta ton karena "penyaluran" 3,1 juta ton yang bukan transaksi
        # pasar (lihat catatan sesi) -> tidak dipakai.
        if b in it and b != '2026-09' and v > 0:
            bulog.append((it[b], float(v), 1))

    # INATRADE pedagang, diagregasi per pulau (komposisi pelapor per provinsi terlalu berubah-ubah)
    P = pd.read_csv(os.path.join(data, 'panel_provinsi.csv'))
    P = P[(P.stok_akhir_ton > 0) & P.prov.isin(PROV) & P.periode.isin(per)].copy()
    P['pulau'] = P.prov.map(PULAU_DARI)
    G = P.groupby(['pulau', 'periode'], as_index=False)[['stok_akhir_ton', 'perusahaan']].sum()
    G = G[G.perusahaan >= 2]
    pl = list(PULAU)
    inat = (np.array([pl.index(g) for g in G.pulau]), np.array([it[b] for b in G.periode]),
            np.log(G.stok_akhir_ton / G.perusahaan).values)

    # harga penggilingan medium: perubahan log 12 bulan, tiap 3 bulan (mengurangi autokorelasi)
    H = pd.read_csv(os.path.join(data, 'harga_penggilingan.csv'))
    H = H[H.kualitas == 'MEDIUM'].set_index('periode').rp_kg
    harga = []
    for b in per:
        b12 = str(pd.Period(b) - 12)
        if b in H.index and b12 in H.index and b12 in it and int(b[5:]) % 3 == 0:
            harga.append((it[b], it[b12], np.log(H[b] / H[b12])))
    harga = np.array(harga)

    # arus antar provinsi -> matriks pangsa asal O[q, p]
    pbar = prod.mean(axis=1)
    surplus0 = pbar * 0.95 - cbar * (kons_bapanas / cons[:, -1].sum())
    sp = np.clip(surplus0, 0, None)
    pul = np.array([PULAU_DARI[p] for p in PROV])
    grav = sp[None, :] * np.where(pul[:, None] == pul[None, :], 3.0, 1.0)
    np.fill_diagonal(grav, 0)
    grav = grav / grav.sum(axis=1, keepdims=True)
    inat_o = np.zeros((N, N))
    for f in ['arus_penyaluran.csv', 'arus_pengadaan.csv']:
        A = pd.read_csv(os.path.join(data, f))
        A = A[A.asal.isin(PROV) & A.tujuan.isin(PROV) & (A.asal != A.tujuan)]
        for r in A.itertuples():
            if sp[ip[r.asal]] > 0:  # hanya provinsi surplus yang bisa jadi asal bersih
                inat_o[ip[r.tujuan], ip[r.asal]] += r.ton
    tot = inat_o.sum(axis=1, keepdims=True)
    w = np.where(tot > 0, tot / (tot + 12 * 0.05 * cbar[:, None]), 0.0)  # bobot data ~ tonase relatif
    w = np.minimum(w, 0.7)
    O = (1 - w) * grav + w * np.divide(inat_o, tot, out=np.zeros_like(inat_o), where=tot > 0)
    de = np.clip(-surplus0, 0, None)
    Mq = de[:, None] * O
    target = sp / sp.sum() * de.sum()
    for _ in range(200):  # RAS: baris = defisit tujuan, kolom = kiriman sebanding surplus asal
        cs = Mq.sum(axis=0)
        Mq = Mq * np.divide(target, cs, out=np.ones_like(cs), where=cs > 0)[None, :]
        rs = Mq.sum(axis=1)
        Mq = Mq * np.divide(de, rs, out=np.zeros_like(rs), where=rs > 0)[:, None]
    O = np.divide(Mq, de[:, None], out=np.zeros_like(Mq), where=de[:, None] > 0)

    musim_prov = prod / prod.mean(axis=1, keepdims=True)
    tahun = sorted({b[:4] for b in per})
    idx_tahun = np.array([tahun.index(b[:4]) for b in per])
    return dict(musim_prov=musim_prov, tahun=tahun, idx_tahun=idx_tahun, per=per, T=T, N=N, prod=prod, sumber_prod=sumber_prod, cons=cons, cbar=cbar, wcons=wcons,
                imp=imp, kons_bapanas=kons_bapanas, surv=surv, bulog=bulog, inat=inat, harga=harga, O=O,
                w_inat=w[:, 0], pbar=pbar)


def grup(tingkat):
    if tingkat == 'provinsi':
        return np.eye(len(PROV))
    if tingkat == 'nasional':
        return np.ones((1, len(PROV)))
    return np.array([[1.0 if PULAU_DARI[p] == k else 0.0 for p in PROV] for k in PULAU])


def bangun(D):
    import pymc as pm
    import pytensor.tensor as pt

    N, T = D['N'], D['T']
    cons, prod, cbar = D['cons'], D['prod'], D['cbar']
    nu_mu = np.log(D['kons_bapanas'] / cons[:, -1].sum())
    with pm.Model() as m:
        s = pm.Deterministic('susut', 0.025 + 0.075 * pm.Beta('susut_b', 2, 2))
        lognu = pm.Normal('log_1_plus_nu', nu_mu, 0.1)
        # simpangan tahunan konsumsi non-RT/kehilangan (2022..2026), prior ketat
        dnu = pm.Normal('dev_tahunan_nu', 0, D.get('sd_tahunan', 0.03), shape=len(D['tahun']))
        fnu_t = pt.exp(lognu + dnu[D['idx_tahun']])  # per bulan
        fnu = pt.exp(lognu)
        sigma = pm.HalfNormal('sigma_proses', 0.05)
        X0n = pm.LogNormal('stok_awal_nasional', np.log(8e6), 0.5)
        a0 = 0.5 * cbar / cbar.sum() + 0.5 * D['pbar'] / D['pbar'].sum()
        sh0 = pm.Dirichlet('pangsa_awal', 20 * N * a0)
        X0 = X0n * sh0
        tau_th = pm.HalfNormal('tau_theta', 0.1)
        theta = pt.exp(tau_th * pm.Normal('eta_theta', 0, 1, shape=N))
        neto = D['pbar'] * (1 - s) + D['imp'].mean() * D['wcons'] - cbar * fnu
        k = 0.05 * cbar  # max(x, 0) dihaluskan (softplus) supaya gradien tidak patah saat neraca berganti tanda
        masuk = theta * k * pt.softplus(-neto / k)
        surplus = k * pt.softplus(neto / k)
        shs = surplus / surplus.sum()
        keluar = masuk.sum() * shs  # tiap provinsi surplus mengirim sebanding surplusnya
        # kiriman mengikuti musim panen provinsi asal; penerimaan mengikuti musim gabungan asal
        # (rata-rata tertimbang), sehingga jumlah masuk = jumlah keluar di setiap bulan
        ma = 0.5 + 0.5 * D['musim_prov']
        g = pt.dot(shs, ma)
        z = pm.Normal('z', 0, 1, shape=(N, T))
        e = sigma * cbar[:, None] * z
        e = e - (cbar / cbar.sum())[:, None] * e.sum(axis=0)[None, :]  # guncangan = arus tak termodel, jumlah 0
        d = (prod * (1 - s) + D['imp'][None, :] * D['wcons'][:, None] - cons * fnu_t[None, :]
             + masuk[:, None] * g[None, :] - keluar[:, None] * ma + e)
        X = pt.concatenate([X0[:, None], X0[:, None] + pt.cumsum(d, axis=1)], axis=1)
        X = pm.Deterministic('stok', X)
        Xn = X.sum(axis=0)

        # BULOG nasional
        sB = pm.HalfNormal('sigma_bulog', 0.15)
        lB0 = pm.Normal('log_bulog_awal', np.log(1.1e6), 0.3)
        zB = pm.Normal('zB', 0, 1, shape=T)
        lB = pt.concatenate([lB0[None], lB0 + pt.cumsum(sB * zB)])
        B = pm.Deterministic('bulog', pt.exp(lB))
        bt, bv, bs = map(np.array, zip(*D['bulog']))
        bias_b = pt.stack([0.0, pm.Normal('bias_bulog_inatrade', 0, 0.1)])
        pm.Normal('obs_bulog', lB[bt] + bias_b[bs], 0.05, observed=np.log(bv))  # noise angka stok BULOG ~5%

        # pangsa BULOG per provinsi: tidak ada data kanwil, prior = campuran pangsa produksi & konsumsi
        wB = pm.Dirichlet('pangsa_bulog', 5 * N * a0)
        swasta = X - B[None, :] * wB[:, None]
        if 'positif' not in D.get('tanpa', ()):
            # stok swasta tidak boleh negatif. Diterapkan per kelompok (pulau secara baku): di tingkat provinsi
            # model arus terlalu kasar sehingga kendala per provinsi justru memaksa level nasional naik.
            G = D['grup_positif']
            sg, cg = pt.dot(G, swasta), G @ cbar
            neg = pt.maximum(-sg, 0) / (0.3 * cg[:, None])
            pm.Potential('swasta_positif', -0.5 * pt.sum(neg ** 2))
            # stok total tiap provinsi tidak negatif (kendala fisik; lebih lemah dari swasta >= 0 per provinsi)
            negp = pt.maximum(-X, 0) / (0.3 * cbar[:, None])
            pm.Potential('total_provinsi_positif', -0.5 * pt.sum(negp ** 2))
        pm.Dirichlet('pangsa_komponen', 30 * PANGSA_SURVEI)

        # survei stok total
        st = np.array([x[0] for x in D['surv'] if x[3]])
        sv = np.array([x[1] for x in D['surv'] if x[3]])
        ss = np.array([0 if x[2] == 'survei_bapanas' else 1 for x in D['surv'] if x[3]])
        bias_s = pm.Normal('bias_survei', 0, 0.25, shape=2)  # 0 = SSBAT Bapanas-BPS, 1 = SCBN BPS 2022
        pm.Normal('obs_survei', pt.log(Xn[st]) + bias_s[ss], 0.05, observed=np.log(sv))

        # INATRADE pedagang
        pi_, ti_, yi = D['inat'] if 'inatrade' not in D.get('tanpa', ()) else (D['inat'][0][:1], D['inat'][1][:1], D['inat'][2][:1])
        Gp = grup('pulau')
        swp = pt.dot(Gp, swasta)  # stok swasta per pulau
        mu_a = pm.Normal('mu_a', -8, 3)
        tau_a = pm.HalfNormal('tau_a', 1)
        a = mu_a + tau_a * pm.Normal('eta_a', 0, 1, shape=Gp.shape[0])
        sd_i = pm.HalfNormal('sd_inatrade', 0.5)
        cg = Gp @ cbar
        lsw = pt.log(0.2 * cg[pi_] * pt.softplus(swp[pi_, ti_] / (0.2 * cg[pi_])))
        pm.StudentT('obs_inatrade', nu=4, mu=a[pi_] + lsw, sigma=sd_i, observed=yi)

        # harga
        H = D['harga'] if 'harga' not in D.get('tanpa', ()) else D['harga'][:1]
        c = pm.Normal('c_harga', 0.05, 0.1)
        beta = pm.Normal('beta_harga', -0.1, 0.1)
        sd_h = pm.HalfNormal('sd_harga', 0.1)
        h1, h0 = H[:, 0].astype(int), H[:, 1].astype(int)
        pm.Normal('obs_harga', c + beta * (pt.log(Xn[h1]) - pt.log(Xn[h0])), sd_h, observed=H[:, 2])
    return m


def ringkas(D, post, out, label):
    """post: dict/posterior berisi stok, bulog, pangsa_komponen, pangsa_bulog (dimensi chain, draw, ...)."""
    X = np.asarray(post['stok']).reshape(-1, D['N'], D['T'] + 1)
    B = np.asarray(post['bulog']).reshape(-1, D['T'] + 1)
    pk = np.asarray(post['pangsa_komponen']).reshape(-1, 4)
    wB = np.asarray(post['pangsa_bulog']).reshape(-1, D['N'])
    Bp = B[:, None, :] * wB[:, :, None]
    sw = np.clip(X - Bp, 0, None)
    comp = {'total': X, 'bulog': Bp, 'swasta': sw}
    for j, k in enumerate(KOMP):
        comp[k] = sw * pk[:, j][:, None, None]
    per = ['2022-06'] + D['per']
    keep = [i for i, b in enumerate(per) if b >= '2024-01']

    def q(a):
        return np.percentile(a, [5, 50, 95], axis=0)

    rows = []
    for k, arr in comp.items():
        lv = {'provinsi': (arr, PROV)}
        isl = np.stack([arr[:, [PROV.index(p) for p in v], :].sum(axis=1) for v in PULAU.values()], axis=1)
        lv['pulau'] = (isl, list(PULAU))
        lv['nasional'] = (arr.sum(axis=1, keepdims=True), ['INDONESIA'])
        for lvl, (a, names) in lv.items():
            lo, me, hi = q(a / 1e6)
            for i, n in enumerate(names):
                for t in keep:
                    rows.append((lvl, n, PULAU_DARI.get(n, n if lvl == 'pulau' else ''), per[t], k,
                                 me[i, t], lo[i, t], hi[i, t]))
    R = pd.DataFrame(rows, columns=['tingkat', 'wilayah', 'pulau', 'periode', 'komponen', 'median_juta_ton',
                                    'p05', 'p95'])
    R.to_csv(os.path.join(out, f'posterior_{label}.csv'), index=False)
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data')
    ap.add_argument('out')
    ap.add_argument('--holdout', default=None)
    ap.add_argument('--draws', type=int, default=1000)
    ap.add_argument('--tune', type=int, default=2000)
    ap.add_argument('--chains', type=int, default=4)
    ap.add_argument('--seed', type=int, default=2026)
    ap.add_argument('--positif', default='pulau', choices=['provinsi', 'pulau', 'nasional'],
                    help='tingkat kendala stok swasta >= 0')
    ap.add_argument('--ringkas-saja', default=None, help='label posterior yang ringkasannya dihitung ulang')
    ap.add_argument('--tanpa', default='', help='diagnostik: matikan komponen, mis. positif,inatrade')
    A = ap.parse_args()
    import arviz as az
    import pymc as pm

    os.makedirs(A.out, exist_ok=True)
    D = siapkan(A.data, A.holdout)
    if A.ringkas_saja:  # hitung ulang ringkasan dari posterior_<label>.npz yang sudah ada
        z = np.load(os.path.join(A.out, f'posterior_{A.ringkas_saja}.npz'))
        ringkas(D, z, A.out, A.ringkas_saja)
        print('ringkasan ditulis ulang:', A.ringkas_saja)
        return
    D['tanpa'] = tuple(x for x in A.tanpa.split(',') if x)
    D['grup_positif'] = grup(A.positif)
    m = bangun(D)
    with m:
        try:
            import nutpie  # noqa: F401  (adaptasi matriks massa lebih baik untuk posterior berkorelasi)
            kw = dict(nuts_sampler='nutpie', nuts_sampler_kwargs={'low_rank_modified_mass_matrix': True,
                                                                  'target_accept': 0.95})
        except ImportError:
            kw = dict(target_accept=0.95)
        idata = pm.sample(A.draws, tune=A.tune, chains=A.chains, cores=A.chains, random_seed=A.seed,
                          progressbar=False, **kw)
    label = ('holdout_' + A.holdout if A.holdout else 'penuh') + ('' if A.positif == 'pulau' else '_positif_' + A.positif) + ('_tanpa_' + '_'.join(D['tanpa']) if D['tanpa'] else '')
    np.savez_compressed(os.path.join(A.out, f'posterior_{label}.npz'),
                        **{v: np.asarray(idata.posterior[v]) for v in ['stok', 'bulog', 'pangsa_komponen', 'pangsa_bulog',
                                                                        'bias_survei', 'susut', 'log_1_plus_nu']})
    vars_ = ['susut', 'log_1_plus_nu', 'dev_tahunan_nu', 'sigma_proses', 'stok_awal_nasional', 'tau_theta', 'sigma_bulog',
             'bias_bulog_inatrade', 'bias_survei', 'mu_a', 'tau_a', 'sd_inatrade', 'c_harga',
             'beta_harga', 'sd_harga', 'pangsa_komponen']
    S = az.summary(idata, var_names=vars_, ci_prob=0.9)
    S.to_csv(os.path.join(A.out, f'parameter_{label}.csv'))
    print(S.to_string())
    rh = az.rhat(idata, var_names=['stok', 'bulog'])
    rh = max(float(np.nanmax(np.asarray(rh[v]))) for v in ['stok', 'bulog'])
    dv = np.asarray(idata.sample_stats['diverging']).sum(axis=1)
    div = int(dv.sum())
    print(f'r_hat maks stok/bulog: {rh:.3f}; divergen: {div} (per rantai {dv.tolist()})')
    Xc = np.asarray(idata.posterior['stok']).sum(axis=2)
    print('stok nasional akhir per rantai (juta ton):', np.round(Xc[:, :, -1].mean(axis=1) / 1e6, 2).tolist())
    R = ringkas(D, idata.posterior, A.out, label)
    nas = R[(R.tingkat == 'nasional') & (R.komponen == 'total')]
    print(nas[nas.periode.str.endswith(('-03', '-06', '-09', '-12'))].to_string(index=False))
    # validasi titik survei yang disembunyikan
    Xn = idata.posterior['stok'].values.reshape(-1, D['N'], D['T'] + 1).sum(axis=1)
    bias = idata.posterior['bias_survei'].values.reshape(-1, 2)
    val = []
    for t, v, src, dipakai, b in D['surv']:
        j = 0 if src == 'survei_bapanas' else 1
        pred = Xn[:, t] * np.exp(bias[:, j] + 0.05 * np.random.default_rng(1).standard_normal(len(Xn)))
        lo, me, hi = np.percentile(pred / 1e6, [5, 50, 95])
        val.append((b, src, v / 1e6, me, lo, hi, 'ya' if dipakai else 'tidak (disembunyikan)'))
        print(f'survei {b} {src}: amatan {v / 1e6:.2f}; prediksi {me:.2f} ({lo:.2f}-{hi:.2f})'
              f'{"" if dipakai else "  <- disembunyikan"}')
    pd.DataFrame(val, columns=['periode', 'sumber', 'amatan_juta_ton', 'prediksi_median', 'prediksi_p05',
                               'prediksi_p95', 'dipakai_untuk_fit']).to_csv(
        os.path.join(A.out, f'validasi_{label}.csv'), index=False)


if __name__ == '__main__':
    main()
