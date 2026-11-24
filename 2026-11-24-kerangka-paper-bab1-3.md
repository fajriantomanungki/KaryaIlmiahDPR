# Kerangka Paper — Bab 1 sampai Bab 3

**Judul:** Ketika Anggaran Menyusut, Siapa yang Dilindungi? Optimalisasi Transfer Fiskal Berbasis Risiko Penurunan Layanan Publik dalam Perspektif Keadilan Konstitusional

Kerangka ini disusun dari hasil analisis yang sudah berjalan (`output/siap/`). Setiap subbab berisi pokok yang perlu diuraikan, angka atau temuan yang bisa dipakai sebagai pijakan, dan sumber tabelnya. Rujukan pustaka yang disebut adalah titik awal dan **wajib diverifikasi** (tahun, judul, halaman) sebelum dipakai.

**Pesan utama paper (dipegang sejak Bab 1):** potongan TKDD 2026 tidak dirancang menurut kebutuhan. Siapa yang terlindungi lebih ditentukan oleh komposisi transfer daripada oleh kerentanan, dan penyangga fiskal daerah tidak meredam potongan. Efek pada luaran layanan belum terdeteksi dalam jangka pendek. Aturan pembagian yang lebih baik terutama mencegah layanan mundur, bukan mengangkat banyak orang ke atas lantai minimum.

---

## BAB 1 PENDAHULUAN

### 1.1 Latar Belakang

Alur argumen, dari umum ke khusus:

1. **Penyusutan transfer 2026 sebagai peristiwa fiskal besar.**
   - TKDD kab/kota turun 20,1% (Rp706,9 T → Rp564,7 T); 97% kab/kota dipotong, median 17,2%.
   - Penurunan tidak merata antarkomponen: DBH −60%, Dana Desa −64%, DAK fisik −70%, DAU hanya −3,5%.
   - Sumber: `37_deskriptif/T3_komposisi_tkdd.csv`, `T4_sebaran_potongan.csv`.
2. **Ketergantungan daerah pada transfer.**
   - Rata-rata TKDD 69% (tertimbang penduduk) dari pendapatan daerah; 89,7% pada kuartil paling rentan.
   - Implikasinya: potongan transfer hampir pasti menjadi potongan belanja.
3. **Layanan dasar masih timpang.**
   - Kuartil paling rentan: P0 15,8% vs 5,8%, RLS 7,2 vs 10,8 tahun, UHH 72,4 vs 75,7 tahun.
   - Peringkat kemiskinan menetap (korelasi peringkat 2021–2025 sebesar 0,99): wilayah yang rentan adalah wilayah yang sama dari tahun ke tahun.
4. **Persoalan konstitusional.**
   - Hak atas kesehatan dan pendidikan (Pasal 28H, 31) dan tanggung jawab negara atas fakir miskin (Pasal 34).
   - Hubungan keuangan pusat–daerah yang adil dan selaras (Pasal 18A ayat 2).
   - Dalam kerangka hak ekonomi-sosial: kewajiban realisasi progresif, larangan langkah mundur (non-retrogresi), dan inti minimum.
   - Pertanyaannya: ketika anggaran menyusut, apakah pembagian potongan menghormati prinsip-prinsip itu?
5. **Celah yang diisi.**
   - Kajian transfer di Indonesia umumnya menilai dampak transfer saat naik, bukan saat dipotong besar-besaran.
   - Jarang ada yang menautkan distribusi beban potongan dengan norma konstitusional secara terukur.
   - Belum ada penilaian aturan pembagian potongan pada tingkat kab/kota di bawah ketidakpastian efek anggaran.

> Catatan peneliti: buka dengan angka penyusutan (kuat dan baru), lalu tunjukkan bahwa yang rentan sekaligus paling bergantung dan paling tidak punya penyangga. Itu jembatan ke pertanyaan "siapa yang dilindungi".

### 1.2 Rumusan Masalah

- **RQ1.** Bagaimana beban potongan TKDD 2026 terdistribusi menurut kerentanan kab/kota, dan apa yang menentukan besarnya?
- **RQ2.** Seberapa besar potongan transfer diteruskan menjadi pengurangan belanja, dan apakah penyangga fiskal daerah meredamnya?
- **RQ3.** Apakah perubahan transfer berpengaruh terhadap luaran layanan (UHH, HLS, RLS, P0), dan siapa yang berisiko berada atau jatuh di bawah lantai layanan?
- **RQ4.** Aturan pembagian potongan seperti apa yang paling melindungi lantai layanan dan mencegah kemunduran, dan bagaimana pertukaran di antara keduanya?

