import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
W = sys.argv[1]; G = f'{W}/grafik'
d = Document(); sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'): setattr(sec, m, Cm(2.3))
def gaya(nama, size, bold=None, warna=(0, 0, 0), sebelum=None, sesudah=None):
    s = d.styles[nama]; s.font.name = 'Arial'; s.element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    s.font.size = Pt(size); s.font.color.rgb = RGBColor(*warna)
    if bold is not None: s.font.bold = bold
    if sebelum is not None: s.paragraph_format.space_before = Pt(sebelum)
    if sesudah is not None: s.paragraph_format.space_after = Pt(sesudah)
gaya('Normal', 11, sesudah=6); d.styles['Normal'].paragraph_format.line_spacing = 1.15
gaya('Title', 18, bold=True, sesudah=4)
gaya('Heading 1', 15, bold=True, sebelum=16, sesudah=6)
gaya('Heading 2', 12, bold=True, sebelum=10, sesudah=4)
for h in ('Heading 1', 'Heading 2'): d.styles[h].paragraph_format.keep_with_next = True
gaya('List Bullet', 11, sesudah=3); gaya('List Number', 11, sesudah=3)
gaya('Caption', 9, bold=False, warna=(0x52, 0x51, 0x4e), sesudah=10)

def p(teks, style=None, tengah=False):
    par = d.add_paragraph(style=style)
    for i, b in enumerate(teks.split('**')):
        if b: r = par.add_run(b); r.bold = (i % 2 == 1)
    if tengah: par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return par
def b(t): return p(t, 'List Bullet')
def n(t): return p(t, 'List Number')
def h1(t): d.add_heading(t, level=1)
def h2(t): d.add_heading(t, level=2)
NG = [0]
def gbr(nama, ket, lebar=16.2):
    NG[0] += 1
    par = d.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.keep_with_next = True; par.paragraph_format.space_after = Pt(2)
    par.add_run().add_picture(f'{G}/{nama}.png', width=Cm(lebar))
    p(f'Gambar {NG[0]}. {ket}', 'Caption', tengah=True)
def baca(t): return p('**Cara membaca:** ' + t)
def arsir(sel, warna='E8E8E8'):
    tcPr = sel._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), warna); tcPr.append(shd)
def tabel(baris, lebar, uk=9.5):
    t = d.add_table(rows=len(baris), cols=len(baris[0])); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, r in enumerate(baris):
        trPr = t.rows[i]._tr.get_or_add_trPr(); trPr.append(OxmlElement('w:cantSplit'))
        if i == 0: trPr.append(OxmlElement('w:tblHeader'))
        for j, v in enumerate(r):
            c = t.cell(i, j); c.width = Cm(lebar[j]); par = c.paragraphs[0]
            par.paragraph_format.space_after = Pt(0); par.paragraph_format.line_spacing = 1.0
            for k, s_ in enumerate(str(v).split('**')):
                if s_: run = par.add_run(s_); run.font.size = Pt(uk); run.bold = (i == 0) or (k % 2 == 1)
            if i == 0: arsir(c)
    d.add_paragraph().paragraph_format.space_after = Pt(2)

# =============================================================== isi
d.add_paragraph('Beras: Apa yang Dikerjakan, Datanya, Caranya, dan Hasilnya', style='Title')
p('Penjelasan dengan bahasa sederhana dan gambar, khusus beras. Semua angka diambil dari hasil yang sudah tercatat; '
  'tidak ada ujian yang diulang untuk membuat dokumen ini. 25 November 2026.')

h1('Ringkasan dalam satu halaman')
p('Kemendag menerima laporan distribusi beras dari para distributor lewat INATRADE. Laporan ini berguna, tetapi punya '
  'tiga kekurangan: pelapornya sedikit, laporannya sering bolong, dan isinya hanya sebagian kecil dari pasar beras. '
  'Selain itu, tidak ada angka resmi stok beras total sesudah 2023. Dari situ muncul tiga pertanyaan, dan masing-masing '
  'dijawab oleh satu pekerjaan (Gambar 1).')
