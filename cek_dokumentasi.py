"""cek_dokumentasi.py — mencocokkan angka yang tertulis di DOKUMENTASI_HASIL.md dengan keluaran skrip.

Setiap baris: (butir, angka di dokumen, angka dari keluaran, toleransi). Status OK bila selisih mutlak <= toleransi.
Dijalankan SETELAH run_all.py. Keluaran: output/siap/cek_dokumentasi.csv dan ringkasan di layar.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from util_siap import ROOT, OUT

O = OUT
X = ROOT / "Data Pakai Penelitian" / "Data Digunakan" / "Data_Siap_Analisis.xlsx"
rd = lambda *p, **k: pd.read_csv(O.joinpath(*p), **k)
cek = []
def c(butir, dok, aktual, tol=0.006):
    ok = bool(abs(float(dok) - float(aktual)) <= tol)
    cek.append({"butir": butir, "angka_di_dokumen": dok, "angka_dari_keluaran": round(float(aktual), 4), "toleransi": tol, "status": "OK" if ok else "BEDA"})

# ---------------------------------------------------------------- 2. data
R = pd.read_excel(X, sheet_name="Ringkasan").set_index("butir")["jumlah"]
c("isian terbaca", 4545, R["Isian manual terbaca (sel terisi di Isi_Missing)"], 0)
c("isian masuk langsung", 4085, R["  masuk ke panel langsung"], 0)
c("isian koreksi skala", 428, R["  masuk setelah koreksi skala"], 0)
c("dikembalikan ke pemilik", 7, R["  dikembalikan ke pemilik"], 0)
c("sel Isi_Missing masih kosong", 2608, R["Sel Isi_Missing yang masih kosong"], 0)
c("penduduk turunan baru", 103, R["Penduduk turunan baru dihitung (aturan metadata)"], 0)
c("kab/kota lengkap", 508, R["Tingkat A (inti lengkap)"], 0)
c("kab/kota seri 2021-2025 lengkap", 450, R["Tingkat B (A dan seri 2021-2025 lengkap)"], 0)
c("kab/kota tidak lengkap", 6, R["Tidak lengkap"], 0)
L = pd.read_csv(ROOT / "data" / "siap_analisis" / "log_koreksi.csv", dtype={"kode_bps": str})
c("log: koreksi skala acuan provinsi", 264, (L.aturan == "koreksi_skala_x1000^1_acuan_provinsi").sum(), 0)
c("log: di luar rentang QC dipertahankan", 25, (L.aturan == "di_luar_rentang_QC_dipertahankan").sum(), 0)
c("patahan UHH (wilayah)", 6, len(rd("33_risiko_layanan", "T0_patahan_uhh.csv")), 0)

# ---------------------------------------------------------------- 3. deskriptif
T1 = rd("37_deskriptif", "T1_statistik_deskriptif.csv").set_index("variabel")
c("penduduk total 2025 (juta)", 279.9, T1.loc["Penduduk (jiwa)", "rata2"] * 508 / 1e6, 0.06)
c("P0 nasional tertimbang", 8.8, T1.loc["P0 (%)", "rata2_tertimbang_penduduk"], 0.05)
c("UHH nasional tertimbang", 74.7, T1.loc["UHH (tahun)", "rata2_tertimbang_penduduk"], 0.05)
c("HLS nasional tertimbang", 13.4, T1.loc["HLS (tahun)", "rata2_tertimbang_penduduk"], 0.05)
c("RLS nasional tertimbang", 9.0, T1.loc["RLS (tahun)", "rata2_tertimbang_penduduk"], 0.05)
T2 = rd("37_deskriptif", "T2_tren_luaran.csv")
g = lambda t, v, k: T2[(T2.tahun == t) & (T2.luaran == v) & (T2.kelompok == k)].rata2_tertimbang.iloc[0]
c("P0 nasional turun 2020-2025", 1.4, g(2020, "p0", "nasional") - g(2025, "p0", "nasional"), 0.06)
c("P0 Q4 2020", 18.1, g(2020, "p0", "Q4 (paling rentan)"), 0.06)
c("P0 Q4 2025", 15.8, g(2025, "p0", "Q4 (paling rentan)"), 0.06)
c("UHH naik 2020-2025", 1.2, g(2025, "uhh", "nasional") - g(2020, "uhh", "nasional"), 0.06)
c("UHH Q4 2025", 72.4, g(2025, "uhh", "Q4 (paling rentan)"), 0.06)
c("UHH Q1 2025", 75.7, g(2025, "uhh", "Q1 (paling tidak rentan)"), 0.06)
c("RLS Q4 2025", 7.2, g(2025, "rls", "Q4 (paling rentan)"), 0.06)
c("RLS Q1 2025", 10.8, g(2025, "rls", "Q1 (paling tidak rentan)"), 0.06)
c("P0 Q1 2025", 5.8, g(2025, "p0", "Q1 (paling tidak rentan)"), 0.06)
c("persistensi P0 2021 vs 2025", 0.99, rd("37_deskriptif", "T7_persistensi.csv", index_col=0).loc["Spearman P0 2021 vs 2025", "spearman"], 0.005)
U = rd("31_siapa_menanggung", "unit_dengan_beban.csv", dtype={"kode_bps": str})
c("TKDD 2025 (Rp T)", 706.9, U.tkdd_2025.sum() / 1e12, 0.06)
c("TKDD 2026 (Rp T)", 564.7, U.tkdd_2026.sum() / 1e12, 0.06)
c("perubahan TKDD (%)", -20.1, (U.tkdd_2026.sum() / U.tkdd_2025.sum() - 1) * 100, 0.06)
D4 = rd("37_deskriptif", "T4_sebaran_potongan.csv", index_col=0)["nilai"]
c("unit dipotong (%)", 97.4, D4["unit_dipotong_pct"], 0.06)
c("potongan median (%)", 17.2, D4["potongan_median"], 0.06)
c("potongan P10 (%)", 3.6, D4["potongan_P10"], 0.06)
c("potongan P90 (%)", 29.9, D4["potongan_P90"], 0.06)
c("unit dipotong >=25% (%)", 17.7, D4["unit_dipotong_>=25pct"], 0.06)
c("penduduk di unit potongan >=25% (juta)", 48.7, D4["penduduk_di_unit_potongan_>=25pct_juta"], 0.06)
c("pangsa potongan 10% unit terbesar", 37.7, D4["pangsa_potongan_rupiah_10pct_unit_terbesar"], 0.06)
K = rd("37_deskriptif", "T3_komposisi_tkdd.csv").set_index("komponen")
for nm, v in (("DBH", -60.0), ("Dana Desa", -63.8), ("DAK fisik", -70.3), ("DAU", -3.5), ("DAK nonfisik", 1.6)):
    c(f"perubahan {nm} (%)", v, K.loc[nm, "perubahan_pct"], 0.06)
c("pangsa DBH dari potongan", 50.7, K.loc["DBH", "pangsa_dari_total_potongan_pct"], 0.06)
c("pangsa Dana Desa dari potongan", 30.9, K.loc["Dana Desa", "pangsa_dari_total_potongan_pct"], 0.06)
P5 = rd("37_deskriptif", "T5_potongan_per_provinsi.csv", index_col=0)
c("Jatim potongan Rp T", 15.5, P5.loc["Jawa Timur", "potongan_Rp_T"], 0.06)
c("Kaltim potongan Rp T", 14.2, P5.loc["Kalimantan Timur", "potongan_Rp_T"], 0.06)
c("Kaltim potongan % TKDD", 42, P5.loc["Kalimantan Timur", "potongan_pct"], 0.5)
c("Kaltim potongan per kapita (juta Rp)", 3.5, P5.loc["Kalimantan Timur", "potongan_pk_rb"] / 1000, 0.06)
TP = rd("37_deskriptif", "T6_tipologi_kerentanan_ganda.csv", index_col=0)
c("tipologi 3 ciri: kab/kota", 87, TP.loc[3, "kab_kota"], 0)
c("tipologi 3 ciri: penduduk (juta)", 14.4, TP.loc[3, "penduduk_juta"], 0.06)
c("tipologi 3 ciri: potongan % TKDD", 12.0, TP.loc[3, "potongan_pct_TKDD"], 0.06)
c("tipologi 0 ciri: potongan % TKDD", 21.8, TP.loc[0, "potongan_pct_TKDD"], 0.06)
c("tipologi 3 ciri: per kapita (rb)", 729, TP.loc[3, "potongan_per_kapita_rb"], 1)
c("tipologi 0 ciri: per kapita (rb)", 425, TP.loc[0, "potongan_per_kapita_rb"], 1)
c("rasio per kapita 3 ciri / 0 ciri", 1.7, TP.loc[3, "potongan_per_kapita_rb"] / TP.loc[0, "potongan_per_kapita_rb"], 0.06)
B8 = rd("37_deskriptif", "T8_belanja_apbd.csv").set_index("pos")["perubahan_pct"]
for nm, v in (("Belanja total", -10.3), ("Belanja modal", -27.0), ("Bantuan keuangan", -22.4), ("Belanja barang-jasa", -7.8), ("Belanja pegawai", -1.3), ("PAD", 6.8)):
    c(f"APBD {nm} (%)", v, B8[nm], 0.06)

# ---------------------------------------------------------------- 4. siapa menanggung
Q5 = rd("31_siapa_menanggung", "T5_beban_2026_per_kuartil.csv", index_col=0).T       # baris = metrik, kolom = kuartil
q1, q4 = Q5.columns[0], Q5.columns[-1]
c("potongan median Q1 (% TKDD)", 19.9, Q5.loc["potongan_pct_TKDD_median", q1], 0.06)
c("potongan median Q4 (% TKDD)", 12.7, Q5.loc["potongan_pct_TKDD_median", q4], 0.06)
c("potongan per kapita Q1 (rb)", 423, Q5.loc["potongan_per_kapita_rb", q1], 1)
c("potongan per kapita Q4 (rb)", 516, Q5.loc["potongan_per_kapita_rb", q4], 1)
c("penyangga Q1 (%)", 27.8, Q5.loc["penyangga_PAD_SiLPA_pct_belanja_median", q1], 0.06)
c("penyangga Q4 (%)", 8.8, Q5.loc["penyangga_PAD_SiLPA_pct_belanja_median", q4], 0.06)
c("ketergantungan Q1 (%)", 68.7, Q5.loc["ketergantungan_TKDD_pct_pendapatan_median", q1], 0.06)
c("ketergantungan Q4 (%)", 89.7, Q5.loc["ketergantungan_TKDD_pct_pendapatan_median", q4], 0.06)
c("TKDD per kapita Q1 (rb)", 1935, Q5.loc["tkdd_per_kapita_2025_rb", q1], 1)
c("TKDD per kapita Q4 (rb)", 3666, Q5.loc["tkdd_per_kapita_2025_rb", q4], 1)
IK = rd("31_siapa_menanggung", "T2_indeks_konsentrasi_per_tahun.csv").set_index("tahun")
c("indeks konsentrasi 2026", 0.071, IK.loc[2026, "indeks_konsentrasi_beban"], 0.0015)
c("indeks konsentrasi 2026 batas bawah", -0.039, IK.loc[2026, "ci95_lo"], 0.02)
c("indeks konsentrasi 2026 batas atas", 0.189, IK.loc[2026, "ci95_hi"], 0.02)
c("indeks konsentrasi 2021", 0.18, IK.loc[2021, "indeks_konsentrasi_beban"], 0.01)
c("indeks konsentrasi 2023", 0.24, IK.loc[2023, "indeks_konsentrasi_beban"], 0.01)
c("kab/kota dipotong 2021 (%) < 50", 35.8, IK.loc[2021, "pct_kabkota_dipotong"], 0.06)
c("kab/kota dipotong 2023 (%) < 50", 40.4, IK.loc[2023, "pct_kabkota_dipotong"], 0.06)
DK = rd("31_siapa_menanggung", "T3_dekomposisi_komponen_2026.csv").set_index("komponen")
for nm, v in (("DBH", -0.03), ("Dana Desa", 0.28), ("DAK fisik", 0.26), ("DAU", -0.07)):
    c(f"indeks konsentrasi {nm}", v, DK.loc[nm, "indeks_konsentrasi"], 0.006)
RG = rd("31_siapa_menanggung", "T4_potongan_vs_kerentanan_regresi.csv").set_index("spesifikasi")
c("regresi V saja: koefisien", -1.5, RG.iloc[0]["koef_V_poin_persen_per_SD"], 0.06)
c("regresi V saja: p wild", 0.12, RG.iloc[0]["p_wild_bootstrap"], 0.03)
c("regresi + komposisi: koefisien", 0.03, RG.iloc[2]["koef_V_poin_persen_per_SD"], 0.01)
c("regresi + komposisi: p wild", 0.95, RG.iloc[2]["p_wild_bootstrap"], 0.03)
c("R2 V saja", 0.02, RG.iloc[0]["R2"], 0.006)
c("R2 + komposisi", 0.60, RG.iloc[2]["R2"], 0.006)

# ---------------------------------------------------------------- 5. pass-through
PT = rd("32_penyangga_passthrough", "T1_passthrough.csv")
pt = lambda s, l, k: PT[(PT.sampel == s) & (PT.luaran == l)][k].iloc[0]
c("OLS belanja total", 1.2, pt("2021-2026", "Belanja total", "OLS_koef"), 0.1)
c("OLS belanja modal 2021-2026", 0.59, pt("2021-2026", "Belanja modal", "OLS_koef"), 0.006)
c("OLS belanja modal 2021-2025", 0.63, pt("2021-2025", "Belanja modal", "OLS_koef"), 0.006)
c("OLS barang-jasa", 0.33, pt("2021-2026", "Belanja barang-jasa", "OLS_koef"), 0.006)
c("OLS pegawai 2021-2026", 0.12, pt("2021-2026", "Belanja pegawai", "OLS_koef"), 0.006)
c("OLS pegawai 2021-2025", 0.18, pt("2021-2025", "Belanja pegawai", "OLS_koef"), 0.006)
c("bentuk reduksi belanja total", 0.22, pt("2021-2026", "Belanja total", "RF_koef"), 0.006)
c("p bentuk reduksi belanja total", 0.07, pt("2021-2026", "Belanja total", "RF_p_wild"), 0.01)
c("IV Wald belanja total", 0.57, pt("2021-2026", "Belanja total", "IV_wald"), 0.006)
c("F tahap pertama 2021-2026", 14.9, pt("2021-2026", "Belanja total", "FS_F"), 0.06)
c("F tahap pertama 2021-2025", 0.6, pt("2021-2025", "Belanja total", "FS_F"), 0.06)
H = rd("32_penyangga_passthrough", "T2_heterogenitas_penyangga.csv")
hm = lambda k: H[(H.dimensi == "penyangga") & (H.luaran == "Belanja modal") & (H.kelompok == k)].iloc[0]
c("modal penyangga tipis", 0.63, hm("penyangga_tipis").koef, 0.006)
c("modal penyangga tebal", 0.58, hm("penyangga_tebal").koef, 0.006)
c("selisih tipis-tebal", 0.05, hm("selisih penyangga_tipis - penyangga_tebal").koef, 0.006)
c("galat selisih", 0.09, hm("selisih penyangga_tipis - penyangga_tebal").se, 0.006)
AS = rd("32_penyangga_passthrough", "T4_asimetri.csv").set_index("luaran")
c("modal saat potongan", 0.58, AS.loc["Belanja modal", "koef_saat_potongan"], 0.006)
c("modal saat kenaikan", 0.61, AS.loc["Belanja modal", "koef_saat_kenaikan"], 0.006)

# ---------------------------------------------------------------- 6. efek layanan dan risiko
LP = rd("33_risiko_layanan", "T1_proyeksi_lokal.csv")
lp = lambda v, k, tag="potongan_nyata": LP[(LP.luaran == v) & (LP.horizon_h == 1) & (LP.ukuran_paparan == tag)][k].iloc[0]
c("UHH efek h=1", 0.012, lp("uhh", "koef_per_10pp"), 0.0006)
c("HLS efek h=1", -0.002, lp("hls", "koef_per_10pp"), 0.0006)
c("RLS efek h=1", 0.001, lp("rls", "koef_per_10pp"), 0.0006)
c("P0 efek h=1", 0.010, lp("p0", "koef_per_10pp"), 0.0006)
c("UHH MDE", 0.025, lp("uhh", "MDE_80pct_daya"), 0.0006)
c("HLS MDE", 0.006, lp("hls", "MDE_80pct_daya"), 0.0006)
c("RLS MDE", 0.009, lp("rls", "MDE_80pct_daya"), 0.0006)
c("P0 MDE", 0.031, lp("p0", "MDE_80pct_daya"), 0.0006)
c("eksposur komposisi UHH h=1", -0.033, lp("uhh", "koef_per_10pp", "eksposur_komposisi"), 0.0006)
c("p eksposur komposisi UHH", 0.018, lp("uhh", "p_wild", "eksposur_komposisi"), 0.006)
PR = rd("33_risiko_layanan", "T2_uji_pra_tren.csv")
pr = PR[(PR.luaran == "uhh") & (PR.ukuran_paparan == "eksposur_komposisi")].iloc[0]
c("pra-tren UHH eksposur koef", -0.011, pr.koef_pra_tren, 0.0006)
c("pra-tren UHH eksposur t", -1.6, pr.t, 0.06)
BT = rd("33_risiko_layanan", "T4_uji_mundur.csv").groupby(["luaran", "model"]).RMSE.mean().unstack()
for v, naif_r, ang_r in (("uhh", 0.778, 1.029), ("p0", 0.909, 0.980), ("rls", 0.9715, 1.004), ("hls", 1.030, 1.004)):
    c(f"RMSE tren EB / naif {v}", naif_r, BT.loc[v, "tren_EB"] / BT.loc[v, "naif"], 0.006)
    c(f"RMSE dengan anggaran / tanpa {v}", ang_r, BT.loc[v, "GBM_dengan_anggaran"] / BT.loc[v, "GBM_tanpa_anggaran"], 0.006)
RK = rd("33_risiko_layanan", "T6_risiko_per_kabkota.csv", dtype={"kode_bps": str})
c("korelasi risiko dengan V", 0.92, RK.risiko_rata2.corr(RK.V, method="spearman"), 0.006)
KT = rd("34_aturan_alokasi", "T6_kategori_risiko.csv", dtype={"kode_bps": str}).merge(RK[["kode_bps", "pop"]], on="kode_bps")
c("sudah di bawah lantai (kab/kota)", 119, KT.sudah_di_bawah.sum(), 0)
c("sudah di bawah lantai (juta jiwa)", 40.8, KT.loc[KT.sudah_di_bawah, "pop"].sum() / 1e6, 0.06)
c("rawan jatuh (kab/kota)", 22, KT.rawan_jatuh.sum(), 0)
c("rawan jatuh (juta jiwa)", 14.6, KT.loc[KT.rawan_jatuh, "pop"].sum() / 1e6, 0.06)

# ---------------------------------------------------------------- 7. aturan alokasi
def tabel(sfx):
    return rd("34_aturan_alokasi", f"T1_perbandingan_aturan{sfx}.csv").set_index("aturan")
T = tabel("")
spec = {"Aktual 2026": (3.19, 7.19, 1.11, 4.90), "Proporsional (sama persen)": (3.22, 6.76, 0.30, 1.44), "Per kapita sama (dalam kotak)": (2.83, 2.13, 0.02, 0.10),
        "Berbasis kebutuhan lembut": (2.71, 7.21, 0.16, 1.09), "Berbasis kebutuhan tegas": (2.69, 7.50, 0.19, 1.30), "Optimal robust (minimax relatif)": (2.64, 1.89, 0.00, 0.02)}
for nm, (a, b, r1, r2) in spec.items():
    c(f"{nm}: di bawah lantai", a, T.loc[nm, "tengah_penduduk_di_bawah_lantai_pct"], 0.006)
    c(f"{nm}: mundur", b, T.loc[nm, "tengah_penduduk_mundur_pct"], 0.006)
    c(f"{nm}: regret rata2", r1, T.loc[nm, "regret_relatif_rata2"], 0.006)
    c(f"{nm}: regret terburuk", r2, T.loc[nm, "regret_relatif_terburuk"], 0.006)
Tw = tabel("_kotak0.25-1.75"); Tn = tabel("_kotak0.75-1.25")
rb = "Optimal robust (minimax relatif)"
c("kotak lebar: di bawah lantai", 2.53, Tw.loc[rb, "tengah_penduduk_di_bawah_lantai_pct"], 0.006)
c("kotak lebar: mundur", 0.42, Tw.loc[rb, "tengah_penduduk_mundur_pct"], 0.006)
c("kotak sempit: di bawah lantai", 2.95, Tn.loc[rb, "tengah_penduduk_di_bawah_lantai_pct"], 0.006)
c("kotak sempit: mundur", 3.89, Tn.loc[rb, "tengah_penduduk_mundur_pct"], 0.006)
BS = rd("34_aturan_alokasi", "T4_batas_potongan.csv").set_index("potongan_pct_TKDD")
c("potongan 0%: di bawah lantai", 2.4, BS.loc[0.0, "optimal_di_bawah_lantai_pct"], 0.06)
c("potongan 30%: sama persen di bawah lantai", 3.8, BS.loc[30.0, "proporsional_di_bawah_lantai_pct"], 0.06)
c("potongan 30%: optimal di bawah lantai", 2.9, BS.loc[30.0, "optimal_di_bawah_lantai_pct"], 0.06)
c("potongan 30%: sama persen mundur", 14.0, BS.loc[30.0, "proporsional_mundur_pct"], 0.06)
c("potongan 30%: optimal mundur", 3.9, BS.loc[30.0, "optimal_mundur_pct"], 0.06)

# ---------------------------------------------------------------- 8. HJB
f36 = O / "36_hjb" / "T1_hjb_vs_aturan.csv"
if f36.exists():
    HJ = pd.read_csv(f36)
    col = "penduduk_di_bawah_lantai_pct(U)"
    h = lambda d, k, kolom=col: HJ[(HJ.dunia.str.startswith(d)) & (HJ.kebijakan == k)][kolom].iloc[0]
    for k, v in (("Aktual 2026 (pola)", 6.91), ("Pangkas merata", 6.91), ("Berbobot kebutuhan (ala DAU)", 6.79), ("HJB", 6.75), ("Aturan r_i", 6.67), ("Per kapita sama", 7.36)):
        c(f"HJB dunia tengah: {k}", v, h("tengah", k), 0.006)
    for k, v in (("Aktual 2026 (pola)", 44.4), ("Pangkas merata", 45.7), ("Berbobot kebutuhan (ala DAU)", 38.3), ("HJB", 39.3), ("Aturan r_i", 35.0), ("Per kapita sama", 55.9)):
        c(f"HJB dunia tengah Q4 lantai kesehatan: {k}", v, h("tengah", k, "Q4_rentan_lantai_kesehatan_pct"), 0.06)
    c("HJB dunia persen", 6.86, h("persen", "HJB"), 0.006); c("aktual dunia persen", 6.81, h("persen", "Aktual 2026 (pola)"), 0.006)
    c("HJB dunia kuat", 7.26, h("kuat", "HJB"), 0.006); c("aktual dunia kuat", 7.24, h("kuat", "Aktual 2026 (pola)"), 0.006)
    c("mundur dunia kuat: r_i", 9.3, h("kuat", "Aturan r_i", "mundur_kesehatan_pct"), 0.06)
    c("mundur dunia kuat: HJB", 7.2, h("kuat", "HJB", "mundur_kesehatan_pct"), 0.06)
    c("mundur dunia kuat: aktual", 4.8, h("kuat", "Aktual 2026 (pola)", "mundur_kesehatan_pct"), 0.06)
    c("robust theta 0.1", 6.753, HJ[HJ.dunia.str.startswith("robust")][col].iloc[0], 0.0006)
    sel = HJ[HJ.kebijakan.notna()].copy(); sel["gap"] = sel[col] - sel.groupby("dunia")[col].transform("min")
    gm = sel.groupby("kebijakan").gap.agg(["mean", "max"])
    c("rata2 selisih HJB", 0.14, gm.loc["HJB", "mean"], 0.006); c("selisih terburuk HJB", 0.50, gm.loc["HJB", "max"], 0.006)
    c("rata2 selisih berbobot kebutuhan", 0.10, gm.loc["Berbobot kebutuhan (ala DAU)", "mean"], 0.006)
    c("rata2 selisih aturan r_i", 0.0, gm.loc["Aturan r_i", "mean"], 0.006)
    pm = pd.read_csv(O / "36_hjb" / "T2_peta_potongan_HJB.csv")
    c("korelasi potongan HJB vs P0", -0.57, pm.potongan_HJB_pct.corr(pm.V_P0, method="spearman"), 0.006)
    c("korelasi potongan aktual vs P0", -0.33, pm.potongan_aktual_pct.corr(pm.V_P0, method="spearman"), 0.006)
    c("HJB unit di batas bawah (tengah)", 12, h("tengah", "HJB", "unit_di_batas_bawah"), 0)

D = pd.DataFrame(cek)
D.to_csv(O / "cek_dokumentasi.csv", index=False)
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 400)
beda = D[D.status == "BEDA"]
print(f"{len(D)} angka diperiksa: {int((D.status == 'OK').sum())} cocok, {len(beda)} berbeda")
if len(beda):
    print(beda.to_string(index=False))