### 1.3 Tujuan Penelitian

Satu tujuan untuk setiap RQ, ditambah satu tujuan metodologis: menguji apakah kebijakan dinamis berbasis HJB memberi perbaikan berarti dibanding aturan sederhana.

### 1.4 Hipotesis

| Kode | Hipotesis | Status hasil (untuk disesuaikan di Bab 4) |
|---|---|---|
| H1 | Besar potongan tidak mengikuti kerentanan (buta kebutuhan) | Didukung |
| H2 | Penyangga fiskal menurunkan pass-through potongan ke belanja | Tidak didukung |
| H3 | Potongan transfer menurunkan luaran layanan | Tak terdeteksi (1–2 tahun) |
| H4 | Aturan sederhana mendekati kinerja aturan optimal | Sebagian; bergantung perumusan efek |
| H5 | Ada batas potongan yang aman (titik patah) | Tidak ada titik patah |

> Catatan peneliti: hipotesis dirumuskan sebelum hasil. Di Bab 1 tulis sebagai dugaan, jangan sebagai temuan.

### 1.5 Kontribusi

1. **Empiris:**
   - Bukti tingkat kab/kota (508 unit) tentang siapa menanggung potongan transfer terbesar dalam satu dekade.
   - Temuan bahwa penyangga fiskal tidak bekerja.
2. **Metodologis:**
   - Menggabungkan pengukuran distribusi beban (indeks konsentrasi dan dekomposisi), identifikasi semi-kausal (shift-share, DML, proyeksi lokal), dan optimisasi keputusan di bawah ketidakpastian (minimax regret, HJB).
   - Hasil nol dilaporkan bersama efek minimum terdeteksi.
3. **Kebijakan dan hukum:**
   - Menerjemahkan prinsip lantai minimum dan non-retrogresi menjadi ukuran yang bisa dihitung dan dipakai menilai formula transfer.

### 1.6 Ruang Lingkup dan Batasan

- Unit: 508 dari 514 kab/kota; DKI Jakarta (6) tidak punya APBD/TKDD tingkat kab/kota.
- Periode: 2019–2026. Data 2026 berupa anggaran, bukan realisasi. Nilai nominal.
- Luaran yang diamati: UHH, HLS, RLS, P0. Mutu layanan dan SPM tidak diamati langsung.
- Efek anggaran terhadap layanan tidak teridentifikasi, sehingga analisis aturan bersifat simulasi bersyarat.

### 1.7 Sistematika Penulisan

Satu paragraf: Bab 2 teori dan kerangka konseptual; Bab 3 data dan metode; Bab 4 hasil; Bab 5 pembahasan dan implikasi konstitusional; Bab 6 simpulan dan rekomendasi.

---

## BAB 2 TINJAUAN PUSTAKA DAN KERANGKA KONSEPTUAL

### 2.1 Keadilan Konstitusional dan Hak atas Layanan Dasar

Pokok bahasan:
- Pasal 28H ayat 1, Pasal 31, Pasal 34 UUD 1945 sebagai dasar hak atas kesehatan, pendidikan, dan perlindungan fakir miskin.
- Pasal 18A ayat 2: hubungan keuangan pusat–daerah yang adil dan selaras.
- UU 1/2022 tentang Hubungan Keuangan Pusat dan Pemerintahan Daerah (HKPD): tujuan pemerataan, desain DAU berbasis kebutuhan, DBH berbasis daerah penghasil.
- Standar Pelayanan Minimal (PP 2/2018) sebagai bentuk normatif "lantai".
- Kovenan Hak Ekosob (diratifikasi UU 11/2005) dan Komentar Umum No. 3 (realisasi progresif, inti minimum, larangan langkah mundur yang disengaja), serta No. 13 (pendidikan) dan No. 14 (kesehatan).
- Tiga norma operasional yang dipakai paper:
  - **lantai minimum**: tidak ada penduduk di bawah standar dasar;
  - **non-retrogresi**: layanan tidak boleh mundur;
  - **prioritas bagi yang terburuk**: beban tidak jatuh pada yang paling rentan.

> Catatan: redaksi pasal dan status hukum komentar umum perlu diperiksa ahli hukum tata negara.

