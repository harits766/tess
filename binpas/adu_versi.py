"""Adu versi penguatan INATRADE (RANCANGAN_INATRADE.md bagian 4 dan 7; ambang di ambang_ujian.md).

Pakai:
  python -I binpas/adu_versi.py coba       <xlsm> <keluaran> [folder bps]   # uji kode, beberapa ulangan saja
  python -I binpas/adu_versi.py penyetelan <xlsm> <keluaran> [folder bps]   # tahap 1a-5 + gerbang, blok Jan 2024-Jun 2025
  python -I binpas/adu_versi.py kalibrasi  <xlsm> <keluaran> [folder bps]   # Q konformal + bias, blok Jul-Des 2025
  python -I binpas/adu_versi.py ujian      <xlsm> <keluaran> [folder bps]   # U1, Jan-Sep 2026, SEKALI JALAN

Satu ulangan = satu pola hapus acak (lubang tengah + lubang akhir) yang sama untuk semua versi dan pembanding.
Keluaran berisi angka agregat per sel; tidak ada data per perusahaan.
"""
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adu_metode as AM  # noqa: E402

KU = AM.KUANTIL
NQ = len(KU)
QC = [f'q{i}' for i in range(NQ)]
IMED = int(np.argmin(np.abs(KU - 0.5)))
PASANG = {0.50: (int(np.argmin(np.abs(KU - 0.25))), int(np.argmin(np.abs(KU - 0.75)))),
          0.80: (int(np.argmin(np.abs(KU - 0.10))), int(np.argmin(np.abs(KU - 0.90)))),
          0.90: (int(np.argmin(np.abs(KU - 0.05))), int(np.argmin(np.abs(KU - 0.95)))),
          0.95: (0, NQ - 1)}
TINGKAT = ['prov', 'wil', 'nas']
UTAMA = 'wil'
MIN_POP = 3
PEMBANDING = ['A', 'A3', 'A5']
D = P = None


def cfg(ident='I0', metode='R2', batas=99, add=(), bobot=3, ragam=1.0, rekon=0):
    return (ident, metode, batas, tuple(sorted(add)), bobot, ragam, rekon)


def nama(c):
    return c if isinstance(c, str) else '|'.join(['+'.join(x) if isinstance(x, tuple) else str(x) for x in c])


# ---------------------------------------------------------------- satu ulangan
def _sel(M, tmax):
    """Daftar sel yang dinilai: (tingkat, id sel, bulan, anggota, sisa)."""
    O = ~np.isnan(D['Y']['peny'])
    ids = {'prov': D['prov'], 'wil': D['wil'], 'nas': np.zeros(D['n'], int)}
    out = []
    for t in np.where(M.any(0))[0]:
        for tk in TINGKAT:
            for c in np.unique(ids[tk][M[:, t]]):
                ang = (ids[tk] == c) & O[:, t]
                sisa = ang & ~M[:, t]
                if ang.sum() >= MIN_POP and sisa.any() and D['Y']['peny'][sisa, t].sum() > 0:
                    out.append((tk, int(c), int(t), ang, sisa))
    return out


def _dasar(cells, M):
    """Tiga pembanding (log taksiran) dan jawaban benar tiap sel."""
    Y = D['Y']['peny']
    bs = D['besar']
    rows = []
    for tk, c, t, ang, sisa in cells:
        benar = math.log(Y[ang, t].sum())
        a = Y[sisa, t].sum()
        est = {'A': a}
        for cap in (3, 5):
            tot = 0.0
            for u in (False, True):
                N, nn = (ang & (bs == u)).sum(), (sisa & (bs == u)).sum()
                if nn > 0:
                    tot += Y[sisa & (bs == u), t].sum() * min(N / nn, cap)
            if tot <= 0:
                tot = a * min(ang.sum() / sisa.sum(), cap)
            est[f'A{cap}'] = tot
        rows.append((tk, c, t, benar, {k: math.log(v) for k, v in est.items()}))
    return rows


def _isi_cfg(c, soal, cache, rng_seed):
    """Tarikan penyaluran untuk semua sasaran sebuah soal menurut konfigurasi c (sebelum bobot)."""
    ident, metode, batas, add, bobot, ragam, rekon = c
    add = frozenset(add)
    ti, tt, Yav, tmax = soal['ti'], soal['tt'], soal['Yav'], soal['tmax']
    out = {}
    for v in (['peny'] if ident == 'I0' else ['peny', 'peng']):
        k = (metode, add, v)
        if k not in cache:
            rng = np.random.default_rng([rng_seed, hash(nama(k)) % (1 << 31)])
            cache[k] = AM.isi(metode, D, P, Yav[v], tmax, ti, tt, rng, add, soal['mode'] == 'akhir')
        out[v] = cache[k]
    dr = out['peny']
    if ident != 'I0' and len(ti):
        dr = _identitas(dr, out['peng'], soal, ident, np.random.default_rng([rng_seed, 7]))
    if ragam == 'titik':
        dr = np.repeat(np.median(dr, axis=1, keepdims=True), dr.shape[1], axis=1)
    elif ragam != 1.0:
        pos = dr > 0
        lg = np.log(np.where(pos, dr, 1.0))
        med = np.array([np.median(lg[j][pos[j]]) if pos[j].any() else 0.0 for j in range(len(dr))])[:, None]
        dr = np.where(pos, np.exp(med + math.sqrt(ragam) * (lg - med)), 0.0)
    return dr


