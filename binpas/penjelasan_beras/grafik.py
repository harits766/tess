import sys, json, importlib.util, lzma
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

W, T, REPO = sys.argv[1], sys.argv[2], sys.argv[3]
G = f'{W}/grafik'
A = json.load(open(f'{W}/angka.json'))
PERM, TINTA, TINTA2, REDUP, GRID, SUMBU = '#fcfcfb', '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7'
BIRU, BIRU_M, ORANYE, AQUA, ABU = '#2a78d6', '#9ec5f4', '#eb6834', '#1baf7a', '#c3c2b7'
plt.rcParams.update({'figure.facecolor': PERM, 'axes.facecolor': PERM, 'savefig.facecolor': PERM, 'font.size': 10,
    'text.color': TINTA, 'axes.labelcolor': TINTA2, 'xtick.color': TINTA2, 'ytick.color': TINTA2, 'axes.edgecolor': SUMBU,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.titlesize': 11, 'axes.titleweight': 'bold',
    'axes.titlelocation': 'left', 'xtick.major.size': 0, 'ytick.major.size': 0, 'legend.frameon': False})
BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
def nmprov(s):
    return s.title().replace('Dki', 'DKI').replace('Daerah Istimewa Yogyakarta', 'DI Yogyakarta')
def idn(x, d=1):
    s = f'{x:,.{d}f}'
    return s.replace(',', '_').replace('.', ',').replace('_', '.')
def simpan(fig, nama):
    fig.savefig(f'{G}/{nama}.png', dpi=200, bbox_inches='tight', pad_inches=0.12)
    plt.close(fig)
def grid(ax, sb='y'):
    (ax.yaxis if sb == 'y' else ax.xaxis).grid(True, color=GRID, lw=1); ax.set_axisbelow(True)
def label_bulan(ax, per, tiap=3):
    ix = [i for i, p in enumerate(per) if int(p[5:]) in (1, 4, 7, 10)] if tiap == 3 else list(range(0, len(per), tiap))
    ax.set_xticks(ix); ax.set_xticklabels([f"{BLN[int(per[i][5:]) - 1]}\n{per[i][:4]}" if per[i][5:] == '01' or i == ix[0] else BLN[int(per[i][5:]) - 1] for i in ix])

def kotak(ax, x, y, w, h, t, fc='white', ec=TINTA, fs=9.5, bold=False, ls='-'):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0,rounding_size=0.12', fc=fc, ec=ec, lw=1.1, ls=ls))
    ax.text(x, y, t, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', linespacing=1.3)
def panah(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='-|>', lw=1.1, color=TINTA, mutation_scale=10, shrinkA=0, shrinkB=0))

# ---------------------------------------------------------------- G01 peta besar
fig, ax = plt.subplots(figsize=(9.6, 6.0)); ax.set_xlim(0, 12); ax.set_ylim(1.1, 8.2); ax.axis('off')
kotak(ax, 6, 7.6, 9.0, 0.95, 'MASALAH: Kemendag punya laporan distribusi beras (INATRADE),\ntapi pelapornya sedikit, laporannya bolong, dan tidak ada angka stok resmi terbaru', fc='#f0efec', bold=True)
xs = [2.1, 6, 9.9]
tanya = ['Pertanyaan 1\nLaporan yang bolong\nbisa ditambal dengan\ncara apa yang paling tepat?',
         'Pertanyaan 2\nBerapa stok beras\nsebenarnya per provinsi\ntiap bulan?',
         'Pertanyaan 3\nApakah jalur kiriman\nantarprovinsi di INATRADE\nsama dengan versi BPS?']
kerja = ['PEKERJAAN 1\nMenambal laporan\n(adu 79 metode,\nuji sekali di 2026)', 'PEKERJAAN 2\nModel stok Bayesian\n(neraca masuk-keluar\nper provinsi)', 'PEKERJAAN 3\nUji keterwakilan\n(cocokkan jalur dengan\nPola Distribusi BPS)']
hasil = ['HASIL\nLolos di tingkat wilayah:\nmeleset ±2%, pembanding ±15%',
         'HASIL\nStok Sep 2026 ±14,2 juta ton\n(kisaran 11,3–18,6)',
         'HASIL\nBerguna sebagai penguat\njalur BPS, tapi tidak\nmewakili asal beras']
for x, a, b, c in zip(xs, tanya, kerja, hasil):
    panah(ax, x, 7.12, x, 6.75)
    kotak(ax, x, 5.95, 3.6, 1.6, a)
    panah(ax, x, 5.15, x, 4.8)
    kotak(ax, x, 4.0, 3.6, 1.6, b, fc='#e8f1fc', ec=BIRU, bold=True)
    panah(ax, x, 3.2, x, 2.85)
    kotak(ax, x, 2.05, 3.6, 1.6, c, fc='white')
simpan(fig, 'g01_peta')

