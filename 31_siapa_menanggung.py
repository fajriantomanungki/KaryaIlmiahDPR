"""31_siapa_menanggung.py — Analisis 1: siapa yang menanggung potongan TKDD?

Unit: 481 kab/kota Tingkat A. Kerentanan V (2025) = rata-rata z(P0, -UHH, -HLS, -RLS), tinggi = rentan. Bobot penduduk 2025.
Keluaran: output/siap/31_siapa_menanggung/*.csv|png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from util_siap import RNG_SEED, out, plt, reg_cluster, unit_tabel, wcov_rank_index, wild_cluster_p, wmean

O = out("31_siapa_menanggung")
U = unit_tabel()
rng = np.random.default_rng(RNG_SEED)
print("unit:", len(U), "| penduduk dari turunan Susenas:", int((~U.pop_dari_bps).sum()))

# ------------------------------------------------------------------ beban per tahun (perubahan TKDD per kapita, pop 2025 tetap)
rows = []
for t in range(2020, 2027):
    d = (U[f"tkdd_{t}"] - U[f"tkdd_{t-1}"])
    U[f"d_pk_{t}"] = d / U["pop"] / 1000          # ribu rupiah per kapita
    U[f"d_pct_{t}"] = d / U[f"tkdd_{t-1}"] * 100
U["kuartil_V"] = pd.qcut(U.V.rank(method="first"), 4, labels=["Q1 (paling tidak rentan)", "Q2", "Q3", "Q4 (paling rentan)"])
for t in range(2020, 2027):
    g = U.groupby("kuartil_V", observed=True).apply(
        lambda x: pd.Series({"perubahan_pct_median": x[f"d_pct_{t}"].median(), "perubahan_per_kapita_rata2": wmean(x[f"d_pk_{t}"], x["bobot"])}), include_groups=False)
    g["tahun"] = t
    rows.append(g.reset_index())
Q = pd.concat(rows)
Q.to_csv(O / "T1_perubahan_tkdd_per_kuartil_kerentanan.csv", index=False)
print(Q[Q.tahun.isin([2021, 2025, 2026])].round(2).to_string(index=False))

# ------------------------------------------------------------------ indeks konsentrasi beban potongan, selang bootstrap per provinsi
def ci_stat(df, t):
    L = -(df[f"d_pk_{t}"])                      # beban = penurunan (positif bila dipotong)
    return wcov_rank_index(L, df.V, df.bobot)

provs = U.kode_prov_bps.unique()
def boot(t, B=2000):
    b = []
    for _ in range(B):
        pick = rng.choice(provs, size=len(provs), replace=True)
        d = pd.concat([U[U.kode_prov_bps == p] for p in pick])
        try:
            b.append(ci_stat(d, t))
        except Exception:
            pass
    return np.percentile(b, [2.5, 97.5])
res = []
for t in range(2021, 2027):
    mean_cut = wmean(-U[f"d_pk_{t}"], U.bobot)
    c = ci_stat(U, t)
    lo, hi = boot(t, 1000)
    r_sp = pd.Series(U[f"d_pct_{t}"]).corr(U.V, method="spearman")
    res.append({"tahun": t, "rata2_potongan_per_kapita_rb": mean_cut, "indeks_konsentrasi_beban": c, "ci95_lo": lo, "ci95_hi": hi,
                "spearman_perubahan_pct_vs_V": r_sp, "pct_kabkota_dipotong": (U[f"d_pct_{t}"] < 0).mean() * 100})
R = pd.DataFrame(res)
R.to_csv(O / "T2_indeks_konsentrasi_per_tahun.csv", index=False)
print("\nIndeks konsentrasi beban (positif = beban condong ke rentan; hanya bermakna bila rata2 potongan > 0):")
print(R.round(3).to_string(index=False))

# ------------------------------------------------------------------ dekomposisi 2026 per komponen (Wagstaff)
komp = {"DAU": "dau", "DBH": "dbh", "DAK fisik": "dak_fisik", "DAK nonfisik": "dak_nonfisik", "Dana Desa": "dana_desa", "Otsus": "otsus"}
tot_cut = -(U.tkdd_2026 - U.tkdd_2025)
dek = []
for nama, c in komp.items():
    x = U[f"{c}_2026"].fillna(0) - U[f"{c}_2025"].fillna(0)
    L = -x / U["pop"] / 1000
    muL = wmean(L, U.bobot)
    Ctot_pk = wmean(-(U.tkdd_2026 - U.tkdd_2025) / U["pop"] / 1000, U.bobot)
    dek.append({"komponen": nama, "potongan_nasional_Rp_T": -x.sum() / 1e12, "pangsa_potongan_pct": -x.sum() / (-(U.tkdd_2026 - U.tkdd_2025).sum()) * 100,
                "rata2_potongan_per_kapita_rb": muL, "indeks_konsentrasi": wcov_rank_index(L, U.V, U.bobot) if abs(muL) > 1e-9 else np.nan})
Dk = pd.DataFrame(dek)
Dk["kontribusi_ke_indeks_total"] = Dk.rata2_potongan_per_kapita_rb / Dk.rata2_potongan_per_kapita_rb.sum() * Dk.indeks_konsentrasi
Dk.to_csv(O / "T3_dekomposisi_komponen_2026.csv", index=False)
print("\nDekomposisi 2026 per komponen:\n", Dk.round(3).to_string(index=False))

# ------------------------------------------------------------------ beban 2026 terhadap pendapatan APBD 2025 dan kapasitas penyangga, per kuartil
U["pot_pct_pend"] = -(U.tkdd_2026 - U.tkdd_2025) / U.pend_total * 100
BQ = U.groupby("kuartil_V", observed=True).apply(lambda x: pd.Series({
    "potongan_pct_TKDD_median": -x.d_pct_2026.median(), "potongan_pct_pendapatan_median": x.pot_pct_pend.median(),
    "potongan_per_kapita_rb": wmean(-x.d_pk_2026, x.bobot), "tkdd_per_kapita_2025_rb": wmean(x.tkdd_2025 / x["pop"] / 1000, x.bobot),
    "penyangga_PAD_SiLPA_pct_belanja_median": x.buf.median() * 100, "ketergantungan_TKDD_pct_pendapatan_median": x.dep.median() * 100,
    "penduduk_juta": x["pop"].sum() / 1e6, "n": len(x)}), include_groups=False)
BQ.to_csv(O / "T5_beban_2026_per_kuartil.csv")
print("\nBeban 2026 per kuartil kerentanan:\n", BQ.round(2).T.to_string())

# ------------------------------------------------------------------ apakah potongan mengikuti kerentanan, di luar komposisi transfer?
U["pot_pct26"] = -U.d_pct_2026
for c in ["dbh", "dak_fisik", "dana_desa", "dau"]:
    U[f"sh_{c}"] = U[f"{c}_2025"].fillna(0) / U.tkdd_2025
U["lnpop"] = np.log(U["pop"])
U["kota"] = (U.jenis_wilayah == "Kota").astype(float)
spek = {
    "S1 V saja": ["V"],
    "S2 + ukuran dan jenis": ["V", "lnpop", "kota"],
    "S3 + komposisi transfer 2025": ["V", "lnpop", "kota", "sh_dbh", "sh_dak_fisik", "sh_dana_desa"],
    "S4 + ketergantungan dan penyangga": ["V", "lnpop", "kota", "sh_dbh", "sh_dak_fisik", "sh_dana_desa", "dep", "buf"],
}
Dm = U.dropna(subset=["dep", "buf"]).copy()
Dm = Dm[np.isfinite(Dm.dep) & np.isfinite(Dm.buf)]
rr = []
for nama, xs in spek.items():
    X = np.column_stack([np.ones(len(Dm))] + [Dm[c].values for c in xs])
    y = Dm.pot_pct26.values
    b, se, G = reg_cluster(y, X, Dm.kode_prov_bps.values)
    p = wild_cluster_p(y, X, Dm.kode_prov_bps.values, 1, B=999)
    r2 = 1 - ((y - X @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    rr.append({"spesifikasi": nama, "koef_V_poin_persen_per_SD": b[1], "se_terkelompok": se[1], "p_wild_bootstrap": p, "R2": r2, "N": len(Dm), "provinsi": G})
Rg = pd.DataFrame(rr)
Rg.to_csv(O / "T4_potongan_vs_kerentanan_regresi.csv", index=False)
print("\nPotongan TKDD 2026 (poin persen) vs kerentanan:\n", Rg.round(3).to_string(index=False))

# ------------------------------------------------------------------ gambar
p = plt()
fig, ax = p.subplots(1, 3, figsize=(14, 4))
Qp = Q.pivot(index="tahun", columns="kuartil_V", values="perubahan_pct_median")
Qp.plot(ax=ax[0], marker="o"); ax[0].axhline(0, c="k", lw=.5); ax[0].set_ylabel("perubahan TKDD, median (%)"); ax[0].set_title("Perubahan TKDD menurut kuartil kerentanan"); ax[0].legend(fontsize=7)
ax[1].errorbar(R.tahun, R.indeks_konsentrasi_beban, yerr=[R.indeks_konsentrasi_beban - R.ci95_lo, R.ci95_hi - R.indeks_konsentrasi_beban], fmt="o-", capsize=3)
ax[1].set_ylim(-1, 1.5)
ax[1].axhline(0, c="k", lw=.5); ax[1].set_title("Indeks konsentrasi beban potongan"); ax[1].set_ylabel("indeks (>0: condong ke rentan)")
ax[2].barh(Dk.komponen, Dk.pangsa_potongan_pct, color="#7aa6c2"); ax[2].set_title("Pangsa potongan 2026 per komponen (%)")
p.tight_layout(); p.savefig(O / "G1_siapa_menanggung.png"); p.close()
U.to_csv(O / "unit_dengan_beban.csv", index=False, encoding="utf-8-sig")
print("selesai:", O)