gbr('g01_peta', 'Peta besar: tiga pertanyaan, tiga pekerjaan, tiga hasil.')
n('**Menambal laporan bolong.** Dari 79 cara yang diadu, yang paling tepat justru yang paling sederhana: mengisi bulan '
  'yang kosong dengan garis lurus di antara laporan sebelum dan sesudahnya. Dengan cara ini, total beras per wilayah '
  '(Jawa, Sumatera, pulau lain) hanya meleset sekitar 2%, sedangkan cara koreksi biasa meleset sekitar 15%.')
n('**Menghitung stok.** Model memperkirakan stok beras total Indonesia akhir September 2026 sekitar **14,2 juta ton**, '
  'dengan kisaran 11,3–18,6 juta ton. Kisarannya lebar karena tidak ada survei stok sesudah 2023 untuk mengecek angkanya.')
n('**Mengecek jalur kiriman.** INATRADE membantu menebak jalur beras antarprovinsi versi BPS, tetapi tidak mewakili dari '
  'provinsi mana beras berasal, karena kiriman antarprovinsi di INATRADE hanya berasal dari 26 perusahaan.')

# --------------------------------------------------------------- 1 data
h1('1. Datanya apa')
p('Ada satu data utama dan beberapa data pembanding. Data utama adalah laporan INATRADE. Data pembanding dipakai untuk '
  'mengecek dan melengkapi INATRADE.')
tabel([
    ['Data', 'Isinya', 'Dipakai untuk'],
    ['Laporan INATRADE (Kemendag)', 'Tiap perusahaan, tiap bulan: stok awal, beras masuk (pengadaan), beras keluar (penyaluran), '
     'stok akhir, provinsi tujuan, harga jual. Jan 2024–Sep 2026, 91 perusahaan beras', 'Semua pekerjaan'],
    ['Produksi padi (BPS)', 'Produksi per provinsi per bulan; dikali 0,5762 supaya jadi beras', 'Model stok (beras masuk)'],
    ['Konsumsi beras (BPS, Susenas)', 'Konsumsi rumah tangga per provinsi', 'Model stok (beras keluar)'],
    ['Survei stok beras', 'SCBN BPS Jun 2022 (9,71 juta ton), SSBAT Des 2022 (4,06) dan Des 2023 (4,13)', 'Model stok (patokan level)'],
    ['Stok BULOG', 'Angka publik dan laporan BULOG di INATRADE', 'Model stok (komponen BULOG)'],
    ['Pola Distribusi Perdagangan Beras (BPS)', 'Daftar provinsi asal dan tujuan perdagangan tiap provinsi, edisi 2024 dan 2025',
     'Mengecek jalur kiriman'],
], [4.2, 8.6, 3.6])

h2('Kondisi laporan INATRADE')
p('Sebelum dipakai, laporan INATRADE diperiksa dulu. Ada tiga hal yang paling berpengaruh pada semua pekerjaan berikutnya.')
gbr('g02_pelapor', 'Jumlah perusahaan beras yang melapor per bulan.')
baca('garis biru adalah jumlah perusahaan yang melapor tiap bulan. Sepanjang 2024 hanya 11–15 perusahaan, lalu sejak '
     'Oktober–November 2024 melonjak ke sekitar 50. Garis tegak membagi waktu ke tiga blok yang nanti dipakai untuk menguji '
     'metode (dijelaskan di bagian 2).')
p('Akibatnya, total beras di INATRADE bisa naik hanya karena lebih banyak perusahaan yang melapor, bukan karena berasnya '
  'bertambah. Total mentah tidak bisa langsung dibaca sebagai tren.')
gbr('g03_kualitas', 'Kiri: panjang laporan bolong. Kanan: apakah stok awal cocok dengan stok akhir bulan sebelumnya.')
baca('grafik kiri menghitung lubang di tengah, yaitu bulan kosong padahal perusahaan masih melapor sebelum dan sesudahnya. '
     'Kebanyakan lubangnya hanya 1 bulan (83 lubang). Grafik kanan: stok awal sebuah perusahaan seharusnya sama dengan stok '
     'akhirnya bulan lalu. Itu hanya terjadi di 76% pasangan laporan, dan 12% beda lebih dari seperempat.')
p('Dua hal ini penting nanti: lubang yang pendek membuat tebakan dari laporan tetangga cukup akurat, sedangkan stok yang '
  'sering tidak nyambung membuat cara menambal yang mengandalkan rumus stok kurang berguna.')