# ---------------------------------------------------------------- G02 pelapor per bulan
N = pd.read_csv(f'{T}/pelapor_per_bulan.csv', index_col=0)
y = N['BERAS'].values; per = list(N.index); x = np.arange(len(per))
fig, ax = plt.subplots(figsize=(9.6, 3.6)); grid(ax)
for b0, b1, nm in ((-0.5, 17.5, 'blok penyetelan'), (17.5, 23.5, 'kalibrasi'), (23.5, 32.5, 'ujian akhir')):
    ax.text((b0 + b1) / 2, 75, nm, ha='center', fontsize=8.5, color=TINTA2)
for b in (17.5, 23.5): ax.axvline(b, color=SUMBU, lw=1)
ax.plot(x, y, color=BIRU, lw=2.2)
ax.plot(x[-1], y[-1], 'o', ms=7, color=BIRU, mec=PERM, mew=2)
ax.annotate(f'{int(y[-1])} perusahaan\n(Sep 2026)', (x[-1], y[-1]), xytext=(-8, -30), textcoords='offset points', ha='right', fontsize=9)
ax.annotate('Okt–Nov 2024: pelapor\nmelonjak (patahan)', (9.5, 30), xytext=(1, 45), fontsize=9, arrowprops=dict(arrowstyle='-', color=REDUP, lw=1))
ax.set_ylim(0, 82); ax.set_xlim(-0.8, 33); label_bulan(ax, per)
ax.set_ylabel('perusahaan yang melapor')
ax.set_title('Jumlah perusahaan beras yang melapor ke INATRADE tiap bulan (termasuk BULOG)')
simpan(fig, 'g02_pelapor')

# ---------------------------------------------------------------- G03 kualitas data
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.4), gridspec_kw=dict(wspace=0.45))
lb = pd.read_csv(f'{T}/lubang.csv').set_index('kom').loc['BERAS']
kat = ['1', '2', '3', '4-6', '7+']; v = [int(lb[k]) for k in kat]
grid(a1); a1.bar(range(5), v, width=0.55, color=BIRU)
for i, n in enumerate(v): a1.text(i, n + 1.5, str(n), ha='center', fontsize=9)
a1.set_xticks(range(5)); a1.set_xticklabels(['1', '2', '3', '4–6', '7+']); a1.set_xlabel('panjang lubang (bulan)')
a1.set_ylim(0, 95); a1.set_title('Panjang laporan bolong di tengah\n(perusahaan masih aktif)', fontsize=10)
I = pd.read_csv(f'{T}/identitas.csv'); r = I[I.iloc[:, 0] == 'BERAS'].iloc[0, 2:6].astype(float).values * 100
lab = ['sama persis', 'beda ≤ 5%', 'beda 5–25%', 'beda > 25%']
grid(a2, 'x'); a2.barh(range(4)[::-1], r, height=0.5, color=[BIRU, BIRU_M, BIRU_M, ORANYE])
for i, val in enumerate(r): a2.text(val + 1.5, 3 - i, f'{idn(val, 0)}%', va='center', fontsize=9)
a2.set_yticks(range(4)[::-1]); a2.set_yticklabels(lab); a2.set_xlim(0, 95); a2.tick_params(axis='y', colors=TINTA)
a2.set_xticks([0, 25, 50, 75]); a2.set_xticklabels(['0%', '25%', '50%', '75%'])
a2.set_title('Stok awal bulan ini vs stok akhir bulan lalu\n(1.187 pasang laporan)', fontsize=10)
simpan(fig, 'g03_kualitas')

# ---------------------------------------------------------------- G04 cakupan
fig, ax = plt.subplots(figsize=(9.6, 2.7))
th = [('2024', 0.008), ('2025', 0.028), ('2026 (Jan–Sep)', 0.025)]
for i, (t, p) in enumerate(th[::-1]):
    ax.barh(i, 1, height=0.42, color='#f0efec', edgecolor=SUMBU, lw=0.8)
    ax.barh(i, p, height=0.42, color=BIRU)
    ax.text(p + 0.012, i, f'{idn(p * 100)}% dari konsumsi beras rumah tangga', va='center', fontsize=9)
ax.set_yticks(range(3)); ax.set_yticklabels([t for t, _ in th[::-1]]); ax.tick_params(axis='y', colors=TINTA)
ax.set_xlim(0, 1); ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
ax.spines['left'].set_visible(False)
ax.set_title('Seberapa besar beras yang disalurkan pelapor INATRADE dibanding konsumsi rumah tangga (Susenas)')
simpan(fig, 'g04_cakupan')

