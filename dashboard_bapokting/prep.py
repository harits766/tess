"""Ringkasan data pelaporan distribusi bapokting untuk dashboard.
Input : Data_Publish_FINAL.xlsx (sheet ALL)   Output: 7 CSV di folder keluaran.
Pemakaian: python3 prep.py <input.xlsx|pickle> <folder_keluaran>
"""
import sys, pandas as pd, numpy as np
src, out = sys.argv[1], sys.argv[2]
df = pd.read_pickle(src) if src.endswith('.pkl') else pd.read_excel(src, sheet_name='ALL')
df = df.dropna(subset=['Perusahaan']).copy()          # 159 baris tanpa kode perusahaan dibuang
df['kode'] = df['Perusahaan'].astype(int).map('{:05d}'.format)
df['pm'] = pd.to_datetime(df['Tanggal Distribusi'], format='%d/%m/%Y').dt.to_period('M')
strip = lambda s: s.str.replace('Provinsi ', '', regex=False)
df['prov'] = strip(df['Provinsi Perusahaan'])
df['kab'] = df['Kabupaten / Kota']
df['kom'] = df['Jenis Komoditi'].replace({'Kedelai bahan baku tempe dan tahu': 'Kedelai',
        'Ikan Segar (Bandeng, kembung dan tongkol/tuna/cakalang)': 'Ikan Segar'})

# periode acuan = periode lengkap terakhir (periode paling baru yang pelapornya >= 50% periode sebelumnya)
per = df.groupby('pm').kode.nunique().sort_index()
ref = per.index[-1]
while per[ref] < 0.5 * per[ref - 1]: ref -= 1
aktif_win = [ref - 2, ref - 1, ref]
bln = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']
lab = lambda p: f"{bln[p.month-1]} {p.year}"
iso = lambda p: f"{p.year}-{p.month:02d}"

# ---------- 1. perusahaan ----------
g = df.groupby('kode')
kabmode = g.kab.agg(lambda s: s.value_counts().index[0])
P = pd.DataFrame({'provinsi': g.prov.first(), 'kab_kota': kabmode,
    'komoditas': g.kom.agg(lambda s: '; '.join(sorted(s.unique()))),
    'periode_pertama': g.pm.min(), 'periode_terakhir': g.pm.max(), 'jumlah_periode_lapor': g.pm.nunique()})
P['bulan_tanpa_laporan'] = (ref.ordinal - P.periode_terakhir.map(lambda p: p.ordinal)).clip(lower=0)
def kel(n):
    if n == 0: return 'Lapor periode terakhir'
    if n <= 3: return f'{n} bulan'
    if n <= 6: return '4-6 bulan'
    if n <= 12: return '7-12 bulan'
    return 'Tidak aktif (>12 bulan)'
P['kelompok'] = P.bulan_tanpa_laporan.map(kel)
last12 = [ref - i for i in range(11, -1, -1)]
has = df.groupby(['kode', 'pm']).size().unstack(fill_value=0).reindex(columns=last12, fill_value=0) > 0
P['riwayat_12_bulan'] = has.astype(int).astype(str).agg(''.join, axis=1).reindex(P.index)
P['lapor_12_bulan'] = has.sum(axis=1).reindex(P.index)
P['aktif_3_bulan'] = (P.periode_terakhir >= aktif_win[0]).astype(int)
for c in ('periode_pertama', 'periode_terakhir'): P[c] = P[c].map(iso)
P = P.reset_index().sort_values(['bulan_tanpa_laporan', 'kode'])
P.to_csv(f'{out}/perusahaan.csv', index=False)

# ---------- 2. bulanan ----------
sets = df.groupby('pm').kode.agg(set).sort_index()
first = df.groupby('kode').pm.min()
rows = []
for p in pd.period_range(sets.index[0], sets.index[-1], freq='M'):
    cur = sets.get(p, set()); prev = sets.get(p - 1, set())
    hil = len(prev - cur)
    rows.append({'periode': iso(p), 'label': lab(p), 'pelapor': len(cur), 'pelapor_baru': int((first == p).sum()),
        'lapor_lagi': len(cur & prev), 'berhenti_lapor': hil,
        'persen_berhenti': round(100 * hil / len(prev), 1) if prev else '', 'lengkap': int(p <= ref)})
pd.DataFrame(rows).to_csv(f'{out}/bulanan.csv', index=False)

# ---------- 3. provinsi (38, termasuk yang belum punya pelapor) ----------
GRID = {  # nama: (kode ISO, kolom, baris) -> peta petak
 'Aceh':('AC',0,0),'Sumatera Utara':('SU',0,1),'Riau':('RI',1,1),'Kepulauan Riau':('KR',2,1),
 'Sumatera Barat':('SB',0,2),'Jambi':('JA',1,2),'Kepulauan Bangka Belitung':('BB',2,2),
 'Bengkulu':('BE',0,3),'Sumatera Selatan':('SS',1,3),'Lampung':('LA',1,4),
 'Banten':('BT',2,5),'DKI Jakarta':('JK',3,5),'Jawa Barat':('JB',4,5),'Jawa Tengah':('JT',5,5),
 'Daerah Istimewa Yogyakarta':('YO',5,6),'Jawa Timur':('JI',6,5),'Bali':('BA',7,5),
 'Nusa Tenggara Barat':('NB',8,5),'Nusa Tenggara Timur':('NT',9,5),
 'Kalimantan Barat':('KB',4,2),'Kalimantan Tengah':('KT',5,2),'Kalimantan Timur':('KI',6,2),
 'Kalimantan Utara':('KU',6,1),'Kalimantan Selatan':('KS',5,3),
 'Gorontalo':('GO',8,1),'Sulawesi Utara':('SA',9,1),'Sulawesi Tengah':('ST',8,2),
 'Sulawesi Barat':('SR',8,3),'Sulawesi Tenggara':('SG',9,3),'Sulawesi Selatan':('SN',8,4),
 'Maluku Utara':('MU',11,1),'Maluku':('MA',11,3),
 'Papua Barat Daya':('PD',12,2),'Papua Barat':('PB',13,2),'Papua':('PA',14,2),
 'Papua Tengah':('PT',13,3),'Papua Pegunungan':('PE',14,3),'Papua Selatan':('PS',14,4)}
