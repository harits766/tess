"""Ambil data resmi BPS (WebAPI) untuk model stok beras dan simpan sebagai CSV rapi.

Pakai:  BPS_API_KEY=... python -I ambil_bps.py <folder cache json> <folder keluaran>

Variabel BPS (domain 0000):
  2506  Produksi Padi Menurut Provinsi (Bulanan), ton GKG, 2025-2026 (Sep-Nov 2026 angka potensi)
  1498  Luas Panen, Produksi, dan Produktivitas Padi Menurut Provinsi (tahunan, s.d. 2024)
  2094  Rata-rata Konsumsi Perkapita Seminggu Kelompok Padi-Padian per Kab/Kota (Susenas), kg
  2790  Jumlah Penduduk menurut Kabupaten/Kota dan Kelompok Umur (TOTAL), jiwa
  500   Rata-Rata Harga Beras Bulanan di Tingkat Penggilingan Menurut Kualitas, Rp/kg (s.d. 2023)
  2277  idem, lanjutan 2024-2025 (2026 belum tersedia di WebAPI)

Keluaran: produksi_tahunan.csv, produksi_bulanan_ksa.csv, konsumsi_provinsi.csv, harga_penggilingan.csv
Kunci API dibaca dari env var BPS_API_KEY dan tidak pernah ditulis ke file.
"""
import json
import os
import sys
import time
import urllib.request

import pandas as pd

BASE = 'https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{var}/th/{th}/key/{key}/'
TH = {y: y - 1900 for y in range(2018, 2027)}  # th_id BPS: 2024 -> 124


def ambil(var, tahun, cache):
    th = ';'.join(str(TH[y]) for y in tahun)
    f = os.path.join(cache, f'{var}_{th.replace(";", "-")}.json')
    if not os.path.exists(f):
        url = BASE.format(var=var, th=th, key=os.environ['BPS_API_KEY'])
        for i in range(4):
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    data = r.read()
                break
            except OSError:
                time.sleep(2 ** (i + 1))
        else:
            raise RuntimeError(f'gagal ambil var {var}')
        with open(f, 'wb') as h:
            h.write(data)
    with open(f) as h:
        return json.load(h)


def urai(d):
    """datacontent BPS -> DataFrame (vervar, turvar, tahun, turtahun, nilai).

    Kunci datacontent = vervar + var + turvar + th_id + turtahun (tanpa pemisah)."""
    var = str(d['var'][0]['val'])
    vv = {str(x['val']): x['label'] for x in d['vervar']}
    tv = [str(x['val']) for x in d['turvar']]
    th = {str(x['val']): x['label'] for x in d['tahun']}
    tt = [str(x['val']) for x in d['turtahun']]
    rows = []
    for k, v in d['datacontent'].items():
        for a in vv:
            if not k.startswith(a + var):
                continue
            rest = k[len(a) + len(var):]
            for b in tv:
                if not rest.startswith(b):
                    continue
                r2 = rest[len(b):]
                for c in th:
                    if r2.startswith(c) and r2[len(c):] in tt:
                        rows.append((a, vv[a], b, int(th[c]), int(r2[len(c):]), v))
    return pd.DataFrame(rows, columns=['kode', 'wilayah', 'turvar', 'tahun', 'turtahun', 'nilai'])


def nama_prov(s):
    s = s.replace('<b>', '').replace('</b>', '').strip().upper()
    return {'KEP. BANGKA BELITUNG': 'KEPULAUAN BANGKA BELITUNG', 'KEP. RIAU': 'KEPULAUAN RIAU',
            'DI YOGYAKARTA': 'DAERAH ISTIMEWA YOGYAKARTA', 'D I YOGYAKARTA': 'DAERAH ISTIMEWA YOGYAKARTA'}.get(s, s)


