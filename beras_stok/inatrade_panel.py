"""Panel beras INATRADE per provinsi per bulan + matriks arus antar provinsi.

Pakai:  python -I inatrade_panel.py <file Non_PAW_dari_nol.xlsm> <folder keluaran> [semua|nonpaw|paw]

Langkah:
1. Ambil semua baris Jenis Komoditi = Beras dari sheet "2024-2026" (PAW + Non PAW).
2. Satu laporan = perusahaan x bulan x sub komoditi (nilai kepala laporan berulang di tiap baris rincian).
3. Koreksi satuan: laporan yang volumenya >= 100x median laporan perusahaan itu sendiri
   dianggap ditulis dalam kg -> dibagi 1000.
4. BULOG (kode 00372) dipisah dari pedagang.
5. Keluaran: laporan.csv, panel_provinsi.csv, arus_penyaluran.csv, arus_pengadaan.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import U, a0, normprov, periode  # noqa: E402

KODE_BULOG = '00372'
AMBANG_KG = 100
Q = ['Pengadaan', 'Penyaluran', 'Stok Awal', 'Stok Akhir']


def baca(path, baris='semua', komoditi='BERAS'):
    """baris: 'semua', 'nonpaw' (Provinsi Perusahaan = Provinsi Penyaluran) atau 'paw' (berbeda).
    komoditi: isi kolom Jenis Komoditi (huruf besar), mis. 'KEDELAI BAHAN BAKU TEMPE DAN TAHU'."""
    S = pd.read_excel(path, sheet_name='2024-2026', dtype=object)
    B = S[S['Jenis Komoditi'].map(U) == komoditi].copy().reset_index(drop=True)
    B['kode'] = B['Nama Perusahaan'].astype(str).str.strip().str.zfill(5)
    B['periode'] = [periode(b, t) for b, t in zip(B['Bulan'], B['Tahun'])]
    B['sub'] = B['Sub Komoditi'].astype(str).str.strip()
    B['prov'] = B['Provinsi Perusahaan'].map(normprov)
    B['prov_tujuan'] = B['Provinsi Penyaluran'].map(normprov)
    B['prov_asal'] = B['Asal Pengadaan'].map(normprov)
    for c in Q + ['Rincian Pengadaan', 'Rincian Penyaluran', 'Harga Jual']:
        B[c] = B[c].map(a0)
    B = B.dropna(subset=['periode'])
    if baris == 'nonpaw':
        B = B[B['prov_tujuan'] == B['prov']]
    elif baris == 'paw':
        B = B[(B['prov_tujuan'] != '') & (B['prov_tujuan'] != B['prov'])]
    return B.reset_index(drop=True)


def laporan(B):
    L = B.groupby(['kode', 'periode', 'sub'], as_index=False).agg(
        prov=('prov', 'first'), peng=('Pengadaan', 'max'), peny=('Penyaluran', 'max'),
        sa=('Stok Awal', 'max'), sk=('Stok Akhir', 'max'), baris=('periode', 'size'))
    base = {}
    for k, g in L.groupby(['kode', 'sub']):
        v = g[['peny', 'sa', 'sk', 'peng']].replace(0, np.nan).stack()
        base[k] = v.median() if len(v) else np.nan
    L['basis'] = [base[(a, b)] for a, b in zip(L['kode'], L['sub'])]
    besar = L[['peny', 'sa', 'sk', 'peng']].max(axis=1) / L['basis']
    L['faktor'] = np.where((L['basis'] > 0) & (besar >= AMBANG_KG), 1 / 1000, 1.0)
    for c in ['peng', 'peny', 'sa', 'sk']:
        L[c] = L[c] * L['faktor']
    L['bulog'] = L['kode'] == KODE_BULOG
    L['cover_bln'] = np.where(L['peny'] > 0, L['sk'] / L['peny'], np.nan)
    return L


def panel(L):
    T = L[~L['bulog']]
    P = T.groupby(['prov', 'periode']).agg(
        perusahaan=('kode', 'nunique'), laporan=('kode', 'size'),
        penyaluran_ton=('peny', 'sum'), stok_akhir_ton=('sk', 'sum'),
        cover_median_bln=('cover_bln', 'median')).reset_index()
    nas = T.groupby('periode')['cover_bln'].median().rename('cover_nasional_bln')
    P = P.join(nas, on='periode')
    P['indeks_cover'] = P['cover_median_bln'] / P['cover_nasional_bln']
    return P


def arus(B, L):
    fx = dict(zip(zip(L['kode'], L['periode'], L['sub']), L['faktor']))
    B = B[B['kode'] != KODE_BULOG].copy()
    f = [fx.get(k, 1.0) for k in zip(B['kode'], B['periode'], B['sub'])]
    B['vol_jual'] = B['Rincian Penyaluran'] * f
    B['vol_beli'] = B['Rincian Pengadaan'] * f
    jual = B[(B['prov_tujuan'] != '') & (B['vol_jual'] > 0)].groupby(
        ['periode', 'prov', 'prov_tujuan'], as_index=False)['vol_jual'].sum()
    jual.columns = ['periode', 'asal', 'tujuan', 'ton']
    beli = B[(B['prov_asal'] != '') & (B['vol_beli'] > 0)].groupby(
        ['periode', 'prov_asal', 'prov'], as_index=False)['vol_beli'].sum()
    beli.columns = ['periode', 'asal', 'tujuan', 'ton']
    return jual, beli


def main(path, out, baris='semua'):
    os.makedirs(out, exist_ok=True)
    B = baca(path, baris)
    L = laporan(B)
    P = panel(L)
    jual, beli = arus(B, L)
    L.to_csv(os.path.join(out, 'laporan.csv'), index=False)
    P.to_csv(os.path.join(out, 'panel_provinsi.csv'), index=False)
    jual.to_csv(os.path.join(out, 'arus_penyaluran.csv'), index=False)
    beli.to_csv(os.path.join(out, 'arus_pengadaan.csv'), index=False)
    print(f'{len(B)} baris beras, {len(L)} laporan ({int((L.faktor < 1).sum())} dikoreksi kg->ton)')
    print(f'{P.prov.nunique()} provinsi pelapor, {len(P)} sel provinsi-bulan')
    print(f'arus penyaluran: {len(jual)} baris, antar provinsi {int((jual.asal != jual.tujuan).sum())}')
    print(f'arus pengadaan: {len(beli)} baris, antar provinsi {int((beli.asal != beli.tujuan).sum())}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'semua')
