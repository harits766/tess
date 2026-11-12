"""Gerbang blok penyetelan untuk tiap opsi koreksi tahap 5, dari tabel tahap 4 yang sudah ada (tanpa isian baru).
Sama persis dengan potongan tahap 5 di adu_versi.penyetelan."""
import sys, json, os
import pandas as pd
sys.path.insert(0, sys.argv[1])
import adu_versi as AV, adu_metode as AM
out = sys.argv[2]
AV.D = pd.read_pickle(os.path.join(out, 'data_beras.pkl')); AV.P = AM.profil_hapus(AV.D)
st = json.load(open(os.path.join(out, 'status.json')))
df4, p, pstar = pd.read_pickle(os.path.join(out, 'tahap4_penuh.pkl')), st['penggabung'], st['pstar']
x = df4[df4.cfg == p]; cal, ev = x[x.t <= 11], x[x.t >= 12]
opsi = {'tanpa': ev.assign(cfg='tanpa'),
        'konformal': AV.terapkan_koreksi(ev, AV.param_koreksi(cal, bias=False), label='konformal'),
        'konformal+bias': AV.terapkan_koreksi(ev, AV.param_koreksi(cal, bias=True), label='konformal+bias'),
        'konformal+bias+halus': AV.terapkan_koreksi(ev, AV.param_koreksi(cal, bias=True), halus=True, label='konformal+bias+halus')}
df5 = pd.concat(list(opsi.values()) + [df4[df4.cfg.isin(AV.PEMBANDING) & (df4.t >= 12)]])
pd.set_option('display.width', 250)
print(AV.peringkat(df5).round(6).to_string())
for k in opsi:
    G = [dict(AV.gerbang(df5, k, pstar, tk), arah=AV.arah(df5, k, tk)) for tk in AV.TINGKAT]
    g = pd.DataFrame(G)
    g.insert(0, 'koreksi', k)
    print('==', k); print(g.drop(columns='koreksi').T.to_string())
    g.to_csv(os.path.join(out, 'gerbang_opsi5.csv'), mode='a', header=not os.path.exists(os.path.join(out, 'gerbang_opsi5.csv')), index=False)
m, lo, hi = AV.selisih_bulan(df5, 'konformal', 'konformal+bias', AV.UTAMA); print('konformal - konformal+bias:', m, lo, hi)