def main(cache, out):
    os.makedirs(cache, exist_ok=True)
    os.makedirs(out, exist_ok=True)

    # produksi bulanan KSA 2025-2026
    m = urai(ambil(2506, [2025, 2026], cache))
    m = m[(m.turtahun <= 12) & (m.kode != '9999')]
    m['prov'] = m.wilayah.map(nama_prov)
    m['periode'] = m.tahun.astype(str) + '-' + m.turtahun.map('{:02d}'.format)
    m = m[m.prov != 'INDONESIA'][['prov', 'periode', 'nilai']].rename(columns={'nilai': 'padi_gkg_ton'})
    m['potensi'] = m.periode.isin(['2026-09', '2026-10', '2026-11', '2026-12'])
    m.sort_values(['prov', 'periode']).to_csv(os.path.join(out, 'produksi_bulanan_ksa.csv'), index=False)

    # produksi tahunan 2022-2024 (turvar 1193 = produksi ton)
    a = urai(ambil(1498, [2022, 2023, 2024], cache))
    a = a[(a.turvar == '1193')]
    a['prov'] = a.wilayah.map(nama_prov)
    a = a[a.prov != 'INDONESIA'][['prov', 'tahun', 'nilai']].rename(columns={'nilai': 'padi_gkg_ton'})
    a.sort_values(['prov', 'tahun']).to_csv(os.path.join(out, 'produksi_tahunan.csv'), index=False)

    # konsumsi beras per kapita (kab/kota) dibobot penduduk kab/kota -> provinsi
    rows = []
    for y in [2022, 2023, 2024, 2025]:
        k = urai(ambil(2094, [y], cache))
        k = k[k.turvar == '1735'][['kode', 'nilai']].rename(columns={'nilai': 'kg_minggu'})
        p = urai(ambil(2790, [y], cache))
        p = p[p.turvar == '23'][['kode', 'wilayah', 'nilai']].rename(columns={'nilai': 'jiwa'})
        prov = p[p.kode.str.endswith('00')].copy()
        prov['prov'] = prov.wilayah.map(nama_prov)
        kab = p[~p.kode.str.endswith('00')].merge(k, on='kode', how='left')
        kab['pkode'] = kab.kode.str[:2] + '00'
        for pk, g in kab.groupby('pkode'):
            g2 = g.dropna(subset=['kg_minggu'])
            nm = prov.loc[prov.kode == pk, 'prov']
            if not len(nm) or not len(g2):
                continue
            jiwa = float(prov.loc[prov.kode == pk, 'jiwa'].iloc[0])
            kgm = (g2.kg_minggu * g2.jiwa).sum() / g2.jiwa.sum()
            rows.append((nm.iloc[0], y, jiwa, kgm, len(g2), len(g)))
    K = pd.DataFrame(rows, columns=['prov', 'tahun', 'penduduk', 'beras_kg_kapita_minggu', 'kab_ada', 'kab_total'])
    K['konsumsi_rt_ton_bulan'] = K.penduduk * K.beras_kg_kapita_minggu * 52 / 12 / 1000
    K.sort_values(['prov', 'tahun']).to_csv(os.path.join(out, 'konsumsi_provinsi.csv'), index=False)

    # harga beras penggilingan bulanan nasional
    hs = []
    for var, th in [(500, [2022, 2023]), (2277, [2024, 2025])]:
        d = ambil(var, th, cache)
        x = urai(d)
        x['kualitas'] = x.wilayah.str.strip().str.upper()
        hs.append(x)
    h = pd.concat(hs)
    h = h[(h.turtahun <= 12) & h.kualitas.isin(['PREMIUM', 'MEDIUM'])]
    h['periode'] = h.tahun.astype(str) + '-' + h.turtahun.map('{:02d}'.format)
    h[['periode', 'kualitas', 'nilai']].rename(columns={'nilai': 'rp_kg'}).sort_values(
        ['kualitas', 'periode']).to_csv(os.path.join(out, 'harga_penggilingan.csv'), index=False)

    print(f'produksi bulanan: {m.prov.nunique()} prov, {m.periode.nunique()} bulan;'
          f' tahunan {a.prov.nunique()} prov x {a.tahun.nunique()} th')
    print(f'konsumsi: {len(K)} baris; nasional RT 2025 = '
          f'{K[K.tahun == 2025].konsumsi_rt_ton_bulan.sum() / 1e6:.3f} juta ton/bulan')
    print(f'harga: {h.periode.nunique()} bulan, kualitas {sorted(h.kualitas.unique())}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
