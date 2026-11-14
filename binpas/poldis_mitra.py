"""Ekstrak daftar provinsi mitra dari publikasi BPS "Distribusi Perdagangan Komoditas Beras Indonesia" (PDF).

Pakai:  python -I binpas/poldis_mitra.py <pdf> <keluaran.csv>

Tiap bagian provinsi memuat diagram dengan kolom kiri "WILAYAH PEMBELIAN DARI LUAR PROVINSI" (provinsi asal) dan kolom
kanan "WILAYAH PENJUALAN KE LUAR PROVINSI" (provinsi tujuan). Publikasi hanya memberi DAFTAR provinsi mitra, bukan
pangsa per provinsi asal. Keluaran: satu baris per (provinsi, arah, mitra); arah = beli (mitra -> provinsi) atau
jual (provinsi -> mitra). Nama provinsi dicocokkan dengan daftar baku; negara asal impor diabaikan.
"""
import os
import re
import sys

import pandas as pd
import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tahap0 as T0  # noqa: E402

PROV = sorted(T0.PULAU_DARI, key=lambda p: -len(p))
ALIAS = {'DI YOGYAKARTA': 'DAERAH ISTIMEWA YOGYAKARTA', 'D.I. YOGYAKARTA': 'DAERAH ISTIMEWA YOGYAKARTA',
         'DKI JAKARTA': 'DKI JAKARTA', 'KEP. BANGKA BELITUNG': 'KEPULAUAN BANGKA BELITUNG', 'BANGKA BELITUNG': 'KEPULAUAN BANGKA BELITUNG',
         'KEP. RIAU': 'KEPULAUAN RIAU',
         # singkatan dan salah ketik yang muncul di kalimat edisi 2025 (tanda baca sudah dibuang)
         'KEP BABEL': 'KEPULAUAN BANGKA BELITUNG', 'BABEL': 'KEPULAUAN BANGKA BELITUNG', 'KEP RIAU': 'KEPULAUAN RIAU',
         'KEPRI': 'KEPULAUAN RIAU', 'SUMUT': 'SUMATERA UTARA', 'SUMBAR': 'SUMATERA BARAT', 'SUMSEL': 'SUMATERA SELATAN',
         'JABAR': 'JAWA BARAT', 'JATENG': 'JAWA TENGAH', 'JATIM': 'JAWA TIMUR', 'DIY': 'DAERAH ISTIMEWA YOGYAKARTA',
         'NTB': 'NUSA TENGGARA BARAT', 'NTT': 'NUSA TENGGARA TIMUR', 'KALBAR': 'KALIMANTAN BARAT',
         'KALTENG': 'KALIMANTAN TENGAH', 'KALSEL': 'KALIMANTAN SELATAN', 'KALTIM': 'KALIMANTAN TIMUR',
         'KALTARA': 'KALIMANTAN UTARA', 'SULUT': 'SULAWESI UTARA', 'SULTENG': 'SULAWESI TENGAH', 'SULSEL': 'SULAWESI SELATAN',
         'SULTRA': 'SULAWESI TENGGARA', 'SULBAR': 'SULAWESI BARAT', 'MALUT': 'MALUKU UTARA', 'JAWA TIIMUR': 'JAWA TIMUR'}
NAMA = {**{p: p for p in PROV}, **ALIAS}
URUT = sorted(NAMA, key=lambda p: -len(p))


def baris(words, tol=3):
    """Kelompokkan kata menjadi baris menurut posisi vertikal."""
    out = []
    for w in sorted(words, key=lambda w: (w['top'], w['x0'])):
        if out and abs(out[-1][0] - w['top']) <= tol:
            out[-1][1].append(w)
        else:
            out.append([w['top'], [w]])
    return [sorted(b, key=lambda w: w['x0']) for _, b in out]


def cari_prov(teks):
    """Semua nama provinsi di dalam satu potongan teks (nama terpanjang dulu)."""
    t, hasil = ' ' + re.sub(r'\s+', ' ', teks.upper()) + ' ', []
    for p in URUT:
        while f' {p} ' in t:
            hasil.append(NAMA[p])
            t = t.replace(f' {p} ', ' # ', 1)
    return hasil


def ekstrak(pdf):
    rows = []
    with pdfplumber.open(pdf) as doc:
        for no, page in enumerate(doc.pages, 1):
            words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
            teks = ' '.join(w['text'] for w in words).upper()
            if 'POLA DISTRIBUSI PERDAGANGAN BERAS' not in teks or 'DALAM PROVINSI' not in teks:
                continue
            L = baris(words)
            W = float(page.width)
            kepala = None
            for b in L[:6]:
                s = ' '.join(w['text'] for w in b).upper()
                if s.startswith('PROVINSI'):
                    c = cari_prov(s.replace('PROVINSI', ' '))
                    if c:
                        kepala = c[0]
            if kepala is None:
                c = cari_prov(' '.join(' '.join(w['text'] for w in b) for b in L[:4]))
                kepala = c[0] if c else None
            if kepala is None:
                rows.append((no, None, None, None))
                continue
            ada = False
            # kolom ditentukan dari posisi judul "PEMBELIAN" (kiri) dan "PENJUALAN" (kanan); nama di bawah judul itu
            for arah, judul in (('beli', 'PEMBELIAN'), ('jual', 'PENJUALAN')):
                hd = [w for w in words if w['text'].upper() == judul]
                if not hd:
                    continue
                pusat = sum((w['x0'] + w['x1']) / 2 for w in hd) / len(hd) - 20   # judul dua kata; nama rata tengah kolom
                atas = min(w['top'] for w in hd) + 18
                kol = [w for w in words if w['top'] > atas and abs((w['x0'] + w['x1']) / 2 - pusat) <= 85
                       and w['text'].upper() not in ('WILAYAH', 'PEMBELIAN', 'PENJUALAN', 'DARI', 'KE', 'LUAR', 'NEGERI')
                       and w['text'].isupper()]
                kel = []
                for b_ in baris(kol):
                    if kel and b_[0]['top'] - kel[-1][-1]['top'] < 15:   # nama terpotong ke baris berikutnya
                        kel[-1] += b_
                    else:
                        kel.append(list(b_))
                for k_ in kel:
                    for mitra in cari_prov(' '.join(w['text'] for w in k_)):
                        if mitra != kepala:
                            rows.append((no, kepala, arah, mitra))
                            ada = True
            if not ada:
                rows.append((no, kepala, 'tidak ada', None))
    return pd.DataFrame(rows, columns=['halaman', 'prov', 'arah', 'mitra']).drop_duplicates(['prov', 'arah', 'mitra'])


if __name__ == '__main__':
    df = ekstrak(sys.argv[1])
    df.to_csv(sys.argv[2], index=False)
    g = df[df.mitra.notna()]
    print(f'{df.prov.nunique()} provinsi; {len(g)} tautan ({(g.arah == "beli").sum()} beli, {(g.arah == "jual").sum()} jual); '
          f'halaman tanpa kepala: {df.prov.isna().sum()}')
    print(g.groupby(['prov', 'arah']).size().unstack(fill_value=0).to_string())
