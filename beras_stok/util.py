"""Fungsi bantu pembacaan data laporan distribusi INATRADE (port dari makro PembersihanNonPAW)."""
import math
import re

BULAN = {'JANUARI': 1, 'FEBRUARI': 2, 'MARET': 3, 'APRIL': 4, 'MEI': 5, 'JUNI': 6, 'JULI': 7,
         'AGUSTUS': 8, 'SEPTEMBER': 9, 'OKTOBER': 10, 'NOVEMBER': 11, 'DESEMBER': 12}


def kosong(v):
    return v is None or (isinstance(v, float) and math.isnan(v)) or str(v).strip() == ''


def U(v):
    return '' if kosong(v) else re.sub(' +', ' ', str(v).strip().upper())


def angka(v):
    """Angka dari sel; format Indonesia 1.234,5 dikenali. None bila kosong."""
    if kosong(v):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    t = ''.join(c for c in str(v) if c.isdigit() or c in ',.-')
    if not any(c.isdigit() for c in t):
        return None
    if re.fullmatch(r'-?\d{1,3}(\.\d{3})+(,\d*)?', t):
        t = t.replace('.', '').replace(',', '.')
    else:
        t = t.replace(',', '')
    try:
        return float(re.match(r'-?\d*\.?\d*', t).group(0))
    except ValueError:
        return 0.0


def a0(v):
    x = angka(v)
    return 0.0 if x is None else x


def normprov(v):
    s = U(v)
    for p in ('PROVINSI ', 'PROV. '):
        if s.startswith(p):
            s = s[len(p):].strip()
    return s


def periode(bulan, tahun):
    """'2026-09' dari ('SEPTEMBER', 2026); None bila tak terbaca."""
    b = BULAN.get(U(bulan))
    t = angka(tahun)
    if not b or t is None:
        return None
    return f'{int(t)}-{b:02d}'