def _identitas(peny, peng, soal, ident, rng):
    ti, tt, Yav = soal['ti'], soal['tt'], soal['Yav']
    ip = soal['ident']
    pv, nx = soal['pv'], soal['nx']
    peny, peng = peny.copy(), peng.copy()
    idx = {(i, t): j for j, (i, t) in enumerate(zip(ti, tt))}
    seen = set()
    for j, (i, t) in enumerate(zip(ti, tt)):
        p, q = pv[i, t], nx[i, t]
        if p < 0 or q < 0 or (i, p) in seen:
            continue
        seen.add((i, p))
        run = [idx.get((i, u)) for u in range(p + 1, q)]
        if any(r is None for r in run):
            continue
        sk, sa = Yav['sk'][i, p], Yav['sa'][i, q]
        if not (np.isfinite(sk) and np.isfinite(sa)):
            continue
        v = ip['v'] if ident == 'I2' else 0.0
        N = sa / (1 - v) - sk * (1 - v)
        r = N - (peng[run].sum(0) - peny[run].sum(0))
        if ident == 'I2':
            r = r + rng.standard_normal(r.shape) * ip['s'] * max(sk, sa)
            r = np.where(rng.random(r.shape) < ip['pe'], 0.0, r)
        vg, vy = peng[run].var(1) + 1e-9, peny[run].var(1) + 1e-9
        tot = vg.sum() + vy.sum()
        peng[run] = np.maximum(peng[run] + vg[:, None] * r[None, :] / tot, 0)
        peny[run] = np.maximum(peny[run] - vy[:, None] * r[None, :] / tot, 0)
    return peny


def _total(c, soal, dr):
    """Kuantil log total per sel untuk konfigurasi c."""
    ident, metode, batas, add, bobot, ragam, rekon = c
    Y, bs = D['Y']['peny'], D['besar']
    ti, tt = soal['ti'], soal['tt']
    terisi = bs[ti] | (soal['panjang'] <= batas)
    pos = {}
    for j, (i, t) in enumerate(zip(ti, tt)):
        pos.setdefault(t, []).append(j)
    hasil, tarik = [], {}
    for tk, cc, t, ang, sisa in soal['cells']:
        js = np.array([j for j in pos[t] if ang[ti[j]]])
        jb, jk = js[bs[ti[js]]], js[~bs[ti[js]] & terisi[js]]
        n_u = int((~bs[ti[js]] & ~terisi[js]).sum())
        N_k = int((ang & ~bs).sum())
        w = 1.0
        if bobot and n_u > 0 and N_k - n_u > 0:
            w = min(N_k / (N_k - n_u), bobot)
        tot = Y[sisa & bs, t].sum() + dr[jb].sum(0) + w * (Y[sisa & ~bs, t].sum() + dr[jk].sum(0))
        tarik[(tk, cc, t)] = np.maximum(tot, 1e-6)
    if rekon:
        for t in {k[2] for k in tarik}:
            if ('nas', 0, t) not in tarik:
                continue
            O = ~np.isnan(Y)
            yh, var = [np.median(tarik[('nas', 0, t)])], [tarik[('nas', 0, t)].var() + 1e-6]
            for w_ in range(3):
                if ('wil', w_, t) in tarik:
                    yh.append(np.median(tarik[('wil', w_, t)]))
                    var.append(tarik[('wil', w_, t)].var() + 1e-6)
                else:
                    yh.append(Y[(D['wil'] == w_) & O[:, t] & ~soal['M'][:, t], t].sum())
                    var.append(1e-6)
            Smat = np.vstack([np.ones(3), np.eye(3)])
            Wi = np.diag(1 / np.array(var))
            yt = Smat @ np.linalg.solve(Smat.T @ Wi @ Smat, Smat.T @ Wi @ np.array(yh))
            for k, node in enumerate([('nas', 0, t)] + [('wil', w_, t) for w_ in range(3)]):
                if node in tarik:
                    tarik[node] = np.maximum(tarik[node] + (yt[k] - yh[k]), 1e-6)
    for tk, cc, t, ang, sisa in soal['cells']:
        hasil.append(np.quantile(np.log(tarik[(tk, cc, t)]), KU))
    return hasil


def _soal(mode, M, tmax):
    Yav = {}
    for v in AM.VAR:
        y = D['Y'][v].copy()
        y[M] = np.nan
        y[:, tmax + 1:] = np.nan
        Yav[v] = y
    obs = ~np.isnan(Yav['peny'])
    pv, nx = AM.tetangga(obs)
    ti, tt = np.where(M)
    p, q = pv[ti, tt], nx[ti, tt]
    panjang = np.where((p >= 0) & (q >= 0), q - p - 1, np.where(p >= 0, tmax - p, np.where(q >= 0, q - tt, 99)))
    cells = _sel(M, tmax)
    tanpa_next = {}
    for j, (i, t) in enumerate(zip(ti, tt)):
        tanpa_next.setdefault(t, []).append((i, q[j] < 0))
    jenis = []
    for tk, c, t, ang, sisa in cells:
        f = [b for i, b in tanpa_next[t] if ang[i]]
        jenis.append('akhir' if np.mean(f) >= 0.5 else 'tengah')
    return dict(mode=mode, M=M, tmax=tmax, Yav=Yav, ti=ti, tt=tt, pv=pv, nx=nx, panjang=panjang, cells=cells,
                jenis=jenis, ident=AM.identitas_param(D, Yav))