gbr('g04_cakupan', 'Penyaluran seluruh pelapor INATRADE dibanding konsumsi beras rumah tangga.')
baca('kotak abu-abu adalah 100% konsumsi beras rumah tangga menurut BPS. Bagian biru adalah porsi yang disalurkan semua '
     'pelapor INATRADE: hanya sekitar 2–3%.')
p('Artinya, sebagus apa pun INATRADE ditambal, ia tetap hanya memotret sebagian kecil pasar. INATRADE cocok untuk melihat '
  'naik-turun di antara pelapornya sendiri, bukan untuk mengukur besarnya pasar beras.')

# --------------------------------------------------------------- 2 menambal
h1('2. Pekerjaan 1: menambal laporan yang bolong')
h2('Kenapa perlu ditambal')
p('Kalau sebuah perusahaan besar tidak melapor di satu bulan, total wilayahnya turun drastis di bulan itu, padahal berasnya '
  'tidak hilang. Supaya total per bulan bisa dibandingkan, laporan yang bolong perlu ditebak. Pertanyaannya: ditebak dengan '
  'cara apa, dan seberapa tepat?')

h2('Cara mengujinya: membuat soal latihan dari data sendiri')
p('Nilai laporan yang benar-benar hilang tidak pernah diketahui, jadi tidak bisa dicek langsung. Jalan keluarnya: buat soal '
  'latihan dari laporan yang ada (Gambar 5).')
gbr('g05_simulasi', 'Ilustrasi cara menguji (bukan data asli). Tiap kotak = laporan satu perusahaan di satu bulan.')
n('Mulai dari data asli, yang sudah punya lubang (kotak putih). Lubang asli ini tidak bisa dinilai karena jawabannya tidak ada.')
n('Hapus sebagian laporan yang ada (oranye), dengan pola yang meniru pola bolong sebenarnya: ada yang di tengah, ada yang di '
  'bulan terakhir seperti laporan yang belum masuk.')
n('Suruh metode menebak kotak oranye, lalu jumlahkan per wilayah per bulan dan bandingkan dengan total aslinya (hijau). '
  'Karena kotak oranye sebenarnya ada nilainya, kita tahu persis berapa melesetnya.')
p('Langkah ini diulang 500 kali dengan pola hapus yang berbeda-beda, supaya hasilnya tidak kebetulan.')
p('Waktu juga dibagi tiga, seperti latihan, try out, dan ujian:')
b('**Blok penyetelan (Jan 2024–Jun 2025):** dipakai untuk memilih metode terbaik.')
b('**Blok kalibrasi (Jul–Des 2025):** dipakai untuk menyetel seberapa lebar kisaran tebakan.')
b('**Blok ujian akhir (Jan–Sep 2026):** metode yang sudah dipilih diuji satu kali saja. Hasil inilah yang dilaporkan. '
  'Karena metodenya dikunci sebelum ujian, skor ujian tidak bisa ikut memengaruhi pilihan metode.')

h2('Metode yang diadu')
p('Ada 79 kombinasi, dari yang paling sederhana sampai machine learning: interpolasi (garis lurus), meniru pertumbuhan '
  'perusahaan sejenis, empat jenis regresi, quantile regression forest, CatBoost, dan MRP, ditambah pilihan seperti bobot, '
  'penggabung, dan koreksi rentang. Semuanya harus mengalahkan **pembanding P***, yaitu cara paling sederhana yang biasa '
  'dipakai: total yang melapor dikali rasio jumlah perusahaan aktif terhadap jumlah yang melapor (Gambar 6, kanan).')
gbr('g06_metode', 'Ilustrasi dua cara menebak (angka contoh). Kiri: metode yang akhirnya terpilih. Kanan: pembanding P*.')
baca('di kiri, sebuah perusahaan tidak melapor di bulan 4 dan 5. Interpolasi mengisinya dengan garis lurus dari laporan '
     'bulan 3 ke bulan 6. Di kanan, 8 dari 10 perusahaan melapor dengan total 800 ton. P* menganggap 2 perusahaan yang hilang '
     'sama dengan rata-rata, jadi totalnya dikali 10/8 menjadi 1.000 ton. Kalau yang hilang ternyata perusahaan kecil, '
     'tebakan P* kebanyakan (total aslinya 920 ton); kalau yang hilang perusahaan besar, tebakannya kekurangan.')