# ---------------------------------------------------------------- G05 ilustrasi simulasi
rng = np.random.default_rng(3)
P, B = 8, 10
ada = np.ones((P, B), bool)
for i, j in [(1, 3), (4, 6), (4, 7), (6, 2)]: ada[i, j] = False
hapus = np.zeros((P, B), bool)
for i, j in [(0, 5), (2, 7), (3, 4), (5, 8), (7, 6), (2, 9), (6, 9)]: hapus[i, j] = True
fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.6), gridspec_kw=dict(wspace=0.12))
judul = ['① Data asli: ada yang bolong', '② Sebagian laporan yang ADA\n    sengaja dihapus', '③ Metode menebak yang dihapus,\n    lalu dicocokkan dengan aslinya']
for k, ax in enumerate(axs):
    for i in range(P):
        for j in range(B):
            if not ada[i, j]: fc, t = '#ffffff', ''
            elif k >= 1 and hapus[i, j]: fc, t = (ORANYE if k == 1 else AQUA), ('?' if k == 1 else '✓')
            else: fc, t = BIRU_M, ''
            ax.add_patch(Rectangle((j, P - 1 - i), 0.92, 0.88, fc=fc, ec=SUMBU if not ada[i, j] else 'none', lw=0.8, ls=':' if not ada[i, j] else '-'))
            if t: ax.text(j + 0.46, P - 1 - i + 0.44, t, ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    ax.set_xlim(-0.1, B); ax.set_ylim(-0.1, P); ax.axis('off'); ax.set_title(judul[k], fontsize=9.5)
    if k == 0:
        for i in range(P): ax.text(-0.3, P - 1 - i + 0.44, f'PT {chr(65 + i)}', ha='right', va='center', fontsize=8, color=TINTA2)
    ax.text(B / 2, -0.55, 'bulan →', ha='center', fontsize=8, color=TINTA2)
fig.legend(handles=[Rectangle((0, 0), 1, 1, fc=BIRU_M), Rectangle((0, 0), 1, 1, fc='white', ec=SUMBU, ls=':'),
                    Rectangle((0, 0), 1, 1, fc=ORANYE), Rectangle((0, 0), 1, 1, fc=AQUA)],
           labels=['laporan ada', 'bolong asli (tidak bisa dinilai)', 'dihapus untuk soal', 'ditebak, nilai aslinya diketahui'],
           loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.1), fontsize=8.5)
simpan(fig, 'g05_simulasi')

# ---------------------------------------------------------------- G06 ilustrasi metode
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw=dict(wspace=0.35))
bl = np.arange(1, 9); ys = np.array([120, 135, 128, np.nan, np.nan, 150, 142, 155])
grid(a1); a1.plot(bl[:3], ys[:3], '-o', color=BIRU, lw=2, ms=6, mec=PERM, mew=1.5); a1.plot(bl[5:], ys[5:], '-o', color=BIRU, lw=2, ms=6, mec=PERM, mew=1.5)
isi = np.interp([4, 5], [3, 6], [128, 150])
a1.plot([3, 4, 5, 6], [128, *isi, 150], '--', color=AQUA, lw=2); a1.plot([4, 5], isi, 'o', color=AQUA, ms=7, mec=PERM, mew=1.5)
a1.annotate('lubang diisi garis lurus\nantara dua laporan tetangga', (4.5, isi.mean()), xytext=(4.4, 100), ha='center', fontsize=8.5,
            arrowprops=dict(arrowstyle='-', color=REDUP, lw=1))
a1.set_ylim(90, 170); a1.set_xlabel('bulan'); a1.set_ylabel('penyaluran (ton)')
a1.set_title('Metode terpilih: interpolasi (1 perusahaan)', fontsize=10)
# P*: rasio
grid(a2)
a2.bar([0], [800], width=0.5, color=BIRU_M); a2.bar([1], [1000], width=0.5, color=ABU); a2.bar([2], [920], width=0.5, color=BIRU)
for i, (v, t) in enumerate([(800, '800'), (1000, '1.000'), (920, '920')]): a2.text(i, v + 25, t, ha='center', fontsize=9)
a2.set_xticks([0, 1, 2]); a2.set_xticklabels(['total yang\nmelapor\n(8 dari 10 PT)', 'P*: dikali 10/8\n(anggap yang hilang\n= rata-rata)', 'total\nsebenarnya'])
a2.set_ylim(0, 1150); a2.set_ylabel('total wilayah (ton)')
a2.set_title('Pembanding P*: total dikali rasio pelapor', fontsize=10)
simpan(fig, 'g06_metode')