### 2.2 Desentralisasi Fiskal dan Desain Transfer

- Teori federalisme fiskal: fungsi pemerataan transfer dan kesenjangan fiskal vertikal dan horizontal (Oates 1972; Musgrave 1959; Boadway & Shah 2009).
- Tipologi transfer: bebas (DAU), bagi hasil (DBH), bersyarat (DAK), dan khusus (Dana Desa, Otsus).
  - Transfer bagi hasil mengikuti basis penerimaan, bukan kebutuhan, sehingga ikut naik-turun bersama siklus komoditas dan kebijakan pusat.
- Konsekuensi untuk paper: komposisi transfer menentukan paparan terhadap potongan. Ini menjadi dasar teoretis H1 dan dasar paparan shift-share.

### 2.3 Respons Pemerintah Daerah terhadap Guncangan Transfer

- *Flypaper effect*: belanja lebih responsif terhadap transfer daripada terhadap pendapatan sendiri (Hines & Thaler 1995; Gamkhar & Shah 2007).
- Asimetri respons: apakah pemda memotong belanja saat transfer turun sebanyak menaikkannya saat transfer naik (*ratchet* / *fiscal replacement*)?
- Peran tabungan dan SiLPA sebagai penyangga; pinjaman daerah yang terbatas di Indonesia.
- Bukti Indonesia: perilaku belanja, pajak, dan tabungan pemda pasca-desentralisasi (Lewis 2005); belanja modal daerah (Lewis & Oosterman 2009); dampak desentralisasi terhadap investasi publik lokal (Kis-Katos & Sjahrir 2017); kajian belanja publik Bank Dunia.
- Celah: hampir semua bukti berasal dari periode transfer naik.

### 2.4 Belanja Publik dan Luaran Layanan

- Hubungan belanja → luaran bersifat tertunda dan tidak langsung. UHH, RLS, dan HLS adalah variabel stok yang bergerak lambat; P0 lebih peka siklus ekonomi.
- Bukti campuran tentang elastisitas luaran kesehatan dan pendidikan terhadap belanja; peran efisiensi dan kapasitas.
- Implikasi metodologis: hasil nol jangka pendek harus dibaca bersama daya uji, bukan sebagai bukti tidak ada efek.

### 2.5 Keadilan Distributif dan Pengukurannya

- Kerangka normatif: utilitarian, prioritarian, maximin (Rawls 1971), pendekatan kapabilitas (Sen).
- Fungsi kesejahteraan Atkinson (1970): parameter ε sebagai tingkat keengganan terhadap ketimpangan, yang menjembatani prioritarianisme dan maximin.
- Pengukuran distribusi beban: indeks konsentrasi dan dekomposisinya (Wagstaff, van Doorslaer & Watanabe 2003; Erreygers 2009).
- Penautan ke Bagian 2.1: lantai minimum ≈ kepedulian pada kekurangan di bawah ambang; non-retrogresi ≈ hukuman atas kemunduran; prioritas ≈ ε tinggi.

### 2.6 Alokasi Optimal di Bawah Ketidakpastian

- Kontrol optimal stokastik dan persamaan Hamilton–Jacobi–Bellman (HJB) (Fleming & Soner 2006): anggaran sebagai kontrol, layanan sebagai keadaan, harga bayangan anggaran sebagai pengikat antarwilayah (dekomposisi Lagrange).
- Ketidakpastian model: kontrol robust (Hansen & Sargent 2008); keputusan minimax regret (Savage 1951); optimisasi robust (Ben-Tal, El Ghaoui & Nemirovski 2009).
- Aturan sederhana vs optimisasi: formula yang transparan dan tahan terhadap salah spesifikasi sering mendekati kinerja aturan optimal yang peka parameter.
- Posisi paper: HJB dipakai sebagai tolok ukur dinamis, bukan sebagai resep.

### 2.7 Penelitian Terdahulu dan Celah Penelitian

Tabel ringkas (penulis, unit, periode, metode, temuan, keterbatasan), dikelompokkan menjadi:
1. distribusi dan pemerataan transfer di Indonesia;
2. respons fiskal pemda;
3. belanja dan luaran layanan;
4. pendekatan hak dan keadilan dalam anggaran.

Celah yang ditegaskan:
1. episode potongan besar belum dikaji;
2. distribusi beban potongan belum ditautkan ke norma konstitusional;
3. belum ada evaluasi aturan pembagian potongan pada tingkat kab/kota dengan ketidakpastian eksplisit.

