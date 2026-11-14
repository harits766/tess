"""Turun peringkat di blok penyetelan untuk komoditas yang resep pemenangnya gagal gerbang (ambang_ujian.md:
"pemenang dipakai hanya jika lolos semua gerbang; kalau tidak, turun ke peringkat berikutnya (hanya di blok penyetelan)").

Pakai:  python -I binpas/turun_peringkat.py <folder keluaran penyetelan komoditas>

Aturan (ditetapkan sebelum dijalankan):
1. Kandidat = versi yang berbeda dari resep pemenang di TEPAT SATU tahap, dari daftar pilihan yang sudah dibekukan:
   identitas (I0/I1/I2), isian x batas lubang (B, C, R1-R4 x 2/3/6/99), tambahan (tanpa atau satu tambahan),
   bobot x ragam (tanpa/3/5 x titik/0,5/1/2), rekonsiliasi (tanpa/dengan).
2. Semua kandidat dijalankan 500 ulangan di blok penyetelan dengan pola hapus yang sama.
3. Tiap kandidat mendapat perlakuan tahap 5 yang sama dengan adu_versi.penyetelan: Q/bias dari Jan-Des 2024, dinilai
   Jan-Jun 2025; opsi koreksi dipilih menurut peringkat CRPS (selisih tipis -> lebih sederhana), lalu turun ke opsi
   berikutnya bila gagal gerbang.
4. Kandidat lolos bila semua gerbang di tingkat wilayah lolos (lebih baik, konsisten, cakupan, bias, arah >= 80%).
5. Dari yang lolos dipilih CRPS wilayah terkecil; bila selisihnya dengan kandidat lolos yang lebih sederhana tipis
   (rentang 90% bootstrap per blok bulan mencakup 0), dipilih yang lebih sederhana.
6. Tidak ada yang lolos -> resep tidak diubah; komoditas memakai A berlabel "tercatat".
Blok kalibrasi dan ujian tidak disentuh.
"""
import json
import os
import shutil
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adu_versi as AV  # noqa: E402
import adu_metode as AM  # noqa: E402

N_ULANG = 500
BATAS = {99: 0, 6: 1, 3: 2, 2: 3}
BOBOT = {None: 0, 3: 1, 5: 2}
RAGAM = {1.0: 0, 'titik': 1, 0.5: 2, 2.0: 2}
KOREKSI = ['tanpa', 'konformal', 'konformal+bias', 'konformal+bias+halus']
IDENT = ['I0', 'I1', 'I2']


def sederhana(c, koreksi):
    ident, metode, batas, add, bobot, ragam, rekon = c
    return (AV.M_URUT.index(metode), BATAS[batas], len(add), BOBOT[bobot], RAGAM[ragam], rekon, IDENT.index(ident),
            KOREKSI.index(koreksi))


def tahap5(df, c, pstar):
    """Perlakuan tahap 5 untuk satu versi; mengembalikan (opsi terpilih, lolos, tabel opsi terpilih, gerbang)."""
    p = AV.nama(c)
    x = df[df.cfg == p]
    cal, ev = x[x.t <= 11], x[x.t >= 12]
    opsi = {'tanpa': ev.assign(cfg='tanpa'),
            'konformal': AV.terapkan_koreksi(ev, AV.param_koreksi(cal, bias=False), label='konformal'),
            'konformal+bias': AV.terapkan_koreksi(ev, AV.param_koreksi(cal, bias=True), label='konformal+bias'),
            'konformal+bias+halus': AV.terapkan_koreksi(ev, AV.param_koreksi(cal, bias=True), halus=True,
                                                        label='konformal+bias+halus')}
    df5 = pd.concat(list(opsi.values()) + [df[df.cfg.isin(AV.PEMBANDING) & (df.t >= 12)]])
    p5, _ = AV.pilih(df5, KOREKSI, {k: j for j, k in enumerate(KOREKSI)})
    urut = [p5] + [k for k in AV.peringkat(df5).index if k in KOREKSI and k != p5]
    hasil = None
    for k in urut:
        G = [dict(AV.gerbang(df5, k, pstar, tk), arah=AV.arah(df5, k, tk)) for tk in AV.TINGKAT]
        g = G[AV.TINGKAT.index(AV.UTAMA)]
        ok = bool(g.get('L_lebih_baik') and g.get('L_konsisten') and g.get('L_cakupan') and g.get('L_bias')
                  and g.get('arah', 0) >= 0.80)
        if hasil is None or ok:
            hasil = (k, ok, opsi[k], G)
        if ok:
            break
    return hasil


