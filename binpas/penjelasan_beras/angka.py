import sys, json, numpy as np, pandas as pd
sys.path.insert(0, 'binpas')
import u2_beras as U, tahap0 as T0
W, T, X = sys.argv[1], sys.argv[2], sys.argv[3]
out = {}
# --- laporan beras: perubahan bulanan per perusahaan dan galat interpolasi lubang buatan 1 bulan
L = pd.read_csv(f'{T}/laporan.csv', dtype={'kode': str})
L = L[(L.kom == 'BERAS') & (~L.bulog)]
F = L.groupby(['kode', 'per']).peny.sum().unstack()
cols = [str(p) for p in pd.period_range('2024-01', '2026-09', freq='M')]
F = F.reindex(columns=cols)
lg = np.log(F.where(F > 0))
d = (lg.diff(axis=1)).stack()
out['perubahan_bulanan_median_abs'] = float(np.exp(d.abs().median()) - 1)
out['perubahan_bulanan_p90_abs'] = float(np.exp(d.abs().quantile(0.9)) - 1)
out['n_pasangan_bulanan'] = int(len(d))
# galat interpolasi pada lubang buatan 1 bulan: y_t vs rata-rata tetangga
a, b, c = F.values[:, :-2], F.values[:, 1:-1], F.values[:, 2:]
m = (a > 0) & (b > 0) & (c > 0)
e_int = np.log(b[m]) - np.log((a[m] + c[m]) / 2)
e_last = np.log(b[m]) - np.log(a[m])
out['galat_interp_median_abs'] = float(np.exp(np.median(np.abs(e_int))) - 1)
out['galat_lapor_terakhir_median_abs'] = float(np.exp(np.median(np.abs(e_last))) - 1)
out['n_interp'] = int(m.sum())
# histogram perubahan bulanan (untuk grafik)
np.save(f'{W}/perubahan_bulanan.npy', d.values)
np.save(f'{W}/galat_interp.npy', e_int)
# --- U2: rincian tautan
p24, L24 = U.tautan_bps('binpas/data_publik/poldis_beras_2024_mitra.csv')
p25, L25 = U.tautan_bps('binpas/data_publik/poldis_beras_2025_mitra.csv')
prov = sorted(set(p24) & set(p25))
R = U.inatrade(X)
pas = [(a_, b_) for a_ in prov for b_ in prov if a_ != b_]
ina = set(zip(R.prov, R.tuj)) & set(pas)
L24p, L25p = L24 & set(pas), L25 & set(pas)
kat = {'ada di BPS 2024 dan INATRADE': L24p & ina, 'hanya di BPS 2024': L24p - ina, 'hanya di INATRADE': ina - L24p,
       'tidak ada di keduanya': set(pas) - L24p - ina}
out['u2_kategori'] = {k: dict(n=len(v), muncul_2025=len(v & L25p), porsi=len(v & L25p) / len(v)) for k, v in kat.items()}
Rr = R[R.prov.isin(prov) & R.tuj.isin(prov)]
vol = Rr.groupby('prov').vol.sum().reindex(prov).fillna(0)
deg25 = pd.Series({p: sum(1 for (a_, b_) in L25p if a_ == p) for p in prov})
deg24 = pd.Series({p: sum(1 for (a_, b_) in L24p if a_ == p) for p in prov})
pd.DataFrame(dict(vol_inatrade=vol, asal_bps2025=deg25, asal_bps2024=deg24)).to_csv(f'{W}/u2_asal.csv')
out['u2_spearman'] = float(np.corrcoef(vol.rank(), deg25.rank())[0, 1])
json.dump(out, open(f'{W}/angka.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