def ulangan(arg):
    seed, blok, configs = arg
    a, z = AM.BLOK_IDX[blok]
    rng = np.random.default_rng(seed)
    soal2 = [_soal('tengah', AM.hapus_tengah(D, P, rng, a, z, z), z)]
    ts = int(rng.integers(max(a, 5), z + 1))
    soal2.append(_soal('akhir', AM.hapus_akhir(D, P, rng, ts), ts))
    semu = [AM.hapus_akhir(D, P, rng, s) for s in range(max(3, ts - 6), ts)]
    rows = []
    for soal in soal2:
        base = _dasar(soal['cells'], soal['M'])
        kolam = {k: [] for k in PEMBANDING}  # (tingkat, sel, bulan, galat)
        for (tk, c, t, benar, est) in base:
            for k in PEMBANDING:
                kolam[k].append((tk, c, t, est[k] - benar))
        if soal['mode'] == 'akhir':
            for s, Ms in zip(range(max(3, ts - 6), ts), semu):
                for (tk, c, t, benar, est) in _dasar(_sel(Ms, s), Ms):
                    for k in PEMBANDING:
                        kolam[k].append((tk, c, t, est[k] - benar))
        kunci = [(soal['mode'], soal['jenis'][j], tk, c, t, benar, int(soal['M'][ang, t].sum()))
                 for j, ((tk, c, t, ang, sisa), (_, _, _, benar, _)) in enumerate(zip(soal['cells'], base))]
        for k in PEMBANDING:
            for j, (tk, c, t, benar, est) in enumerate(base):
                e = [x[3] for x in kolam[k] if x[0] == tk and x[1] == c and t - 6 <= x[2] < t]
                if len(e) < 6:
                    e = [x[3] for x in kolam[k] if x[0] == tk and t - 6 <= x[2] < t]
                if len(e) < 6:
                    e = [x[3] for x in kolam[k] if x[0] == tk and x[2] < t]
                q = est[k] - np.quantile(e, 1 - KU) if len(e) >= 3 else np.full(NQ, est[k])
                rows.append((k, seed) + kunci[j] + tuple(np.sort(q)))
        cache = {}
        for c in configs:
            dr = _isi_cfg(c, soal, cache, seed * 2 + (soal['mode'] == 'akhir'))
            for j, q in enumerate(_total(c, soal, dr)):
                rows.append((nama(c), seed) + kunci[j] + tuple(q))
    return rows


KOL = ['cfg', 'rep', 'soal', 'jenis', 'tingkat', 'w', 't', 'benar', 'nhapus'] + QC


def jalankan(configs, blok, seeds, proses=4):
    args = [(s, blok, configs) for s in seeds]
    if proses > 1 and len(args) > 1:
        with Pool(proses) as pool:
            res = pool.map(ulangan, args, chunksize=1)
    else:
        res = [ulangan(a) for a in args]
    return pd.DataFrame([r for rr in res for r in rr], columns=KOL)


# ---------------------------------------------------------------- skor
def tambah_skor(df):
    q, y = df[QC].values, df.benar.values[:, None]
    d = y - q
    df = df.copy()
    df['crps'] = 2 * np.mean(np.maximum(KU * d, (KU - 1) * d), axis=1)
    df['galat'] = q[:, IMED] - y[:, 0]
    df['mae'] = np.abs(df.galat)
    lo, hi = PASANG[0.90]
    df['cakup90'] = ((q[:, lo] <= y[:, 0]) & (y[:, 0] <= q[:, hi])).astype(float)
    df['lebar90'] = q[:, hi] - q[:, lo]
    return df


def per_unit(df, kol):
    """Rata-rata antarulangan per satuan (jenis, tingkat, w, t): tiap ulangan berbobot 1/R."""
    return df.groupby(['cfg', 'jenis', 'tingkat', 'w', 't'], as_index=False)[kol].mean()


def peringkat(df, tingkat=UTAMA, kol='crps'):
    u = per_unit(df[df.tingkat == tingkat], kol)
    return u.groupby('cfg')[kol].mean().sort_values()


def selisih_bulan(df, a, b, tingkat=UTAMA, n=2000, seed=1):
    """Rentang 90% bootstrap per blok bulan dari selisih CRPS (a - b); negatif = a lebih baik."""
    u = per_unit(df[(df.tingkat == tingkat) & df.cfg.isin([a, b])], 'crps')
    pv = u.pivot_table(index=['jenis', 'w', 't'], columns='cfg', values='crps').dropna()
    if len(pv) == 0:
        return (np.nan, np.nan, np.nan)
    d = (pv[a] - pv[b]).groupby('t').agg(['sum', 'size'])
    rng = np.random.default_rng(seed)
    ix = rng.integers(0, len(d), (n, len(d)))
    bs = d['sum'].values[ix].sum(1) / d['size'].values[ix].sum(1)
    return (float((pv[a] - pv[b]).mean()), float(np.quantile(bs, 0.05)), float(np.quantile(bs, 0.95)))