def main(out):
    fb = os.path.join(out, 'blok.json')
    if os.path.exists(fb):
        AM.BLOK_IDX.update({k: tuple(v) for k, v in json.load(open(fb)).items()})
    AV.D = pd.read_pickle(os.path.join(out, 'data_komoditas.pkl'))
    AV.P = AM.profil_hapus(AV.D)
    st = json.load(open(os.path.join(out, 'status.json')))
    resep = json.load(open(os.path.join(out, 'resep.json')))
    log = open(os.path.join(out, 'log_turun_peringkat.txt'), 'a')

    def catat(s):
        print(s, flush=True)
        log.write(str(s) + '\n')
        log.flush()
    _, m0, b0 = st['isian'].split('|')[:3]
    menang = AV.cfg(ident=st['ident'], metode=m0, batas=int(b0), add=tuple(st['add']), bobot=st['bobot'],
                    ragam=st['ragam'], rekon=st['rekon'])
    ident, metode, batas, add, bobot, ragam, rekon = menang
    pstar = st['pstar']
    dasar = dict(ident=ident, metode=metode, batas=batas, add=add, bobot=bobot, ragam=ragam, rekon=rekon)
    K = [menang]
    K += [AV.cfg(**dict(dasar, ident=i)) for i in IDENT]
    K += [AV.cfg(**dict(dasar, metode=m, batas=b)) for m in AV.M_58 for b in (2, 3, 6, 99)]
    K += [AV.cfg(**dict(dasar, add=a)) for a in [()] + [(t,) for t in AV.TAMBAHAN if t != 'luar']]
    K += [AV.cfg(**dict(dasar, bobot=b, ragam=r)) for b in (None, 3, 5) for r in ('titik', 0.5, 1.0, 2.0)]
    K += [AV.cfg(**dict(dasar, rekon=r)) for r in (0, 1)]
    K = list(dict.fromkeys(K))
    catat(f'== turun peringkat {time.strftime("%Y-%m-%d %H:%M:%S")} | {open(os.path.join(out, "komoditas.txt")).read()} | '
          f'pemenang {AV.nama(menang)} | {len(K) - 1} kandidat | P* = {pstar}')
    t0 = time.time()
    df = AV.tambah_skor(AV.jalankan(K, 'penyetelan', range(N_ULANG)))
    catat(f'{len(K)} versi x {df.rep.nunique()} ulangan, {time.time() - t0:.0f} detik')
    baris, tabel, gerb = [], [df[df.cfg.isin(AV.PEMBANDING) & (df.t >= 12)]], {}
    for c in K:
        k, ok, x, G = tahap5(df, c, pstar)
        label = AV.nama(c) + '#' + k
        tabel.append(x.assign(cfg=label))
        gerb[label] = (c, k, G)
        g = G[AV.TINGKAT.index(AV.UTAMA)]
        baris.append(dict(versi=AV.nama(c), koreksi=k, lolos=ok, pemenang_semula=c == menang,
                          **{f: g.get(f) for f in ('sel_bulan', 'crps', 'crps_pembanding', 'perbaikan', 'cakupan', 'wilson_lo',
                                                   'wilson_hi', 'bias', 'bias_pembanding', 'L_lebih_baik', 'L_konsisten',
                                                   'L_cakupan', 'cakupan_belum_bisa', 'L_bias', 'arah')}))
    T = pd.DataFrame(baris).sort_values('crps')
    T.to_csv(os.path.join(out, 'turun_peringkat.csv'), index=False)
    catat(T[['versi', 'koreksi', 'lolos', 'crps', 'perbaikan', 'cakupan', 'bias', 'arah']].round(4).to_string(index=False))
    L = T[T.lolos]
    if not len(L):
        catat('-> tidak ada kandidat yang lolos semua gerbang di tingkat wilayah; resep tidak diubah (A "tercatat").')
        return
    dfc = pd.concat(tabel)
    label = {r.versi + '#' + r.koreksi: sederhana(gerb[r.versi + '#' + r.koreksi][0], r.koreksi) for r in L.itertuples()}
    pilihan, _ = AV.pilih(dfc, list(label), label)
    c, k, G = gerb[pilihan]
    catat(f'-> terbaik yang lolos: {L.iloc[0].versi}#{L.iloc[0].koreksi}; dipilih (aturan lebih sederhana): {pilihan}')
    catat(pd.DataFrame(G).T.to_string())
    if not os.path.exists(os.path.join(out, 'resep_peringkat1.json')):
        shutil.copy(os.path.join(out, 'resep.json'), os.path.join(out, 'resep_peringkat1.json'))
        shutil.copy(os.path.join(out, 'gerbang_penyetelan.csv'), os.path.join(out, 'gerbang_penyetelan_peringkat1.csv'))
    resep.update(ident=c[0], metode=c[1], batas=c[2], add=list(c[3]), bobot=c[4], ragam=c[5], rekon=c[6],
                 anggota=[list(c)], penggabung=AV.nama(c), koreksi=k, lolos_penyetelan=True,
                 turun_peringkat=dict(dari=AV.nama(menang), kandidat=len(K) - 1, lolos=int(len(L)),
                                      dibuat=time.strftime('%Y-%m-%d %H:%M:%S')))
    json.dump(resep, open(os.path.join(out, 'resep.json'), 'w'), indent=1, default=str)
    pd.DataFrame(G).to_csv(os.path.join(out, 'gerbang_penyetelan.csv'), index=False)


if __name__ == '__main__':
    main(sys.argv[1])
