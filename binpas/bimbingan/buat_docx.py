from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

d = Document()
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'):
    setattr(sec, m, Cm(2.5))

FONT = 'Arial'
def gaya(nama, size, bold=None, warna=(0, 0, 0), sebelum=None, sesudah=None):
    s = d.styles[nama]
    s.font.name = FONT
    s.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    s.font.size = Pt(size)
    s.font.color.rgb = RGBColor(*warna)
    if bold is not None:
        s.font.bold = bold
    pf = s.paragraph_format
    if sebelum is not None: pf.space_before = Pt(sebelum)
    if sesudah is not None: pf.space_after = Pt(sesudah)
    return s
gaya('Normal', 11, sesudah=6)
d.styles['Normal'].paragraph_format.line_spacing = 1.15
gaya('Title', 17, bold=True, sesudah=4)
gaya('Heading 1', 14, bold=True, sebelum=14, sesudah=6)
gaya('Heading 2', 12, bold=True, sebelum=10, sesudah=4)
for h in ('Heading 1', 'Heading 2'):
    d.styles[h].paragraph_format.keep_with_next = True
gaya('List Bullet', 11, sesudah=3)
gaya('List Number', 11, sesudah=3)
gaya('Caption', 9, bold=False, warna=(0x44, 0x44, 0x44), sesudah=8)

def p(teks, style=None, rata=None):
    par = d.add_paragraph(style=style)
    # **tebal** sederhana
    bagian = teks.split('**')
    for i, b in enumerate(bagian):
        if b:
            r = par.add_run(b)
            r.bold = (i % 2 == 1)
    if rata == 'tengah':
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return par

def butir(teks):
    return p(teks, 'List Bullet')

def nomor(teks):
    return p(teks, 'List Number')

def arsir(sel, warna='E8E8E8'):
    tcPr = sel._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), warna)
    tcPr.append(shd)

def tabel(baris, lebar, ukuran=9):
    t = d.add_table(rows=len(baris), cols=len(baris[0]))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, r in enumerate(baris):
        tr = t.rows[i]._tr
        trPr = tr.get_or_add_trPr()
        cs = OxmlElement('w:cantSplit'); trPr.append(cs)
        if i == 0:
            th = OxmlElement('w:tblHeader'); trPr.append(th)
        for j, v in enumerate(r):
            c = t.cell(i, j)
            c.width = Cm(lebar[j])
            c.paragraphs[0].text = ''
            par = c.paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = 1.0
            bagian = str(v).split('**')
            for k, b in enumerate(bagian):
                if b:
                    run = par.add_run(b); run.font.size = Pt(ukuran); run.bold = (i == 0) or (k % 2 == 1)
            if i == 0:
                arsir(c)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ------------------------------------------------------------------ isi
d.add_paragraph('Estimasi Stok dan Penguatan Data Distribusi Beras Berbasis Laporan INATRADE', style='Title')
p('Bahan bimbingan: permasalahan, data, metodologi, evaluasi, dan hasil sementara. Harits, Direktorat Bina Pasar '
  'Dalam Negeri, Kementerian Perdagangan. 23 November 2026.')

d.add_heading('1. Permasalahan', level=1)
p('Direktorat Bina Pasar Dalam Negeri menerima laporan distribusi bulanan dari distributor beras melalui sistem '
  'INATRADE: stok awal, pengadaan, penyaluran, stok akhir, provinsi tujuan, dan harga jual. Ini satu-satunya data '
  'distribusi beras yang dimiliki Kementerian Perdagangan sendiri, tetapi belum bisa langsung dipakai untuk '
  'menggambarkan stok dan distribusi beras karena lima masalah berikut.')
butir('**Pelapor sedikit dan berubah-ubah.** Ada 91 perusahaan pelapor beras. Per bulan hanya 11–15 perusahaan pada '
      'Jan–Sep 2024, lalu naik menjadi 47–66 perusahaan sejak Nov 2024, sehingga deret waktunya patah.')
butir('**Laporan bolong.** Sebanyak 15% perusahaan-bulan kosong padahal perusahaannya masih aktif melapor, dan '
      'laporan bulan terakhir sering belum masuk.')