# ---------------------------------------------------------------- G07 ilustrasi CRPS
from math import erf
xx = np.linspace(60, 140, 400)
def pdf(m, s): return np.exp(-0.5 * ((xx - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))
def crps(m, s, y):
    z = (y - m) / s; Phi = 0.5 * (1 + erf(z / np.sqrt(2))); phi = np.exp(-z * z / 2) / np.sqrt(2 * np.pi)
    return s * (z * (2 * Phi - 1) + 2 * phi - 1 / np.sqrt(np.pi))
benar = 100
fig, ax = plt.subplots(figsize=(9.6, 3.3)); grid(ax)
for (m, s, c, nm) in [(99, 4, BIRU, 'tebakan A: dekat & yakin'), (92, 6, ORANYE, 'tebakan B: meleset & yakin'), (100, 15, AQUA, 'tebakan C: tepat tapi ragu')]:
    ax.plot(xx, pdf(m, s), color=c, lw=2, label=f'{nm} → CRPS {idn(crps(m, s, benar))}')
    ax.fill_between(xx, pdf(m, s), color=c, alpha=0.08)
ax.axvline(benar, color=TINTA, lw=1.3); ax.text(benar + 0.8, 0.098, 'nilai asli = 100', fontsize=9)
ax.set_yticks([]); ax.set_ylim(0, 0.105); ax.set_xlabel('total yang ditebak (ton)'); ax.spines['left'].set_visible(False)
ax.legend(loc='upper left', fontsize=8.5)
ax.set_title('Cara kerja CRPS: tebakan berupa sebaran, dinilai jarak dan lebarnya (makin kecil makin baik)')
simpan(fig, 'g07_crps')

# ---------------------------------------------------------------- G08 hasil U1
g = pd.read_csv(f'{REPO}/binpas/hasil_adu_beras/gerbang_U1.csv').set_index('tingkat')
nm = {'prov': 'Provinsi\n(7 provinsi)', 'wil': 'Wilayah\n(target utama)', 'nas': 'Nasional'}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw=dict(wspace=0.35))
grid(a1); xk = np.arange(3); w = 0.34
v1 = [g.loc[t, 'mae'] for t in ('prov', 'wil', 'nas')]; v2 = [g.loc[t, 'mae_pembanding'] for t in ('prov', 'wil', 'nas')]
p1 = [(np.exp(v) - 1) * 100 for v in v1]; p2 = [(np.exp(v) - 1) * 100 for v in v2]
a1.bar(xk - w / 2 - 0.02, p1, w, color=BIRU, label='metode terpilih'); a1.bar(xk + w / 2 + 0.02, p2, w, color=ABU, label='pembanding P*')
for i in range(3):
    a1.text(i - w / 2 - 0.02, p1[i] + 0.6, f'{idn(p1[i])}%', ha='center', fontsize=8.5)
    a1.text(i + w / 2 + 0.02, p2[i] + 0.6, f'{idn(p2[i])}%', ha='center', fontsize=8.5)
a1.set_xticks(xk); a1.set_xticklabels([nm[t] for t in ('prov', 'wil', 'nas')]); a1.set_ylim(0, 40)
a1.set_ylabel('meleset (median, %)'); a1.legend(loc='upper right', fontsize=8.5)
a1.set_title('Berapa persen tebakan total meleset', fontsize=10)
grid(a2, 'x')
for i, t in enumerate(('nas', 'wil', 'prov')):
    lo, hi, c = g.loc[t, 'wilson_lo'] * 100, g.loc[t, 'wilson_hi'] * 100, g.loc[t, 'cakupan'] * 100
    a2.plot([lo, hi], [i, i], color=BIRU, lw=2); a2.plot(c, i, 'o', color=BIRU, ms=8, mec=PERM, mew=2)
    a2.text(c, i + 0.22, f'{idn(c)}%', ha='center', fontsize=8.5)
a2.axvline(90, color=TINTA2, lw=1); a2.text(90, 2.55, 'sasaran 90%', ha='center', fontsize=8.5, color=TINTA2)
a2.axvline(80, color=SUMBU, lw=1); a2.text(80, 2.55, 'lantai 80%', ha='center', fontsize=8.5, color=TINTA2)
a2.set_yticks(range(3)); a2.set_yticklabels([nm[t].replace('\n', ' ') for t in ('nas', 'wil', 'prov')]); a2.tick_params(axis='y', colors=TINTA)
a2.set_xlim(60, 101); a2.set_ylim(-0.5, 2.8); a2.set_xticks([60, 70, 80, 90, 100]); a2.set_xticklabels(['60%', '70%', '80%', '90%', '100%'])
a2.set_title('Rentang 90%: seberapa sering memuat nilai asli\n(garis = ketidakpastian dari jumlah data)', fontsize=10)
simpan(fig, 'g08_u1')

