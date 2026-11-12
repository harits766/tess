"""Uji kepekaan SESUDAH hasil (bukan hasil resmi): gerbang U1 hanya untuk sel Jan-Sep 2026 (t >= 24)."""
import sys, pandas as pd
sys.path.insert(0, sys.argv[1])
import adu_versi as AV
u = pd.read_csv(sys.argv[2] + '/U1_sel.csv')
print(u[u.cfg == 'resep'].groupby(['tingkat', 'soal', 'jenis']).apply(lambda d: pd.Series(dict(sel=d.groupby(['w', 't']).ngroups, sel_lt24=d[d.t < 24].groupby(['w', 't']).ngroups, baris_lt24=round((d.t < 24).mean(), 3)))).to_string())
G = pd.DataFrame([AV.gerbang(u[u.t >= 24], 'resep', 'A5', tk) for tk in AV.TINGKAT])
print(G.T.to_string())
G.to_csv(sys.argv[2] + '/gerbang_U1_peka_2026saja.csv', index=False)