butir('**Kualitas isian.** Semua baris berlabel ton, tetapi sebagian diisi dalam kg (58 laporan beras dikoreksi). '
      'Stok awal hanya 76% sama dengan stok akhir bulan sebelumnya.')
butir('**Cakupan volume kecil.** Penyaluran seluruh pelapor hanya ±1,5–3% dari konsumsi beras rumah tangga '
      '(Susenas), sehingga INATRADE tidak bisa dibaca sebagai gambaran pasar.')
butir('**Tidak ada angka stok total terbaru.** Survei stok beras akhir tahun (SSBAT) terakhir terbit untuk Desember '
      '2023, sehingga stok beras 2024–2026 tidak diketahui secara langsung.')
p('Dari situ dirumuskan tiga pertanyaan:')
nomor('Berapa stok beras total per provinsi per bulan pada Jan 2024–Sep 2026, beserta ketidakpastiannya?')
nomor('Metode apa yang paling tepat untuk menutup laporan INATRADE yang bolong, dan apakah metode itu tetap tepat '
      'pada data yang belum pernah dilihat?')
nomor('Apakah jalur distribusi antarprovinsi di INATRADE sesuai dengan pola distribusi resmi BPS?')

d.add_heading('2. Data dan sumber', level=1)
tabel([
    ['Data', 'Isi', 'Periode', 'Sumber'],
    ['Laporan distribusi INATRADE', 'Stok awal, pengadaan, penyaluran, stok akhir, provinsi tujuan, harga jual per perusahaan '
     'per bulan; 91 pelapor beras', 'Jan 2024–Sep 2026', 'Kemendag (internal Dit. Binpas)'],
    ['Produksi padi', 'Bulanan per provinsi (var 2506) dan tahunan (var 1498); dikonversi ke beras × 0,5762',
     '2022–2026', 'WebAPI BPS'],
    ['Konsumsi beras rumah tangga', 'Susenas per kabupaten/kota (var 2094) dibobot penduduk (var 2790)', '2022–2025', 'WebAPI BPS'],
    ['Harga beras penggilingan', 'Rata-rata bulanan nasional (var 500, 2277)', 's.d. 2025', 'WebAPI BPS'],
    ['Survei stok beras', 'SCBN Jun 2022 (9,71 juta ton); SSBAT Des 2022 (4,06) dan Des 2023 (4,13)', '2022–2023',
     'BPS, Bapanas–BPS (angka publik)'],
    ['Stok BULOG dan impor', 'Angka publik; laporan INATRADE BULOG', '2022–2026', 'Rilis publik, INATRADE'],
    ['Pola Distribusi Perdagangan Beras', 'Daftar provinsi asal pembelian dan tujuan penjualan tiap provinsi',
     'Edisi 2024 dan 2025', 'BPS (PDF lewat WebAPI)'],
], [3.4, 6.6, 2.6, 3.4])
p('Data per perusahaan bersifat internal; dokumen ini hanya memuat angka agregat. Semua data BPS diambil otomatis '
  'lewat WebAPI, dan seluruh pengolahan dapat dijalankan ulang dari satu notebook Python.')

d.add_heading('3. Metodologi', level=1)
p('Alur kerja ditunjukkan pada Gambar 1. Sesudah data dikumpulkan, diperiksa, dan dibersihkan, data dibagi ke tiga '
  'blok waktu. Pengembangan model berjalan di tiga cabang yang menjawab tiga pertanyaan di bagian 1, lalu semua cabang '
  'dinilai dengan ukuran dan ambang yang ditetapkan sebelum ujian.')
d.add_picture('diagram_alir.png', width=Cm(15.5))
d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p('Gambar 1. Diagram alir metodologi.', 'Caption', rata='tengah')

d.add_heading('3.1 Eksplorasi dan preprocessing', level=2)
p('Eksplorasi (Tahap 0) memprofil data tanpa menilai metode: kehadiran pelapor, panjang laporan bolong, kecocokan '
  'stok antarbulan, konsentrasi perusahaan, dan cakupan volume terhadap BPS. Preprocessing meliputi koreksi satuan '
  'kg ke ton (nilai ≥ 100 kali median perusahaan itu sendiri), pemisahan BULOG dari pedagang, penjumlahan laporan '
  'berkepala ganda, dan penyusunan panel perusahaan × bulan. Untuk penguatan data, provinsi dikelompokkan ke tiga '
  'wilayah: Jawa, Sumatera, dan pulau lain (pulau lain hanya ±4 pelapor per bulan).')