### 2.8 Kerangka Konseptual dan Turunan Hipotesis

Rantai yang digambarkan dalam diagram:

> Kebijakan pusat (penyusutan TKDD) → **komposisi transfer** (DBH, Dana Desa, DAK, DAU) → **besar potongan per kab/kota** [H1] → **penyangga fiskal** (PAD, SiLPA, pembiayaan) → **pass-through ke belanja** (modal, barang-jasa, pegawai) [H2] → **luaran layanan** (UHH, HLS, RLS, P0) [H3] → **norma konstitusional**: lantai minimum, non-retrogresi, prioritas yang terburuk → **aturan pembagian alternatif** [H4, H5]

Tulis satu paragraf per panah: mekanisme teorinya dan hipotesis yang diturunkan.

---

## BAB 3 METODOLOGI PENELITIAN

### 3.1 Desain Penelitian

Penelitian kuantitatif dengan panel kab/kota, dalam tiga lapis:
1. **deskriptif-distributif**: siapa menanggung (RQ1);
2. **semi-kausal**: pass-through dan efek layanan (RQ2–RQ3);
3. **normatif-simulatif**: evaluasi aturan di bawah ketidakpastian, dengan HJB sebagai pembanding (RQ4).

Tabel pemetaan (cantumkan di naskah):

| RQ | Hipotesis | Metode | Skrip | Tabel keluaran utama |
|---|---|---|---|---|
| RQ1 | H1 | Statistik deskriptif, indeks konsentrasi, dekomposisi komponen, regresi dengan wild cluster bootstrap | `37_deskriptif.py`, `31_siapa_menanggung.py` | `T2`–`T5` (31), `T1`–`T8` (37) |
| RQ2 | H2 | Beda pertama, shift-share, double machine learning, uji asimetri | `32_penyangga_passthrough.py` | `T1`–`T4` (32) |
| RQ3 | H3 | Proyeksi lokal, efek minimum terdeteksi, uji pra-tren, uji mundur ramalan, risiko empiris-Bayes | `33_risiko_layanan.py` | `T1`–`T6` (33) |
| RQ4 | H4, H5 | Optimisasi berbasis skenario, minimax regret, kurva besar potongan; HJB | `34_aturan_alokasi.py`, `36_hjb_kabkota.py` | `T1`–`T7` (34), `T1`–`T2` (36) |

### 3.2 Data dan Sumber

- APBD dan TKDD 2019–2026 (DJPK Kemenkeu): pendapatan, belanja per jenis, pembiayaan, rincian komponen TKDD.
- Indikator BPS kab/kota: UHH, HLS, RLS, P0/P1/P2, PPK, TPT, PDRB per kapita, penduduk, IKK.
- Isian manual pemilik data untuk sel yang kosong (4.545 sel).
- Padanan kode DJPK–BPS, termasuk pemekaran Papua.
- Unit akhir: 508 kab/kota (279,9 juta jiwa); seri 2021–2025 lengkap untuk 450.

### 3.3 Pengolahan Data

Prinsip:
- tidak ada imputasi, interpolasi, atau proyeksi;
- sel yang sudah terisi tidak ditimpa;
- setiap koreksi tercatat.

Langkah:
1. Penggabungan isian.
2. Penyamaan satuan: koreksi kelipatan 1.000 bila sejalan dengan deret sendiri atau pola provinsi (428 sel).
3. Nilai ekstrem Papua pegunungan dipertahankan dengan tanda (25 sel).
4. Pengembalian sel rusak (7 sel).
5. Pemeriksaan konsistensi.
6. Klasifikasi kelengkapan.

Masalah data yang harus dilaporkan:
- patahan sumber UHH di enam kab/kota Papua (dikeluarkan dari model deret waktu);
- kenaikan UHH NTB 2023;
- sumber isian manual yang belum tercatat.

Sumber: `Data_Siap_Analisis.xlsx` (sheet `Ringkasan`, `Log_Koreksi`).

### 3.4 Definisi Operasional Variabel

