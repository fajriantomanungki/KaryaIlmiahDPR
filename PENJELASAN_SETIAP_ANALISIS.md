# Penjelasan setiap analisis, kode yang dipakai, dan kesesuaiannya dengan hasil

Folder proyek: `D:\SE Robots\Paper_HJB_Transfer_Fiskal`. Semua kode Python yang saya buat ada di dua tempat:

- `code\30_siapkan_data.py` : pengolahan data (satu-satunya skrip saya di luar subfolder `siap`).
- `code\siap\` : seluruh analisis, yaitu `util_siap.py`, `31`…`37`, `run_all.py`, `cek_dokumentasi.py`.

Mesin HJB (`code\hjb_core.py`, `code\hjb_jobs.py`, `code\hjb_kab.py`) dibuat pada tahap sebelumnya. Hari ini hanya `hjb_kab.py` yang saya ubah satu baris, supaya folder datanya bisa dipilih lewat variabel lingkungan `HJB_DATA_DIR`.

Dokumen lain: `DOKUMENTASI_HASIL.md` (ringkasan temuan dan batasan). Dokumen ini lebih rinci: untuk setiap analisis, apa pertanyaannya, apa yang dilakukan kodenya, apa hasilnya, dan bagaimana membacanya.

## Kesesuaian kode dengan hasil (sudah diperiksa)

1. **Jalankan ulang dari nol.** Seluruh rangkaian tanpa HJB (`python -I code/siap/run_all.py cepat`) dijalankan ulang: 8 langkah selesai tanpa galat. 51 berkas CSV hasilnya identik dengan hasil sebelumnya (angka tidak berubah; acakan memakai bibit tetap `20261123`).
2. **Cocokkan angka dokumen dengan keluaran.** `code\siap\cek_dokumentasi.py` membaca keluaran dan membandingkannya dengan 190 angka yang tertulis di `DOKUMENTASI_HASIL.md`: 190 cocok, 0 berbeda (hasil di `output\siap\cek_dokumentasi.csv`). Jalankan lagi kapan saja setelah `run_all.py`.
3. **HJB belum dijalankan ulang dalam pemeriksaan ini** karena butuh sekitar 30 menit. Hasilnya berasal dari satu kali jalan memakai berkas kode yang sama dengan yang ada sekarang (tidak diubah sesudahnya). Angka HJB di dokumen ikut dicek terhadap keluarannya, tetapi tidak dibuat ulang. Untuk membuat ulang: `python -I code/siap/run_all.py`.
4. Satu kendala yang ditemukan saat pemeriksaan: `Data_Siap_Analisis.xlsx` gagal ditulis ulang ketika berkasnya sedang dibuka di Excel. Skrip 30 sekarang menyimpan ke `Data_Siap_Analisis_baru.xlsx` bila berkas terkunci. Bukan galat analisis.

## 0. Pengolahan data — `code\30_siapkan_data.py`

**Pertanyaan:** bagaimana membuat data yang bisa dipakai tanpa menebak angka?

**Yang dilakukan kode:**
1. Membaca `data jurnal_missingv3.xlsx` (sheet `Data_Panel`, `Isi_Missing`, `Metadata_Variabel`).
2. Menaruh tiap isian (4.545 sel) ke panel hanya pada sel yang kosong. Tidak ada sel yang ditimpa (ada pernyataan `assert` yang menghentikan skrip bila terjadi).
3. Memeriksa satuan terhadap rentang wajar. Bila nilai di luar rentang pada variabel yang bisa keliru kelipatan 1.000 (PPK, PDRB per kapita, penduduk, total APBD/TKDD), skrip mencoba kelipatan 1.000 dan menerimanya hanya jika hasilnya sejalan dengan deret wilayah itu sendiri. Bila wilayah tak punya deret pembanding, skala boleh diterima hanya jika sama dengan pola mayoritas isian di provinsinya (diberi tanda).
4. Untuk UHH, HLS, dan RLS memakai rentang yang lebih longgar (UHH 45–87, HLS 3–18,5, RLS 0,5–13,5) dengan syarat deret isian wilayah itu mulus. Ini menyelamatkan nilai ekstrem Papua pegunungan yang asli. Nilainya diberi tanda `di_luar_rentang_QC_dipertahankan`.
5. Sel yang berisi tanggal akibat format Excel dikembalikan ke pemilik.
6. Menghitung penduduk turunan memakai rumus di metadata, mengisi seri UHH, dan menghitung ulang penanda.
7. Menjalankan pemeriksaan konsistensi (P1 ≤ P0, penduduk turunan vs penduduk BPS, belanja vs pendapatan, lonjakan antartahun).
8. Menentukan kelengkapan per kab/kota (Tingkat A) dan memisahkan yang tidak lengkap.

**Keluaran:** `Data Pakai Penelitian\Data Digunakan\Data_Siap_Analisis.xlsx` (sheet `Ringkasan`, `Lengkap_A`, `Tidak_Lengkap`, `Status_Kelengkapan`, `Log_Koreksi`, `Kembali_ke_Pemilik`, `Cek_Konsistensi`, `Cakupan_Sebelum_Sesudah`, `Kamus`) dan `data\siap_analisis\*.csv`.

**Hasil:** 508 dari 514 kab/kota lengkap; 450 punya seri 2021–2025 lengkap; 6 DKI tidak punya anggaran kab/kota. Dari 4.545 isian: 4.085 masuk langsung, 428 dikoreksi skalanya, 25 nilai ekstrem dipertahankan, 7 dikembalikan.

**Cara membaca / catatan:** `Log_Koreksi` memuat setiap sel beserta nilai asli, nilai yang dipakai, aturan, dan status. Kolom `sumber_isian` kosong dari awal, jadi asal angka tidak tercatat. Tiga hal yang perlu Anda cek: 25 nilai ekstrem Papua, 7 sel PPK tanggal, dan UHH NTB 2023 (naik 4–5 tahun untuk seluruh kab/kota, belum ditangani).

## 1. Analisis deskriptif — `code\siap\37_deskriptif.py`

**Pertanyaan:** seperti apa kondisi layanan, besar dan bentuk potongan, dan siapa yang punya kemampuan menyerapnya?

**Yang dilakukan kode:**
- Statistik deskriptif 2025 (N, rata-rata, rata-rata tertimbang penduduk, sebaran).
- Tren UHH, HLS, RLS, P0 2020–2025 untuk nasional dan untuk kuartil kerentanan 2025 (kuartil tetap, supaya perbandingannya adil).
- Komposisi TKDD 2025 dan perubahannya 2026 per komponen, dan komposisi per kuartil kerentanan.
- Sebaran potongan (persen dipotong, P10/median/P90, pangsa 10% terbesar), potongan per provinsi.
- Tipologi kerentanan ganda: miskin (tertil teratas), bergantung pada TKDD (tertil teratas), penyangga tipis (tertil terbawah).
- Persistensi peringkat kemiskinan, dan perubahan belanja APBD per jenis.

**Kerentanan (V):** rata-rata z dari P0, −UHH, −HLS, −RLS tahun 2025, dibakukan; makin tinggi makin rentan. Fungsinya ada di `util_siap.py` (`unit_tabel`). Pembobotan penduduk memakai penduduk 2025.

**Hasil utama:** P0 nasional 8,8%, UHH 74,7 tahun. Kuartil paling rentan P0 15,8% vs 5,8%, RLS 7,2 vs 10,8 tahun. TKDD turun 20,1% (Rp706,9 T ke Rp564,7 T); 97% kab/kota dipotong, median 17,2%. DBH menyumbang 50,7% potongan dan Dana Desa 30,9%. Belanja modal turun 27%, pegawai hanya 1,3%. Kerentanan ganda: 87 kab/kota, per kapita menanggung 1,7 kali lipat kelompok tanpa kerentanan.

**Cara membaca:** tabel `T1`–`T8` dan gambar `G1`–`G3` di `output\siap\37_deskriptif\`. Persen "dipotong" selalu membandingkan TKDD 2026 (anggaran) dengan 2025.

**Batas:** ini deskripsi, bukan penyebab. Kuartil V dibuat dari data 2025 yang sama dengan sebagian luaran.

## 2. Siapa yang menanggung potongan — `code\siap\31_siapa_menanggung.py`

**Pertanyaan:** apakah potongan 2026 jatuh lebih berat pada yang rentan, dan apa yang menentukan besarnya?

**Yang dilakukan kode:**
- Perubahan TKDD per kapita dan persen untuk 2020–2026 menurut kuartil V.
- **Indeks konsentrasi** beban (Wagstaff): beban potongan per kapita diurutkan menurut V (peringkat pecahan, berbobot penduduk). Nol berarti beban tersebar netral, positif berarti condong ke yang rentan. Fungsinya `wcov_rank_index` di `util_siap.py`. Selang 95% dengan bootstrap per provinsi (1.000 ulangan).
- Dekomposisi per komponen (DAU, DBH, DAK, Dana Desa, Otsus): pangsa dari total potongan dan indeks konsentrasi masing-masing.
- Regresi persen potongan pada V dalam empat spesifikasi (V saja; + ukuran dan jenis; + komposisi transfer; + ketergantungan dan penyangga), galat baku dikelompokkan per provinsi, p-value dengan wild cluster bootstrap (999 ulangan).

**Hasil:** indeks konsentrasi 2026 = 0,071 (selang −0,039 sampai 0,189), jadi tidak berbeda dari netral. DBH (51% potongan) netral; Dana Desa dan DAK fisik condong ke yang rentan; DAU condong ke yang kurang rentan. Koefisien V pada persen potongan −1,5 (p=0,12) menjadi 0,03 (p=0,95) setelah komposisi transfer dimasukkan, dan R² naik dari 0,02 ke 0,60.

**Cara membaca:** potongan ditentukan oleh komposisi transfer, bukan kebutuhan. Kelompok rentan dipotong lebih ringan dalam persen karena kebetulan kurang bergantung pada DBH, bukan karena dilindungi.

**Batas:** indeks konsentrasi hanya bermakna pada tahun dengan rata-rata potongan positif (2026). Tahun lain (kebanyakan kenaikan) saya laporkan tetapi tidak saya tafsirkan. Angka 2026 adalah anggaran.

## 3. Dari potongan ke belanja — `code\siap\32_penyangga_passthrough.py`

**Pertanyaan:** berapa rupiah belanja yang hilang untuk tiap rupiah TKDD yang hilang, dan apakah pemda dengan penyangga meneruskannya lebih sedikit?

**Yang dilakukan kode:**
- Beda pertama per kab/kota (perubahan tahun ke tahun, ribu rupiah per kapita memakai penduduk 2025 tetap) dengan efek tahun; galat baku per provinsi, wild cluster bootstrap untuk p-value.
- Luaran: belanja modal, barang-jasa, pegawai, bantuan keuangan, total, PAD, pembiayaan netto. Dua sampel: 2021–2025 dan 2021–2026.
- **Paparan shift-share** sebagai pembanding: pangsa komponen TKDD tahun sebelumnya × pertumbuhan nasional per komponen (provinsi sendiri dikeluarkan). Dilaporkan tahap pertama (F), bentuk reduksi, dan IV Wald (rasio bentuk reduksi/tahap pertama; **tanpa galat baku**).
- Heterogenitas menurut tertil penyangga (PAD+SiLPA dibagi belanja, tahun sebelumnya) dan ketergantungan TKDD: regresi interaksi, dan double machine learning (LightGBM, lipatan per provinsi, residualisasi lalu regresi per kelompok).
- Asimetri: potongan dan kenaikan diestimasi terpisah.

**Hasil:** tiap Rp1 TKDD hilang mengurangi belanja total Rp1,2, modal Rp0,59–0,63, barang-jasa Rp0,33, pegawai Rp0,12–0,18. Modal turun 0,58 saat potongan dan naik 0,61 saat kenaikan (simetris). Penyangga tidak membedakan (0,63 vs 0,58, selisih 0,05 ± 0,09). Instrumen shift-share kuat pada 2021–2026 (F 14,9) tetapi lemah pada 2021–2025 (F 0,6); IV Wald belanja total 0,57, lebih kecil dari OLS.

**Cara membaca:** pass-through tinggi di semua kelompok, jadi penyangga fiskal tidak bekerja sebagai pelindung. Besar pastinya bergantung pada identifikasi (OLS vs IV), tetapi arahnya konsisten.

**Batas:** instrumen kuat hanya karena variasi 2026 (anggaran). Pada pengujian beda antarkelompok, galat baku selisih saya hitung dengan menjumlahkan varians tanpa kovarians (konservatif bila kovarians positif). Kolom `bantuan keuangan` adalah transfer antartingkat.

## 4. Efek pada layanan dan risiko — `code\siap\33_risiko_layanan.py`

**Pertanyaan:** apakah potongan menggeser UHH, HLS, RLS, P0; seberapa baik data memprediksi luaran; siapa berisiko di bawah lantai?

**Yang dilakukan kode:**
- **Proyeksi lokal:** perubahan luaran dari t−1 ke t+h (h = 0, 1, 2) pada potongan TKDD tahun t (per 10 poin persen), dengan efek tahun dan luaran awal. Dua ukuran paparan: potongan nyata dan porsi komposisi (DBH + DAK fisik + Dana Desa). Dilaporkan koefisien, galat baku, p wild bootstrap, dan **efek minimum terdeteksi** (2,8 × galat baku, daya 80%).
- **Uji pra-tren:** perubahan luaran sebelum t pada paparan t. Sensitivitas sederhana: selang dilebarkan sebesar M × |koefisien pra-tren| (bukan implementasi penuh Rambachan–Roth).
- **Uji mundur bergulir** untuk ramalan satu tahun (asal 2023 dan 2024): naif, tren per wilayah yang dikerutkan ke tren provinsi (empiris-Bayes), model LightGBM tanpa dan dengan fitur anggaran. Selang prediksi dikalibrasi ulang dari galat uji mundur.
- **Risiko per kab/kota:** peluang luaran 2028 di bawah lantai (persentil ke-10 distribusi 2025; untuk P0 persentil ke-90), asumsi galat normal dengan simpangan terkalibrasi. Skor risiko = rata-rata peluang empat luaran.
- Enam kab/kota dengan patahan UHH (selisih 2023 ke 2024 lebih dari 5 tahun) dikeluarkan deret 2020–2023-nya dari model deret waktu. Daftarnya `T0_patahan_uhh.csv`.

**Hasil:** efek potongan 10 poin pada luaran (h=1): UHH +0,012 ± 0,009 tahun, HLS −0,002 ± 0,002, RLS +0,001 ± 0,003, P0 +0,010 ± 0,011; efek terkecil terdeteksi UHH 0,025, HLS 0,006, RLS 0,009, P0 0,031. Sinyal paparan komposisi pada UHH (−0,033, p=0,018) ikut uji pra-tren arah sama (−0,011, t=−1,6) dan tidak dilaporkan sebagai efek kausal. Fitur anggaran tidak menambah akurasi ramalan (rasio RMSE 0,98–1,03). Tren terkerutkan mengalahkan naif untuk UHH (−22%), P0 (−9%), RLS (−3%), tidak untuk HLS (+3%). 119 kab/kota (40,8 juta jiwa) sudah di bawah lantai; 22 (14,6 juta) rawan jatuh; skor risiko berkorelasi 0,92 dengan V.

**Cara membaca:** tidak ada efek jangka pendek besar yang terdeteksi, tetapi efek kecil yang menumpuk bertahun-tahun tidak bisa dikesampingkan. Karena anggaran tidak menambah akurasi, pengaruh anggaran pada layanan diperlakukan sebagai skenario (bagian 5), bukan prediksi.

**Batas:** variasi 2021–2025 sebagian besar berupa kenaikan transfer. Lantai bersifat relatif, bukan standar mutlak (misalnya SPM). Skor risiko praktis mengulang kerentanan.

## 5. Aturan pembagian potongan — `code\siap\34_aturan_alokasi.py`

**Pertanyaan:** dengan total potongan yang sama, bagaimana pembagian yang paling baik bagi lantai layanan dan bagi non-retrogresi?

**Yang dilakukan kode:**
- Keadaan layanan X = −V (satuan simpangan baku). Dasar 2028 = proyeksi tren empiris-Bayes dari skrip 33. Lantai = persentil ke-10 X 2025. Kerugian tiap wilayah = bobot penduduk × [kekurangan di bawah lantai^(1+ε) + 2 × (mundur dibanding 2025 di atas toleransi 0,05 SD)²].
- Efek potongan terhadap layanan tidak teridentifikasi dari data, jadi dibuat **18 skenario**: efek rata-rata aktual 0,05/0,10/0,20 SD, ε = 0/2/6, dengan atau tanpa penyangga. Efek wilayah sebanding dengan potongan per kapita dibagi indeks biaya konstruksi.
- Total potongan tetap sama dengan aktual (Rp142,2 T). Persen potongan tiap wilayah dibatasi 0,5–1,5 kali rata-rata (kotak realokasi; juga diuji 0,25–1,75 dan 0,75–1,25).
- Aturan yang dibandingkan: pola aktual, sama persen, per kapita sama (dalam kotak yang sama), berbasis kebutuhan lembut dan tegas, optimal per skenario (penyelesaian dualitas Lagrange per wilayah), optimal robust (minimax regret relatif dengan bobot multiplikatif atas 18 skenario).
- Ketahanan: tiga pembobotan wilayah, tiga tinggi lantai (P05/P10/P20), kurva besar potongan 0–30%, pertukaran lantai vs non-retrogresi.

**Hasil (skenario tengah):** penduduk di bawah lantai aktual 3,19%, optimal robust 2,64%. Yang mundur 7,19% menjadi 1,89%. Per kapita sama 2,83% dan 2,13%; aturan berbasis kebutuhan tidak mengurangi yang mundur (7,2–7,5%). Pada pola aktual, penduduk mundur terkonsentrasi di Kaltim, Kalteng, Sumsel. Kotak sempit memperkecil perbaikan (mundur 3,89%). Tidak ada titik patah pada kurva besar potongan. Pertukaran lantai vs non-retrogresi baru muncul bila efek besar (0,4 SD).

**Cara membaca:** perbedaan terbesar ada pada siapa yang mundur, bukan pada penduduk di bawah lantai. Karena efek anggaran adalah skenario, tabel ini simulasi bersyarat, bukan prediksi.

**Batas:** kotak 0,5–1,5 melampaui rumus DBH dan DAU yang diatur undang-undang. Kesimpulan "per kapita sama hampir optimal" bergantung pada cara efek dimodelkan (di sini efek ∝ 1/penduduk); perumusan HJB (bagian 6) memberi hasil sebaliknya.

## 6. HJB — `code\siap\35_siapkan_hjb.py` dan `36_hjb_kabkota.py`

**Pertanyaan:** bila anggaran dibagi secara dinamis tahun 2026–2028 lewat satu harga bayangan per tahun, apakah hasilnya lebih baik dari aturan sederhana?

**Yang dilakukan kode:**
- `35_siapkan_hjb.py` membentuk tabel unit untuk 508 kab/kota: indeks UHH, indeks pendidikan, TKDD per kapita 2025 dan 2026, penyangga, P0, indeks biaya konstruksi.
- `36_hjb_kabkota.py` memanggil mesin HJB tahap sebelumnya. Dua keadaan per kab/kota (indeks UHH dan indeks pendidikan) bergerak menuju rata-rata jangka panjang dan terdorong belanja per kapita. Tujuannya keadilan ala Atkinson (ε=6) ditambah hukuman bila di bawah lantai. Anggaran tiap tahun dibagi lewat satu harga bayangan λ per tahun, sehingga tiap kab/kota menyelesaikan persamaan HJB-nya sendiri (skema semi-Lagrangian).
- Dibandingkan dengan lima aturan statis pada anggaran 2026 yang sama, dalam lima dunia (kepekaan layanan 0,5/1,0/2,3; respons rupiah atau persen; pemulihan lambat) ditambah satu jalan dengan ketahanan model (θ=0,1).
- Ukuran: persen penduduk di bawah lantai (rata-rata 2026–2028), kuartil rentan di bawah lantai kesehatan, yang mundur.

**Hasil (dunia tengah, persen penduduk di bawah lantai):** pola aktual 6,91; pangkas merata 6,91; berbobot kebutuhan 6,79; HJB 6,75; aturan r_i 6,67; per kapita sama 7,36. HJB memperbaiki 0,16 poin dari pola aktual, tetapi lebih buruk dari aktual di dunia "persen" dan dunia "kuat". Aturan r_i terbaik di kelima dunia. Peta potongan HJB lebih melindungi yang miskin (korelasi peringkat dengan P0 −0,57; pola aktual −0,33).

**Cara membaca:** HJB bermanfaat sebagai kerangka dan tolok ukur dinamis, tetapi pada data ini tidak mengalahkan aturan sederhana dan hasilnya peka pada parameter yang tidak teridentifikasi. Tulis sebagai pembanding, bukan metode utama.

**Batas:** parameter aturan r_i dikalibrasi pada tahap sebelumnya dengan ukuran yang sama (data 472 kab/kota) dan tidak dikalibrasi ulang. Ukuran HJB (indeks UHH dan pendidikan) berbeda dari ukuran gabungan di bagian 5, sehingga angka kedua bagian tidak boleh dibandingkan langsung. Keadaan hanya dua dimensi dan tidak memuat kemiskinan.

## 7. Berkas pendukung

- `code\siap\util_siap.py` : memuat panel, membuat kerentanan V, indeks konsentrasi, regresi galat baku per kelompok, wild cluster bootstrap.
- `code\siap\run_all.py` : menjalankan semuanya berurutan, mencatat jalannya tiap langkah di `output\siap\log\`.
- `code\siap\cek_dokumentasi.py` : mencocokkan angka dokumen dengan keluaran.