d.add_heading('3.2 Pembagian blok waktu', level=2)
p('Penyetelan Jan 2024–Jun 2025 dipakai untuk memilih metode, kalibrasi Jul–Des 2025 untuk menyetel lebar rentang, '
  'dan ujian akhir Jan–Sep 2026 hanya dijalankan sekali sesudah metode dikunci. Dengan begitu skor ujian tidak '
  'ikut memengaruhi pilihan metode.')

d.add_heading('3.3 Penguatan data INATRADE', level=2)
p('Karena nilai laporan yang hilang tidak diketahui, kemampuan menebaknya diuji dengan simulasi: dari laporan yang '
  'ada, sebagian dihapus secara acak mengikuti pola bolong yang sebenarnya (lubang di tengah dan laporan terakhir '
  'yang belum masuk), lalu ditebak kembali. Total tebakan per sel (provinsi, wilayah, nasional per bulan) dibandingkan '
  'dengan total yang sebenarnya. Pembanding P* adalah data apa adanya, dengan atau tanpa bobot pelapor.')
p('Sebanyak 79 kombinasi diadu bertahap: identitas stok, metode isian (interpolasi dan laporan terakhir, pertumbuhan '
  'perusahaan sejenis, empat varian regresi panel, quantile regression forest, CatBoost, dan multilevel regression '
  'with poststratification), batas panjang lubang, tambahan model (misalnya galat berekor tebal), bobot pelapor dan '
  'skala ragam, rekonsiliasi antartingkat, penggabung model, serta koreksi akhir konformal. Kombinasi disaring '
  'dengan 50, lalu 200, lalu 500 ulangan simulasi. Bila selisih dua kombinasi tipis, dipilih yang lebih sederhana.')

d.add_heading('3.4 Model stok Bayesian', level=2)
p('Stok beras total (rumah tangga, penggilingan, pedagang, BULOG, horeka) per provinsi diestimasi dengan model '
  'state-space Bayesian:')
p('stok(t) = stok(t−1) + produksi − selisih tak tercatat + impor − konsumsi + arus masuk − arus keluar + guncangan.', rata='tengah')
p('Survei stok, stok BULOG, stok pedagang INATRADE, dan harga penggilingan masuk sebagai pengukuran, masing-masing '
  'dengan bias dan galat sendiri. Arus antarprovinsi mengikuti surplus dan defisit tiap provinsi, dan stok swasta '
  'dibatasi tidak negatif per pulau. Model mulai Jun 2022 agar tiga survei stok terpakai, dan diestimasi dengan PyMC '
  '(sampler nutpie, 4 rantai × 1.000 tarikan).')

d.add_heading('3.5 Keterwakilan jalur distribusi', level=2)
p('Satuan analisis adalah pasangan provinsi berarah asal → tujuan (34 provinsi, 1.122 pasangan). Jawabannya adalah '
  'tautan yang tercatat di Pola Distribusi BPS edisi 2025, yang disembunyikan sampai definisi uji dikunci. Tiga skor '
  'diadu: INATRADE mentah (jumlah laporan perusahaan-bulan pada tautan itu), BPS 2024 apa adanya, dan gabungan '
  '(BPS 2024 ditambah tanda tautan INATRADE).')

d.add_heading('4. Evaluasi', level=1)
p('Ukuran dan ambang lolos ditetapkan dan dikunci pada 11 November 2026, sebelum ujian pertama dijalankan, dan tidak '
  'diubah sesudahnya. Hasil dinilai terpisah untuk tiga tingkat: provinsi, wilayah (target utama), dan nasional.')
