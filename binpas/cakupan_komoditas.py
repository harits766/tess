"""Cakupan volume INATRADE terhadap sumber resmi BPS, per komoditas (padanan HASIL_TAHAP0 bagian 6 untuk beras).

Pakai:  BPS_API_KEY=... python -I binpas/cakupan_komoditas.py <Non_PAW_dari_nol.xlsm> <cache json> <keluaran>

Sumber BPS (WebAPI, domain 0000):
  konsumsi rumah tangga  Susenas kg/kapita/minggu per kab/kota x penduduk (var 2790):
                         daging 2097 (2024) / 2552 (2025), telur 2099 / 2554, kacang-kacangan 2101
  produksi per provinsi  daging sapi 480, daging kerbau 481, daging ayam ras pedaging 488, telur ayam petelur 491
  impor (dataexim)       daging sapi/kerbau HS 0201 + 0202, kedelai HS 12019000, pupuk HS 3102-3105
Keluaran: cakupan_komoditas.csv (agregat nasional per tahun). INATRADE: pedagang tanpa BULOG, satuan sesudah koreksi
tahap0 (termasuk KOREKSI_KG).
"""
import json
import os
import sys
import time
import urllib.request

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'beras_stok'))
import ambil_bps as A  # noqa: E402
import tahap0 as T0  # noqa: E402

# komoditas -> item Susenas {tahun: (var, {turvar: faktor setara komoditas})}, var produksi, kode HS impor
KOM = {
    'DAGING SAPI': dict(susenas={2024: (2097, {'1786': 1.0}), 2025: (2552, {'2237': 1.0})}, produksi=480,
                        hs=['02011000', '02012000', '02013000', '02021000', '02022000', '02023000']),
    'DAGING KERBAU': dict(susenas={2025: (2552, {'2238': 1.0})}, produksi=481, hs=[]),
    'DAGING AYAM RAS': dict(susenas={2024: (2097, {'1789': 1.0}), 2025: (2552, {'2241': 1.0})}, produksi=488, hs=[]),
    # Susenas mencatat telur ayam ras dalam BUTIR; asumsi 16 butir per kg
    'TELUR AYAM RAS': dict(susenas={2024: (2099, {'1796': 1 / 16}), 2025: (2554, {'2250': 1 / 16})}, produksi=491, hs=[]),
    'KEDELAI BAHAN BAKU TEMPE DAN TAHU': dict(susenas={2024: (2101, {'1833': 1.0, '1835': 0.30, '1836': 0.60}),
                                                       2025: (2101, {'1833': 1.0, '1835': 0.30, '1836': 0.60})},
                                              produksi=None, hs=['12019000']),
    'PUPUK': dict(susenas={}, produksi=None, hs=['31021000', '31022100', '31042000', '31052000']),
}


def konsumsi_rt(var, items, y, cache):
    """Konsumsi rumah tangga nasional (ton/tahun) = sum kab/kota kg/kapita/minggu x penduduk x 52."""
    k = A.urai(A.ambil(var, [y], cache))
    k = k[k.turvar.isin(items)].assign(f=lambda d: d.turvar.map(items))
    k = (k.assign(kg=k.nilai * k.f).groupby('kode').kg.sum()).rename('kg_minggu').reset_index()
    p = A.urai(A.ambil(2790, [y], cache))
    p = p[p.turvar == '23'][['kode', 'nilai']].rename(columns={'nilai': 'jiwa'})
    prov = p[p.kode.str.endswith('00') & (p.kode != '9999')]
    kab = p[~p.kode.str.endswith('00')].merge(k, on='kode', how='left').dropna(subset=['kg_minggu'])
    kab['pkode'] = kab.kode.str[:2] + '00'
    rata = kab.groupby('pkode').apply(lambda g: (g.kg_minggu * g.jiwa).sum() / g.jiwa.sum()).rename('kgm')
    x = prov.merge(rata, left_on='kode', right_index=True, how='inner')
    return float((x.jiwa * x.kgm).sum() * 52 / 1000), float((x.jiwa * x.kgm).sum() / x.jiwa.sum())