h2('Cara menilai tebakan')
p('Tiap metode tidak hanya memberi satu angka, tetapi juga kisaran: misalnya "totalnya sekitar 100 ton, kemungkinan besar '
  'antara 95 dan 105". Karena itu dinilai dengan **CRPS**, ukuran yang sekaligus melihat seberapa dekat tebakan ke nilai '
  'asli dan seberapa wajar lebar kisarannya (Gambar 7).')
gbr('g07_crps', 'Ilustrasi CRPS (angka contoh). Garis hitam = nilai asli; tiap kurva = satu tebakan beserta kisarannya.')
baca('tebakan A dekat dan yakin, jadi CRPS-nya paling kecil (paling bagus). Tebakan B yakin tapi meleset, jadi dihukum '
     'paling berat. Tebakan C tepat di tengah tapi ragu-ragu (kurvanya lebar), jadi juga dihukum. Makin kecil CRPS, makin bagus.')
p('Supaya lolos, metode harus lulus semua syarat berikut. Syarat ini ditulis dan dikunci sebelum ujian dijalankan:')
b('galatnya paling tidak 10% lebih kecil dari P*, dan menang di hampir semua bulan, bukan cuma rata-ratanya;')
b('tidak cenderung kebanyakan atau kekurangan: rata-rata kemelesetannya (bias) paling banyak 3%;')
b('kisaran 90%-nya memang memuat nilai asli sekitar 90% dari waktu (minimal 80%);')
b('arah naik-turun bulanannya benar di paling tidak 80% bulan;')
b('di ujian akhir tidak memburuk lebih dari 20% dibanding saat penyetelan.')

h2('Hasilnya')
p('Metode yang terpilih adalah **interpolasi** dengan kisaran yang dilebarkan memakai data blok kalibrasi (koreksi '
  'konformal). Hasil ujian akhirnya ada di Gambar 8 dan 9.')
gbr('g08_u1', 'Hasil ujian akhir Jan–Sep 2026 per tingkat.')
baca('grafik kiri: batang biru adalah kemelesetan metode terpilih, batang abu-abu kemelesetan pembanding P*. Di tingkat '
     'wilayah, metode meleset sekitar 2,1%, sedangkan P* sekitar 14,5%. Grafik kanan: titik menunjukkan seberapa sering '
     'kisaran 90% memuat nilai asli; garis di sekitarnya adalah ketidakpastian karena jumlah datanya terbatas. Syaratnya, '
     'garis itu harus memotong garis 90% dan titiknya di kanan 80%.')
gbr('g09_galat', 'Sebaran kemelesetan di tingkat wilayah untuk semua soal ujian.')
baca('makin tinggi dan sempit puncak di sekitar 0, makin tepat. Tebakan metode terpilih (biru) menumpuk rapat di sekitar 0. '
     'Tebakan P* (abu-abu) jauh lebih menyebar, dan ekor kirinya lebih panjang: P* lebih sering kekurangan banyak.')
tabel([
    ['Tingkat', 'Status', 'Penjelasan singkat'],
    ['Wilayah (Jawa, Sumatera, pulau lain)', '**Lolos semua syarat**', 'Target utama. Galat 86% lebih kecil dari P*, bias hampir 0, arah benar 96%'],
    ['Provinsi (hanya 7 provinsi)', 'Lolos dengan catatan', 'Hanya 7 provinsi punya minimal 3 pelapor. Galat memburuk 13% atau 28% dibanding penyetelan, tergantung acuannya'],
    ['Nasional', 'Belum bisa diputuskan', 'Syarat lain lolos, tapi hanya 19 sel-bulan: terlalu sedikit untuk memutuskan syarat kisaran 90%'],
], [4.4, 3.6, 8.4])