tabel([
    ['Gerbang', 'Ukuran', 'Ambang lolos'],
    ['Lebih baik', 'CRPS (galat sebaran tebakan, skala log) dan MAE angka tengah', 'CRPS ≥ 10% lebih kecil dari P* dan MAE tidak lebih buruk'],
    ['Konsisten', 'Selisih CRPS terhadap P*, bootstrap per blok bulan', 'Rentang 90% seluruhnya < 0'],
    ['Cakupan', 'Porsi nilai sebenarnya yang masuk rentang 90%', '90% ada di selang Wilson (n efektif) dan cakupan ≥ 80%'],
    ['Bias', 'Rata-rata galat log', '≤ 3% dan tidak lebih buruk dari P*'],
    ['Arah', 'Porsi bulan dengan arah perubahan yang benar', '≥ 80%'],
    ['Stabil', 'CRPS ujian dibanding penyetelan, metode yang sama', 'Memburuk ≤ 20%'],
    ['Keterwakilan (U2)', 'Average precision; korelasi peringkat volume asal', 'Gabungan > dua pembanding (selang tidak memuat 0); korelasi ≥ 0,6'],
], [2.8, 6.6, 6.6])
p('Bila data terlalu sedikit untuk memutuskan, misalnya setengah lebar selang Wilson lebih dari 10 poin persen, '
  'status yang dipakai adalah "belum bisa diputuskan", bukan lolos atau gagal. Model stok divalidasi dengan '
  'menyembunyikan survei SSBAT Des 2022 lalu membandingkan prediksi model dengan angka survei itu.')

d.add_heading('5. Hasil saat ini', level=1)
d.add_heading('5.1 Penguatan data: metode terpilih dan ujian akhir (U1)', level=2)
p('Metode yang terpilih di blok penyetelan adalah interpolasi antara dua laporan tetangga (atau laporan terakhir '
  'bila belum ada laporan sesudahnya) dengan galat berekor tebal, semua lubang diisi, tanpa bobot pelapor, dan '
  'koreksi konformal. Quantile regression forest sempat sedikit lebih baik di satu tahap, tetapi selisihnya tipis '
  'sehingga dipilih interpolasi yang lebih sederhana; penggabung model juga tidak lebih baik. '
  'Pembanding terbaik P* adalah data apa adanya dengan bobot pelapor batas 5.')
tabel([
    ['Ukuran (Jan–Sep 2026)', 'Provinsi', 'Wilayah', 'Nasional'],
    ['Sel-bulan', '133 (7 provinsi)', '57', '19'],
    ['CRPS metode / P*', '0,043 / 0,244', '0,016 / 0,116', '0,011 / 0,048'],
    ['Perbaikan CRPS', '82%', '86%', '78%'],
    ['Bias metode / P*', '+0,9% / −11,0%', '+0,04% / −4,3%', '+0,3% / −1,3%'],
    ['Arah perubahan benar', '93%', '96%', '98%'],
    ['Cakupan rentang 90% (selang Wilson)', '93,3% (87,3–96,6)', '97,8% (88,1–99,6)', '96,9% (69,3–99,8)'],
    ['CRPS dibanding penyetelan', '+13%', '−3%', '−4%'],
    ['Status', 'Lolos dengan catatan', '**Lolos semua gerbang**', 'Cakupan belum bisa diputuskan'],
], [5.0, 3.6, 3.6, 3.8])
p('Di target utama (wilayah), metode terpilih lolos semua gerbang: galatnya 86% lebih kecil dari data apa adanya dan '
  'biasnya hampir nol. Rentangnya cenderung terlalu lebar (cakupan 97,8% untuk sasaran 90%). Di tingkat provinsi '
  'hanya 7 provinsi yang punya minimal 3 pelapor. Galatnya memburuk 13% dibanding metode yang sama di blok penyetelan, '
  'atau 28% bila acuannya angka seluruh blok penyetelan tanpa koreksi. Acuan pertama diputuskan sesudah hasil ujian '
  'dilihat, sehingga provinsi dilaporkan "lolos dengan catatan" dan kedua angka disebut. Di tingkat nasional, 19 '
  'sel-bulan terlalu sedikit untuk memutuskan gerbang cakupan.')

d.add_heading('5.2 Stok beras total', level=2)
butir('**Stok nasional akhir Sep 2026: 14,2 juta ton** (interval 90%: 11,3–18,6), setara Sep 2025 (14,4). Dari jumlah '
      'itu, BULOG 4,65 juta ton (4,29–5,04) dan swasta 9,6 juta ton (6,7–14,0). Stok terendah tiap Jan–Feb dan naik '
      'setelah panen Mar–Apr.')