def pilih(df, kandidat, sederhana, tingkat=UTAMA):
    """Peringkat CRPS; bila selisih dengan versi lebih sederhana tipis (rentang mencakup 0), pilih yang lebih sederhana."""
    pr = peringkat(df[df.cfg.isin(kandidat)], tingkat)
    terbaik = pr.index[0]
    pilihan = terbaik
    for k in sorted(kandidat, key=lambda x: sederhana[x]):
        if sederhana[k] >= sederhana[terbaik]:
            break
        m, lo, hi = selisih_bulan(df, k, terbaik, tingkat)
        if np.isfinite(lo) and lo <= 0:
            pilihan = k
            break
    return pilihan, pr


def saring(configs, blok, skala, catat, label):
    """Semua versi x R1 ulangan -> 10 teratas x R2 -> 5 teratas x R3; <= 5 pilihan langsung R3."""
    R1, R2, R3 = skala
    t0 = time.time()
    if len(configs) <= 5:
        df = jalankan(configs, blok, range(R3))
    else:
        df = jalankan(configs, blok, range(R1))
        top = [c for c in configs if nama(c) in set(peringkat(tambah_skor(df)).drop(PEMBANDING, errors='ignore').index[:10])]
        d2 = jalankan(top, blok, range(R1, R2))
        df = pd.concat([df, d2])
        ok = tambah_skor(df[df.rep >= R1])
        top5 = [c for c in top if nama(c) in set(peringkat(ok).drop(PEMBANDING, errors='ignore').index[:5])]
        df = pd.concat([df, jalankan(top5, blok, range(R2, R3))])
    df = tambah_skor(df)
    catat(f'[{label}] {len(configs)} versi, {df.rep.nunique()} ulangan, {time.time() - t0:.0f} detik')
    return df


def lengkap(df, kandidat):
    """Baris dari ulangan yang dimiliki semua kandidat (supaya berpasangan)."""
    reps = None
    for k in kandidat:
        r = set(df[df.cfg == k].rep.unique())
        reps = r if reps is None else reps & r
    return df[df.rep.isin(reps) & df.cfg.isin(list(kandidat) + PEMBANDING)]


# ---------------------------------------------------------------- penggabung (tahap 4)
def _susun(df, anggota):
    idx = ['rep', 'soal', 'jenis', 'tingkat', 'w', 't']
    base = df[df.cfg == anggota[0]].set_index(idx).sort_index()
    Qs = []
    for a in anggota:
        x = df[df.cfg == a].set_index(idx).sort_index()
        base = base[base.index.isin(x.index)]
    for a in anggota:
        x = df[df.cfg == a].set_index(idx).sort_index()
        Qs.append(x.loc[base.index, QC].values)
    return base.reset_index(), np.stack(Qs)


def _crps_q(q, y):
    d = y[:, None] - q
    return 2 * np.mean(np.maximum(KU * d, (KU - 1) * d), axis=1)


def _bobot_crps(Qs, y):
    from scipy.optimize import minimize
    m = Qs.shape[0]
    f = lambda z: _crps_q(np.tensordot(np.exp(z) / np.exp(z).sum(), Qs, 1), y).mean()
    z = minimize(f, np.zeros(m), method='Nelder-Mead', options=dict(maxiter=200, xatol=1e-3, fatol=1e-5)).x
    return np.exp(z) / np.exp(z).sum()


def _fitur_juri(base, Qs):
    med = Qs[:, :, IMED]
    lo, hi = PASANG[0.90]
    pusat = med.mean(0)
    X = np.column_stack([(med - pusat).T, (Qs[:, :, hi] - Qs[:, :, lo]).T, (base.jenis == 'akhir').astype(float),
                         base.tingkat.map({'prov': 0, 'wil': 1, 'nas': 2}).astype(float), base.nhapus.astype(float)])
    return X, pusat