h2('Kenapa hasilnya begitu')
gbr('g10_kenapa', 'Kemelesetan per perusahaan dan setelah dijumlah per wilayah.', lebar=14.5)
p('**Kenapa cara paling sederhana menang.**')
b('Kebanyakan lubang hanya 1 bulan (Gambar 3). Untuk lubang sependek itu, laporan bulan sebelum dan sesudahnya adalah '
  'petunjuk terbaik, dan interpolasi memakai keduanya secara langsung.')
b('Metode machine learning butuh banyak contoh yang mirip untuk belajar. Pelapor beras hanya sekitar 90 perusahaan dengan '
  'riwayat pendek, jadi tidak ada cukup contoh. QRF sempat hampir menyamai, tetapi selisihnya terlalu tipis, sehingga '
  'aturan "kalau selisih tipis, pilih yang lebih sederhana" memilih interpolasi.')
p('**Kenapa per perusahaan melesetnya sekitar 20%, tapi per wilayah cuma 2%** (Gambar 10).')
b('Laporan satu perusahaan memang naik-turun cukup besar dari bulan ke bulan (setengahnya berubah lebih dari 27%), jadi '
  'tebakan untuk satu perusahaan wajar meleset sekitar 20%.')
b('Tetapi dalam satu wilayah, hanya sedikit perusahaan yang bolong sekaligus. Sebagian besar total wilayah berasal dari '
  'laporan yang memang ada (nilainya pasti). Kemelesetan beberapa tebakan juga sebagian saling menutup: ada yang kelebihan, '
  'ada yang kekurangan. Hasilnya total wilayah hanya meleset sekitar 2%.')
p('**Kenapa P* jauh lebih buruk.** P* menganggap perusahaan yang tidak melapor sama dengan rata-rata. Di beras, '
  'ukuran perusahaan sangat timpang (di Jawa, 5 perusahaan memegang 92% penyaluran), jadi anggapan itu sering salah besar. '
  'Begitu satu perusahaan besar bolong, P* kekurangan banyak; itulah ekor kiri yang panjang di Gambar 9.')
p('**Kenapa provinsi dan nasional lebih lemah.** Di tingkat provinsi, tiap sel hanya berisi sedikit perusahaan, jadi satu '
  'tebakan yang meleset langsung terasa; hanya 7 provinsi yang cukup pelapornya untuk dinilai. Di tingkat nasional, '
  'jumlah bulannya sedikit, jadi syarat kisaran belum bisa diputuskan, walaupun angkanya bagus.')
p('**Batas arti "lolos".** Lolos berarti metode bisa menutup laporan yang bolong secara konsisten. Ini tidak membuktikan '
  '90 pelapor itu mewakili pasar beras; ingat cakupannya hanya 2–3% (Gambar 4).')

# --------------------------------------------------------------- 3 stok
h1('3. Pekerjaan 2: menghitung stok beras total')
h2('Idenya: neraca masuk dan keluar')
p('Stok beras total (di rumah tangga, penggilingan, pedagang, BULOG, hotel-restoran) tidak pernah diukur tiap bulan. '
  'Yang ada hanya beberapa survei sesekali. Jadi stok dihitung seperti saldo rekening: saldo bulan ini = saldo bulan lalu '
  '+ uang masuk − uang keluar (Gambar 11). Ini dihitung untuk tiap provinsi, tiap bulan, mulai Juni 2022.')
gbr('g11_neraca', 'Neraca stok beras satu provinsi.')
p('Masalahnya, hampir semua angka di neraca ini tidak pasti: produksi bisa kurang tercatat, konsumsi di luar rumah tangga '
  'tidak diketahui persis, kiriman antarprovinsi tidak diukur. Karena itu dipakai **model Bayesian**: semua angka yang tidak '
  'pasti diberi kisaran yang masuk akal, lalu model mencari kombinasi yang paling cocok dengan semua data pengukur sekaligus '
  '(survei stok, stok BULOG, stok pedagang INATRADE, harga beras). Hasilnya bukan satu angka, tetapi kisaran kemungkinan.')
p('Setiap data pengukur dianggap boleh punya kesalahan sendiri (bias). Contohnya, sebuah survei boleh konsisten terlalu '
  'rendah. Model memperkirakan besar bias itu, bukan menelan angka survei mentah-mentah.')