# ---------------------------------------------------------------- G09 sebaran galat wilayah
U1 = pd.read_csv(lzma.open(f'{REPO}/binpas/hasil_adu_beras/U1_sel.csv.xz'), usecols=['cfg', 'tingkat', 'galat'])
U1 = U1[U1.tingkat == 'wil']
gm, gp = (np.exp(U1[U1.cfg == 'resep'].galat) - 1) * 100, (np.exp(U1[U1.cfg == 'A5'].galat) - 1) * 100
fig, ax = plt.subplots(figsize=(9.6, 3.4)); grid(ax)
bins = np.arange(-60, 61, 2)
ax.hist(np.clip(gp, -59.9, 59.9), bins=bins, color=ABU, label='pembanding P* (data apa adanya + rasio pelapor)', density=True)
ax.hist(np.clip(gm, -59.9, 59.9), bins=bins, color=BIRU, alpha=0.9, label='metode terpilih (interpolasi + konformal)', density=True)
ax.axvline(0, color=TINTA, lw=1)
ax.set_xlabel('selisih tebakan terhadap total asli (%): negatif = kekurangan, positif = kelebihan; nilai di luar ±60% ditumpuk di ujung'); ax.set_yticks([]); ax.spines['left'].set_visible(False)
ax.legend(loc='upper left', fontsize=8.5)
ax.set_title('Sebaran meleset di tingkat wilayah, ujian akhir Jan–Sep 2026 (semua soal × 500 ulangan)')
simpan(fig, 'g09_galat')

# ---------------------------------------------------------------- G10 kenapa interpolasi menang
fig, ax = plt.subplots(figsize=(8.0, 3.0)); grid(ax, 'x')
lab = ['Laporan 1 perusahaan berubah dari bulan ke bulan', 'Tebakan interpolasi untuk 1 perusahaan',
       'Total wilayah, metode terpilih (ujian akhir)', 'Total wilayah, pembanding P* (ujian akhir)']
val = [A['perubahan_bulanan_median_abs'] * 100, A['galat_interp_median_abs'] * 100, p1[1], p2[1]]
col = [ABU, BIRU_M, BIRU, ABU]
ax.barh(range(4)[::-1], val, height=0.5, color=col)
for i, v in enumerate(val): ax.text(v + 0.5, 3 - i, f'±{idn(v)}%', va='center', fontsize=9)
ax.set_yticks(range(4)[::-1]); ax.set_yticklabels(lab); ax.tick_params(axis='y', colors=TINTA); ax.set_xlim(0, 33)
ax.set_xticks([0, 10, 20, 30]); ax.set_xticklabels(['0%', '10%', '20%', '30%'])
ax.set_title('Meleset (median): per perusahaan besar, tapi kecil setelah dijumlah')
simpan(fig, 'g10_kenapa')

# ---------------------------------------------------------------- G11 diagram neraca
fig, ax = plt.subplots(figsize=(9.6, 4.2)); ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis('off')
ax.add_patch(FancyBboxPatch((4.4, 1.3), 3.2, 3.2, boxstyle='round,pad=0,rounding_size=0.15', fc='white', ec=TINTA, lw=1.3))
ax.add_patch(Rectangle((4.45, 1.35), 3.1, 1.9, fc=BIRU_M, ec='none'))
ax.text(6, 3.9, 'STOK provinsi\nbulan ini', ha='center', va='center', fontsize=10.5, fontweight='bold')
ax.text(6, 2.25, '= stok bulan lalu\n+ yang masuk − yang keluar', ha='center', va='center', fontsize=9)
for y_, t in [(4.6, 'Produksi padi (BPS)\n× 0,5762 jadi beras'), (3.0, 'Impor'), (1.4, 'Kiriman dari provinsi lain\n(provinsi kekurangan)')]:
    kotak(ax, 1.9, y_, 3.2, 0.95, t, fc='#e8f1fc', ec=BIRU); panah(ax, 3.5, y_, 4.4, y_ * 0.55 + 1.2)
for y_, t in [(4.6, 'Konsumsi (Susenas × faktor\nhoreka & industri)'), (3.0, 'Selisih tak tercatat\n(susut, dll.)'), (1.4, 'Kiriman ke provinsi lain\n(provinsi surplus)')]:
    kotak(ax, 10.1, y_, 3.2, 0.95, t, fc='#fdeee7', ec=ORANYE); panah(ax, 7.6, y_ * 0.55 + 1.2, 8.5, y_)
ax.text(1.9, 5.55, 'MASUK', ha='center', fontsize=10, fontweight='bold', color=BIRU)
ax.text(10.1, 5.55, 'KELUAR', ha='center', fontsize=10, fontweight='bold', color=ORANYE)
ax.text(6, 0.55, 'Diukur oleh: survei stok (SCBN, SSBAT), stok BULOG, stok pedagang INATRADE, harga beras penggilingan',
        ha='center', fontsize=8.8, color=TINTA2, style='italic')
simpan(fig, 'g11_neraca')

# ---------------------------------------------------------------- data stok
sp = importlib.util.spec_from_file_location('sf', f'{REPO}/beras_stok/stok_beras_satu_file.py'); sf = importlib.util.module_from_spec(sp); sp.loader.exec_module(sf)
H = pd.DataFrame(sf.muat_hasil())
nas = H[(H.skenario == 'dasar') & (H.tingkat == 'nasional')]
tot = nas[nas.komponen == 'total'].set_index('periode').sort_index(); bul = nas[nas.komponen == 'bulog'].set_index('periode').sort_index()
pr = list(tot.index)