def gabung(df, anggota, cara, latih=None):
    """Gabungkan anggota. latih=None: bobot/juri dipelajari out-of-fold per bulan; selain itu dari tabel latih."""
    base, Qs = _susun(df, anggota)
    y = base.benar.values
    if cara == 'rata':
        Q = Qs.mean(0)
    elif cara == 'pool':
        u = np.linspace(0.01, 0.99, 99)
        samp = np.concatenate([np.stack([np.interp(u, KU, q) for q in Qm]) for Qm in Qs], axis=1)
        Q = np.quantile(samp, KU, axis=1).T
    else:
        Q = np.zeros_like(Qs[0])
        if latih is not None:
            bl, Ql = _susun(latih, anggota)
            lipat = [(np.ones(len(bl), bool), np.ones(len(base), bool))]
        else:
            bl, Ql = base, Qs
            lipat = [((base.t != t).values, (base.t == t).values) for t in sorted(base.t.unique())]
        for tr, te in lipat:
            if cara == 'crps':
                sub = np.where(tr)[0]
                sub = sub[:: max(1, len(sub) // 4000)]
                w = _bobot_crps(Ql[:, sub], bl.benar.values[sub])
                Q[te] = np.tensordot(w, Qs[:, te], 1)
            else:
                from quantile_forest import RandomForestQuantileRegressor
                Xl, pl = _fitur_juri(bl, Ql)
                sub = np.where(tr)[0]
                sub = sub[:: max(1, len(sub) // 6000)]
                m = RandomForestQuantileRegressor(n_estimators=100, min_samples_leaf=10, random_state=0, n_jobs=4)
                m.fit(Xl[sub], bl.benar.values[sub] - pl[sub])
                Xe, pe = _fitur_juri(base[te], Qs[:, te])
                Q[te] = pe[:, None] + m.predict(Xe, quantiles=list(KU))
    out = base.copy()
    out[QC] = np.sort(Q, axis=1)
    out['cfg'] = 'G:' + cara
    return tambah_skor(out[KOL])


# ---------------------------------------------------------------- koreksi akhir (tahap 5, kalibrasi, U1)
def _bobot_unit(df):
    return 1.0 / df.groupby(['jenis', 'tingkat', 'w', 't']).rep.transform('size')


def _kuantil_bobot(x, w, p):
    o = np.argsort(x)
    c = np.cumsum(w[o]) / w.sum()
    return x[o][min(np.searchsorted(c, p), len(x) - 1)]


def param_koreksi(cal, bias=True):
    """Bias (median galat) dan pelebar Q per (tingkat, jenis) di 4 tingkat rentang; n = jumlah sel-bulan."""
    out = {}
    cal = cal.copy()
    cal['bw'] = _bobot_unit(cal)
    kel = [(tk, jn) for tk in TINGKAT for jn in ('tengah', 'akhir')]
    for tk, jn in kel:
        g = cal[(cal.tingkat == tk) & (cal.jenis == jn)]
        n = g.groupby(['w', 't']).ngroups
        if n < 20:
            g = cal[cal.tingkat == tk]
            n = g.groupby(['jenis', 'w', 't']).ngroups
        if n < 20:
            g, n = cal, cal.groupby(['jenis', 'tingkat', 'w', 't']).ngroups
        b = _kuantil_bobot(g.galat.values, g.bw.values, 0.5) if bias else 0.0
        q, y = g[QC].values - b, g.benar.values
        Q = {}
        for lv, (lo, hi) in PASANG.items():
            s = np.maximum(q[:, lo] - y, y - q[:, hi])
            Q[lv] = _kuantil_bobot(s, g.bw.values, min(math.ceil((n + 1) * lv) / n, 1.0))
        out[(tk, jn)] = dict(b=float(b), Q=Q, n=int(n))
    return out


def terapkan_koreksi(df, par, halus=False, label='K'):
    out = df.copy()
    q = out[QC].values.copy()
    for (tk, jn), p in par.items():
        m = ((out.tingkat == tk) & (out.jenis == jn)).values
        if not m.any():
            continue
        q[m] -= p['b']
        for lv, (lo, hi) in PASANG.items():
            q[m, lo] -= p['Q'][lv]
            q[m, hi] += p['Q'][lv]
    if halus:
        out[QC] = q
        out = out.sort_values(['rep', 'soal', 'tingkat', 'w', 't'])
        q = out[QC].values.copy()
        g = out.groupby(['rep', 'soal', 'tingkat', 'w']).ngroup().values
        for lv, (lo, hi) in PASANG.items():
            wd, c = q[:, hi] - q[:, lo], (q[:, hi] + q[:, lo]) / 2
            sm = wd.copy()
            for j in range(len(wd)):
                tet = [wd[k] for k in (j - 1, j, j + 1) if 0 <= k < len(wd) and g[k] == g[j]]
                sm[j] = np.mean(tet)
            q[:, lo], q[:, hi] = c - sm / 2, c + sm / 2
    # jaga urutan kuantil: sisi bawah tidak naik melewati median, sisi atas tidak turun
    q[:, :IMED + 1] = np.minimum.accumulate(q[:, :IMED + 1][:, ::-1], axis=1)[:, ::-1]
    q[:, IMED:] = np.maximum.accumulate(q[:, IMED:], axis=1)
    out[QC] = q
    out['cfg'] = label
    return tambah_skor(out[KOL])


# ---------------------------------------------------------------- gerbang
def wilson(p, n, z=1.645):
    if n <= 0:
        return (0.0, 1.0)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def gerbang(df, versi, pstar, tingkat):
    x, p = df[(df.cfg == versi) & (df.tingkat == tingkat)], df[(df.cfg == pstar) & (df.tingkat == tingkat)]
    if len(x) == 0 or len(p) == 0:
        return dict(tingkat=tingkat, status='tidak ada sel')
    ux, up = per_unit(x, ['crps', 'mae', 'galat', 'cakup90']), per_unit(p, ['crps', 'mae', 'galat', 'cakup90'])
    cx, cp = ux.crps.mean(), up.crps.mean()
    m, lo, hi = selisih_bulan(df, versi, pstar, tingkat)
    cov, n = ux.cakup90.mean(), len(ux)
    seri = ux.pivot_table(index='t', columns=['jenis', 'w'], values='cakup90')
    rs = [seri[c].dropna().autocorr(1) for c in seri if seri[c].notna().sum() >= 4]
    rho = float(np.clip(np.nanmean(rs), 0, 0.9)) if len(rs) and np.isfinite(np.nanmean(rs)) else 0.0
    neff = n * (1 - rho) / (1 + rho)
    wl, wh = wilson(cov, neff)
    bias_x, bias_p = math.exp(ux.galat.mean()) - 1, math.exp(up.galat.mean()) - 1
    g = dict(tingkat=tingkat, sel_bulan=n, crps=cx, crps_pembanding=cp, perbaikan=1 - cx / cp, mae=ux.mae.mean(),
             mae_pembanding=up.mae.mean(), selisih_lo=lo, selisih_hi=hi, cakupan=cov, n_efektif=neff, wilson_lo=wl,
             wilson_hi=wh, bias=bias_x, bias_pembanding=bias_p)
    g['L_lebih_baik'] = bool(g['perbaikan'] >= 0.10 and g['mae'] <= g['mae_pembanding'])
    g['L_konsisten'] = bool(np.isfinite(hi) and hi < 0)
    g['L_cakupan'] = bool(wl <= 0.90 <= wh and cov >= 0.80)
    g['cakupan_belum_bisa'] = bool((wh - wl) / 2 > 0.10)
    g['L_bias'] = bool(abs(bias_x) <= 0.03 and abs(bias_x) <= abs(bias_p) + 1e-12)
    return g


def arah(df, versi, tingkat):
    """Porsi bulan dengan arah perubahan (median taksiran) sama dengan jawaban benar; soal lubang tengah."""
    Y, O = D['Y']['peny'], ~np.isnan(D['Y']['peny'])
    ids = {'prov': D['prov'], 'wil': D['wil'], 'nas': np.zeros(D['n'], int)}[tingkat]
    x = df[(df.cfg == versi) & (df.tingkat == tingkat) & (df.soal == 'tengah')]
    benar, total = 0, 0
    for (rep, w), g in x.groupby(['rep', 'w']):
        tr = np.array([np.log(max(Y[(ids == w) & O[:, t], t].sum(), 1e-6)) for t in range(D['T'])])
        es = tr.copy()
        es[g.t.values] = g[QC[IMED]].values
        for t in g.t.values:
            for u in (t, t + 1):
                if 1 <= u < D['T'] and tr[u] != tr[u - 1]:
                    total += 1
                    benar += np.sign(es[u] - es[u - 1]) == np.sign(tr[u] - tr[u - 1])
    return benar / total if total else np.nan


# ---------------------------------------------------------------- alur
M_URUT = ['B', 'C', 'R1', 'R2', 'R3', 'R4', 'R7', 'R5', 'R6a', 'R6b', 'R6c']
KELUARGA = {'B': 'regresi', 'C': 'regresi', 'R1': 'regresi', 'R2': 'regresi', 'R3': 'regresi', 'R4': 'regresi',
            'R7': 'survei', 'R5': 'pohon', 'R6a': 'pohon', 'R6b': 'pohon', 'R6c': 'pohon'}
TAMBAHAN = ['kalender', 'ragamkel', 'tdist', 'pola', 'ciri', 'luar']


def penyetelan(out, skala, catat, metode=M_URUT):
    blok = 'penyetelan'
    simpan = lambda df, nm: df.drop(columns=QC).to_csv(os.path.join(out, nm + '.csv'), index=False)
    resep = {}
    # 1a identitas (metode baku R2, semua lubang diisi)
    K = [cfg(ident=i) for i in ('I0', 'I1', 'I2')]
    df = saring(K, blok, skala, catat, '1a identitas')
    p, pr = pilih(lengkap(df, [nama(k) for k in K]), [nama(k) for k in K], {nama(k): j for j, k in enumerate(K)})
    ident = p.split('|')[0]
    catat(pr.round(4).to_string()); catat(f'-> identitas: {ident}')
    simpan(df, 'tahap1a')
    pstar = peringkat(df[df.cfg.isin(PEMBANDING)]).index[0]
    catat(f'-> pembanding P* = {pstar}')
    # 1b isian x batas lubang
    K = [cfg(ident=ident, metode=m, batas=b) for m in metode for b in (2, 3, 6, 99)]
    sd = {nama(k): M_URUT.index(k[1]) * 10 + {99: 0, 6: 1, 3: 2, 2: 3}[k[2]] for k in K}
    df1b = saring(K, blok, skala, catat, '1b isian')
    pr_all = peringkat(df1b[df1b.rep < skala[0]])
    catat(pr_all.round(4).to_string())
    penuh = [k for k in sd if df1b[df1b.cfg == k].rep.nunique() == df1b.rep.nunique()]
    p, pr = pilih(lengkap(df1b, penuh), penuh, sd)
    win = next(k for k in K if nama(k) == p)
    catat(f'-> isian: {p}')
    simpan(df1b, 'tahap1b')
    juara = {}
    for k in pr_all.index:
        if k in sd:
            juara.setdefault(KELUARGA[k.split('|')[1]], k)
    # 1c tambahan
    dasar = dict(ident=ident, metode=win[1], batas=win[2])
    K = [cfg(**dasar)] + [cfg(add=(a,), **dasar) for a in TAMBAHAN]
    df = saring(K, blok, (skala[0], skala[0], skala[0]) if len(K) > 5 else skala, catat, '1c tambahan (satu per satu)')
    pr = peringkat(df).drop(PEMBANDING, errors='ignore')
    baik = [k.split('|')[3] for k in pr.index if pr[k] < pr[nama(K[0])] and k != nama(K[0])]
    K2 = K + ([cfg(add=tuple(baik), **dasar)] if len(baik) >= 2 else [])
    df = saring(K2, blok, skala, catat, '1c tambahan')
    sd = {nama(k): (0 if not k[3] else 1 if len(k[3]) == 1 else 2) for k in K2}
    penuh = [k for k in sd if df[df.cfg == k].rep.nunique() == df.rep.nunique()]
    p, pr = pilih(lengkap(df, penuh), penuh, sd)
    add = next(k for k in K2 if nama(k) == p)[3]
    catat(peringkat(df).round(4).to_string()); catat(f'-> tambahan: {add or "tanpa"}')
    simpan(df, 'tahap1c')
    dasar['add'] = add
    # 2 bobot x ragam
    K = [cfg(bobot=b, ragam=r, **dasar) for b in (None, 3, 5) for r in ('titik', 0.5, 1.0, 2.0)]
    sd = {nama(k): {None: 0, 3: 1, 5: 2}[k[4]] * 10 + {1.0: 0, 'titik': 1, 0.5: 2, 2.0: 2}[k[5]] for k in K}
    df = saring(K, blok, skala, catat, '2 bobot x ragam')
    penuh = [k for k in sd if df[df.cfg == k].rep.nunique() == df.rep.nunique()]
    p, pr = pilih(lengkap(df, penuh), penuh, sd)
    w2 = next(k for k in K if nama(k) == p)
    catat(peringkat(df[df.rep < skala[0]]).round(4).to_string()); catat(f'-> bobot {w2[4]}, ragam {w2[5]}')
    simpan(df, 'tahap2')
    dasar.update(bobot=w2[4], ragam=w2[5])
    # 3 rekonsiliasi
    K = [cfg(rekon=r, **dasar) for r in (0, 1)]
    df = saring(K, blok, skala, catat, '3 rekonsiliasi')
    p, pr = pilih(df, [nama(k) for k in K], {nama(k): k[6] for k in K}, tingkat='nas')
    rekon = next(k for k in K if nama(k) == p)[6]
    catat(peringkat(df, 'nas').round(4).to_string()); catat(f'-> rekonsiliasi: {"dengan" if rekon else "tanpa"}')
    simpan(df, 'tahap3')
    dasar['rekon'] = rekon
    tunggal = cfg(**dasar)
    # 4 penggabung: juara tiap keluarga dengan pengaturan pemenang
    angg = [tunggal]
    for fam, k in juara.items():
        kk = next(c for c in [cfg(ident=ident, metode=m, batas=b) for m in M_URUT for b in (2, 3, 6, 99)] if nama(c) == k)
        c2 = cfg(ident=ident, metode=kk[1], batas=kk[2], add=add, bobot=dasar['bobot'], ragam=dasar['ragam'], rekon=rekon)
        if KELUARGA[kk[1]] != KELUARGA[tunggal[1]] and c2 not in angg:
            angg.append(c2)
    df = jalankan(angg, blok, range(skala[2]))
    df = tambah_skor(df)
    an = [nama(a) for a in angg]
    tabel = [df]
    if len(an) >= 2:
        for cara in ('rata', 'pool', 'crps', 'juri'):
            tabel.append(gabung(df, an, cara))
    df4 = pd.concat(tabel)
    kand = [nama(tunggal)] + [f'G:{c}' for c in ('rata', 'pool', 'crps', 'juri') if len(an) >= 2]
    sd = {k: j for j, k in enumerate(kand)}
    p, pr = pilih(lengkap(df4, kand) if len(kand) > 1 else df4, kand, sd)
    catat(f'anggota: {an}'); catat(peringkat(df4).round(4).to_string()); catat(f'-> penggabung: {p}')
    simpan(df4, 'tahap4')
    # 5 koreksi akhir (konformal mini: setel Jan-Des 2024, nilai Jan-Jun 2025)
    x = df4[df4.cfg == p]
    cal, ev = x[x.t <= 11], x[x.t >= 12]
    opsi = {'tanpa': ev.assign(cfg='tanpa')}
    opsi['konformal'] = terapkan_koreksi(ev, param_koreksi(cal, bias=False), label='konformal')
    opsi['konformal+bias'] = terapkan_koreksi(ev, param_koreksi(cal, bias=True), label='konformal+bias')
    opsi['konformal+bias+halus'] = terapkan_koreksi(ev, param_koreksi(cal, bias=True), halus=True, label='konformal+bias+halus')
    df5 = pd.concat(list(opsi.values()) + [df4[df4.cfg.isin(PEMBANDING) & (df4.t >= 12)]])
    kand5 = list(opsi)
    p5, pr = pilih(df5, kand5, {k: j for j, k in enumerate(kand5)})
    cov = per_unit(df5[df5.tingkat == UTAMA], 'cakup90').groupby('cfg').cakup90.mean()
    catat(pd.concat([peringkat(df5).rename('crps'), cov], axis=1).round(4).to_string()); catat(f'-> koreksi: {p5}')
    simpan(df5, 'tahap5')
    resep = dict(ident=ident, metode=tunggal[1], batas=tunggal[2], add=list(add), bobot=dasar['bobot'], ragam=dasar['ragam'],
                 rekon=rekon, anggota=[list(a) for a in angg], penggabung=p, koreksi=p5, pstar=pstar,
                 skala=list(skala), dibuat=time.strftime('%Y-%m-%d %H:%M:%S'))
    json.dump(resep, open(os.path.join(out, 'resep.json'), 'w'), indent=1, default=str)
    # gerbang di blok penyetelan (resep akhir; bila ada koreksi, dinilai di Jan-Jun 2025)
    akhir = df5 if p5 != 'tanpa' else df4.assign(cfg=df4.cfg.replace({p: 'tanpa'}))
    G = [dict(gerbang(akhir, p5, pstar, tk), arah=arah(akhir, p5, tk)) for tk in TINGKAT]
    pd.DataFrame(G).to_csv(os.path.join(out, 'gerbang_penyetelan.csv'), index=False)
    catat(pd.DataFrame(G).T.to_string())
    df4.to_pickle(os.path.join(out, 'tahap4_penuh.pkl'))
    return resep


def jalankan_resep(resep, blok, n, latih):
    """Jalankan resep terkunci di sebuah blok: anggota -> penggabung (bobot/juri dari tabel latih penyetelan)."""
    angg = [tuple(tuple(x) if isinstance(x, list) else x for x in a) for a in resep['anggota']]
    df = tambah_skor(jalankan(angg, blok, range(n)))
    p = resep['penggabung']
    if p.startswith('G:'):
        g = gabung(df, [nama(a) for a in angg], p[2:], latih=latih if p[2:] in ('crps', 'juri') else None)
        df = pd.concat([df, g])
    return df, p


def main():
    global D, P
    mode, xlsm, out = sys.argv[1], sys.argv[2], sys.argv[3]
    bps = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(out, exist_ok=True)
    pk = os.path.join(out, 'data_beras.pkl')
    if os.path.exists(pk):
        D = pd.read_pickle(pk)
    else:
        D = AM.muat(xlsm, 'BERAS', bps)
        pd.to_pickle(D, pk)
    P = AM.profil_hapus(D)
    log = open(os.path.join(out, f'log_{mode}.txt'), 'a')

    def catat(s):
        print(s, flush=True)
        log.write(str(s) + '\n'); log.flush()
    catat(f'== {mode} {time.strftime("%Y-%m-%d %H:%M:%S")} | perusahaan {D["n"]}, besar {int(D["besar"].sum())}, '
          f'wilayah {np.bincount(D["wil"]).tolist()} | pola hapus: h={P["h"].round(3)}, p_ekor={P["p_ekor"].round(3)}')
    if mode == 'coba':
        penyetelan(out, (4, 6, 8), catat)
    elif mode == 'penyetelan':
        penyetelan(out, (50, 200, 500), catat)
    elif mode in ('kalibrasi', 'ujian'):
        resep = json.load(open(os.path.join(out, 'resep.json')))
        latih = pd.read_pickle(os.path.join(out, 'tahap4_penuh.pkl'))
        if mode == 'kalibrasi':
            df, p = jalankan_resep(resep, 'kalibrasi', 500, latih)
            par = param_koreksi(df[df.cfg == p], bias='bias' in resep['koreksi'])
            pd.to_pickle(dict(par=par, tabel=df[df.cfg == p]), os.path.join(out, 'kalibrasi.pkl'))
            catat(pd.DataFrame({f'{k[0]}/{k[1]}': dict(bias=v['b'], n=v['n'], **{f'Q{int(a * 100)}': b for a, b in v['Q'].items()})
                                for k, v in par.items()}).T.round(4).to_string())
        else:
            kunci = os.path.join(out, 'U1_SUDAH_JALAN.json')
            if os.path.exists(kunci):
                sys.exit('U1 sudah pernah dijalankan; ujian akhir hanya sekali jalan.')
            json.dump(dict(mulai=time.strftime('%Y-%m-%d %H:%M:%S'), resep=resep), open(kunci, 'w'), default=str)
            df, p = jalankan_resep(resep, 'ujian', 500, latih)
            kal = pd.read_pickle(os.path.join(out, 'kalibrasi.pkl'))
            x = df[df.cfg == p]
            if resep['koreksi'] == 'tanpa':
                akhir = x.assign(cfg='resep')
            else:  # Q dan bias diperbarui bergulir tiap bulan: kolam = kalibrasi + bulan ujian yang sudah dinilai
                bagian, kolam = [], kal['tabel']
                for t in sorted(x.t.unique()):
                    par = param_koreksi(kolam, bias='bias' in resep['koreksi'])
                    bagian.append(terapkan_koreksi(x[x.t == t], par, halus='halus' in resep['koreksi'], label='resep'))
                    kolam = pd.concat([kolam, x[x.t == t]])
                akhir = pd.concat(bagian)
            semua = pd.concat([akhir, df[df.cfg.isin(PEMBANDING)]])
            G = [dict(gerbang(semua, 'resep', resep['pstar'], tk), arah=arah(semua, 'resep', tk)) for tk in TINGKAT]
            pd.DataFrame(G).to_csv(os.path.join(out, 'gerbang_U1.csv'), index=False)
            semua.drop(columns=QC).to_csv(os.path.join(out, 'U1_sel.csv'), index=False)
            catat(pd.DataFrame(G).T.to_string())
    log.close()


if __name__ == '__main__':
    main()