| Variabel | Definisi | Satuan |
|---|---|---|
| Kerentanan (V) | Rata-rata z dari P0, −UHH, −HLS, −RLS 2025, dibakukan | SD |
| Potongan TKDD | (TKDD 2025 − TKDD 2026) / TKDD 2025; juga per kapita | %, ribu Rp/jiwa |
| Penyangga | (PAD + SiLPA) / belanja total | % |
| Ketergantungan | TKDD di APBD / pendapatan daerah | % |
| Paparan komposisi | Porsi DBH + DAK fisik + Dana Desa dalam TKDD tahun sebelumnya | % |
| Pass-through | Perubahan belanja per kapita per Rp1 perubahan TKDD per kapita | Rp/Rp |
| Lantai layanan | Persentil ke-10 distribusi 2025 (P0: persentil ke-90); uji P05 dan P20 | — |
| Mundur (retrogresi) | Layanan 2028 di bawah 2025 lebih dari 0,05 SD | % penduduk |
| Indeks biaya | Indeks Kemahalan Konstruksi | indeks |

### 3.5 Metode Analisis

#### 3.5.1 Analisis deskriptif (RQ1, konteks)
- Statistik deskriptif, rata-rata tertimbang penduduk.
- Tren 2020–2025 menurut kuartil kerentanan tetap.
- Komposisi TKDD, sebaran potongan, potongan per provinsi.
- Tipologi kerentanan ganda (miskin, bergantung, penyangga tipis).

#### 3.5.2 Distribusi beban potongan (RQ1, H1)
- Indeks konsentrasi beban: $C = \frac{2}{\mu}\,\mathrm{cov}_w(L_i, R_i)$, dengan $L_i$ beban per kapita, $R_i$ peringkat pecahan kerentanan berbobot penduduk, dan $\mu$ rata-rata beban tertimbang.
- Selang dengan bootstrap per provinsi.
- Dekomposisi per komponen: kontribusi tiap komponen = (pangsa beban × indeks konsentrasinya).
- Regresi persen potongan pada V, bertahap: tambahkan ukuran dan jenis, komposisi transfer, lalu ketergantungan dan penyangga. Penurunan koefisien V dan kenaikan R² menunjukkan peran komposisi.
- Inferensi: galat baku per provinsi (37 kelompok), wild cluster bootstrap (Rademacher, nol dipaksakan).

#### 3.5.3 Pass-through dan penyangga (RQ2, H2)
- Beda pertama dengan efek tahun: $\Delta Y_{it} = \beta\,\Delta T_{it} + \gamma_t + \varepsilon_{it}$, per kapita dengan penduduk 2025 tetap.
- Paparan shift-share: $Z_{it} = \sum_k s_{ik,t-1}\, g_{k,t}^{(-p)}$, yaitu pangsa komponen tahun sebelumnya dikali pertumbuhan nasional komponen tanpa provinsi sendiri. Laporkan tahap pertama, bentuk reduksi, IV Wald (rujukan inferensi shift-share: Borusyak, Hull & Jaravel 2022; Goldsmith-Pinkham, Sorkin & Swift 2020).
- Heterogenitas menurut tertil penyangga dan ketergantungan: regresi interaksi dan double machine learning dengan *cross-fitting* per provinsi (Chernozhukov et al. 2018).
- Uji asimetri: koefisien terpisah untuk potongan dan kenaikan.

#### 3.5.4 Efek layanan dan risiko (RQ3, H3)
- Proyeksi lokal (Jordà 2005): $y_{i,t+h} - y_{i,t-1} = \beta_h\,X_{it} + \delta\, y_{i,t-1} + \gamma_t + u$, untuk h = 0, 1, 2, dengan X berupa potongan nyata atau paparan komposisi.
- Daya uji: efek minimum terdeteksi = 2,8 × galat baku.
- Uji pra-tren dan sensitivitas terhadap pelanggaran tren sejajar (diilhami Rambachan & Roth 2023; versi sederhana: selang dilebarkan M × |pra-tren|).
- Uji mundur bergulir (asal 2023, 2024): naif, tren empiris-Bayes, LightGBM tanpa dan dengan fitur anggaran; RMSE dan cakupan selang; kalibrasi ulang selang dari galat uji mundur.
- Risiko 2028 per kab/kota: peluang di bawah lantai dari proyeksi tren terkerutkan; kategori "sudah di bawah" dan "rawan jatuh".

