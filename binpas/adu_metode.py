"""Bahan adu versi penguatan INATRADE: data, pola hapus, dan metode isian (RANCANGAN_INATRADE.md bagian 4 dan 7).

Semua metode mengembalikan tarikan (jumlah sasaran x S) dalam satuan asli (ton) untuk perusahaan-bulan yang dihapus.
Dipakai oleh adu_versi.py; tidak dijalankan sendiri.
"""
import os
import warnings

import numpy as np
import pandas as pd

import tahap0 as T0

S_TARIK = 200
KUANTIL = np.array([0.025, 0.05] + [round(0.1 + 0.05 * i, 2) for i in range(17)] + [0.95, 0.975])
WIL = ['Jawa', 'Sumatera', 'Pulau lain']
BLOK_IDX = {'penyetelan': (0, 17), 'kalibrasi': (18, 23), 'ujian': (24, 32)}
LEBARAN = {'2024-04', '2025-03', '2026-03'}
VAR = ['peny', 'peng', 'sa', 'sk']


# ---------------------------------------------------------------- data
def muat(xlsm, kom='BERAS', bps=None):
    S = T0.baca(xlsm)
    L = T0.laporan(S)
    L = L[(L.kom == kom) & ~L.bulog]
    per = T0.PER
    ix = {p: i for i, p in enumerate(per)}
    F = L.groupby(['kode', 'per'], as_index=False).agg(peny=('peny', 'sum'), peng=('peng', 'sum'), sa=('sa', 'sum'),
                                                       sk=('sk', 'sum'), prov=('prov', 'first'))
    kode = sorted(F.kode.unique())
    ik = {k: i for i, k in enumerate(kode)}
    n, T = len(kode), len(per)
    Y = {v: np.full((n, T), np.nan) for v in VAR}
    for r in F.itertuples():
        for v in VAR:
            Y[v][ik[r.kode], ix[r.per]] = getattr(r, v)
    prov = F.groupby('kode').prov.first().reindex(kode)
    provs = sorted(prov.unique())
    wil = np.array([0 if T0.PULAU_DARI.get(p) == 'Jawa' else 1 if T0.PULAU_DARI.get(p) == 'Sumatera' else 2 for p in prov])
    R = S[(S.kom == kom) & S.kode.isin(kode)]
    antar = (R.tuj != '') & (R.tuj != R.prov)
    paw_share = (R['Rincian Penyaluran'] * antar).groupby(R.kode).sum() / R['Rincian Penyaluran'].groupby(R.kode).sum().replace(0, np.nan)
    paw = (paw_share.reindex(kode).fillna(0).values > 0.1).astype(int)
    prem = L.assign(pr=L['sub'].str.contains('Premium', case=False) * L.peny).groupby('kode').pr.sum() / \
        L.groupby('kode').peny.sum().replace(0, np.nan)
    prem = prem.reindex(kode).fillna(0.5).values
    a, z = BLOK_IDX['penyetelan']
    tot = np.nansum(Y['peny'][:, a:z + 1], axis=1)
    besar = np.zeros(n, bool)
    for w in range(3):
        idx = np.where(wil == w)[0]
        o = idx[np.argsort(-tot[idx])]
        c = np.cumsum(tot[o]) / max(tot[o].sum(), 1e-9)
        besar[o[:int((c < 0.8).sum()) + 1]] = tot[o[:int((c < 0.8).sum()) + 1]] > 0
    D = dict(n=n, T=T, per=per, kode=kode, Y=Y, wil=wil, prov=np.array([provs.index(p) for p in prov]), provs=provs,
             besar=besar, paw=paw, prem=prem, moy=np.array([int(p[5:]) for p in per]),
             leb=np.array([p in LEBARAN for p in per], float), dx=np.zeros((3, T)))
    if bps and os.path.exists(os.path.join(bps, 'produksi_bulanan_ksa.csv')):
        pb = pd.read_csv(os.path.join(bps, 'produksi_bulanan_ksa.csv'))
        pt = pd.read_csv(os.path.join(bps, 'produksi_tahunan.csv'))
        pb['w'] = [0 if T0.PULAU_DARI.get(p) == 'Jawa' else 1 if T0.PULAU_DARI.get(p) == 'Sumatera' else 2 for p in pb.prov]
        pt['w'] = [0 if T0.PULAU_DARI.get(p) == 'Jawa' else 1 if T0.PULAU_DARI.get(p) == 'Sumatera' else 2 for p in pt.prov]
        m25 = pb[pb.periode.str[:4] == '2025'].groupby(['w', 'periode']).padi_gkg_ton.sum()
        P = np.full((3, T), np.nan)
        for w in range(3):
            pola = m25[w] / m25[w].sum()
            t24 = pt[(pt.w == w) & (pt.tahun == 2024)].padi_gkg_ton.sum()
            for p, i in ix.items():
                if p[:4] == '2024':
                    P[w, i] = t24 * pola.get('2025' + p[4:], np.nan)
            for p, v in pb[pb.w == w].groupby('periode').padi_gkg_ton.sum().items():
                if p in ix:
                    P[w, ix[p]] = v
        lp = np.log(np.where(P > 0, P, np.nan))
        D['dx'] = np.nan_to_num(np.diff(lp, axis=1, prepend=lp[:, :1]))
    return D


