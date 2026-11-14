"""Ekstrak daftar provinsi mitra dari KALIMAT di halaman "PENDISTRIBUSIAN DARI/KE LUAR PROVINSI" (edisi 2025).

Pakai:  python -I binpas/poldis_mitra_narasi.py <pdf> <keluaran.csv>

Edisi 2025 menulis daftar mitra sebagai kalimat, mis. "Provinsi X melakukan pembelian beras dari 3 provinsi lain yaitu
Provinsi A, B, dan C ... penjualan beras ke 1 provinsi lain yaitu Provinsi D". Jumlah yang tertulis (3, 1) dipakai
untuk memeriksa hasil ekstraksi. Keluaran berformat sama dengan poldis_mitra.py, ditambah kolom jumlah tertulis.
"""
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poldis_mitra as PM  # noqa: E402

import pdfplumber  # noqa: E402

CAP = {'ht', 'tp', 's:', 's', '://', '//w', 'w', '.b', 'ps', '.g', 'o', 'o.', 'id', '.id', 'ww', '//ww'}


def blok_teks(page):
    """Blok teks di bawah judul "PENDISTRIBUSIAN DARI/KE LUAR PROVINSI": kolom kiri dan kanan dipisah menurut posisi x."""
    words = [w for w in page.extract_words() if w['text'] not in CAP]
    hd = [w for w in words if w['text'].upper().startswith('PENDISTRIBUSIAN')]
    if not hd or 'DARI/KE LUAR PROVINSI' not in ' '.join(w['text'] for w in words).upper():
        return None
    atas = max(w['bottom'] for w in hd)
    bawah = [w for w in words if w['top'] > atas and w['top'] < page.height - 45]
    seg = []
    for b in PM.baris(bawah):
        cur = [b[0]]
        for w in b[1:]:
            if w['x0'] - cur[-1]['x1'] > 40:
                seg.append(cur)
                cur = [w]
            else:
                cur.append(w)
        seg.append(cur)
    blok = []
    for sg in sorted(seg, key=lambda g: g[0]['top']):
        x0, x1 = sg[0]['x0'], sg[-1]['x1']
        for bl in blok:
            if min(x1, bl['x1']) - max(x0, bl['x0']) > 0:
                bl['x0'], bl['x1'] = min(x0, bl['x0']), max(x1, bl['x1'])
                bl['teks'].append(' '.join(w['text'] for w in sg))
                break
        else:
            blok.append(dict(x0=x0, x1=x1, teks=[' '.join(w['text'] for w in sg)]))
    return [' '.join(bl['teks']) for bl in blok]


def bersih(t):
    return re.sub(r'[.,;:()]', ' ', t.replace('D.I.', 'DI').replace('D.I', 'DI'))


def ekstrak(pdf):
    rows = []
    with pdfplumber.open(pdf) as doc:
        for no, page in enumerate(doc.pages, 1):
            blok = blok_teks(page)
            if blok is None:
                continue
            semua = ' '.join(blok)
            m = re.search(r'Provinsi\s+(.+?)\s+(?:tidak\s+)?melakukan', semua)
            kepala = PM.cari_prov(bersih(m.group(1))) if m else []
            if not kepala:
                rows.append((no, None, 'tanpa kepala', None, None))
                continue
            kepala = kepala[0]
            ada = False
            for t in blok:
                for arah, pola in (('beli', r'pembelian\s+beras\s+dari\s.*?(\d+)\s+provinsi\s+lain\s*,?\s*yaitu(.+)$'),
                                   ('jual', r'penjualan\s+beras\s+ke\s.*?(\d+)\s+provinsi\s+lain\s*,?\s*yaitu(.+)$')):
                    m = re.search(pola, t, flags=re.I)
                    if not m:
                        continue
                    for mitra in dict.fromkeys(PM.cari_prov(bersih(m.group(2)))):
                        if mitra != kepala:
                            rows.append((no, kepala, arah, mitra, int(m.group(1))))
                            ada = True
            if not ada:
                rows.append((no, kepala, 'tidak ada', None, None))
    return pd.DataFrame(rows, columns=['halaman', 'prov', 'arah', 'mitra', 'jumlah_tertulis'])


if __name__ == '__main__':
    df = ekstrak(sys.argv[1])
    df.to_csv(sys.argv[2], index=False)
    g = df[df.mitra.notna()]
    c = g.groupby(['prov', 'arah']).agg(parse=('mitra', 'size'), tertulis=('jumlah_tertulis', 'first')).reset_index()
    print(f'{df.prov.nunique()} provinsi; {len(g)} tautan ({(g.arah == "beli").sum()} beli, {(g.arah == "jual").sum()} jual); '
          f'tanpa kepala: {(df.arah == "tanpa kepala").sum()}; jumlah cocok dengan yang tertulis: {(c.parse == c.tertulis).sum()} dari {len(c)}')
    print(c[c.parse != c.tertulis].to_string(index=False))
    print('tanpa mitra:', sorted(df[df.arah == 'tidak ada'].prov))