#### 3.5.5 Evaluasi aturan pembagian potongan (RQ4, H4–H5)
- Keadaan layanan $X_i$ (−V, satuan SD); dasar 2028 dari proyeksi tren.
- Efek potongan: $X_i = X^0_i - d\,k_i\,c_i$, dengan $k_i \propto (1-\text{penyangga}_i)/(\text{penduduk}_i \times \text{biaya}_i)$, dinormalkan sehingga efek rata-rata pola aktual = d.
- Kerugian: $\sum_i w_i\,[\max(0, F - X_i)^{1+\varepsilon} + \rho \max(0, X^{25}_i - X_i - \tau)^2]$.
- Himpunan skenario: d ∈ {0,05; 0,10; 0,20}, ε ∈ {0; 2; 6}, penyangga ya/tidak (18 skenario).
- Kendala: total potongan = aktual; persen potongan dalam kotak [0,5; 1,5] × rata-rata (uji [0,25; 1,75] dan [0,75; 1,25]).
- Aturan:
  - aktual, sama persen, per kapita sama, berbasis kebutuhan lembut dan tegas;
  - optimal per skenario (dualitas Lagrange per wilayah);
  - optimal robust (minimax regret relatif, bobot multiplikatif).
- Ukuran: penduduk di bawah lantai, penduduk yang mundur, regret rata-rata dan terburuk, beban per kuartil.
- Analisis tambahan: pertukaran lantai vs non-retrogresi (variasi ρ, lantai, besar efek), kurva besar potongan 0–30%, tiga pembobotan wilayah.

#### 3.5.6 HJB sebagai metode pembanding
- Keadaan dua dimensi per kab/kota (indeks UHH, indeks pendidikan), dinamika Ornstein–Uhlenbeck dengan dorongan belanja.
- Persamaan per wilayah dengan harga bayangan anggaran $\lambda_t$:
  $\rho V - V_t = \max_{r}\{R(x) - \lambda_t\,u^{ref} r + \mathcal{L}^r V\}$,
  dengan R berbentuk Atkinson ditambah hukuman di bawah lantai.
- $\lambda_t$ dicari agar belanja harapan tiap tahun sama dengan anggaran.
- Skema numerik semi-Lagrangian; varian robust (θ).
- Lima dunia parameter; pembanding lima aturan statis.
- Ukuran dan pembanding sama dengan 3.5.5, tetapi keadaannya berbeda, jadi angka kedua bagian tidak dibandingkan langsung.

### 3.6 Uji Ketahanan

- Bobot wilayah (penduduk, akar penduduk, sama).
- Tinggi lantai (P05, P10, P20).
- Lebar kotak realokasi.
- Sampel dengan dan tanpa 2026.
- Ukuran paparan alternatif.
- Penanganan patahan UHH.
- Satu tabel: temuan mana yang tahan dan mana yang bergantung asumsi (misalnya kesimpulan "per kapita sama" bergantung perumusan efek).

### 3.7 Reprodusibilitas

- Seluruh langkah dapat dijalankan ulang (`code/siap/run_all.py`); bibit acak tetap.
- Angka naskah dicocokkan otomatis dengan keluaran (`cek_dokumentasi.py`).
- Data, log koreksi, dan kode disertakan sebagai lampiran atau repositori.

### 3.8 Keterbatasan Metodologis

1. Efek anggaran terhadap layanan tidak teridentifikasi; evaluasi aturan bersifat skenario.
2. 2026 berupa anggaran; instrumen shift-share kuat hanya karena variasi 2026.
3. Luaran berupa indikator stok yang bergerak lambat; jendela pasca-guncangan pendek.
4. Lantai bersifat relatif, belum memakai standar SPM mutlak.
5. Kotak realokasi melampaui rumus DBH dan DAU dalam UU HKPD; hasil sebagai tolok ukur.
6. Kualitas data: isian manual tanpa catatan sumber, patahan UHH, penduduk turunan untuk 187 kab/kota.

---

## Saran untuk bab berikutnya (tidak diminta, sebagai pegangan)

- **Bab 4 Hasil:** urutkan mengikuti RQ1 sampai RQ4; HJB sebagai subbab terakhir.
- **Bab 5 Pembahasan:** tiga pertanyaan konstitusional.
  1. Apakah potongan menghormati prioritas yang terburuk? Tidak secara sengaja; ditentukan komposisi.
  2. Apakah lantai minimum terjaga? Penurunannya kecil dalam jangka pendek, tetapi kelompok rentan sudah lama di bawah lantai.
  3. Apakah ada kemunduran? Ya, terkonsentrasi di daerah dengan potongan DBH besar, dan aturan alternatif bisa menekannya.
