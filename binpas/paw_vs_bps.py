"""Bandingkan tautan antarprovinsi beras di INATRADE (PAW, tanpa BULOG) dengan daftar mitra Pola Distribusi BPS.

Pakai:  python -I binpas/paw_vs_bps.py binpas <S.pkl hasil tahap0.baca> <mitra.csv dari poldis_mitra.py>
Hanya untuk edisi BPS yang TIDAK disembunyikan (2024). Keluaran agregat saja.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, sys.argv[1])
import tahap0 as T0
S = pd.read_pickle(sys.argv[2])
B = pd.read_csv(sys.argv[3]); B = B[B.mitra.notna()]
# tautan BPS berarah asal -> tujuan
bps = set((r.mitra, r.prov) for r in B[B.arah == 'beli'].itertuples()) | set((r.prov, r.mitra) for r in B[B.arah == 'jual'].itertuples())
bps_beli = set((r.mitra, r.prov) for r in B[B.arah == 'beli'].itertuples()); bps_jual = set((r.prov, r.mitra) for r in B[B.arah == 'jual'].itertuples())
print('BPS edisi 2024: tautan berarah', len(bps), '| dari sisi beli', len(bps_beli), '| dari sisi jual', len(bps_jual), '| disebut dua sisi', len(bps_beli & bps_jual))
R = S[(S.kom == 'BERAS') & (S.kode != T0.KODE_BULOG) & (S.tuj != '') & S.tuj.notna() & (S.tuj != S.prov) & (S['Rincian Penyaluran'] > 0)].copy()
R['thn'] = R.per.str[:4]
print('baris PAW beras (tanpa BULOG):', len(R), '| perusahaan', R.kode.nunique(), '| tujuan tidak dikenal:', sorted(set(R.tuj) - set(T0.PULAU_DARI))[:8])
R = R[R.tuj.isin(T0.PULAU_DARI) & R.prov.isin(T0.PULAU_DARI)]
P34 = set(B.prov)
for thn, g in list(R.groupby('thn')) + [('semua', R)]:
    v = g.groupby(['prov', 'tuj'])['Rincian Penyaluran'].sum()
    n = g.groupby(['prov', 'tuj']).kode.nunique()
    ina = set(v.index)
    kena = ina & bps
    print(f'{thn}: perusahaan {g.kode.nunique()}, tautan INATRADE {len(ina)} (asal {len(set(a for a, _ in ina))} prov, tujuan {len(set(b for _, b in ina))} prov) | '
          f'ada di BPS {len(kena)} -> presisi {len(kena) / len(ina):.0%}, presisi tertimbang volume {v[list(kena)].sum() / v.sum():.0%}, '
          f'recall {len(kena) / len(bps):.0%} | tautan dengan >= 3 perusahaan: {(n >= 3).sum()}')
    asal = v.groupby('prov').sum().sort_values(ascending=False)
    print('    pangsa asal 5 terbesar:', {k: f'{x / asal.sum():.0%}' for k, x in asal.head(5).items()})
# peluang acak: kepadatan graf BPS
print('kepadatan graf BPS:', round(len(bps) / (34 * 33), 3))
