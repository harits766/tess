"""Panel data satu komoditas untuk model stok generik.

Pakai:
  BPS_API_KEY=... python -I siapkan_data.py <komoditas> <file Non_PAW_dari_nol.xlsm> <cache BPS> \
      <psd_oilseeds.csv> <folder keluaran> [semua|nonpaw|paw]

Keluaran di <folder keluaran>:
  impor_bulanan.csv       prov, periode, ton            impor BPS per pelabuhan -> provinsi pelabuhan
  produksi_bulanan.csv    prov, periode, ton            produksi nasional USDA/12 x pangsa provinsi (asumsi)
  konsumsi_provinsi.csv   prov, tahun, penduduk, kg per item, konsumsi_rt_ton_bulan (setara biji)
  usda_neraca.csv         neraca USDA per tahun pemasaran (pembanding + jangkar stok akhir)
  inatrade_laporan.csv    laporan per perusahaan x bulan x subkomoditas (setelah koreksi kg->ton)
  inatrade_nasional.csv   per bulan: pelapor, stok tercatat, penyaluran, indeks berantai stok
  inatrade_provinsi.csv   per provinsi perusahaan x bulan: stok dan penyaluran tercatat
  arus_penyaluran.csv     periode, asal, tujuan, ton (dari rincian penyaluran)
Kunci BPS hanya dibaca dari env var BPS_API_KEY.
"""
import json
import os
import sys
import time
import urllib.request

import numpy as np
import pandas as pd

AKAR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AKAR)
sys.path.insert(0, os.path.join(AKAR, '..', 'beras_stok'))
import ambil_bps as A  # noqa: E402
import inatrade_panel as IP  # noqa: E402
from konfigurasi import KOMODITAS  # noqa: E402
from model_stok import PROV  # noqa: E402

EXIM = 'https://webapi.bps.go.id/v1/api/dataexim/sumber/2/kodehs/{hs}/jenishs/2/tahun/{y}/periode/1/key/{key}/'


def bulan_list(awal, akhir):
    return [str(p) for p in pd.period_range(awal, akhir, freq='M')]


def ambil_exim(hs, y, cache):
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


def impor(K, cache, per):
    rows, tak = [], set()
    for hs in K['hs']:
        for y in range(int(per[0][:4]), int(per[-1][:4]) + 1):
            for r in ambil_exim(hs, y, cache):
                pod = r['pod'].strip().upper()
                prov = K['pelabuhan'].get(pod)
                if prov is None:
                    tak.add(pod)
                    continue
                rows.append((prov, f"{r['tahun']}-{r['bulan'][1:3]}", r['netweight'] / 1000))
    if tak:
        raise ValueError(f'pelabuhan belum dipetakan di konfigurasi: {sorted(tak)}')
    I = pd.DataFrame(rows, columns=['prov', 'periode', 'ton']).groupby(['prov', 'periode'], as_index=False).ton.sum()
    return I[I.periode.isin(per)]


def konsumsi(K, cache):
    out = []
    for y in K['susenas_tahun']:
        k = A.urai(A.ambil(K['susenas_var'], [y], cache))
        p = A.urai(A.ambil(2790, [y], cache))
        p = p[p.turvar == '23'][['kode', 'wilayah', 'nilai']].rename(columns={'nilai': 'jiwa'})
        prov = p[p.kode.str.endswith('00')].copy()
        prov['prov'] = prov.wilayah.map(A.nama_prov)
        kab = p[~p.kode.str.endswith('00')].copy()
        for tv, (nm, _) in K['susenas_item'].items():
            kab = kab.merge(k[k.turvar == tv][['kode', 'nilai']].rename(columns={'nilai': nm}), on='kode', how='left')
        kab['pkode'] = kab.kode.str[:2] + '00'
        for pk, g in kab.groupby('pkode'):
            nm = prov.loc[prov.kode == pk, 'prov']
            if not len(nm) or nm.iloc[0] not in PROV:
                continue
            row = {'prov': nm.iloc[0], 'tahun': y, 'penduduk': float(prov.loc[prov.kode == pk, 'jiwa'].iloc[0])}
            setara = 0.0
            for _, (it, f) in K['susenas_item'].items():
                g2 = g.dropna(subset=[it])
                row[it + '_kg_kapita_minggu'] = (g2[it] * g2.jiwa).sum() / g2.jiwa.sum() if len(g2) else np.nan
                setara += f * np.nan_to_num(row[it + '_kg_kapita_minggu'])  # item tanpa data = 0 (kedele mentah sangat kecil)
            row['setara_kg_kapita_minggu'] = setara
            row['konsumsi_rt_ton_bulan'] = row['penduduk'] * setara * 52 / 12 / 1000
            out.append(row)
    C = pd.DataFrame(out)
    hilang = sorted(set(PROV) - set(C.prov))
    if hilang:
        raise ValueError(f'konsumsi tidak ada untuk {hilang}')
    return C


