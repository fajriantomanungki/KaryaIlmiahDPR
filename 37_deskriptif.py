"""37_deskriptif.py — analisis deskriptif yang bertalian langsung dengan judul (siapa menanggung, siapa rentan, siapa punya penyangga).

Unit: kab/kota Tingkat A. Bobot penduduk 2025 bila disebut "tertimbang". Keluaran: output/siap/37_deskriptif/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from util_siap import out, panel, plt, unit_tabel, wmean

O = out("37_deskriptif")
D = panel()
U = unit_tabel(D)
A = D[D.lengkap_A].copy()
n = len(U)
print(f"unit = {n}; penduduk 2025 = {U['pop'].sum()/1e6:.1f} juta")
U["potongan_pct"] = -(U.tkdd_2026 / U.tkdd_2025 - 1) * 100
U["potongan_rp"] = U.tkdd_2025 - U.tkdd_2026
U["potongan_pk_rb"] = U.potongan_rp / U["pop"] / 1000
U["kuartil"] = pd.qcut(U.V.rank(method="first"), 4, labels=["Q1 (paling tidak rentan)", "Q2", "Q3", "Q4 (paling rentan)"])

# ---- 1. statistik deskriptif 2025
vars_ = {"P0 (%)": "p0", "UHH (tahun)": "uhh", "HLS (tahun)": "hls", "RLS (tahun)": "rls", "PPK (ribu Rp)": "ppk", "Penduduk (jiwa)": "pop", "TKDD 2025 (Rp miliar)": None,
         "Potongan TKDD 2026 (%)": "potongan_pct", "Potongan per kapita (ribu Rp)": "potongan_pk_rb", "Penyangga PAD+SiLPA (% belanja)": None, "Ketergantungan TKDD (% pendapatan)": None}
rows = []
for nm, c in vars_.items():
    if nm.startswith("TKDD 2025"): x = U.tkdd_2025 / 1e9
    elif nm.startswith("Penyangga"): x = U.buf * 100
    elif nm.startswith("Ketergantungan"): x = U.dep * 100
    else: x = U[c]
    x = x.replace([np.inf, -np.inf], np.nan)
    rows.append({"variabel": nm, "N": int(x.notna().sum()), "rata2": x.mean(), "rata2_tertimbang_penduduk": wmean(x, U["pop"]), "SD": x.std(), "min": x.min(), "P25": x.quantile(.25), "median": x.median(), "P75": x.quantile(.75), "maks": x.max()})
T1 = pd.DataFrame(rows); T1.to_csv(O / "T1_statistik_deskriptif.csv", index=False)
print(T1.round(2).to_string(index=False))

# ---- 2. tren nasional tertimbang dan kesenjangan kuartil (kuartil dari V 2025, tetap)
tr = []
for t in range(2020, 2026):
    z = A[A.tahun == t].merge(U[["kode_bps", "kuartil", "pop"]].rename(columns={"pop": "pop25"}), on="kode_bps")
    for var in ("uhh", "hls", "rls", "p0"):
        for q in ("Q1 (paling tidak rentan)", "Q4 (paling rentan)"):
            m = z[(z.kuartil == q) & z[var].notna()]
            tr.append({"tahun": t, "luaran": var, "kelompok": q, "rata2_tertimbang": wmean(m[var], m.pop25)})
        m = z[z[var].notna()]
        tr.append({"tahun": t, "luaran": var, "kelompok": "nasional", "rata2_tertimbang": wmean(m[var], m.pop25)})
T2 = pd.DataFrame(tr); T2.to_csv(O / "T2_tren_luaran.csv", index=False)
pv = T2[T2.tahun.isin([2020, 2025])].pivot_table(index=["luaran", "kelompok"], columns="tahun", values="rata2_tertimbang")
pv["perubahan"] = pv[2025] - pv[2020]
print("\nTren luaran (tertimbang penduduk):\n", pv.round(2).to_string())
gap = T2.pivot_table(index=["tahun", "luaran"], columns="kelompok", values="rata2_tertimbang")
gap["kesenjangan_Q4_Q1"] = gap["Q4 (paling rentan)"] - gap["Q1 (paling tidak rentan)"]
gap.to_csv(O / "T2b_kesenjangan_kuartil.csv")

# ---- 3. komposisi TKDD 2025 vs 2026
comp = {"DAU": "dau", "DBH": "dbh", "DAK fisik": "dak_fisik", "DAK nonfisik": "dak_nonfisik", "Dana Desa": "dana_desa", "Otsus": "otsus"}
cr = []
for nm, c in comp.items():
    a25, a26 = U[f"{c}_2025"].fillna(0).sum(), U[f"{c}_2026"].fillna(0).sum()
    cr.append({"komponen": nm, "Rp_T_2025": a25 / 1e12, "Rp_T_2026": a26 / 1e12, "perubahan_pct": (a26 / a25 - 1) * 100 if a25 else np.nan, "pangsa_2025_pct": a25 / U.tkdd_2025.sum() * 100,
               "pangsa_dari_total_potongan_pct": (a25 - a26) / U.potongan_rp.sum() * 100})
T3 = pd.DataFrame(cr); T3.to_csv(O / "T3_komposisi_tkdd.csv", index=False)
print("\nKomposisi TKDD:\n", T3.round(2).to_string(index=False))
# komposisi menurut kuartil
sh = []
for q, g in U.groupby("kuartil", observed=True):
    r = {"kuartil": q}
    for nm, c in comp.items():
        r[f"pangsa_{nm}_pct"] = g[f"{c}_2025"].fillna(0).sum() / g.tkdd_2025.sum() * 100
    sh.append(r)
T3b = pd.DataFrame(sh); T3b.to_csv(O / "T3b_komposisi_menurut_kuartil.csv", index=False)
print(T3b.round(1).to_string(index=False))

# ---- 4. sebaran potongan dan konsentrasi
srt = U.sort_values("potongan_rp", ascending=False)
top10 = srt.head(int(round(n * 0.10)))
dist = {"unit_dipotong_pct": (U.potongan_pct > 0).mean() * 100, "potongan_P10": U.potongan_pct.quantile(.1), "potongan_median": U.potongan_pct.median(), "potongan_P90": U.potongan_pct.quantile(.9),
        "unit_dipotong_>=25pct": (U.potongan_pct >= 25).mean() * 100, "pangsa_potongan_rupiah_10pct_unit_terbesar": top10.potongan_rp.sum() / U.potongan_rp.sum() * 100,
        "penduduk_di_unit_potongan_>=25pct_juta": U.loc[U.potongan_pct >= 25, "pop"].sum() / 1e6}
print("\nSebaran potongan 2026:", {k: round(v, 2) for k, v in dist.items()})
pd.Series(dist).to_csv(O / "T4_sebaran_potongan.csv", header=["nilai"])
prv = U.groupby("provinsi").apply(lambda g: pd.Series({"potongan_Rp_T": g.potongan_rp.sum() / 1e12, "potongan_pct": g.potongan_rp.sum() / g.tkdd_2025.sum() * 100, "penduduk_juta": g["pop"].sum() / 1e6,
                                                    "potongan_pk_rb": g.potongan_rp.sum() / g["pop"].sum() / 1000, "rata2_V": wmean(g.V, g["pop"])}), include_groups=False).sort_values("potongan_Rp_T", ascending=False)
prv.to_csv(O / "T5_potongan_per_provinsi.csv")
print("\nProvinsi dengan potongan terbesar:\n", prv.head(8).round(2).to_string())

# ---- 5. tipologi kerentanan ganda
U["miskin_tinggi"] = U.p0 >= U.p0.quantile(2 / 3)
U["bergantung_tinggi"] = U.dep >= U.dep.quantile(2 / 3)
U["penyangga_tipis"] = U.buf <= U.buf.quantile(1 / 3)
U["jumlah_kerentanan"] = U[["miskin_tinggi", "bergantung_tinggi", "penyangga_tipis"]].sum(axis=1)
tp = U.groupby("jumlah_kerentanan").apply(lambda g: pd.Series({"kab_kota": len(g), "penduduk_juta": g["pop"].sum() / 1e6, "pangsa_penduduk_pct": g["pop"].sum() / U["pop"].sum() * 100,
                                                              "pangsa_potongan_Rp_pct": g.potongan_rp.sum() / U.potongan_rp.sum() * 100, "potongan_pct_TKDD": g.potongan_rp.sum() / g.tkdd_2025.sum() * 100,
                                                              "potongan_per_kapita_rb": g.potongan_rp.sum() / g["pop"].sum() / 1000}), include_groups=False)
tp.to_csv(O / "T6_tipologi_kerentanan_ganda.csv")
print("\nTipologi kerentanan ganda (miskin tinggi, bergantung tinggi, penyangga tipis):\n", tp.round(1).to_string())

# ---- 6. persistensi kebutuhan
w = A.pivot(index="kode_bps", columns="tahun", values="p0")
pers = {f"Spearman P0 {a} vs {b}": w[a].corr(w[b], method="spearman") for a, b in [(2021, 2025), (2023, 2025), (2024, 2025)]}
print("\nPersistensi peringkat kemiskinan:", {k: round(v, 3) for k, v in pers.items()})
pd.Series(pers).to_csv(O / "T7_persistensi.csv", header=["spearman"])

# ---- 7. belanja APBD 2025 -> 2026 (anggaran)
bj = []
for nm, c in {"Belanja total": "belanja_total", "Belanja pegawai": "b_pegawai", "Belanja barang-jasa": "b_barangjasa", "Belanja modal": "b_modal", "Bantuan keuangan": "b_bankeu", "PAD": "pad", "TKDD di APBD": "tkdd_apbd"}.items():
    a = A[A.tahun == 2025][c].sum(); b = A[A.tahun == 2026][c].sum()
    bj.append({"pos": nm, "Rp_T_2025": a / 1e12, "Rp_T_2026": b / 1e12, "perubahan_pct": (b / a - 1) * 100})
T8 = pd.DataFrame(bj); T8.to_csv(O / "T8_belanja_apbd.csv", index=False)
print("\nAPBD 2025 -> 2026 (anggaran):\n", T8.round(2).to_string(index=False))

# ---- gambar
p = plt()
fig, ax = p.subplots(2, 2, figsize=(12, 8))
for a_, var, lab in zip(ax.ravel(), ("uhh", "hls", "rls", "p0"), ("UHH (tahun)", "HLS (tahun)", "RLS (tahun)", "Kemiskinan P0 (%)")):
    for kel, c in (("nasional", "k"), ("Q1 (paling tidak rentan)", "#2a9d8f"), ("Q4 (paling rentan)", "#e76f51")):
        z = T2[(T2.luaran == var) & (T2.kelompok == kel)]
        a_.plot(z.tahun, z.rata2_tertimbang, "o-", c=c, label=kel)
    a_.set_title(lab); a_.legend(fontsize=7)
p.suptitle("Luaran layanan 2020–2025, tertimbang penduduk"); p.tight_layout(); p.savefig(O / "G1_tren_luaran.png"); p.close()

fig, ax = p.subplots(1, 3, figsize=(15, 4.2))
ax[0].barh(T3.komponen, T3.perubahan_pct, color="#7aa6c2"); ax[0].set_title("Perubahan komponen TKDD 2025→2026 (%)")
T3b.set_index("kuartil")[[c for c in T3b.columns if c.startswith("pangsa_") and "Otsus" not in c]].plot(kind="bar", stacked=True, ax=ax[1], legend=True, width=.8)
ax[1].set_title("Komposisi TKDD 2025 menurut kuartil kerentanan (%)"); ax[1].legend(fontsize=6); ax[1].set_xticklabels([t.get_text()[:2] for t in ax[1].get_xticklabels()], rotation=0)
ax[2].scatter(U.V, U.potongan_pct, s=np.sqrt(U["pop"]) / 15, alpha=.4, c="#1f6f8b"); ax[2].set_xlabel("indeks kerentanan V (SD)"); ax[2].set_ylabel("potongan TKDD 2026 (%)"); ax[2].set_title("Potongan vs kerentanan (ukuran titik = penduduk)")
p.tight_layout(); p.savefig(O / "G2_komposisi_dan_potongan.png"); p.close()

fig, ax = p.subplots(1, 2, figsize=(11, 4.2))
q = U.groupby("kuartil", observed=True).apply(lambda g: pd.Series({"potongan_pct_TKDD": g.potongan_rp.sum() / g.tkdd_2025.sum() * 100, "penyangga": g.buf.median() * 100, "ketergantungan": g.dep.median() * 100}), include_groups=False)
q[["potongan_pct_TKDD", "penyangga", "ketergantungan"]].plot(kind="bar", ax=ax[0]); ax[0].set_xticklabels([t.get_text()[:2] for t in ax[0].get_xticklabels()], rotation=0); ax[0].set_title("Potongan, penyangga, ketergantungan (%)")
tp[["pangsa_penduduk_pct", "pangsa_potongan_Rp_pct"]].plot(kind="bar", ax=ax[1]); ax[1].set_xlabel("jumlah kerentanan (miskin, bergantung, penyangga tipis)"); ax[1].set_title("Pangsa penduduk dan pangsa potongan"); ax[1].tick_params(axis="x", rotation=0)
p.tight_layout(); p.savefig(O / "G3_penyangga_dan_tipologi.png"); p.close()
print("selesai:", O)
