import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

W = 16.0
fig, ax = plt.subplots(figsize=(8.2, 11.0))
ax.set_xlim(0, W); ax.set_ylim(0, 22); ax.axis('off')
fig.canvas.draw()
R = fig.canvas.get_renderer()
LW, FS, PX, PY, GAP = 1.1, 7.2, 0.35, 0.22, 0.45

def ukur(t):
    tx = ax.text(0, 0, t, fontsize=FS, fontweight='bold', linespacing=1.3, ha='center', va='center')
    bb = tx.get_window_extent(R).transformed(ax.transData.inverted())
    tx.remove()
    return bb.width, bb.height

def ukuran(t, jenis, wmin=0):
    w, h = ukur(t)
    ex = 0.9 if jenis == 'io' else (0.6 if jenis == 'terminal' else 0)
    return max(w + 2 * PX + ex, wmin), h + 2 * PY

def gambar(x, ytop, w, h, t, jenis):
    y = ytop - h / 2
    if jenis == 'terminal':
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0,rounding_size=%f' % (h / 2), fc='white', ec='black', lw=LW))
    elif jenis == 'io':
        s = 0.3
        ax.add_patch(Polygon([(x - w / 2 + s, y + h / 2), (x + w / 2 + s, y + h / 2), (x + w / 2 - s, y - h / 2), (x - w / 2 - s, y - h / 2)], closed=True, fc='white', ec='black', lw=LW))
    else:
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='square,pad=0', fc='white', ec='black', lw=LW))
    ax.text(x, y, t, ha='center', va='center', fontsize=FS, fontweight='bold', linespacing=1.3)
    return ytop - h

def panah(x, y1, y2):
    ax.annotate('', xy=(x, y2), xytext=(x, y1), arrowprops=dict(arrowstyle='-|>', lw=LW, color='black', mutation_scale=9, shrinkA=0, shrinkB=0))

def garis(pts):
    xs, ys = zip(*pts); ax.plot(xs, ys, color='black', lw=LW, solid_capstyle='butt')

def tumpuk(x, ytop, isi, wmin=0):
    """isi: list (teks, jenis). Mengembalikan y bawah kotak terakhir."""
    y = ytop
    for i, (t, j) in enumerate(isi):
        w, h = ukuran(t, j, wmin)
        if i:
            panah(x, y, y - GAP); y -= GAP
        y = gambar(x, y, w, h, t, j)
    return y

cx = W / 2
atas = [('Mulai', 'terminal'),
        ('Pengumpulan Data\n(INATRADE Kemendag, WebAPI BPS, survei stok & angka publik)', 'proses'),
        ('Eksplorasi Data (Tahap 0)\n(kehadiran pelapor, laporan bolong, identitas stok,\nkonsentrasi, cakupan volume)', 'proses'),
        ('Preprocessing Data\n(koreksi satuan kg → ton, pemisahan BULOG, penggabungan kepala laporan,\nharmonisasi provinsi, penyusunan panel perusahaan × bulan)', 'proses'),
        ('Pembagian Blok Waktu\n(penyetelan Jan 2024–Jun 2025, kalibrasi Jul–Des 2025, ujian Jan–Sep 2026)', 'proses'),
        ('Pengembangan Model', 'proses')]
y = tumpuk(cx, 21.8, atas, wmin=3.4)

xs = [2.75, 8.0, 13.25]
cab = [
    [('Penguatan Data INATRADE\n(isian laporan bolong)', 'proses'),
     ('Adu Versi Bertahap\n79 kombinasi metode isian\n(interpolasi, regresi panel,\nQRF, CatBoost, MRP)\n50 → 200 → 500 ulangan', 'proses'),
     ('Koreksi Akhir Konformal\n(kalibrasi rentang 90%)', 'proses'),
     ('Resep Isian Terbaik', 'io')],
    [('Model Stok Bayesian\nState-Space per Provinsi', 'proses'),
     ('Neraca Bulanan + Pengukuran\n(produksi, konsumsi, arus,\nBULOG, INATRADE, survei stok;\nbias per sumber)', 'proses'),
     ('Inferensi Posterior\n(PyMC + nutpie, 4 rantai)', 'proses'),
     ('Estimasi & Prakiraan Stok', 'io')],
    [('Keterwakilan Jalur Distribusi\n(INATRADE vs BPS)', 'proses'),
     ('Ekstraksi Tautan Antarprovinsi\n(Pola Distribusi BPS\n2024 & 2025; arus antar-\nprovinsi INATRADE)', 'proses'),
     ('Skor Tautan\n(INATRADE, BPS 2024, gabungan)', 'proses'),
     ('Peta Jalur Gabungan', 'io')],
]
WC = 4.75
cab_y = y - 0.55
garis([(cx, y), (cx, cab_y)]); garis([(xs[0], cab_y), (xs[2], cab_y)])
# samakan tinggi tiap baris antarcabang
tinggi = [max(ukuran(c[k][0], c[k][1], WC)[1] for c in cab) for k in range(4)]
bawah = []
for x, isi in zip(xs, cab):
    panah(x, cab_y, cab_y - GAP)
    yy = cab_y - GAP
    for k, (t, j) in enumerate(isi):
        if k:
            panah(x, yy, yy - GAP); yy -= GAP
        yy = gambar(x, yy, WC if j != 'io' else WC - 0.5, tinggi[k], t, j)
    bawah.append(yy)
gab_y = min(bawah) - 0.5
for x, b in zip(xs, bawah):
    garis([(x, b), (x, gab_y)])
garis([(xs[0], gab_y), (xs[2], gab_y)])
panah(cx, gab_y, gab_y - GAP)
akhir = [('Evaluasi Kinerja\nU1: CRPS, MAE, bias, cakupan rentang 90%, arah perubahan (blok ujian)\nValidasi stok: survei SSBAT Des 2022 disembunyikan\nU2: average precision, korelasi peringkat', 'proses'),
         ('Pemeriksaan Gerbang yang Dikunci Sebelum Ujian\n(lolos / gagal / belum bisa diputuskan)', 'proses'),
         ('Interpretasi Hasil & Penentuan Status\nper Tingkat (provinsi, wilayah, nasional)', 'io'),
         ('Selesai', 'terminal')]
yb = tumpuk(cx, gab_y - GAP, akhir, wmin=3.4)
ax.set_ylim(yb - 0.2, 22.0)
fig.savefig('diagram_alir.png', dpi=220, bbox_inches='tight', facecolor='white', pad_inches=0.08)
print('ok', round(yb, 2))