def usda(K, psd):
    D = pd.read_csv(psd)
    I = D[(D.Country_Name == 'Indonesia') & (D.Commodity_Description == K['usda_komoditas'])]
    N = I.pivot_table(index='Market_Year', columns='Attribute_Description', values='Value')
    N = N[['Beginning Stocks', 'Production', 'Imports', 'Domestic Consumption', 'Exports', 'Ending Stocks']] * 1000
    N.columns = ['stok_awal', 'produksi', 'impor', 'konsumsi', 'ekspor', 'stok_akhir']
    N = N[N.index >= 2020].reset_index().rename(columns={'Market_Year': 'tahun_pemasaran'})
    b = K['usda_bulan_awal']
    N['periode_akhir'] = [f'{y + 1}-{b - 1:02d}' for y in N.tahun_pemasaran]
    return N


def produksi(K, N, per):
    sh = pd.Series(K['pangsa_produksi'])
    sh = sh / sh.sum()
    b = K['usda_bulan_awal']
    rows = []
    for p in per:
        y, m = int(p[:4]), int(p[5:])
        my = y if m >= b else y - 1
        tot = float(N.loc[N.tahun_pemasaran == my, 'produksi'].iloc[0]) / 12
        rows += [(pr, p, tot * s) for pr, s in sh.items()]
    return pd.DataFrame(rows, columns=['prov', 'periode', 'ton'])


def inatrade(K, xlsm, baris, per):
    B = IP.baca(xlsm, baris, K['inatrade_komoditi'])
    # subkomoditas tanpa label: isi dengan label dominan perusahaan itu, sisanya label bawaan
    lab = B[B['sub'] != K['sub_tanpa_label']].groupby('kode')['sub'].agg(lambda s: s.value_counts().index[0])
    kosong = B['sub'] == K['sub_tanpa_label']
    B.loc[kosong, 'sub'] = B.loc[kosong, 'kode'].map(lab).fillna(K['sub_bawaan'])
    L = IP.laporan(B)
    L = L[~L.kode.isin(K['bumn'])]
    L = L[L.periode.isin(per)]
    F = L.groupby(['kode', 'periode'], as_index=False).agg(prov=('prov', 'first'), sk=('sk', 'sum'), peny=('peny', 'sum'))
    nas = F.groupby('periode').agg(pelapor=('kode', 'nunique'), stok_tercatat_ton=('sk', 'sum'),
                                   penyaluran_tercatat_ton=('peny', 'sum')).reindex(per)
    # indeks berantai: perusahaan dengan stok > 0 di bulan t-1 dan t
    W = F.pivot_table(index='kode', columns='periode', values='sk', aggfunc='sum')
    r, n = [np.nan], [0]
    for a, b in zip(per[:-1], per[1:]):
        if a in W and b in W:
            ok = (W[a] > 0) & (W[b] > 0)
            r.append(np.log(W.loc[ok, b].sum() / W.loc[ok, a].sum()) if ok.sum() >= 2 else np.nan)
            n.append(int(ok.sum()))
        else:
            r.append(np.nan)
            n.append(0)
    nas['log_rasio_berantai'] = r
    nas['pasangan'] = n
    prov = F.groupby(['prov', 'periode'], as_index=False).agg(pelapor=('kode', 'nunique'), stok_tercatat_ton=('sk', 'sum'),
                                                               penyaluran_tercatat_ton=('peny', 'sum'))
    jual, _ = IP.arus(B, L)
    return L, nas.reset_index().rename(columns={'index': 'periode'}), prov, jual


def main(nama, xlsm, cache, psd, out, baris='semua'):
    K = KOMODITAS[nama]
    os.makedirs(out, exist_ok=True)
    os.makedirs(cache, exist_ok=True)
    per = bulan_list(K['awal'], K['akhir'])
    I = impor(K, cache, per)
    C = konsumsi(K, cache)
    N = usda(K, psd)
    P = produksi(K, N, per)
    L, nas, prov, jual = inatrade(K, xlsm, baris, per)
    for df, f in [(I, 'impor_bulanan'), (P, 'produksi_bulanan'), (C, 'konsumsi_provinsi'), (N, 'usda_neraca'),
                  (L, 'inatrade_laporan'), (nas, 'inatrade_nasional'), (prov, 'inatrade_provinsi'), (jual, 'arus_penyaluran')]:
        df.to_csv(os.path.join(out, f + '.csv'), index=False)
    th = I.assign(t=I.periode.str[:4]).groupby('t').ton.sum() / 1e6
    print('impor juta ton per tahun:', th.round(3).to_dict())
    print('konsumsi RT setara juta ton/tahun:', (C.groupby('tahun').konsumsi_rt_ton_bulan.sum() * 12 / 1e6).round(3).to_dict())
    print(f'INATRADE ({baris}): {len(L)} laporan, {int((L.faktor < 1).sum())} dikoreksi kg->ton;',
          'stok tercatat median', round(nas.stok_tercatat_ton.median() / 1e3, 1), 'ribu ton')


if __name__ == '__main__':
    main(*sys.argv[1:6], *(sys.argv[6:7] or ['semua']))