# ---------------------------------------------------------------- pola hapus
def profil_hapus(D):
    """Peluang dan panjang lubang dari blok penyetelan saja."""
    a, z = BLOK_IDX['penyetelan']
    O = ~np.isnan(D['Y']['peny'][:, a:z + 1])
    n, T = O.shape
    strata = D['besar'].astype(int)
    mulai, amatan, panjang = np.zeros(2), np.zeros(2), {0: [], 1: []}
    mulai_b, amatan_b = np.zeros(13), np.zeros(13)
    for i in range(n):
        t = np.where(O[i])[0]
        if len(t) < 2:
            continue
        amatan[strata[i]] += len(t)
        for u in t:
            amatan_b[D['moy'][a + u]] += 1
        for p, q in zip(t[:-1], t[1:]):
            if q - p > 1:
                mulai[strata[i]] += 1
                mulai_b[D['moy'][a + p + 1]] += 1
                panjang[strata[i]].append(q - p - 1)
    semua = panjang[0] + panjang[1]
    for s in (0, 1):
        if len(panjang[s]) < 5:
            panjang[s] = semua
    h = (mulai + 1) / (amatan + 20)
    hb = mulai.sum() / max(amatan.sum(), 1)
    mb = (mulai_b + 3) / (amatan_b * hb + 3)
    ekor, pop, klen = np.zeros(2), np.zeros(2), {0: [], 1: []}
    for t in range(3, T):
        for i in range(n):
            lalu = np.where(O[i, max(0, t - 3):t])[0]
            if len(lalu):
                pop[strata[i]] += 1
                if not O[i, t]:
                    ekor[strata[i]] += 1
                    klen[strata[i]].append(min(t - (max(0, t - 3) + lalu[-1]), 3))
    for s in (0, 1):
        if len(klen[s]) < 5:
            klen[s] = klen[0] + klen[1] or [1]
    return dict(h=h, mb=mb, panjang=panjang, p_ekor=(ekor + 1) / (pop + 10), klen=klen)


def hapus_tengah(D, P, rng, a, z, tmax, kali=1.0):
    O = ~np.isnan(D['Y']['peny'])
    O[:, tmax + 1:] = False
    M = np.zeros_like(O)
    for i in rng.permutation(D['n']):
        s = int(D['besar'][i])
        for t in range(a, z + 1):
            if O[i, t] and not M[i, t] and rng.random() < min(P['h'][s] * P['mb'][D['moy'][t]] * kali, 0.9):
                pj = int(rng.choice(P['panjang'][s]))
                baru = np.zeros(D['T'], bool)
                baru[t:min(t + pj, z + 1)] = True
                baru &= O[i] & ~M[i]
                if (O[i] & ~M[i] & ~baru).sum() >= 2:
                    M[i] |= baru
    return M


def hapus_akhir(D, P, rng, ts, kali=1.0):
    O = ~np.isnan(D['Y']['peny'])
    O[:, ts + 1:] = False
    M = np.zeros_like(O)
    for i in range(D['n']):
        s = int(D['besar'][i])
        if O[i, ts] and rng.random() < min(P['p_ekor'][s] * kali, 0.9):
            k = int(rng.choice(P['klen'][s]))
            baru = np.zeros(D['T'], bool)
            baru[ts - k + 1:ts + 1] = True
            baru &= O[i]
            if (O[i] & ~baru).sum() >= 2:
                M[i] = baru
    return M