h2('Kenapa stok naik-turun sepanjang tahun')
gbr('g12_musim', 'Atas: produksi beras per bulan dibanding konsumsi. Bawah: stok nasional hasil model.')
baca('di grafik atas, kalau batang biru (produksi) lebih tinggi dari garis oranye (konsumsi), ada beras yang tersisa dan '
     'stok naik. Saat panen raya Maret–April, produksi hampir dua kali konsumsi, sehingga stok naik tajam. Akhir sampai awal '
     'tahun, produksi lebih rendah dari konsumsi, sehingga stok terpakai dan turun. Grafik bawah menunjukkan stok mengikuti '
     'pola itu.')

h2('Hasilnya')
gbr('g13_stok', 'Stok beras total nasional dan bagian BULOG, plus prakiraan Okt–Des 2026.')
baca('garis biru adalah perkiraan paling mungkin (median); pita biru muda adalah kisaran 90%: stok sebenarnya '
     'kemungkinan besar ada di dalam pita itu. Garis oranye adalah bagian BULOG. Garis putus-putus di ujung adalah prakiraan.')
b('**Akhir September 2026: 14,2 juta ton** (kisaran 11,3–18,6), hampir sama dengan September 2025 (14,4).')
b('Pola tahunan berulang: terendah Januari–Februari, naik setelah panen Maret–April.')
b('Stok BULOG naik dari sekitar 2 juta ton (2024) ke sekitar 4,5–6 juta ton (2026). Jadi, dibanding tahun-tahun '
  'sebelumnya, porsi stok yang dipegang pemerintah lebih besar.')
gbr('g14_komposisi', 'Kiri: siapa yang memegang stok. Kanan: stok per pulau. Akhir September 2026.')
baca('garis tipis di tiap batang adalah kisaran 90%. Lebih dari separuh stok ada di rumah tangga (7,6 juta ton), lalu '
     'BULOG (4,65). Kisaran BULOG sempit karena stok BULOG ada angka resminya; kisaran rumah tangga lebar karena tidak ada '
     'yang mengukurnya langsung. Per pulau, Jawa memegang sekitar separuh stok nasional.')
p('**Prakiraan:** Oktober 13,6, November 12,5, Desember 11,1 juta ton. Stok turun karena Oktober–Desember di luar musim '
  'panen. Stok Desember cukup untuk sekitar 4,1 bulan konsumsi. Provinsi yang paling berisiko kekurangan di Desember: Papua '
  'Tengah, Kepulauan Riau, Riau, dan Bangka Belitung. Prakiraan ini belum pernah diuji dengan meramal periode lalu.')

h2('Bagaimana model diuji')
gbr('g15_validasi', 'Model diminta menebak angka tiga survei stok, termasuk satu yang disembunyikan.')
baca('batang gelap adalah angka survei. Batang biru muda adalah tebakan model kalau semua survei dipakai. Batang biru tua '
     'adalah ujiannya: survei SSBAT Des 2022 disembunyikan dari model, lalu model diminta menebaknya. Hasilnya 4,40 juta ton '
     '(kisaran 3,43–5,59), dan angka survei 4,06 masuk dalam kisaran itu, jadi lolos.')
p('Hal penting yang perlu dipahami dari gambar ini:')
b('**Dua jenis survei tidak cocok satu sama lain.** SCBN BPS Juni 2022 mencatat 9,71 juta ton, sedangkan SSBAT enam bulan '
  'kemudian hanya 4,06. Stok tidak mungkin turun separuh dalam enam bulan menurut neraca. Model memilih level yang cocok dengan '
  'SCBN dan dengan neraca, sehingga survei SSBAT terbaca konsisten sekitar separuh stok model. Mana yang sebenarnya benar '
  'belum bisa dipastikan.')
b('**Yang diuji adalah perubahan stok, bukan levelnya.** Saat Des 2022 disembunyikan, model menyetel "SSBAT membaca sekitar '
  'separuh" dari survei Des 2023, lalu menghitung mundur setahun memakai neraca. Lolosnya ujian ini berarti neraca selama '
  '2023 masuk akal, bukan bahwa 14,2 juta ton pasti benar.')
b('Pemeriksaan lain: konsumsi total 2024 menurut model 29,79 juta ton, hampir sama dengan angka BPS 29,80 juta ton yang '
  'tidak dipakai saat menghitung.')