# ---------------------------------------------------------------- G12 produksi vs konsumsi + stok
pb = pd.read_csv(f'{W}/bps/produksi_bulanan_ksa.csv'); pb = pb.groupby('periode').padi_gkg_ton.sum() * 0.5762 / 1e6
kons = pd.read_csv(f'{W}/bps/konsumsi_provinsi.csv')
kr = kons[kons.tahun == kons.tahun.max()].konsumsi_rt_ton_bulan.sum() / 1e6
ktot = kr * np.exp(0.3413)
p2 = [p for p in pr if p >= '2025-01']
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9.6, 5.6), sharex=True, gridspec_kw=dict(hspace=0.35))
xi = np.arange(len(p2)); grid(a1)
a1.bar(xi, [pb.get(p, np.nan) for p in p2], width=0.6, color=BIRU, label='produksi beras (BPS)')
a1.axhline(ktot, color=ORANYE, lw=2, label=f'konsumsi total ±{idn(ktot, 2)} juta ton/bulan')
a1.set_ylabel('juta ton / bulan'); a1.set_title('Atas: produksi bulanan vs konsumsi. Bawah: stok total hasil model (nasional)', fontsize=10.5)
a1.legend(loc='upper right', fontsize=8.5, ncol=2, bbox_to_anchor=(1, 1.02)); a1.set_ylim(0, 7)
grid(a2)
t2 = tot.loc[p2]
a2.fill_between(xi, t2.p05, t2.p95, color=BIRU, alpha=0.12, lw=0)
a2.plot(xi, t2['median'], color=BIRU, lw=2.2)
a2.set_ylabel('stok, juta ton'); a2.set_ylim(0, 20)
a2.annotate('panen raya Mar–Apr:\nproduksi > konsumsi → stok naik', (3, t2['median'].iloc[4]), xytext=(4.5, 3.0), fontsize=8.5, arrowprops=dict(arrowstyle='-', color=REDUP))
a2.annotate('akhir tahun: produksi < konsumsi\n→ stok turun', (11, t2['median'].iloc[11]), xytext=(12.2, 3.0), fontsize=8.5, arrowprops=dict(arrowstyle='-', color=REDUP))
label_bulan(a2, p2)
simpan(fig, 'g12_musim')

# ---------------------------------------------------------------- G13 stok nasional + prakiraan
fig, ax = plt.subplots(figsize=(9.6, 3.9)); grid(ax)
xi = np.arange(len(pr))
ax.fill_between(xi, tot.p05, tot.p95, color=BIRU, alpha=0.12, lw=0)
ax.plot(xi, tot['median'], color=BIRU, lw=2.2, label='stok total (median)')
ax.plot(xi, bul['median'], color=ORANYE, lw=2, label='di antaranya BULOG')
fk = [len(pr) - 1, len(pr), len(pr) + 1, len(pr) + 2]
fm = [tot['median'].iloc[-1], 13.6, 12.5, 11.1]; flo = [tot.p05.iloc[-1], 10.7, 9.5, 8.1]; fhi = [tot.p95.iloc[-1], 18.1, 17.0, 15.7]
ax.fill_between(fk, flo, fhi, color=REDUP, alpha=0.12, lw=0); ax.plot(fk, fm, '--', color=REDUP, lw=2, label='prakiraan Okt–Des 2026')
ax.plot(xi[-1], tot['median'].iloc[-1], 'o', color=BIRU, ms=7, mec=PERM, mew=2)
ax.annotate(f"Sep 2026: {idn(tot['median'].iloc[-1])} juta ton\n(kisaran {idn(tot.p05.iloc[-1])}–{idn(tot.p95.iloc[-1])})", (xi[-1], tot['median'].iloc[-1]),
            xytext=(-200, 28), textcoords='offset points', fontsize=8.5, ha='right', arrowprops=dict(arrowstyle='-', color=REDUP))
ax.set_ylim(0, 22); ax.set_xlim(-0.5, len(pr) + 2.5); label_bulan(ax, pr + ['2026-10', '2026-11', '2026-12'])
ax.set_ylabel('juta ton'); ax.legend(loc='upper left', fontsize=8.5, ncol=3)
ax.set_title('Stok beras total nasional, Jan 2024–Sep 2026 (pita = kisaran 90%)')
simpan(fig, 'g13_stok')

