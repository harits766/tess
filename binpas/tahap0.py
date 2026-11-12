"""Tahap 0: profil data INATRADE (tanpa menilai metode apa pun).

Pakai:
  python -I binpas/tahap0.py <Non_PAW_dari_nol.xlsm> <folder keluaran> [folder keluaran beras_stok/ambil_bps.py]

Isi (RANCANGAN_INATRADE.md bagian 4 dan 7.1):
  1. Laporan per perusahaan x komoditas x subkomoditas x bulan; koreksi kg->ton (>= 100x median sendiri).
     Bila satu kunci memuat beberapa kepala laporan berbeda, tiap kepala dihitung sebagai sub-laporan dan dijumlah.
  2. Populasi dan profil kehadiran: aktif (bulan pertama..terakhir lapor; varian +3 bulan), melapor, panjang lubang.
  3. Sel hampir lengkap (>= 90% / 85% pelapor aktif melapor, aktif >= 3) per tingkat dan blok waktu.
  4. Identitas stok: Stok Awal[t] vs Stok Akhir[t-1]; Stok Akhir vs Stok Awal + Pengadaan - Penyaluran.
  5. Konsentrasi per komoditas x pulau: pangsa terbesar, pangsa 5 terbesar, Herfindahl.
  6. Cakupan volume beras terhadap BPS (bila folder BPS diberikan).
  7. Harga Jual: sebaran dan kewajaran satuan per komoditas x subkomoditas.
Keluaran berisi data per perusahaan (laporan.csv, perusahaan.csv): internal, tidak disimpan di repo.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'beras_stok'))
from util import U, a0, normprov, periode  # noqa: E402

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
PULAU_DARI = {p: k for k, v in PULAU.items() for p in v}
PER = [str(p) for p in pd.period_range('2024-01', '2026-09', freq='M')]
BLOK = {'penyetelan': ('2024-01', '2025-06'), 'kalibrasi': ('2025-07', '2025-12'), 'ujian': ('2026-01', '2026-09')}
Q = ['Pengadaan', 'Penyaluran', 'Stok Awal', 'Stok Akhir']
KODE_BULOG = '00372'
AMBANG_KG = 100
MIN_AKTIF = 3
TENGGANG = 3  # bulan; varian definisi aktif sesudah laporan terakhir
RENDEMEN = 0.5762  # GKG -> beras (sama dengan model stok beras)


def blok_dari(p):
    for b, (a, z) in BLOK.items():
        if a <= p <= z:
            return b


def baca(path):
    S = pd.read_excel(path, sheet_name='2024-2026', dtype=object)
    S['kode'] = S['Nama Perusahaan'].astype(str).str.strip().str.zfill(5)
    S['kom'] = S['Jenis Komoditi'].map(U)
    S['sub'] = S['Sub Komoditi'].astype(str).str.strip()
    S['per'] = [periode(b, t) for b, t in zip(S['Bulan'], S['Tahun'])]
    S['prov'] = S['Provinsi Perusahaan'].map(normprov)
    S['tuj'] = S['Provinsi Penyaluran'].map(normprov)
    S['satuan'] = S['Satuan'].map(U)
    for c in Q + ['Rincian Pengadaan', 'Rincian Penyaluran', 'Harga Jual']:
        S[c] = S[c].map(a0)
    return S[S.per.isin(PER)].reset_index(drop=True)


def laporan(S):
    """Satu baris per perusahaan x komoditas x subkomoditas x bulan (setelah koreksi satuan)."""
    kunci = ['kode', 'kom', 'sub', 'per']
    K = S.drop_duplicates(kunci + Q)[kunci + Q + ['prov', 'satuan']].copy()  # sub-laporan = kepala laporan berbeda
    K['n_kepala'] = K.groupby(kunci).per.transform('size')
    basis = {}
    for k, g in K.groupby(['kode', 'kom', 'sub']):
        v = g[Q].replace(0, np.nan).stack()
        basis[k] = v.median() if len(v) else np.nan
    K['basis'] = [basis[k] for k in zip(K.kode, K.kom, K['sub'])]
    K['faktor'] = np.where((K.basis > 0) & (K[Q].max(axis=1) / K.basis >= AMBANG_KG), 1 / 1000, 1.0)
    for c in Q:
        K[c] = K[c] * K.faktor
    L = K.groupby(kunci, as_index=False).agg(
        prov=('prov', 'first'), satuan=('satuan', 'first'), peng=('Pengadaan', 'sum'), peny=('Penyaluran', 'sum'),
        sa=('Stok Awal', 'sum'), sk=('Stok Akhir', 'sum'), peny_maks=('Penyaluran', 'max'),
        n_kepala=('n_kepala', 'first'), dikoreksi=('faktor', lambda x: int((x < 1).any())))
    L['pulau'] = L.prov.map(PULAU_DARI)
    L['bulog'] = L.kode == KODE_BULOG
    return L


def kehadiran(L):
    """Matriks pelapor (perusahaan x komoditas) x bulan."""
    F = L.groupby(['kom', 'kode']).agg(prov=('prov', 'first'), pulau=('pulau', 'first'), awal=('per', 'min'),
                                       akhir=('per', 'max'), n_lapor=('per', 'nunique')).reset_index()
    ix = {p: i for i, p in enumerate(PER)}
    T = len(PER)
    M = np.zeros((len(F), T), bool)
    pos = {(k, c): i for i, (k, c) in enumerate(zip(F.kom, F.kode))}
    for k, c, p in zip(L.kom, L.kode, L.per):
        M[pos[(k, c)], ix[p]] = True
    a, z = F.awal.map(ix).values, F.akhir.map(ix).values
    t = np.arange(T)[None, :]
    A0 = (t >= a[:, None]) & (t <= z[:, None])
    A3 = (t >= a[:, None]) & (t <= np.minimum(z + TENGGANG, T - 1)[:, None])
    F['n_aktif'] = A0.sum(1)
    F['hadir'] = F.n_lapor / F.n_aktif
    F['bulan_sejak_lapor_terakhir'] = T - 1 - z
    return F, M, A0, A3


def sel(F, M, A0, A3):
    rows = []
    for tingkat, kol in [('provinsi', F.prov), ('pulau', F.pulau), ('nasional', pd.Series('INDONESIA', index=F.index))]:
        for (kom, w), idx in F.groupby([F.kom, kol]).indices.items():
            for j, p in enumerate(PER):
                rows.append((kom, tingkat, w, p, int(M[idx, j].sum()), int(A0[idx, j].sum()), int(A3[idx, j].sum())))
    C = pd.DataFrame(rows, columns=['kom', 'tingkat', 'wilayah', 'per', 'lapor', 'aktif0', 'aktif3'])
    C['blok'] = C.per.map(blok_dari)
    return C


def ringkas_sel(C):
    out = []
    for (kom, tk, bl), g in C.groupby(['kom', 'tingkat', 'blok']):
        r = dict(kom=kom, tingkat=tk, blok=bl)
        for d in ['aktif0', 'aktif3']:
            e = g[g[d] >= MIN_AKTIF]
            r[f'sel_{d}'] = len(e)
            r[f'hl90_{d}'] = int((e.lapor / e[d] >= 0.90).sum())
            r[f'hl85_{d}'] = int((e.lapor / e[d] >= 0.85).sum())
        out.append(r)
    return pd.DataFrame(out)


def lubang(F, M, A0):
    rows = []
    for i in range(len(F)):
        run = 0
        for j in np.where(A0[i])[0]:
            if not M[i, j]:
                run += 1
            elif run:
                rows.append((F.kom[i], run))
                run = 0
    G = pd.DataFrame(rows, columns=['kom', 'panjang'])
    G['kelas'] = pd.cut(G.panjang, [0, 1, 2, 3, 6, 99], labels=['1', '2', '3', '4-6', '7+'])
    return G


def identitas(L):
    X = L[L.n_kepala == 1].sort_values(['kode', 'kom', 'sub', 'per']).copy()
    X['t'] = X.per.map({p: i for i, p in enumerate(PER)})
    g = X.groupby(['kode', 'kom', 'sub'])
    X['sk_lalu'] = g.sk.shift(1)
    X['berurutan'] = g.t.diff() == 1
    A = X[X.berurutan & ((X.sk_lalu > 0) | (X.sa > 0))].copy()
    A['rel'] = (A.sa - A.sk_lalu) / np.maximum(A.sa.abs(), A.sk_lalu.abs())
    X['sisa'] = X.sk - (X.sa + X.peng - X.peny)
    X['rel_dalam'] = X.sisa / np.maximum.reduce([X.sk.abs(), X.sa.abs(), X.peng.abs(), X.peny.abs(), np.full(len(X), 1e-9)])
    rows = []
    for kom in sorted(X.kom.unique()):
        a, x = A[A.kom == kom], X[X.kom == kom]
        if not len(a):
            continue
        r = a.rel.abs()
        rows.append(dict(
            kom=kom, pasangan=len(a), tepat=(r <= 0.001).mean(), wajar=((r > 0.001) & (r <= 0.05)).mean(),
            sedang=((r > 0.05) & (r <= 0.25)).mean(), ekstrem=(r > 0.25).mean(),
            awal_lebih_kecil=(a.rel < -0.001).mean(), awal_lebih_besar=(a.rel > 0.001).mean(),
            median_rel_tak_tepat=a.rel[r > 0.001].median() if (r > 0.001).any() else 0.0,
            dalam_bulan_tepat=(x.rel_dalam.abs() <= 0.001).mean(), dalam_bulan_ekstrem=(x.rel_dalam.abs() > 0.25).mean()))
    return pd.DataFrame(rows)


def konsentrasi(L):
    rows = []
    for nama, (a, z) in {'penyetelan': BLOK['penyetelan'], 'semua': (PER[0], PER[-1])}.items():
        X = L[(L.per >= a) & (L.per <= z)]
        for tingkat, kol in [('pulau', 'pulau'), ('nasional', None)]:
            keys = ['kom'] + ([kol] if kol else [])
            for k, g in X.groupby(keys):
                v = g.groupby('kode').peny.sum().sort_values(ascending=False)
                tot = v.sum()
                if tot <= 0:
                    continue
                s = v / tot
                k = k if isinstance(k, tuple) else (k,)
                rows.append(dict(periode=nama, kom=k[0], tingkat=tingkat, wilayah=k[1] if kol else 'INDONESIA',
                                 perusahaan=len(v), pangsa_1=s.iloc[0], pangsa_5=s.iloc[:5].sum(),
                                 herfindahl=(s ** 2).sum(), n_untuk_80=int((s.cumsum() < 0.8).sum() + 1)))
    return pd.DataFrame(rows)


def cakupan_beras(L, bps, here):
    B = L[L.kom == 'BERAS'].copy()
    B['tahun'] = B.per.str[:4].astype(int)
    kons = pd.read_csv(os.path.join(bps, 'konsumsi_provinsi.csv'))
    kons = kons[kons.tahun == kons.tahun.max()].set_index('prov').konsumsi_rt_ton_bulan  # tahun Susenas terakhir
    kons_pulau = kons.groupby(PULAU_DARI).sum()
    pt = pd.read_csv(os.path.join(bps, 'produksi_tahunan.csv'))
    pb = pd.read_csv(os.path.join(bps, 'produksi_bulanan_ksa.csv'))
    pb = pb[pb.periode.isin(PER)]
    prod = {int(y): v * RENDEMEN for y, v in pt.groupby('tahun').padi_gkg_ton.sum().items()}
    for y, g in pb.groupby(pb.periode.str[:4].astype(int)):
        prod[y] = g.padi_gkg_ton.sum() * RENDEMEN
    J = pd.read_csv(os.path.join(here, '..', 'beras_stok', 'jangkar_publik.csv'))
    imp = {int(r.periode): r.nilai_juta_ton * 1e6 for r in J[J.jenis == 'impor'].itertuples() if str(r.periode).isdigit()}
    nb = {y: B[B.tahun == y].per.nunique() for y in sorted(B.tahun.unique())}
    rows = []
    for y in sorted(B.tahun.unique()):
        g = B[B.tahun == y]
        for nama, x in [('pedagang (tanpa BULOG)', g[~g.bulog]), ('BULOG', g[g.bulog])]:
            pasok = prod.get(y, np.nan) + imp.get(y, 0.0) * nb[y] / 12
            rows.append(dict(tahun=y, bulan=nb[y], kelompok=nama, wilayah='INDONESIA', pelapor=x.kode.nunique(),
                             pengadaan_ton=x.peng.sum(), penyaluran_ton=x.peny.sum(),
                             pengadaan_per_pasokan=x.peng.sum() / pasok,
                             penyaluran_per_konsumsi_rt=x.peny.sum() / (kons.sum() * nb[y])))
        for pl, x in g[~g.bulog].groupby('pulau'):
            rows.append(dict(tahun=y, bulan=nb[y], kelompok='pedagang (tanpa BULOG)', wilayah=pl,
                             pelapor=x.kode.nunique(), pengadaan_ton=x.peng.sum(), penyaluran_ton=x.peny.sum(),
                             pengadaan_per_pasokan=np.nan,
                             penyaluran_per_konsumsi_rt=x.peny.sum() / (kons_pulau[pl] * nb[y])))
    return pd.DataFrame(rows)


def harga(S):
    H = S[S['Harga Jual'] > 0].drop_duplicates(['kode', 'kom', 'sub', 'per', 'Harga Jual'])
    rows = []
    for (kom, sub), g in H.groupby(['kom', 'sub']):
        h = g['Harga Jual']
        med = h.median()
        rows.append(dict(kom=kom, sub=sub, n=len(h), perusahaan=g.kode.nunique(), p05=h.quantile(.05), p25=h.quantile(.25),
                         median=med, p75=h.quantile(.75), p95=h.quantile(.95),
                         dalam_setengah_dua_kali=((h >= med / 2) & (h <= med * 2)).mean(),
                         kurang_dari_seperseratus=(h < med / 100).mean(), lebih_dari_seratus_kali=(h > med * 100).mean()))
    tanpa = S.groupby(['kode', 'kom', 'sub', 'per'])['Harga Jual'].max().eq(0).groupby('kom').mean()
    R = pd.DataFrame(rows)
    R['laporan_tanpa_harga'] = R.kom.map(tanpa)
    return R


def main(path, out, bps=None):
    os.makedirs(out, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    pd.set_option('display.width', 250, 'display.max_columns', 30, 'display.float_format', '{:.3f}'.format)
    S = baca(path)
    L = laporan(S)
    F, M, A0, A3 = kehadiran(L)
    C = sel(F, M, A0, A3)
    R = ringkas_sel(C)
    G = lubang(F, M, A0)
    I = identitas(L)
    K = konsentrasi(L)
    H = harga(S)
    L.to_csv(os.path.join(out, 'laporan.csv'), index=False)
    F.to_csv(os.path.join(out, 'perusahaan.csv'), index=False)
    C.to_csv(os.path.join(out, 'kehadiran_sel.csv'), index=False)
    R.to_csv(os.path.join(out, 'sel_hampir_lengkap.csv'), index=False)
    I.to_csv(os.path.join(out, 'identitas.csv'), index=False)
    K.to_csv(os.path.join(out, 'konsentrasi.csv'), index=False)
    H.to_csv(os.path.join(out, 'harga_jual.csv'), index=False)

    print(f'== DATA: {len(S)} baris, {len(L)} laporan, {S.kode.nunique()} kode perusahaan, {L.kom.nunique()} komoditas')
    print(f'   laporan dengan > 1 kepala (dijumlah): {int((L.n_kepala > 1).sum())}; '
          f'penyaluran total jumlah vs maks: {L.peny.sum() / L.peny_maks.sum():.3f}x')
    U_ = L.groupby('kom').agg(pelapor=('kode', 'nunique'), laporan=('per', 'size'), dikoreksi=('dikoreksi', 'sum'),
                              satuan=('satuan', lambda x: '/'.join(sorted(set(x)))), kepala_ganda=('n_kepala', lambda x: int((x > 1).sum())))
    th = L.assign(th=L.per.str[:4]).pivot_table(index='kom', columns='th', values='peny', aggfunc='sum')
    U_ = U_.join(th.add_prefix('penyaluran_'))
    U_.to_csv(os.path.join(out, 'komoditas.csv'))
    print('\n== KOMODITAS (penyaluran dalam satuan laporan, sesudah koreksi kg->ton)')
    print(U_.sort_values('pelapor', ascending=False).to_string(float_format='{:,.0f}'.format))

    print('\n== KEHADIRAN per komoditas')
    Kh = F.groupby('kom').agg(pelapor=('kode', 'size'), median_bulan_aktif=('n_aktif', 'median'),
                              median_hadir=('hadir', 'median'), hadir_penuh=('hadir', lambda x: (x == 1).mean()),
                              hanya_1_bulan=('n_lapor', lambda x: (x == 1).mean()),
                              lapor_sep2026=('bulan_sejak_lapor_terakhir', lambda x: (x == 0).mean()),
                              diam_1_3_bln=('bulan_sejak_lapor_terakhir', lambda x: ((x >= 1) & (x <= 3)).mean()),
                              diam_lebih_3_bln=('bulan_sejak_lapor_terakhir', lambda x: (x > 3).mean()))
    bolong = pd.Series({k: 1 - M[i][A0[i]].mean() for k, i in F.groupby('kom').indices.items()}, name='porsi_bolong_saat_aktif')
    Kh = Kh.join(bolong)
    Kh.to_csv(os.path.join(out, 'kehadiran_komoditas.csv'))
    print(Kh.sort_values('pelapor', ascending=False).to_string())
    N = C[C.tingkat == 'nasional'].pivot_table(index='per', columns='kom', values='lapor')
    N.to_csv(os.path.join(out, 'pelapor_per_bulan.csv'))
    print('\n== PELAPOR per bulan (nasional), 6 komoditas terbesar')
    top = Kh.sort_values('pelapor', ascending=False).index[:6]
    print(N[top].astype(int).T.to_string())

    print('\n== PANJANG LUBANG di tengah (jumlah lubang)')
    Gp = G.pivot_table(index='kom', columns='kelas', values='panjang', aggfunc='size', fill_value=0, observed=False)
    Gp.to_csv(os.path.join(out, 'lubang.csv'))
    print(Gp.to_string())

    print(f'\n== SEL HAMPIR LENGKAP (aktif >= {MIN_AKTIF}); aktif0 = pertama..terakhir lapor, aktif3 = +{TENGGANG} bulan')
    print(R[R.kom.isin(top)].sort_values(['kom', 'tingkat', 'blok']).to_string(index=False))

    print('\n== IDENTITAS STOK (laporan berurutan, satu kepala)')
    print(I.to_string(index=False))

    print('\n== KONSENTRASI (penyaluran, blok penyetelan)')
    print(K[(K.periode == 'penyetelan') & K.kom.isin(top)].drop(columns='periode').to_string(index=False))

    if bps:
        V = cakupan_beras(L, bps, here)
        V.to_csv(os.path.join(out, 'cakupan_beras.csv'), index=False)
        print('\n== CAKUPAN VOLUME BERAS terhadap BPS')
        print(V.to_string(index=False, float_format='{:,.4f}'.format))

    print('\n== HARGA JUAL')
    print(H.to_string(index=False, float_format='{:,.3f}'.format))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