def produksi(var, tahun, cache):
    d = A.urai(A.ambil(var, tahun, cache))
    d['prov'] = d.wilayah.map(A.nama_prov)
    d = d[(d.prov != 'INDONESIA') & (d.kode != '9999')]
    return d.groupby('tahun').nilai.sum().to_dict()


EXIM = 'https://webapi.bps.go.id/v1/api/dataexim/sumber/2/kodehs/{hs}/jenishs/2/tahun/{y}/periode/1/key/{key}/'


def ambil_exim(hs, y, cache):
    """Impor per kode HS dan tahun dari dataexim BPS (sama dengan stok_komoditas/siapkan_data.py); disimpan di cache."""
    f = os.path.join(cache, f'exim_{hs}_{y}.json')
    if not os.path.exists(f):
        url = EXIM.format(hs=hs, y=y, key=os.environ['BPS_API_KEY'])
        for i in range(4):
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    data = r.read()
                break
            except OSError:
                time.sleep(2 ** (i + 1))
        else:
            raise RuntimeError(f'gagal ambil exim {hs} {y}')
        with open(f, 'wb') as h:
            h.write(data)
    with open(f) as h:
        return json.load(h).get('data') or []


def impor(hs, tahun, cache, bulan_maks):
    """Impor (ton) per tahun; untuk tahun berjalan hanya sampai bulan terakhir INATRADE."""
    out = {}
    for y in tahun:
        tot = 0.0
        for h in hs:
            try:
                tot += sum(r['netweight'] for r in ambil_exim(h, y, cache) if int(r['bulan'][1:3]) <= bulan_maks.get(y, 12)) / 1000
            except Exception:
                tot = np.nan
                break
        out[y] = tot
    return out


def main(xlsm, cache, out):
    os.makedirs(out, exist_ok=True)
    L = T0.laporan(T0.baca(xlsm))
    L = L[~L.bulog].assign(thn=L.per.str[:4].astype(int))
    rows = []
    for kom, K in KOM.items():
        g = L[L.kom == kom]
        ina = g.groupby('thn').agg(pelapor=('kode', 'nunique'), bulan=('per', 'nunique'), peny=('peny', 'sum'), peng=('peng', 'sum'))
        prod = produksi(K['produksi'], [2023, 2024, 2025], cache) if K['produksi'] else {}
        imp = impor(K['hs'], [2024, 2025, 2026], cache, {2026: int(T0.PER[-1][5:])}) if K['hs'] else {}
        for y in (2024, 2025, 2026):
            if y not in ina.index:
                continue
            r = ina.loc[y]
            ys = y if y in K['susenas'] else max(K['susenas']) if K['susenas'] else None
            kons, kgm = konsumsi_rt(K['susenas'][ys][0], K['susenas'][ys][1], ys, cache) if ys else (np.nan, np.nan)
            f = r.bulan / 12   # tahun berjalan: sumber tahunan disetarakan dengan jumlah bulan INATRADE
            pr = prod.get(y, prod.get(max(prod)) if prod else np.nan)
            im = imp.get(y, np.nan) if K['hs'] else 0.0
            pasok = (pr if pr == pr else 0) * f + (im if im == im else 0)   # produksi (disetarakan bulan) + impor
            rows.append(dict(komoditas=kom, tahun=y, bulan_inatrade=int(r.bulan), pelapor=int(r.pelapor), penyaluran_ton=r.peny,
                             pengadaan_ton=r.peng, konsumsi_rt_ton_setahun=kons, kg_kapita_minggu=kgm, tahun_susenas=ys,
                             produksi_ton_setahun=pr, impor_ton=im, pasokan_ton=pasok if pasok > 0 else np.nan,
                             penyaluran_per_konsumsi_rt=r.peny / (kons * f) if kons == kons and kons > 0 else np.nan,
                             penyaluran_per_pasokan=r.peny / pasok if pasok > 0 else np.nan))
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(out, 'cakupan_komoditas.csv'), index=False)
    pd.set_option('display.width', 250)
    print(T.round(4).to_string(index=False))


if __name__ == '__main__':
    main(*sys.argv[1:4])