# ---------------------------------------------------------------- G14 komposisi + pulau
s9 = nas[nas.periode == '2026-09'].set_index('komponen')
pl = H[(H.skenario == 'dasar') & (H.tingkat == 'pulau') & (H.periode == '2026-09')]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw=dict(wspace=0.7))
km = [('rumah_tangga', 'Rumah tangga'), ('bulog', 'BULOG'), ('pedagang', 'Pedagang'), ('penggilingan', 'Penggilingan'), ('horeka', 'Horeka & industri')]
grid(a1, 'x')
for i, (k, n) in enumerate(km):
    r_ = s9.loc[k]; yy = len(km) - 1 - i
    a1.barh(yy, r_['median'], height=0.5, color=ORANYE if k == 'bulog' else BIRU)
    a1.plot([r_.p05, r_.p95], [yy, yy], color=TINTA2, lw=1)
    a1.text(r_.p95 + 0.2, yy, idn(r_['median'], 2), va='center', fontsize=8.5)
a1.set_yticks(range(len(km))[::-1]); a1.set_yticklabels([n for _, n in km]); a1.tick_params(axis='y', colors=TINTA); a1.set_xlim(0, 14)
a1.set_xlabel('juta ton (garis tipis = kisaran 90%)'); a1.set_title('Siapa yang memegang stok (Sep 2026)', fontsize=10)
grid(a2, 'x')
pt_ = pl[pl.komponen == 'total'].sort_values('median')
for i, r_ in enumerate(pt_.itertuples()):
    a2.barh(i, r_.median, height=0.5, color=BIRU); a2.plot([r_.p05, r_.p95], [i, i], color=TINTA2, lw=1)
    a2.text(r_.p95 + 0.15, i, idn(r_.median, 2), va='center', fontsize=8.5)
a2.set_yticks(range(len(pt_))); a2.set_yticklabels(pt_.wilayah); a2.tick_params(axis='y', colors=TINTA); a2.set_xlim(0, 11)
a2.set_xlabel('juta ton'); a2.set_title('Stok per pulau (Sep 2026)', fontsize=10)
simpan(fig, 'g14_komposisi')

# ---------------------------------------------------------------- G15 survei vs model
V = pd.DataFrame(sf.VALIDASI, columns=['run', 'periode', 'sumber', 'amatan', 'med', 'lo', 'hi', 'dipakai'])
fig, ax = plt.subplots(figsize=(9.6, 3.4)); grid(ax)
lab = {'2022-06': 'SCBN BPS\nJun 2022', '2022-12': 'SSBAT\nDes 2022', '2023-12': 'SSBAT\nDes 2023'}
for i, p in enumerate(['2022-06', '2022-12', '2023-12']):
    am = V[(V.periode == p)].amatan.iloc[0]
    f = V[(V.periode == p) & (V.run == 'fit penuh')].iloc[0]; h = V[(V.periode == p) & (V.run != 'fit penuh')].iloc[0]
    ax.bar(i - 0.27, am, 0.24, color=TINTA2); ax.text(i - 0.27, am + 0.25, idn(am, 2), ha='center', fontsize=8.5)
    ax.bar(i, f.med, 0.24, color=BIRU_M); ax.plot([i, i], [f.lo, f.hi], color=TINTA2, lw=1)
    ax.bar(i + 0.27, h.med, 0.24, color=BIRU if p == '2022-12' else BIRU_M, hatch='' if p == '2022-12' else None)
    ax.plot([i + 0.27, i + 0.27], [h.lo, h.hi], color=TINTA2, lw=1)
    ax.text(i + 0.27, h.hi + 0.25, idn(h.med, 2), ha='center', fontsize=8.5)
ax.set_xticks(range(3)); ax.set_xticklabels([lab[p] for p in ['2022-06', '2022-12', '2023-12']]); ax.set_ylim(0, 13.5)
ax.set_ylabel('juta ton')
ax.legend(handles=[Rectangle((0, 0), 1, 1, fc=TINTA2), Rectangle((0, 0), 1, 1, fc=BIRU_M), Rectangle((0, 0), 1, 1, fc=BIRU)],
          labels=['angka survei', 'tebakan model (semua survei dipakai)', 'tebakan model saat Des 2022 DISEMBUNYIKAN'], loc='upper right', fontsize=8.5)
ax.set_title('Uji model: menebak angka survei stok (garis tipis = kisaran 90%)')
simpan(fig, 'g15_validasi')

# ---------------------------------------------------------------- G16 kepekaan
fig, ax = plt.subplots(figsize=(9.6, 3.3)); grid(ax, 'x')
sk = [('Dasar: stok swasta ≥ 0 per pulau', 14.2, 11.3, 18.6, BIRU), ('Aturan ≥ 0 hanya nasional', 14.2, 11.4, 19.1, BIRU_M),
      ('Aturan ≥ 0 per provinsi', 16.8, 14.0, 21.3, BIRU_M), ('Tanpa data INATRADE', 15.1, None, None, ABU),
      ('INATRADE baris dalam provinsi saja', 13.4, None, None, ABU), ('INATRADE baris antarprovinsi saja', 16.4, None, None, ABU)]