assert set(P.provinsi) <= set(GRID), set(P.provinsi) - set(GRID)
def agg_daerah(key):
    a = P.groupby(key)
    return pd.DataFrame({'pernah_lapor': a.size(), 'pelapor_aktif': a.aktif_3_bulan.sum(),
        'lapor_periode_terakhir': a.bulan_tanpa_laporan.agg(lambda s: int((s == 0).sum())),
        'perlu_follow_up': a.bulan_tanpa_laporan.agg(lambda s: int(((s >= 1) & (s <= 12)).sum())),
        'tidak_aktif': a.bulan_tanpa_laporan.agg(lambda s: int((s > 12).sum()))})
V = agg_daerah('provinsi').reindex(list(GRID)).fillna(0).astype(int)
V.insert(0, 'kode_provinsi', [GRID[p][0] for p in V.index]); V['kolom'] = [GRID[p][1] for p in V.index]; V['baris'] = [GRID[p][2] for p in V.index]
V.index.name = 'provinsi'; V.reset_index().to_csv(f'{out}/provinsi.csv', index=False)

# ---------- 4. kab/kota ----------
K = agg_daerah(['provinsi', 'kab_kota']).reset_index()
K = K[['kab_kota', 'provinsi', 'pernah_lapor', 'pelapor_aktif', 'lapor_periode_terakhir', 'perlu_follow_up', 'tidak_aktif']]
K.sort_values(['provinsi', 'pelapor_aktif', 'kab_kota'], ascending=[True, False, True]).to_csv(f'{out}/kabkota.csv', index=False)

# ---------- 5. dominasi volume per provinsi x komoditas (3 periode lengkap terakhir) ----------
w = df[df.pm.isin(aktif_win)]
hdr = w.drop_duplicates(['kode', 'pm', 'kom', 'Sub Komoditi', 'Pengadaan', 'Penyaluran', 'Stok Awal', 'Stok Akhir'])  # angka induk berulang di tiap baris rincian
v = hdr.groupby(['prov', 'kom', 'kode']).Penyaluran.sum().clip(lower=0).reset_index()
sat = w.groupby('kom').Satuan.agg(lambda s: s.value_counts().index[0])
rows = []
for (pr, km), t in v.groupby(['prov', 'kom']):
    t = t.sort_values('Penyaluran', ascending=False); tot = t.Penyaluran.sum()
    if tot <= 0: continue
    rows.append({'kunci': f'{pr} | {km}', 'provinsi': pr, 'komoditas': km, 'satuan': sat[km], 'jumlah_pelapor': len(t),
        'total_penyaluran': round(tot, 2), 'perusahaan_terbesar': t.kode.iloc[0], 'penyaluran_terbesar': round(t.Penyaluran.iloc[0], 2),
        'pangsa_terbesar': round(100 * t.Penyaluran.iloc[0] / tot, 1),
        'pangsa_kedua': round(100 * t.Penyaluran.iloc[1] / tot, 1) if len(t) > 1 else 0})
D = pd.DataFrame(rows).sort_values(['pangsa_terbesar', 'total_penyaluran'], ascending=False); D.to_csv(f'{out}/dominasi.csv', index=False)

# ---------- 6. komoditas ----------
ka = w.groupby('kom').kode.nunique(); kr = df[df.pm == ref].groupby('kom').kode.nunique(); ke = df.groupby('kom').kode.nunique()
C = pd.DataFrame({'pernah_lapor': ke, 'pelapor_aktif': ka, 'lapor_periode_terakhir': kr}).fillna(0).astype(int)
C.index.name = 'komoditas'; C.sort_values('pelapor_aktif', ascending=False).reset_index().to_csv(f'{out}/komoditas.csv', index=False)

# ---------- 7. kohort tahun pertama lapor x tahun laporan ----------
df['th'] = df.pm.dt.year; fy = first.dt.year
rows = []
for y0 in sorted(fy.unique()):
    koh = set(fy[fy == y0].index)
    for y in sorted(df.th.unique()):
        if y < y0: continue
        n = df[(df.th == y) & df.kode.isin(koh)].kode.nunique()
        rows.append({'kunci': f'{y0}-{y}', 'tahun_pertama_lapor': y0, 'tahun_laporan': y, 'perusahaan_kohort': len(koh),
                     'masih_lapor': n, 'persen_masih_lapor': round(100 * n / len(koh), 1)})
pd.DataFrame(rows).to_csv(f'{out}/kohort.csv', index=False)

# ---------- ringkas ----------
print('acuan', ref, 'jendela aktif', [iso(p) for p in aktif_win], 'periode terakhir di data', per.index[-1], per.iloc[-1])
print(P.kelompok.value_counts().to_string())
print('prov aktif=0:', V[V.pelapor_aktif == 0].index.tolist()); print('prov aktif=1:', V[V.pelapor_aktif == 1].index.tolist())
print('prov aktif>=5:', V[V.pelapor_aktif >= 5].index.tolist())
print('dominasi baris', len(D), 'tunggal', (D.jumlah_pelapor == 1).sum(), '>=50% & >1', ((D.jumlah_pelapor > 1) & (D.pangsa_terbesar >= 50)).sum())
print(D.head(6).to_string()); print(C.to_string())
