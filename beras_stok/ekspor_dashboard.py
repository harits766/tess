"""Ekspor hasil model ke JSON untuk tab "Stok beras" di dashboard Monitor Harga Non PAW.

Pakai:  python -I ekspor_dashboard.py <folder hasil> <folder keluaran>

Keluaran:
  stok_beras.json   satu baris per tingkat x wilayah x bulan x komponen (median, p05, p95; juta ton)
  stok_ringkas.json validasi titik survei, uji sensitivitas, pembanding neraca Bapanas, parameter utama
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SENS = [('penuh', 'Swasta ≥ 0 per pulau (dasar)'), ('penuh_positif_provinsi', 'Swasta ≥ 0 per provinsi'),
        ('penuh_positif_nasional', 'Swasta ≥ 0 nasional saja')]


def main(hasil, out):
    os.makedirs(out, exist_ok=True)
    R = pd.read_csv(os.path.join(hasil, 'posterior_penuh.csv'))
    R['pulau'] = R.pulau.fillna('')
    R['id'] = R.tingkat + '|' + R.wilayah + '|' + R.periode + '|' + R.komponen
    rows = [{'id': r.id, 'tingkat': r.tingkat, 'wilayah': r.wilayah, 'pulau': r.pulau, 'periode': r.periode,
             'komponen': r.komponen, 'median': round(r.median_juta_ton, 4), 'p05': round(r.p05, 4),
             'p95': round(r.p95, 4)} for r in R.itertuples()]
    with open(os.path.join(out, 'stok_beras.json'), 'w') as f:
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))

    ring = []
    for lab in ['holdout_2022-12', 'penuh']:
        p = os.path.join(hasil, f'validasi_{lab}.csv')
        if not os.path.exists(p):
            continue
        for r in pd.read_csv(p).itertuples():
            ring.append({'id': f'validasi|{lab}|{r.periode}', 'jenis': 'validasi_' + ('holdout' if 'holdout' in lab
                                                                                       else 'fit'),
                         'label': ('Survei BPS (SCBN)' if r.sumber == 'survei_bps_scbn' else 'Survei SSBAT Bapanas-BPS'),
                         'periode': r.periode, 'amatan': r.amatan_juta_ton, 'median': round(r.prediksi_median, 3),
                         'p05': round(r.prediksi_p05, 3), 'p95': round(r.prediksi_p95, 3),
                         'dipakai': r.dipakai_untuk_fit == 'ya'})
    for lab, nama in SENS:
        p = os.path.join(hasil, f'posterior_{lab}.csv')
        if not os.path.exists(p):
            continue
        S = pd.read_csv(p)
        s = S[(S.tingkat == 'nasional') & (S.komponen == 'total') & (S.periode == '2026-09')].iloc[0]
        ring.append({'id': f'sensitivitas|{lab}', 'jenis': 'sensitivitas', 'label': nama, 'periode': '2026-09',
                     'median': round(s.median_juta_ton, 3), 'p05': round(s.p05, 3), 'p95': round(s.p95, 3),
                     'dasar': lab == 'penuh'})
    J = pd.read_csv(os.path.join(HERE, 'jangkar_publik.csv'))
    for r in J[J.jenis == 'neraca_bapanas'].itertuples():
        ring.append({'id': f'neraca|{r.periode}', 'jenis': 'neraca', 'label': 'Neraca Bapanas',
                     'periode': r.periode, 'nilai': r.nilai_juta_ton})
    P = pd.read_csv(os.path.join(hasil, 'parameter_penuh.csv'), index_col=0)
    for k, nama in [('susut', 'Susut/kehilangan (porsi produksi)'),
                    ('log_1_plus_nu', 'log(1 + porsi konsumsi non rumah tangga)'),
                    ('bias_survei[0]', 'Bias log survei SSBAT terhadap model'),
                    ('bias_survei[1]', 'Bias log survei SCBN BPS terhadap model'),
                    ('beta_harga', 'Elastisitas harga penggilingan terhadap stok (12 bulan)')]:
        if k in P.index:
            ring.append({'id': f'parameter|{k}', 'jenis': 'parameter', 'label': nama,
                         'median': float(P.loc[k, 'mean']), 'p05': float(P.loc[k, 'eti90_lb']),
                         'p95': float(P.loc[k, 'eti90_ub'])})
    with open(os.path.join(out, 'stok_ringkas.json'), 'w') as f:
        json.dump(ring, f, ensure_ascii=False, indent=0, default=lambda o: o.item() if isinstance(o, np.generic) else o)
    print(f'stok_beras.json: {len(rows)} baris; stok_ringkas.json: {len(ring)} baris')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
