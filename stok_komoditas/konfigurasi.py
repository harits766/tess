"""Konfigurasi per komoditas untuk model stok generik (fase 1: kedelai).

Semua perbedaan antar komoditas ditulis di sini, bukan di kode model: sumber data, faktor konversi,
jangkar level, tingkat (A/B/C), dan asumsi yang belum punya data. Beras masih memakai beras_stok/
(model tingkat A dengan survei stok dan BULOG) agar hasil yang sudah divalidasi tidak berubah.
"""

KEDELAI = dict(
    nama='kedelai',
    judul='Kedelai',
    satuan='ton biji kedelai',
    tingkat='B',  # level dijangkarkan lewat neraca impor + laporan importir + USDA (bias diestimasi)
    awal='2023-01',  # bulan pertama neraca (stok awal = akhir Des 2022); impor BPS per pelabuhan mulai 2023
    akhir='2026-09',
    # --- INATRADE
    inatrade_komoditi='KEDELAI BAHAN BAKU TEMPE DAN TAHU',
    bumn=[],  # tidak ada BUMN pelapor kedelai
    sub_tanpa_label='-',  # 31% laporan; diisi dari label dominan perusahaan yang sama, lalu 'Impor'
    sub_bawaan='Impor',
    # --- impor bulanan BPS (dataexim), dipetakan ke provinsi pelabuhan masuk
    hs=['12019000'],  # kedelai selain benih; benih (12011000) diabaikan (< 0,1%)
    pelabuhan={
        'TANJUNG PERAK': 'JAWA TIMUR', 'GRESIK': 'JAWA TIMUR', 'BANYUWANGI': 'JAWA TIMUR',
        'JUANDA (U)-SURABAYA': 'JAWA TIMUR', 'TANJUNG PRIOK': 'DKI JAKARTA', 'JKT./ POS PASAR BARU': 'DKI JAKARTA',
        'TANJUNG EMAS': 'JAWA TENGAH', 'CILACAP': 'JAWA TENGAH', 'CIGADING': 'BANTEN',
        'SOEKARNO-HATTA (U)': 'BANTEN', 'BELAWAN': 'SUMATERA UTARA', 'PANJANG': 'LAMPUNG',
        'PONTIANAK': 'KALIMANTAN BARAT', 'SUPADIO (U)': 'KALIMANTAN BARAT', 'BATU AMPAR': 'KEPULAUAN RIAU',
        'SEKUPANG': 'KEPULAUAN RIAU', 'TANJUNG BALAI KARIMUN': 'KEPULAUAN RIAU', 'DUMAI': 'RIAU',
        'MAKASSAR': 'SULAWESI SELATAN', 'TELUK BAYUR': 'SUMATERA BARAT', 'NGURAH RAI (U)': 'BALI',
    },
    # --- konsumsi rumah tangga Susenas (var 2101, kg/kapita/minggu per kab/kota) -> setara biji kedelai
    susenas_var=2101,
    susenas_tahun=[2023, 2024, 2025],  # 2026 memakai 2025
    susenas_item={'1833': ('kedele', 1.0), '1835': ('tahu', 0.30), '1836': ('tempe', 0.60)},
    # faktor kg biji kedelai per kg produk (asumsi rendemen: tahu 1 kg kedelai -> ~3,3 kg tahu basah,
    # tempe 1 kg -> ~1,7 kg tempe). Hanya hasil kalinya dengan pengali konsumsi (1+nu) yang teridentifikasi.
    # --- produksi dalam negeri: BPS tidak lagi menerbitkan produksi kedelai per provinsi; dipakai produksi
    # nasional USDA PSD per tahun pemasaran (Okt-Sep) dibagi rata per bulan, lalu dibagi ke provinsi dengan
    # pangsa ASUMSI di bawah (pola produksi Kementan sebelum 2020; ganti bila data Kementan tersedia).
    usda_komoditas='Oilseed, Soybean',
    usda_bulan_awal=10,
    pangsa_produksi={
        'JAWA TIMUR': 0.28, 'JAWA TENGAH': 0.15, 'NUSA TENGGARA BARAT': 0.12, 'JAWA BARAT': 0.10,
        'ACEH': 0.06, 'SULAWESI SELATAN': 0.06, 'BANTEN': 0.03, 'DAERAH ISTIMEWA YOGYAKARTA': 0.03,
        'LAMPUNG': 0.03, 'SULAWESI TENGAH': 0.03, 'SULAWESI TENGGARA': 0.02, 'SULAWESI BARAT': 0.02,
        'KALIMANTAN SELATAN': 0.02, 'SUMATERA UTARA': 0.02, 'GORONTALO': 0.01, 'NUSA TENGGARA TIMUR': 0.01,
        'SUMATERA SELATAN': 0.01,
    },
    # --- jangkar level: stok akhir USDA (akhir tahun pemasaran = akhir September). USDA memakai impor
    # yang sama dengan BPS, tetapi konsumsi dan stok awalnya asumsi atase, jadi diberi bias sendiri.
    jangkar_usda_my=[2022, 2023, 2024, 2025],  # stok akhir Sep 2023, 2024, 2025, Sep 2026 (MY2025 = estimasi)
    # --- prior
    prior_stok_awal_ton=3.0e5,  # median stok nasional akhir Des 2022, sebaran lognormal sd 0,7
    prior_konsumsi_total_ton_tahun=2.95e6,  # USDA domestic consumption rata-rata MY2023-2025
    sd_bias_usda=0.4,
)

KOMODITAS = {'kedelai': KEDELAI}