for i, (n, m, lo, hi, c) in enumerate(sk):
    yy = len(sk) - 1 - i
    if lo: ax.plot([lo, hi], [yy, yy], color=c, lw=2)
    ax.plot(m, yy, 'o', color=c, ms=9, mec=PERM, mew=2); ax.text(m, yy + 0.25, idn(m), ha='center', fontsize=8.5)
ax.set_yticks(range(len(sk))[::-1]); ax.set_yticklabels([s[0] for s in sk]); ax.tick_params(axis='y', colors=TINTA)
ax.set_xlim(8, 23); ax.set_ylim(-0.6, len(sk) - 0.2); ax.set_xlabel('stok nasional akhir Sep 2026 (juta ton); garis = kisaran 90%')
ax.set_title('Kalau asumsinya diganti, angkanya berubah sejauh apa?')
simpan(fig, 'g16_kepekaan')

# ---------------------------------------------------------------- G17 U2 AP
fig, ax = plt.subplots(figsize=(9.6, 2.9)); grid(ax, 'x')
ap = [('acak (tebak asal)', 0.093, ABU), ('INATRADE saja', 0.329, ABU), ('BPS 2024 apa adanya', 0.480, ABU), ('Gabungan BPS 2024 + INATRADE', 0.563, BIRU)]
for i, (n, v, c) in enumerate(ap):
    ax.barh(i, v, height=0.5, color=c); ax.text(v + 0.01, i, idn(v, 3), va='center', fontsize=9)
ax.set_yticks(range(4)); ax.set_yticklabels([a[0] for a in ap]); ax.tick_params(axis='y', colors=TINTA); ax.set_xlim(0, 0.68)
ax.set_xlabel('average precision (0 = buruk, 1 = sempurna)')
ax.set_title('Siapa paling tepat menebak jalur beras antarprovinsi versi BPS 2025?')
simpan(fig, 'g17_ap')

# ---------------------------------------------------------------- G18 U2 bertahan
kt = A['u2_kategori']
urut = ['ada di BPS 2024 dan INATRADE', 'hanya di BPS 2024', 'hanya di INATRADE', 'tidak ada di keduanya']
fig, ax = plt.subplots(figsize=(9.6, 2.9)); grid(ax, 'x')
for i, k in enumerate(urut):
    v = kt[k]['porsi'] * 100; yy = 3 - i
    ax.barh(yy, v, height=0.5, color=BIRU if i == 0 else BIRU_M if i < 3 else ABU)
    ax.text(v + 1, yy, f"{idn(v, 0)}%  ({kt[k]['muncul_2025']} dari {kt[k]['n']} pasangan)", va='center', fontsize=9)
ax.set_yticks(range(4)[::-1]); ax.set_yticklabels(urut); ax.tick_params(axis='y', colors=TINTA); ax.set_xlim(0, 100)
ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
ax.set_title('Pasangan provinsi yang ternyata jadi jalur di BPS 2025, menurut kelompoknya')
simpan(fig, 'g18_bertahan')

# ---------------------------------------------------------------- G19 asal
U2 = pd.read_csv(f'{W}/u2_asal.csv', index_col=0)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.7), gridspec_kw=dict(wspace=0.75))
top = U2.sort_values('vol_inatrade', ascending=False)
top = top[top.vol_inatrade > 0]
sh = top.vol_inatrade / top.vol_inatrade.sum() * 100
grid(a1, 'x')
a1.barh(range(len(sh))[::-1], sh.values, height=0.55, color=BIRU)
for i, v in enumerate(sh.values): a1.text(v + 1, len(sh) - 1 - i, f'{idn(v)}%', va='center', fontsize=8)
a1.set_yticks(range(len(sh))[::-1]); a1.set_yticklabels([nmprov(s) for s in sh.index], fontsize=8); a1.tick_params(axis='y', colors=TINTA); a1.set_xlim(0, 85)
a1.set_title('INATRADE: pangsa volume kiriman\nantarprovinsi menurut provinsi asal', fontsize=10)
b25 = U2.asal_bps2025.sort_values(ascending=False).head(10)
grid(a2, 'x')
a2.barh(range(10)[::-1], b25.values, height=0.55, color=[BIRU if U2.loc[p, 'vol_inatrade'] > 0 else ABU for p in b25.index])
for i, v in enumerate(b25.values): a2.text(v + 0.3, 9 - i, str(int(v)), va='center', fontsize=8)
a2.set_yticks(range(10)[::-1]); a2.set_yticklabels([nmprov(s) for s in b25.index], fontsize=8); a2.tick_params(axis='y', colors=TINTA); a2.set_xlim(0, 23)
a2.set_title('BPS 2025: provinsi yang paling banyak\ndisebut sebagai asal (10 teratas)', fontsize=10)
a2.set_xlabel('abu-abu = tidak punya kiriman antarprovinsi di INATRADE', fontsize=8)
simpan(fig, 'g19_asal')
print('selesai')
