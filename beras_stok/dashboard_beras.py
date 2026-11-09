"""Data JSON untuk dashboard "Monitor Stok Beras".

Pakai:  python -I dashboard_beras.py <folder data> <folder hasil> <folder varian> <folder keluaran>

<folder varian> berisi hasil varian INATRADE: h_nonpaw/, h_paw/, h_tanpa/ (keluaran model_stok.py).
Keluaran (satu file per dataset dashboard):
  stok.json        estimasi Jan 2024-Sep 2026 + prakiraan Okt-Des 2026 (nasional, pulau, provinsi; per komponen)
  varian.json      stok nasional bulanan & pulau Sep 2026 untuk 4 varian INATRADE
  uji.json         validasi, sensitivitas, konvergensi
  parameter.json   parameter utama posterior
  pembanding.json  neraca Bapanas dan stok akhir USDA
  jembatan.json    dekomposisi neraca: stok Des 2023 -> Sep 2026
  risiko.json      berapa bulan stok cukup dan peluang < 1 bulan konsumsi, prakiraan per provinsi
  sumber.json      sumber data
  kualitas.json    indikator kualitas data INATRADE beras
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_stok as M  # noqa: E402

DEV_TAHUNAN = {'2022': -0.019, '2023': -0.011, '2024': -0.062, '2025': -0.011, '2026': 0.0036}  # rata-rata posterior
NAMA_PROV = {p: p.title().replace('Dki', 'DKI').replace('Di ', 'DI ') for p in M.PROV}


def tulis(out, nama, rows):
    with open(os.path.join(out, nama), 'w') as f:
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'), default=float)
    print(f'{nama}: {len(rows)} baris')


def r4(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), 4)


def main(data, hasil, varian, out):
    os.makedirs(out, exist_ok=True)
    D = M.siapkan(data)
    per_all = ['2022-06'] + D['per']
    fnu = np.exp(0.3413)
    kons = {}  # konsumsi total per bulan (ton) per provinsi per tahun
    for i, b in enumerate(D['per']):
        kons[b] = D['cons'][:, i] * fnu * np.exp(DEV_TAHUNAN[b[:4]])
    for b in ['2026-10', '2026-11', '2026-12']:
        kons[b] = kons['2026-09']

    def kons_wil(tk, w, b):
        k = kons[b]
        if tk == 'nasional':
            return k.sum()
        if tk == 'pulau':
            return sum(k[M.PROV.index(p)] for p in M.PULAU[w])
        return k[M.PROV.index(w)]

    # ---- stok.json
    E = pd.read_csv(os.path.join(hasil, 'posterior_penuh.csv')).assign(jenis='estimasi')
    F = pd.read_csv(os.path.join(hasil, 'prakiraan.csv')).assign(jenis='prakiraan')
    S = pd.concat([E, F])
    S['pulau'] = S.pulau.fillna('')
    S = S[(S.tingkat != 'provinsi') | S.komponen.isin(['total', 'bulog', 'swasta'])]
    rows = []
    for r in S.itertuples():
        nama = 'Indonesia' if r.tingkat == 'nasional' else (NAMA_PROV.get(r.wilayah, r.wilayah))
        row = {'id': f'{r.tingkat}|{r.wilayah}|{r.periode}|{r.komponen}', 'tingkat': r.tingkat, 'wilayah': r.wilayah,
               'nama': nama, 'pulau': r.pulau, 'periode': r.periode, 'komponen': r.komponen, 'jenis': r.jenis,
               'median': r4(r.median_juta_ton), 'p05': r4(r.p05), 'p95': r4(r.p95), 'cukup_bulan': None}
        if r.komponen == 'total':
            row['cukup_bulan'] = r4(r.median_juta_ton * 1e6 / kons_wil(r.tingkat, r.wilayah, r.periode))
        rows.append(row)
    tulis(out, 'stok.json', rows)

    # ---- varian.json
    V = {'Keduanya (dasar)': os.path.join(hasil, 'posterior_penuh.csv'),
         'Non PAW saja': os.path.join(varian, 'h_nonpaw', 'posterior_penuh.csv'),
         'PAW saja': os.path.join(varian, 'h_paw', 'posterior_penuh.csv'),
         'Tanpa INATRADE': os.path.join(varian, 'h_tanpa', 'posterior_penuh_tanpa_inatrade_bulog_inatrade.csv')}
    rows = []
    for urut, (nm, f) in enumerate(V.items()):
        x = pd.read_csv(f)
        x = x[(x.komponen == 'total') & ((x.tingkat == 'nasional') | ((x.tingkat == 'pulau') & (x.periode == '2026-09')))]
        for r in x.itertuples():
            rows.append({'id': f'{nm}|{r.tingkat}|{r.wilayah}|{r.periode}', 'varian': nm, 'urut': urut,
                         'tingkat': r.tingkat, 'wilayah': 'Indonesia' if r.tingkat == 'nasional' else r.wilayah,
                         'periode': r.periode, 'median': r4(r.median_juta_ton), 'p05': r4(r.p05), 'p95': r4(r.p95)})
    tulis(out, 'varian.json', rows)

    # ---- uji.json
    rows = []
    for lab, f in [('Validasi: SSBAT Des 2022 disembunyikan', 'validasi_holdout_2022-12.csv')]:
        for r in pd.read_csv(os.path.join(hasil, f)).itertuples():
            rows.append({'id': f'validasi|{r.periode}', 'jenis': 'validasi',
                         'uji': ('Survei BPS (SCBN)' if r.sumber == 'survei_bps_scbn' else 'Survei SSBAT Bapanas-BPS')
                         + (' — disembunyikan' if r.dipakai_untuk_fit != 'ya' else ''),
                         'periode': r.periode, 'amatan': r4(r.amatan_juta_ton), 'median': r4(r.prediksi_median),
                         'p05': r4(r.prediksi_p05), 'p95': r4(r.prediksi_p95), 'masuk_interval':
                         bool(r.prediksi_p05 <= r.amatan_juta_ton <= r.prediksi_p95)})
    for lab, f in [('Swasta ≥ 0 per pulau (dasar)', 'posterior_penuh.csv'),
                   ('Swasta ≥ 0 nasional saja', 'posterior_penuh_positif_nasional.csv'),
                   ('Swasta ≥ 0 per provinsi', 'posterior_penuh_positif_provinsi.csv')]:
        x = pd.read_csv(os.path.join(hasil, f))
        r = x[(x.tingkat == 'nasional') & (x.komponen == 'total') & (x.periode == '2026-09')].iloc[0]
        rows.append({'id': f'sensitivitas|{lab}', 'jenis': 'sensitivitas', 'uji': lab, 'periode': '2026-09',
                     'amatan': None, 'median': r4(r.median_juta_ton), 'p05': r4(r.p05), 'p95': r4(r.p95),
                     'masuk_interval': None})
    tulis(out, 'uji.json', rows)

    # ---- parameter.json
    P = pd.read_csv(os.path.join(hasil, 'parameter_penuh.csv'), index_col=0)
    lab = [('susut', 'Susut (porsi produksi)', 'persen', 100),
           ('log_1_plus_nu', 'Konsumsi total ÷ konsumsi rumah tangga', 'kali', None),
           ('bias_survei[0]', 'Bias log survei SSBAT', 'log', 1), ('bias_survei[1]', 'Bias log survei SCBN BPS', 'log', 1),
           ('bias_bulog_inatrade', 'Bias log laporan INATRADE 00372 vs BULOG publik', 'log', 1),
           ('beta_harga', 'Elastisitas harga penggilingan terhadap stok', 'elastisitas', 1),
           ('sigma_proses', 'Guncangan proses (× konsumsi bulanan provinsi)', 'proporsi', 1)]
    rows = []
    for k, nm, sat, f in lab:
        m, lo, hi = P.loc[k, 'mean'], P.loc[k, 'eti90_lb'], P.loc[k, 'eti90_ub']
        if f is None:
            m, lo, hi = np.exp(m), np.exp(lo), np.exp(hi)
        else:
            m, lo, hi = m * f, lo * f, hi * f
        rows.append({'id': k, 'parameter': nm, 'satuan': sat, 'mean': r4(m), 'p05': r4(lo), 'p95': r4(hi),
                     'r_hat': r4(P.loc[k, 'r_hat'])})
    tulis(out, 'parameter.json', rows)

    # ---- pembanding.json
    rows = [{'id': f'neraca|{p}', 'sumber': 'Neraca Bapanas', 'periode': p, 'nilai': v,
             'catatan': 'tanpa pengurangan susut; batas atas'} for p, v in
            [('2024-12', 8.4), ('2025-12', 12.529), ('2026-09', 17.9)]]
    rows += [{'id': f'usda|{y}-12', 'sumber': 'USDA PSD', 'periode': f'{y}-12', 'nilai': v,
              'catatan': 'stok akhir tahun pasar; konsumsi USDA ±35 juta ton/tahun'} for y, v in
             [(2022, 4.70), (2023, 6.17), (2024, 5.575), (2025, 4.475), (2026, 3.575)]]
    rows += [{'id': f'survei|{p}', 'sumber': s, 'periode': p, 'nilai': v, 'catatan': 'survei stok'} for p, s, v in
             [('2022-06', 'Survei BPS (SCBN)', 9.71), ('2022-12', 'Survei SSBAT', 4.06), ('2023-12', 'Survei SSBAT', 4.13)]]
    tulis(out, 'pembanding.json', rows)

    # ---- jembatan.json: dekomposisi neraca nasional dari draw posterior
    z = np.load(os.path.join(hasil, 'posterior_penuh.npz'))
    Xn = z['stok'].reshape(-1, D['N'], D['T'] + 1).sum(axis=1)
    s = z['susut'].reshape(-1)
    lognu = z['log_1_plus_nu'].reshape(-1)
    idx = {b: i for i, b in enumerate(per_all)}
    rows = [{'id': 'awal', 'urut': 0, 'langkah': 'Stok akhir Des 2023', 'jenis': 'total',
             'nilai': r4(np.median(Xn[:, idx['2023-12']]) / 1e6)}]
    urut = 1
    for nm, a, b in [('2024', '2024-01', '2024-12'), ('2025', '2025-01', '2025-12'), ('Jan–Sep 2026', '2026-01', '2026-09')]:
        cols = [i for i, p in enumerate(D['per']) if a <= p <= b]
        prod = D['prod'][:, cols].sum() * (1 - s)
        imp = D['imp'][cols].sum()
        kons_d = sum(D['cons'][:, i].sum() * np.exp(lognu + DEV_TAHUNAN[D['per'][i][:4]]) for i in cols)
        dX = Xn[:, idx[b]] - Xn[:, idx[a] - 1]
        komp = [('Produksi setelah susut', np.median(prod)), ('Impor', imp), ('Konsumsi', -np.median(kons_d))]
        lain = np.median(dX) - sum(v for _, v in komp)
        komp.append(('Selisih lain', lain))
        for k, v in komp:
            rows.append({'id': f'{nm}|{k}', 'urut': urut, 'langkah': f'{nm}: {k}', 'periode': nm, 'jenis': 'ubah',
                         'nilai': r4(v / 1e6)})
            urut += 1
    rows.append({'id': 'akhir', 'urut': urut, 'langkah': 'Stok akhir Sep 2026', 'jenis': 'total',
                 'nilai': r4(np.median(Xn[:, -1]) / 1e6)})
    tulis(out, 'jembatan.json', rows)

    # ---- risiko.json
    K = pd.read_csv(os.path.join(hasil, 'risiko_provinsi.csv'))
    rows = [{'id': f'{r.wilayah}|{r.periode}', 'wilayah': r.wilayah,
             'nama': 'Indonesia' if r.wilayah == 'INDONESIA' else NAMA_PROV.get(r.wilayah, r.wilayah),
             'pulau': r.pulau if isinstance(r.pulau, str) else '', 'periode': r.periode,
             'cukup_bulan': r4(r.cukup_bulan_median), 'peluang_kurang_1_bulan': r4(r.peluang_kurang_1_bulan)}
            for r in K.itertuples()]
    tulis(out, 'risiko.json', rows)

    # ---- sumber.json
    src = [
        ('INATRADE beras', 'Laporan distribusi: pengadaan, penyaluran, stok, asal-tujuan, harga', 'Jan 2024–Sep 2026, per perusahaan', 'File Non_PAW_dari_nol.xlsm', 'indeks stok pedagang per pulau; stok BULOG (00372); peta arus'),
        ('Produksi padi bulanan', 'Padi GKG per provinsi (KSA)', 'Jan 2025–Nov 2026', 'WebAPI BPS var 2506', 'produksi bulanan; Okt–Nov 2026 untuk prakiraan'),
        ('Produksi padi tahunan', 'Padi GKG per provinsi', '2022–2024', 'WebAPI BPS var 1498', 'produksi 2022–2024 (dipecah dengan pola 2025)'),
        ('Konsumsi beras', 'Konsumsi per kapita seminggu (Susenas)', '2022–2025, kab/kota', 'WebAPI BPS var 2094', 'konsumsi rumah tangga'),
        ('Penduduk', 'Jumlah penduduk', '2022–2026, kab/kota', 'WebAPI BPS var 2790', 'bobot dan pengali konsumsi'),
        ('Harga penggilingan', 'Harga beras medium di penggilingan', 'Jan 2022–Des 2025', 'WebAPI BPS var 500, 2277', 'sinyal harga (lemah)'),
        ('Survei stok', 'SCBN BPS Jun 2022; SSBAT Bapanas-BPS Des 2022, Des 2023', '3 titik', 'Rilis BPS/Bapanas', 'jangkar level stok total'),
        ('Stok BULOG', 'Angka stok BULOG yang diumumkan', '10 titik, Mar 2023–Sep 2026', 'Rilis BULOG/Bapanas', 'jangkar komponen BULOG'),
        ('Impor beras', 'Impor tahunan', '2022–2026', 'BPS', 'pasokan (dibagi rata per bulan)'),
        ('Neraca Bapanas', 'Stok neraca, konsumsi 2,591 juta ton/bulan', '2024–2026', 'Rilis Bapanas', 'prior konsumsi; pembanding (batas atas)'),
        ('USDA PSD', 'Stok akhir, konsumsi, produksi, impor', '2022–2026, tahunan', 'Unduhan publik USDA', 'pembanding saja'),
    ]
    tulis(out, 'sumber.json', [{'id': f'{i:02d}', 'data': a, 'isi': b, 'cakupan': c, 'akses': d, 'dipakai_untuk': e}
                               for i, (a, b, c, d, e) in enumerate(src)])

    # ---- kualitas.json
    q = [('Baris beras', '3.662 (Non PAW 1.947; PAW 1.684; tanpa tujuan 31)'),
         ('Laporan (perusahaan × bulan × subkomoditas)', '1.683'),
         ('Pelapor per bulan', 'median 51 (min 9, maks 66); sebelum Okt 2024 hanya 9–15'),
         ('Provinsi pelapor', '20 dari 38; Jawa Barat 1 bulan; Sulawesi Selatan dan Lampung tidak ada'),
         ('Laporan dikoreksi kg → ton', '58'),
         ('Stok akhir 0', '11% laporan'),
         ('Neraca laporan tidak cocok (>5%)', '2% laporan'),
         ('Rincian ≠ total penyaluran (>5%)', '5% laporan'),
         ('Harga jual 0', '2% baris'),
         ('Cakupan penyaluran pedagang', 'sekitar 48 ribu ton/bulan = 1,9% konsumsi nasional')]
    tulis(out, 'kualitas.json', [{'id': f'{i:02d}', 'indikator': a, 'nilai': b} for i, (a, b) in enumerate(q)])


if __name__ == '__main__':
    main(*sys.argv[1:5])
