"""Tabel Excel posterior stok beras per provinsi / pulau / nasional per bulan.

Pakai:  python -I tabel_excel.py <folder hasil model> <file .xlsx keluaran>

Membaca posterior_*.csv, parameter_penuh.csv dan validasi_*.csv dari folder hasil.
"""
import os
import sys

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

KOMP = ['total', 'bulog', 'swasta', 'rumah_tangga', 'penggilingan', 'pedagang', 'horeka']
NAMA = {'total': 'Total', 'rumah_tangga': 'Rumah tangga', 'penggilingan': 'Penggilingan', 'pedagang': 'Pedagang',
        'bulog': 'BULOG', 'swasta': 'Swasta (di luar BULOG)', 'horeka': 'Horeka & industri'}


def lebar(R, tingkat):
    x = R[R.tingkat == tingkat].copy()
    x['komponen'] = pd.Categorical(x.komponen, KOMP, ordered=True)
    w = x.pivot_table(index=['pulau', 'wilayah', 'periode'] if tingkat == 'provinsi' else ['wilayah', 'periode'],
                      columns='komponen', values=['median_juta_ton', 'p05', 'p95'], observed=True)
    cols = []
    for k in KOMP:
        for s, lab in [('median_juta_ton', 'median'), ('p05', 'p05'), ('p95', 'p95')]:
            cols.append((s, k))
    w = w[cols]
    w.columns = [f'{NAMA[k]} {lab}' for k in KOMP for lab in ['median', 'p05', 'p95']]
    return (w * 1000).round(1).reset_index()  # ribu ton


def rapikan(ws, n_kunci):
    head = PatternFill('solid', fgColor='DDE4EE')
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = head
        c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = ws.cell(row=2, column=n_kunci + 1)
    for i, col in enumerate(ws.columns, 1):
        m = max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:200])
        ws.column_dimensions[get_column_letter(i)].width = min(max(10, m + 2), 34 if i <= n_kunci else 14)
    ws.auto_filter.ref = ws.dimensions


def main(hasil, xlsx):
    R = pd.read_csv(os.path.join(hasil, 'posterior_penuh.csv'))
    R['pulau'] = R.pulau.fillna('')
    S = pd.read_csv(os.path.join(hasil, 'parameter_penuh.csv'), index_col=0)
    catatan = [
        ('Isi', 'Posterior stok beras total dan per komponen, akhir bulan, Jan 2024 - Sep 2026. Satuan ribu ton.'),
        ('Interval', 'p05-p95 = interval kredibel 90% dari model Bayesian (PyMC, NUTS).'),
        ('Model', 'Neraca bulanan per provinsi: stok = stok bulan lalu + produksi x (1 - susut) + impor + masuk '
                  '- keluar - konsumsi. Lihat README dan model_stok.py.'),
        ('Jangkar level', 'Survei Cadangan Beras BPS Jun 2022 (9,71 juta ton) dan Survei Stok Beras Akhir Tahun '
                          'Bapanas-BPS Des 2022 (4,06) dan Des 2023 (4,13), masing-masing dengan bias sendiri.'),
        ('BULOG per provinsi', 'Stok BULOG nasional dibagi ke provinsi menurut pangsa konsumsi (bukan data kanwil).'),
        ('Penjumlahan', 'Median komponen tidak harus berjumlah sama dengan median total; interval tiap baris '
                        'dihitung sendiri dari sampel posterior.'),
        ('Komponen swasta', 'Rumah tangga, penggilingan, pedagang, horeka = stok di luar BULOG x pangsa '
                            '(prior dari survei 2022 dan 2023). Pangsa tidak berubah antar provinsi/bulan.'),
        ('Data', 'Produksi KSA BPS (2022-2024 tahunan x pola bulanan 2025; Sep 2026 angka potensi), Susenas '
                 'konsumsi beras per kapita x penduduk, impor BPS, stok BULOG publik dan laporan INATRADE 00372, '
                 'laporan INATRADE pedagang, harga beras penggilingan BPS.'),
    ]
    with pd.ExcelWriter(xlsx, engine='openpyxl') as W:
        pd.DataFrame(catatan, columns=['Butir', 'Keterangan']).to_excel(W, sheet_name='Catatan', index=False)
        lebar(R, 'nasional').to_excel(W, sheet_name='Nasional', index=False)
        lebar(R, 'pulau').rename(columns={'wilayah': 'pulau'}).to_excel(W, sheet_name='Pulau', index=False)
        lebar(R, 'provinsi').rename(columns={'wilayah': 'provinsi'}).to_excel(W, sheet_name='Provinsi', index=False)
        R.to_csv(os.path.join(hasil, 'posterior_panjang.csv'), index=False)
        S.to_excel(W, sheet_name='Parameter')
        val = []
        for lab, ket in [('holdout_2022-12', 'validasi: survei Des 2022 disembunyikan'), ('penuh', 'fit penuh')]:
            v = os.path.join(hasil, f'validasi_{lab}.csv')
            if os.path.exists(v):
                val.append(pd.read_csv(v).assign(run=ket))
        if val:
            pd.concat(val).to_excel(W, sheet_name='Validasi', index=False)
        sens = []
        for lab, ket in [('penuh', 'swasta >= 0 per pulau (dasar)'), ('penuh_positif_provinsi', 'swasta >= 0 per provinsi'),
                         ('penuh_positif_nasional', 'swasta >= 0 nasional saja')]:
            v = os.path.join(hasil, f'posterior_{lab}.csv')
            if os.path.exists(v):
                x = pd.read_csv(v)
                x = x[(x.tingkat == 'nasional') & (x.komponen.isin(['total', 'bulog', 'swasta']))]
                sens.append(x.assign(skenario=ket)[['skenario', 'periode', 'komponen', 'median_juta_ton', 'p05', 'p95']])
        if sens:
            pd.concat(sens).to_excel(W, sheet_name='Sensitivitas', index=False)
        wb = W.book
        rapikan(wb['Catatan'], 1)
        wb['Catatan'].column_dimensions['B'].width = 110
        rapikan(wb['Nasional'], 2)
        rapikan(wb['Pulau'], 2)
        rapikan(wb['Provinsi'], 3)
        rapikan(wb['Parameter'], 1)
        for nm in ['Validasi', 'Sensitivitas']:
            if nm in wb.sheetnames:
                rapikan(wb[nm], 1)
    print('ditulis', xlsx)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