# ---------------------------------------------------------------- alat bantu
def tetangga(obs):
    """Indeks amatan sebelum/sesudah tiap (i, t); -1 bila tidak ada."""
    n, T = obs.shape
    pv, nx = np.full((n, T), -1), np.full((n, T), -1)
    last = np.full(n, -1)
    for t in range(T):
        pv[:, t] = last
        last = np.where(obs[:, t], t, last)
    nxt = np.full(n, -1)
    for t in range(T - 1, -1, -1):
        nx[:, t] = nxt
        nxt = np.where(obs[:, t], t, nxt)
    return pv, nx


def indeks_kelompok(Yl, g, ng):
    """Log indeks berantai per kelompok dari median perubahan log pelapor yang sama."""
    T = Yl.shape[1]
    d = Yl[:, 1:] - Yl[:, :-1]
    G = np.zeros((ng, T))
    nas = np.array([np.nanmedian(d[:, t]) if np.isfinite(d[:, t]).sum() >= 1 else 0.0 for t in range(T - 1)])
    for k in range(ng):
        dk = d[g == k]
        for t in range(T - 1):
            x = dk[:, t]
            G[k, t + 1] = G[k, t] + (np.nanmedian(x) if np.isfinite(x).sum() >= 3 else nas[t])
    return G


def sd_kuat(x, t=False):
    x = x[np.isfinite(x)]
    if len(x) < 5:
        return 0.5
    if t:
        return max(1.4826 * np.median(np.abs(x - np.median(x))), 0.02)
    lo, hi = np.quantile(x, [0.025, 0.975])
    return max(np.clip(x, lo, hi).std(), 0.02)


def acak(rng, shape, t=False):
    return rng.standard_t(4, shape) if t else rng.standard_normal(shape)


def peluang_nol(Y):
    obs = ~np.isnan(Y)
    z = np.nansum(Y == 0, axis=1)
    nn = obs.sum(1)
    return (z + 2 * z.sum() / max(nn.sum(), 1)) / (nn + 2)


def dari_kuantil(Qm, rng, S):
    """Tarikan dari kuantil (baris = sasaran) lewat interpolasi CDF terbalik."""
    Qm = np.sort(Qm, axis=1)
    u = rng.uniform(0.01, 0.99, (Qm.shape[0], S))
    out = np.empty_like(u)
    for j in range(Qm.shape[0]):
        q = Qm[j]
        lo = q[0] - (q[1] - q[0]) * (KUANTIL[0] - 0.01) / (KUANTIL[1] - KUANTIL[0])
        hi = q[-1] + (q[-1] - q[-2]) * (0.99 - KUANTIL[-1]) / (KUANTIL[-1] - KUANTIL[-2])
        out[j] = np.interp(u[j], np.r_[0.01, KUANTIL, 0.99], np.r_[lo, q, hi])
    return out


# ---------------------------------------------------------------- metode sederhana B, C
def isi_bc(metode, D, Yv, ti, tt, rng, add):
    tdist = 'tdist' in add
    Y = Yv
    Yl = np.log(np.where(Y > 0, Y, np.nan))
    obs = np.isfinite(Yl)
    pv, nx = tetangga(obs)
    g = D['wil']
    G = indeks_kelompok(Yl, g, 3)
    Gi = G[g]
    # galat metode itu sendiri pada lubang buatan satu bulan (tengah) dan dari bulan lalu (akhir)
    a, b, c = Yl[:, :-2], Yl[:, 1:-1], Yl[:, 2:]
    if metode == 'B':
        e_mid = b - np.log((np.exp(a) + np.exp(c)) / 2)
        e_tail = Yl[:, 1:] - Yl[:, :-1]
    else:
        f = a + Gi[:, 1:-1] - Gi[:, :-2]
        r = c + Gi[:, 1:-1] - Gi[:, 2:]
        e_mid = b - (f + r) / 2
        e_tail = Yl[:, 1:] - (Yl[:, :-1] + Gi[:, 1:] - Gi[:, :-1])
    s_mid = sd_kuat(e_mid.ravel(), tdist) * np.sqrt(2)
    s_tail = sd_kuat(e_tail.ravel(), tdist)
    p0 = peluang_nol(Y)
    mu, sd = np.zeros(len(ti)), np.zeros(len(ti))
    gm = np.nanmedian(Yl) if obs.any() else 0.0
    for j, (i, t) in enumerate(zip(ti, tt)):
        p, q = pv[i, t], nx[i, t]
        if p >= 0 and q >= 0:
            k, h = t - p, q - p
            if metode == 'B':
                mu[j] = np.log(np.exp(Yl[i, p]) + k / h * (np.exp(Yl[i, q]) - np.exp(Yl[i, p])))
            else:
                mu[j] = (h - k) / h * (Yl[i, p] + Gi[i, t] - Gi[i, p]) + k / h * (Yl[i, q] + Gi[i, t] - Gi[i, q])
            sd[j] = s_mid * np.sqrt(k * (h - k) / h)
        elif p >= 0 or q >= 0:
            o = p if p >= 0 else q
            mu[j] = Yl[i, o] + (Gi[i, t] - Gi[i, o] if metode == 'C' else 0.0)
            sd[j] = s_tail * np.sqrt(abs(t - o))
        else:
            mu[j], sd[j] = gm, 2.0
    out = np.exp(mu[:, None] + sd[:, None] * acak(rng, (len(ti), S_TARIK), tdist))
    out[rng.random(out.shape) < p0[ti][:, None]] = 0.0
    return out


