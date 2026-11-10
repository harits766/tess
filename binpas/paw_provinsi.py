"""Ringkasan laporan distribusi antarprovinsi (PAW) bapokting per provinsi, untuk kartu
"Pelaporan Distribusi Bapokting" di Dashboard Monitoring Perdagangan Antarwilayah (Dit. Binpas).

Pakai:
  python -I paw_provinsi.py <Non_PAW_dari_nol.xlsm> <periode awal YYYY-MM> <periode akhir YYYY-MM> [PROVINSI] [folder keluaran]

Contoh:
  python -I paw_provinsi.py Non_PAW_dari_nol.xlsm 2026-09 2026-09 RIAU hasil_binpas

Definisi (hanya data INATRADE, tanpa model):
  baris PAW      = Provinsi Penyaluran terisi dan berbeda dari Provinsi Perusahaan
  masuk ke P     = baris PAW dengan Provinsi Penyaluran = P; asal = Provinsi Perusahaan pengirim
                   (provinsi kedudukan perusahaan, belum tentu asal fisik barang)
  keluar dari P  = baris PAW dengan Provinsi Perusahaan = P; tujuan = Provinsi Penyaluran
Keluaran: ringkasan_provinsi.csv (38 provinsi: distributor, provinsi mitra, komoditas untuk masuk/keluar)
dan, bila PROVINSI diberikan, detail_<PROVINSI>.csv (per komoditas: distributor, asal/tujuan utama).
Volume (ton) sengaja tidak dihitung: satuan laporan beberapa komoditas belum divalidasi
(mis. minyak goreng dan pupuk Riau terbaca jutaan ton per tahun).
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'beras_stok'))
from util import U, normprov, periode  # noqa: E402


def baca(path):
    S = pd.read_excel(path, sheet_name='2024-2026', dtype=object)
    S['prov'] = S['Provinsi Perusahaan'].map(normprov)
    S['tuj'] = S['Provinsi Penyaluran'].map(normprov)
    S['per'] = [periode(b, t) for b, t in zip(S['Bulan'], S['Tahun'])]
    S['kode'] = S['Nama Perusahaan'].astype(str).str.strip()
    S['kom'] = S['Jenis Komoditi'].map(U)
    return S


def main(path, a, b, prov=None, out='.'):
    os.makedirs(out, exist_ok=True)
    S = baca(path)
    W = S[(S.tuj != '') & (S.tuj != S.prov) & (S.per >= a) & (S.per <= b)]
    mas = W.groupby('tuj').agg(masuk_distributor=('kode', 'nunique'), masuk_provinsi_asal=('prov', 'nunique'),
                               masuk_komoditas=('kom', 'nunique'))
    kel = W.groupby('prov').agg(keluar_distributor=('kode', 'nunique'), keluar_provinsi_tujuan=('tuj', 'nunique'),
                                keluar_komoditas=('kom', 'nunique'))
    R = mas.join(kel, how='outer').fillna(0).astype(int).rename_axis('provinsi').reset_index()
    R.to_csv(os.path.join(out, 'ringkasan_provinsi.csv'), index=False)
    print(f'periode {a} s.d. {b}: {len(mas)} provinsi menerima, {len(kel)} provinsi mengirim')
    if prov:
        rows = []
        for arah, g, mitra in [('masuk', W[W.tuj == prov], 'prov'), ('keluar', W[W.prov == prov], 'tuj')]:
            for k, x in g.groupby('kom'):
                top = x.groupby(mitra).kode.nunique().sort_values(ascending=False).index[:3]
                rows.append((arah, k, x.kode.nunique(), ', '.join(p.title() for p in top)))
        D = pd.DataFrame(rows, columns=['arah', 'komoditas', 'distributor', 'mitra_utama'])
        D.to_csv(os.path.join(out, f'detail_{prov}.csv'), index=False)
        print(R[R.provinsi == prov].to_string(index=False))
        print(D.to_string(index=False))


if __name__ == '__main__':
    main(*sys.argv[1:4], *(sys.argv[4:6]))