h2('Kenapa angkanya segitu, dan seberapa yakin')
gbr('g16_kepekaan', 'Stok akhir Sep 2026 kalau asumsi model diganti.')
baca('tiap baris adalah versi model dengan asumsi berbeda. Titik = perkiraan, garis = kisaran 90% (hanya ada untuk tiga '
     'versi pertama).')
b('Aturan yang paling menentukan adalah "stok swasta tidak boleh negatif". Kalau aturan ini dipasang per provinsi, beberapa '
  'provinsi yang kekurangan beras terlihat stoknya minus karena model kiriman antarprovinsinya masih kasar, lalu model '
  'menaikkan seluruh level supaya tidak minus: hasilnya 16,8. Karena itu aturan dipasang per pulau (14,2).')
b('Tanpa data INATRADE, perkiraan naik ke 15,1. Artinya data stok pedagang dari INATRADE menarik perkiraan sedikit ke bawah.')
b('Kesimpulan: angka 14,2 harus selalu dibaca bersama kisarannya dan asumsinya. Yang paling bisa dipercaya adalah pola '
  'naik-turunnya, bukan angka persisnya.')

# --------------------------------------------------------------- 4 jalur
h1('4. Pekerjaan 3: mengecek jalur kiriman antarprovinsi')
h2('Pertanyaan dan caranya')
p('INATRADE mencatat ke provinsi mana perusahaan mengirim beras. BPS menerbitkan survei Pola Distribusi Perdagangan Beras '
  'yang menyebut, untuk tiap provinsi, dari provinsi mana ia membeli dan ke mana ia menjual. Pertanyaannya: apakah peta '
  'kiriman di INATRADE cocok dengan peta BPS?')
p('Caranya seperti tebak-tebakan. Ada 34 provinsi, jadi ada 1.122 pasangan "provinsi A mengirim ke provinsi B". Kunci '
  'jawabannya adalah edisi BPS 2025, yang memuat 104 jalur. Edisi ini disembunyikan sampai cara penilaiannya dikunci. '
  'Tiga penebak diadu:')
b('**INATRADE saja:** jalur yang pernah dilaporkan perusahaan.')
b('**BPS 2024 apa adanya:** anggap jalur tahun lalu tetap sama.')
b('**Gabungan:** jalur BPS 2024 yang juga muncul di INATRADE ditaruh paling atas, lalu jalur BPS 2024 lainnya, lalu jalur '
  'yang hanya ada di INATRADE.')
p('Penilaiannya memakai **average precision**: tiap penebak mengurutkan 1.122 pasangan dari yang paling yakin, dan nilainya '
  'tinggi kalau jalur yang benar berkumpul di urutan atas. Ada dua syarat: gabungan harus lebih baik dari dua penebak '
  'lainnya, dan urutan provinsi asal terbesar di INATRADE harus mirip dengan BPS (korelasi minimal 0,6).')

h2('Hasilnya')
gbr('g17_ap', 'Ketepatan tiap penebak (average precision).')
baca('makin panjang batang, makin tepat urutan tebakannya. Tebak asal hanya mendapat 0,093. Gabungan paling tinggi (0,563), '
     'di atas BPS 2024 saja (0,480). Selisih ini cukup jelas, bukan kebetulan, jadi syarat pertama lolos.')
gbr('g18_bertahan', 'Dari tiap kelompok pasangan provinsi, berapa persen yang benar-benar jadi jalur di BPS 2025.')
baca('ini menjelaskan kenapa gabungan menang. Jalur yang ada di BPS 2024 dan juga dicatat INATRADE, 74%-nya muncul lagi di '
     '2025. Jalur yang hanya ada di BPS 2024: 50%. Jalur yang hanya ada di INATRADE: 23%. Jadi INATRADE berguna untuk '
     'menandai jalur BPS mana yang paling mungkin bertahan.')