butir('**Validasi:** dengan survei SSBAT Des 2022 disembunyikan, model memprediksi bacaan survei 4,40 juta ton '
      '(3,43–5,59), dan angka survei 4,06 juta ton masih di dalam interval. Uji ini memeriksa konsistensi perubahan stok '
      'selama 2023, bukan level absolut, karena bias survei diestimasi model. Konsumsi total 2024 menurut model (29,79 '
      'juta ton) sesuai dengan angka konsumsi total BPS 2024 (29,80 juta ton) yang tidak dipakai saat estimasi.')
butir('**Kepekaan:** pilihan yang paling menentukan level adalah batas stok swasta tidak negatif. Per pulau '
      '(dasar) 14,2 juta ton, nasional 14,2, per provinsi 16,8. Tanpa data INATRADE hasilnya 15,1 juta ton.')
butir('**Prakiraan:** Okt 2026 13,6 (10,7–18,1), Nov 12,5 (9,5–17,0), Des 11,1 juta ton (8,1–15,7), cukup untuk ±4,1 '
      'bulan konsumsi pada Desember. Provinsi paling rawan pada Desember: Papua Tengah, Kepulauan Riau, Riau, dan '
      'Bangka Belitung.')
butir('Survei SSBAT konsisten berada sekitar separuh level model, sehingga model memberi tiap survei bias sendiri. '
      'Prakiraan belum diuji mundur (backtest).')

d.add_heading('5.3 Keterwakilan jalur distribusi (U2)', level=2)
tabel([
    ['Versi', 'Average precision', 'Tautan', 'Presisi', 'Recall'],
    ['Acak (kepadatan)', '0,093', '–', '9%', '–'],
    ['INATRADE mentah', '0,329', '77', '51%', '38%'],
    ['BPS 2024 apa adanya', '0,480', '150', '57%', '82%'],
    ['Gabungan (BPS 2024 + INATRADE)', '**0,563**', '185', '50%', '89%'],
], [5.6, 3.0, 2.2, 2.4, 2.4])
p('Gabungan lebih tepat menebak jalur BPS 2025 daripada BPS 2024 saja (selisih +0,083; selang 90% 0,041–0,133) dan '
  'daripada INATRADE mentah (+0,234), jadi gerbang "lebih dekat" lolos. Korelasi peringkat volume keluar INATRADE '
  'per provinsi asal dengan BPS 2025 hanya 0,20 (batas 0,6), jadi gerbang keterwakilan gagal: arus antarprovinsi '
  'INATRADE hanya berasal dari 26 perusahaan di 9 provinsi asal, dan "asal" di INATRADE adalah provinsi kedudukan '
  'perusahaan, belum tentu asal fisik barang. Kesimpulannya, INATRADE berguna sebagai penguat peta jalur BPS, tetapi '
  'tidak mewakili pola asal perdagangan beras.')

d.add_heading('6. Keterbatasan dan langkah berikutnya', level=1)
butir('Lolos ujian U1 berarti metode menutup laporan yang bolong secara konsisten. Itu bukan bukti bahwa pelapor '
      'INATRADE mewakili pasar, karena cakupan volumenya hanya ±1,5–3%.')
butir('Level stok 2024–2026 belum bisa divalidasi langsung karena SSBAT 2024–2025 belum tersedia; interval stok masih '
      'lebar dan levelnya bergantung pada batas stok swasta.')
butir('Uji keterwakilan hanya memakai satu tahun pembanding, dan dua edisi BPS diekstrak dengan cara berbeda '
      '(diagram untuk 2024, kalimat untuk 2025).')
butir('**Langkah berikutnya (U3):** menguji apakah data INATRADE memperbaiki prakiraan harga beras eceran per '
      'provinsi 1–2 bulan ke depan, dibanding model tanpa INATRADE. Data harga PIHPS Bank Indonesia per provinsi '
      'sudah dapat diambil; definisi uji akan dikunci sebelum dijalankan.')
butir('Alur penguatan data juga sudah diterapkan ke enam komoditas lain (daging sapi, kedelai, daging kerbau, telur '
      'ayam ras, daging ayam ras, pupuk) dengan 58 kombinasi; beras menjadi acuan.')

d.save('bimbingan_beras.docx')
print('ok')