# ---------------------------------------------------------------- keluarga regresi R1-R4
def isi_reg(metode, D, Yv, ti, tt, rng, add):
    """log y[i,t] = a_i + b[g,t] + x'beta + u;  R2+: u AR(1);  R3+: a_i ditarik ke kelompok;  R4: + musiman."""
    ar, tarik, musim = metode in ('R2', 'R3', 'R4'), metode in ('R3', 'R4'), metode == 'R4'
    tdist = 'tdist' in add
    n, T = Yv.shape
    Yl = np.log(np.where(Yv > 0, Yv, np.nan))
    obs = np.isfinite(Yl)
    besar = D['besar']
    g = D['wil'] * 2 + besar if 'pola' in add else D['wil']
    ng = int(g.max()) + 1
    cols = []
    if musim:
        for m in range(1, 13):
            cols.append(np.outer(besar - besar.mean(), D['moy'] == m))
    if 'kalender' in add:
        panen = np.isin(D['moy'], [3, 4, 5]).astype(float)
        cols += [np.outer(besar - besar.mean(), D['leb']), np.outer(besar - besar.mean(), panen)]
    X = np.stack(cols, axis=2) if cols else None
    beta = np.zeros(len(cols))
    xb = np.zeros((n, T))
    a = np.where(obs.any(1), np.nanmean(np.where(obs, Yl, np.nan), axis=1), np.nan)
    a = np.where(np.isfinite(a), a, np.nanmedian(a) if np.isfinite(a).any() else 0.0)
    ni = obs.sum(1)
    Z = np.column_stack([D['paw'] - D['paw'].mean(), D['prem'] - D['prem'].mean()]) if 'ciri' in add else None
    b = np.zeros((ng, T))
    w = np.ones(n)
    mu_i = np.zeros(n)
    tau2 = np.ones(ng)
    for _ in range(12):
        R = Yl - a[:, None] - xb
        bn = np.array([np.nanmean(R[:, t]) if obs[:, t].any() else 0.0 for t in range(T)])
        for k in range(ng):
            Rk, ok = R[g == k], obs[g == k]
            cnt = ok.sum(0)
            b[k] = np.where(cnt >= 2, np.nansum(np.where(ok, Rk, 0), 0) / np.maximum(cnt, 1), bn)
        R = Yl - b[g] - xb
        am = np.where(ni > 0, np.nansum(np.where(obs, R, 0), 1) / np.maximum(ni, 1), np.nan)
        res = Yl - am[:, None] - b[g] - xb
        s2 = max(np.nanvar(res), 1e-4)
        for k in range(ng):
            sel = (g == k) & (ni > 0)
            if sel.sum() == 0:
                continue
            mk = np.median(am[sel])
            mu_i[g == k] = mk
            if Z is not None and sel.sum() >= 6:
                gam = np.linalg.lstsq(np.column_stack([np.ones(sel.sum()), Z[sel]]), am[sel], rcond=None)[0]
                mu_i[g == k] = gam[0] + Z[g == k] @ gam[1:]
            tau2[k] = max(np.var(am[sel] - mu_i[sel]) - np.mean(s2 / ni[sel]), 0.05)
        if tarik:
            w = np.where(besar, 1.0, tau2[g] / (tau2[g] + s2 / np.maximum(ni, 1)))
            a = np.where(ni > 0, mu_i + w * (np.nan_to_num(am) - mu_i), mu_i)
        else:
            a = np.where(ni > 0, np.nan_to_num(am), mu_i)
        if X is not None:
            Rr = (Yl - a[:, None] - b[g])[obs]
            Xo = X[obs]
            beta = np.linalg.solve(Xo.T @ Xo + 1.0 * np.eye(Xo.shape[1]), Xo.T @ Rr)
            xb = X @ beta
    if 'luar' in add:
        db, dxx = np.diff(b, axis=1).ravel(), D['dx'][:, 1:][np.minimum(np.arange(ng) if ng == 3 else np.arange(ng) // 2, 2)].ravel()
        kap = float(np.clip((db * dxx).sum() / max((dxx ** 2).sum(), 1e-9), -1, 1))
        for k in range(ng):
            cnt = obs[g == k].sum(0)
            wk = min(k if ng == 3 else k // 2, 2)
            for t in range(1, T):
                lam = cnt[t] / (cnt[t] + 3.0)
                b[k, t] = lam * b[k, t] + (1 - lam) * (b[k, t - 1] + kap * D['dx'][wk, t])
    res = Yl - a[:, None] - b[g] - xb
    if 'ragamkel' in add:
        sdv = np.array([sd_kuat(res[besar == u].ravel(), tdist) for u in (False, True)])[besar.astype(int)]
    else:
        sdv = np.full(n, sd_kuat(res.ravel(), tdist))
    rho = 0.0
    if ar:
        r0, r1 = res[:, :-1].ravel(), res[:, 1:].ravel()
        ok = np.isfinite(r0) & np.isfinite(r1)
        if ok.sum() > 10:
            rho = float(np.clip((r0[ok] * r1[ok]).sum() / max((r0[ok] ** 2).sum(), 1e-9), 0.0, 0.95))
    pv, nx = tetangga(obs)
    p0 = peluang_nol(Yv)
    mu, sd = np.zeros(len(ti)), np.zeros(len(ti))
    for j, (i, t) in enumerate(zip(ti, tt)):
        base = a[i] + b[g[i], t] + xb[i, t]
        s = sdv[i]
        p, q = pv[i, t], nx[i, t]
        cm, cv = 0.0, 1.0
        if rho > 0 and (p >= 0 or q >= 0):
            if p >= 0 and q >= 0:
                k, m = t - p, q - t
                den = 1 - rho ** (2 * (k + m))
                cm = (rho ** k * (1 - rho ** (2 * m)) * res[i, p] + rho ** m * (1 - rho ** (2 * k)) * res[i, q]) / den
                cv = (1 - rho ** (2 * k)) * (1 - rho ** (2 * m)) / den
            else:
                o = p if p >= 0 else q
                k = abs(t - o)
                cm, cv = rho ** k * res[i, o], 1 - rho ** (2 * k)
        va = s ** 2 * (w[i] if tarik else 1.0) / ni[i] if ni[i] > 0 else tau2[g[i]]
        mu[j], sd[j] = base + cm, np.sqrt(s ** 2 * cv + va)
    out = np.exp(mu[:, None] + sd[:, None] * acak(rng, (len(ti), S_TARIK), tdist))
    out[rng.random(out.shape) < p0[ti][:, None]] = 0.0
    return out


# ---------------------------------------------------------------- pohon: R5 QRF, R6 CatBoost
CB_SET = {'R6a': (4, 0.05, 500), 'R6b': (6, 0.05, 1000), 'R6c': (8, 0.03, 1500)}


def _fitur(D, Yl, ti, tt, add):
    obs = np.isfinite(Yl)
    pv, nx = tetangga(obs)
    g = D['wil']
    G = indeks_kelompok(Yl, g, 3)[g]
    ni = obs.sum(1)
    a = np.where(ni > 0, np.nansum(np.where(obs, Yl, 0), 1) / np.maximum(ni, 1), np.nan)
    med = np.array([np.nanmedian(a[g == k]) if np.isfinite(a[g == k]).any() else 0.0 for k in range(3)])
    a = np.where(np.isfinite(a), a, med[g])
    sdi = np.array([np.nanstd(Yl[i]) if ni[i] > 2 else np.nan for i in range(D['n'])])
    p, q = pv[ti, tt], nx[ti, tt]
    hp, hq = p >= 0, q >= 0
    lp = np.where(hp, Yl[ti, np.maximum(p, 0)] - a[ti], 0.0)
    lq = np.where(hq, Yl[ti, np.maximum(q, 0)] - a[ti], 0.0)
    cols = [lp, lq, hp.astype(float), hq.astype(float), np.where(hp, tt - p, 12).clip(0, 12),
            np.where(hq, q - tt, 12).clip(0, 12), np.where(hp, G[ti, tt] - G[ti, np.maximum(p, 0)], 0.0),
            np.where(hq, G[ti, tt] - G[ti, np.maximum(q, 0)], 0.0), a[ti] - med[g[ti]], ni[ti].astype(float),
            np.nan_to_num(sdi[ti], nan=0.5), D['besar'][ti].astype(float), g[ti].astype(float), D['moy'][tt].astype(float)]
    if 'kalender' in add:
        cols += [D['leb'][tt], np.isin(D['moy'][tt], [3, 4, 5]).astype(float)]
    if 'ciri' in add:
        cols += [D['paw'][ti].astype(float), D['prem'][ti]]
    return np.column_stack(cols), a


def _latih(D, P, Yv, tmax, rng, add, akhir):
    """Contoh latih dari lubang buatan di data yang tersedia (nilai yang sedang diuji tidak ikut)."""
    Yl0 = np.log(np.where(Yv > 0, Yv, np.nan))
    Xs, ys = [], []
    D2 = dict(D)
    D2['Y'] = {'peny': Yv}
    if akhir:
        for ts in range(3, tmax + 1):
            M = hapus_akhir(D2, P, rng, ts, kali=6.0)
            Yl = Yl0.copy()
            Yl[M] = np.nan
            Yl[:, ts + 1:] = np.nan
            i, t = np.where(M & np.isfinite(Yl0))
            if len(i):
                X, a = _fitur(D, Yl, i, t, add)
                Xs.append(X)
                ys.append(Yl0[i, t] - a[i])
    else:
        for _ in range(6):
            M = hapus_tengah(D2, P, rng, 0, tmax, tmax, kali=5.0)
            Yl = Yl0.copy()
            Yl[M] = np.nan
            i, t = np.where(M & np.isfinite(Yl0))
            if len(i):
                X, a = _fitur(D, Yl, i, t, add)
                Xs.append(X)
                ys.append(Yl0[i, t] - a[i])
    if not Xs:
        return None, None
    return np.vstack(Xs), np.concatenate(ys)


def _model(metode, X, y, seed):
    if metode == 'R5':
        from quantile_forest import RandomForestQuantileRegressor
        m = RandomForestQuantileRegressor(n_estimators=200, min_samples_leaf=5, random_state=seed, n_jobs=1).fit(X, y)
        return lambda Z: m.predict(Z, quantiles=list(KUANTIL))
    from catboost import CatBoostRegressor
    d, lr, it = CB_SET[metode]
    m = CatBoostRegressor(loss_function='MultiQuantile:alpha=' + ','.join(str(q) for q in KUANTIL), depth=d,
                          learning_rate=lr, iterations=it, verbose=0, thread_count=1, random_seed=seed)
    m.fit(X, y)
    return lambda Z: m.predict(Z)


def isi_pohon(metode, D, P, Yv, tmax, ti, tt, rng, add, hanya_akhir):
    Yl = np.log(np.where(Yv > 0, Yv, np.nan))
    X, a = _fitur(D, Yl, ti, tt, add)
    ada_next = X[:, 3] > 0
    Qm = np.zeros((len(ti), len(KUANTIL)))
    seed = int(rng.integers(1 << 30))
    for akhir in (False, True):
        sel = ~ada_next if akhir else ada_next
        if not sel.any():
            continue
        Xt, yt = _latih(D, P, Yv, tmax, rng, add, akhir)
        if Xt is None or len(yt) < 30:
            from scipy.stats import norm
            Qm[sel] = sd_kuat((Yl[:, 1:] - Yl[:, :-1]).ravel()) * norm.ppf(KUANTIL)[None, :]
            continue
        Qm[sel] = _model(metode, Xt, yt, seed)(X[sel])
    out = np.exp(a[ti][:, None] + dari_kuantil(Qm, rng, S_TARIK))
    p0 = peluang_nol(Yv)
    out[rng.random(out.shape) < p0[ti][:, None]] = 0.0
    return out


# ---------------------------------------------------------------- R7: regresi bertingkat + poststratifikasi
def isi_mrp(D, Yv, ti, tt, rng, add):
    tdist = 'tdist' in add
    Yl = np.log(np.where(Yv > 0, Yv, np.nan))
    i, t = np.where(np.isfinite(Yl))
    df = pd.DataFrame(dict(y=Yl[i, t], uk=D['besar'][i].astype(int), wil=D['wil'][i], paw=D['paw'][i], t=t))
    df['wu'] = df.wil * 2 + df.uk
    df['wt'] = df.wil * 100 + df.t
    df['satu'] = 1
    fx = dict(uk={}, wil={}, paw={}, t={}, wu={}, wt={})
    mu0, sd = df.y.mean(), df.y.std()
    try:
        import statsmodels.formula.api as smf
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            vc = {k: f'0 + C({k})' for k in ('wu', 'paw', 't', 'wt')}
            r = smf.mixedlm('y ~ 1', df, groups='satu', vc_formula=vc).fit(reml=True, method='lbfgs', maxiter=60)
        mu0, sd = float(r.fe_params.iloc[0]), float(np.sqrt(r.scale))
        for nama, v in r.random_effects[1].items():
            k, lv = nama.split('[')[0], nama.split('[')[1].rstrip(']')
            k = k.replace('C(', '').replace(')', '')
            fx[k][int(float(lv.split('.')[-1] if '.' in lv and not lv.replace('.', '').isdigit() else lv))] = float(v)
    except Exception:  # cadangan: penarikan empiris berurutan
        res = df.y - mu0
        for k in ('wu', 'paw', 't', 'wt'):
            gm = res.groupby(df[k]).agg(['mean', 'size'])
            s2, v = res.var(), max(gm['mean'].var() if len(gm) > 1 else 0.0, 1e-6)
            eff = gm['mean'] * v / (v + s2 / gm['size'])
            fx[k] = eff.to_dict()
            res = res - df[k].map(eff)
        sd = float(res.std())
    wu, wt = D['wil'][ti] * 2 + D['besar'][ti], D['wil'][ti] * 100 + tt
    mu = mu0 + np.array([fx['wu'].get(int(a_), 0.0) + fx['paw'].get(int(b_), 0.0) + fx['t'].get(int(c_), 0.0) + fx['wt'].get(int(d_), 0.0)
                         for a_, b_, c_, d_ in zip(wu, D['paw'][ti], tt, wt)])
    if tdist:
        sd = sd_kuat((df.y - mu0).values, True)
    out = np.exp(mu[:, None] + sd * acak(rng, (len(ti), S_TARIK), tdist))
    p0 = peluang_nol(Yv)
    out[rng.random(out.shape) < p0[ti][:, None]] = 0.0
    return out


# ---------------------------------------------------------------- pintu tunggal
def isi(metode, D, P, Yv, tmax, ti, tt, rng, add=frozenset(), hanya_akhir=False):
    if len(ti) == 0:
        return np.zeros((0, S_TARIK))
    if metode in ('B', 'C'):
        return isi_bc(metode, D, Yv, ti, tt, rng, add)
    if metode in ('R1', 'R2', 'R3', 'R4'):
        return isi_reg(metode, D, Yv, ti, tt, rng, add)
    if metode in ('R5', 'R6a', 'R6b', 'R6c'):
        return isi_pohon(metode, D, P, Yv, tmax, ti, tt, rng, add, hanya_akhir)
    if metode == 'R7':
        out = isi_mrp(D, Yv, ti, tt, rng, add)
        bs = D['besar'][ti]
        if bs.any():
            out[bs] = isi_reg('R2', D, Yv, ti[bs], tt[bs], rng, add)
        return out
    raise ValueError(metode)


def identitas_param(D, Y):
    """Laju v, simpangan relatif, dan peluang ekstrem dari pasangan Stok Awal[t] vs Stok Akhir[t-1] di data latih."""
    sa, sk = Y['sa'][:, 1:], Y['sk'][:, :-1]
    ok = np.isfinite(sa) & np.isfinite(sk) & ((sa > 0) | (sk > 0))
    rel = (sa[ok] - sk[ok]) / np.maximum(sa[ok], sk[ok])
    if len(rel) < 10:
        return dict(v=0.0, s=0.05, pe=0.1)
    eks = np.abs(rel) > 0.25
    biasa = rel[~eks]
    return dict(v=float(np.clip(-np.median(biasa), 0, 0.05)), s=float(max(biasa.std(), 0.005)), pe=float(eks.mean()))