gbr('g19_asal', 'Kiri: dari provinsi mana kiriman antarprovinsi INATRADE berasal. Kanan: provinsi asal terbanyak menurut BPS 2025.')
baca('di kiri, hampir semua volume kiriman antarprovinsi INATRADE berasal dari tiga provinsi: Jawa Timur (67%), DKI Jakarta, '
     'dan Jawa Tengah. Di kanan, BPS mencatat banyak provinsi asal lain yang penting, seperti Sulawesi Selatan, Lampung, '
     'dan Jawa Barat; batang abu-abu adalah provinsi yang sama sekali tidak punya kiriman antarprovinsi di INATRADE.')
p('Karena itu syarat kedua gagal: korelasi urutan provinsi asal hanya 0,20, jauh di bawah 0,6 (sebagai pembanding, BPS 2024 '
  'dan BPS 2025 berkorelasi 0,89). Penyebabnya:')
b('kiriman antarprovinsi di INATRADE hanya berasal dari 26 perusahaan di 9 provinsi;')
b('"asal" di INATRADE adalah provinsi kantor perusahaan, misalnya kantor pusat di DKI Jakarta, padahal berasnya bisa saja '
  'berasal dari sentra produksi di provinsi lain.')
p('**Kesimpulan:** INATRADE berguna sebagai penguat peta jalur BPS, tetapi tidak boleh dipakai untuk mengatakan dari mana '
  'beras antarprovinsi berasal. Catatan: ini baru satu tahun pembanding (2024 ke 2025).')

# --------------------------------------------------------------- 5 rangkuman
h1('5. Rangkuman: apa yang sudah bisa dan belum bisa dikatakan')
tabel([
    ['Topik', 'Sudah bisa dikatakan', 'Belum bisa dikatakan'],
    ['Menambal laporan', 'Interpolasi menutup laporan bolong dengan tepat di tingkat wilayah (meleset ±2%), jauh lebih baik dari koreksi biasa',
     'Bahwa pelapor INATRADE mewakili pasar beras (cakupannya hanya 2–3%)'],
    ['Stok beras', 'Pola naik-turun stok sepanjang tahun; stok akhir Sep 2026 sekitar 14,2 juta ton dengan kisaran 11,3–18,6; porsi BULOG naik',
     'Angka stok persisnya, karena tidak ada survei stok sesudah 2023 dan dua jenis survei saling tidak cocok'],
    ['Jalur kiriman', 'INATRADE menguatkan tebakan jalur BPS', 'Bahwa INATRADE menggambarkan provinsi asal beras'],
], [3.2, 6.8, 6.4])

h1('6. Kamus istilah')
tabel([
    ['Istilah', 'Artinya'],
    ['Median', 'Angka tengah: separuh kemungkinan di bawahnya, separuh di atasnya. Dipakai sebagai "perkiraan paling mungkin"'],
    ['Kisaran 90%', 'Rentang yang menurut model memuat nilai sebenarnya dengan peluang 90%'],
    ['Interpolasi', 'Mengisi bulan kosong dengan garis lurus antara laporan sebelum dan sesudahnya'],
    ['Pembanding P*', 'Cara koreksi sederhana: total yang melapor dikali rasio perusahaan aktif terhadap yang melapor'],
    ['CRPS', 'Skor tebakan yang berbentuk kisaran: menilai jarak ke nilai asli sekaligus lebar kisaran. Makin kecil makin baik'],
    ['Bias', 'Kecenderungan tebakan konsisten kebanyakan (+) atau kekurangan (−)'],
    ['Koreksi konformal', 'Melebarkan kisaran tebakan berdasarkan seberapa sering tebakan meleset di data kalibrasi, supaya kisaran 90% benar-benar memuat nilai asli 90% dari waktu'],
    ['Blok penyetelan, kalibrasi, ujian', 'Pembagian waktu seperti latihan, try out, dan ujian; ujian hanya dijalankan sekali'],
    ['Model Bayesian', 'Model yang menggabungkan banyak sumber data yang masing-masing tidak pasti, dan hasilnya berupa kisaran kemungkinan'],
    ['Average precision', 'Skor 0–1 untuk menilai urutan tebakan: tinggi kalau jawaban yang benar berkumpul di urutan atas'],
    ['Korelasi peringkat', 'Seberapa mirip dua urutan; 1 = urutannya sama persis, 0 = tidak berhubungan'],
], [4.2, 12.2])

d.save(f'{W}/penjelasan_beras.docx'); print('ok', NG[0], 'gambar')
