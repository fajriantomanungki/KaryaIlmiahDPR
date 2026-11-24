"""32_penyangga_passthrough.py — Analisis 2: siapa meneruskan potongan ke belanja, siapa punya penyangga?

Beda pertama kab/kota (Tingkat A, 481) dengan efek tahun; per kapita memakai penduduk 2025 tetap (ribu rupiah per kapita).
Bentuk reduksi memakai paparan shift-share (komposisi transfer t-1 x pertumbuhan nasional per komponen, dikeluarkan provinsinya sendiri).
Heterogenitas menurut penyangga: regresi interaksi dan double machine learning (LightGBM, lipatan per provinsi).
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
warnings.filterwarnings("ignore")
import lightgbm as lgb
import numpy as np
import pandas as pd

from util_siap import out, panel, plt, reg_cluster, unit_tabel, wild_cluster_p, wmean

O = out("32_penyangga_passthrough")
D = panel()
U = unit_tabel(D)
A = D[D.lengkap_A].copy().sort_values(["kode_bps", "tahun"])
A = A.merge(U[["kode_bps", "pop", "V"]].rename(columns={"pop": "pop25"}), on="kode_bps")
pc = lambda s: s / A["pop25"] / 1000   # ribu rupiah per kapita
A["T"] = pc(A.tkdd_apbd)
A["Ymod"], A["Ybj"], A["Ypeg"], A["Ybk"], A["Ytot"], A["Ypad"], A["Ypemb"] = (pc(A.b_modal), pc(A.b_barangjasa), pc(A.b_pegawai), pc(A.b_bankeu), pc(A.belanja_total), pc(A.pad), pc(A.pembiayaan_netto))
YS = {"Belanja modal": "Ymod", "Belanja barang-jasa": "Ybj", "Belanja pegawai": "Ypeg", "Bantuan keuangan": "Ybk", "Belanja total": "Ytot", "PAD": "Ypad", "Pembiayaan netto": "Ypemb"}
g = A.groupby("kode_bps")
for c in ["T"] + list(YS.values()):
    A["d" + c] = A[c] - g[c].shift()
A["lag_ok"] = g["tahun"].diff() == 1
# penyangga dan ketergantungan pada t-1
A["buf_l"] = g["buf"].shift(); A["dep_l"] = g["dep"].shift()
A["lnpop"] = np.log(A.pop25)
# shift-share
comp = ["dau", "dbh", "dak_fisik", "dak_nonfisik", "dana_desa"]
A["lain"] = A.tkdd_total - A[comp].fillna(0).sum(axis=1)
comp_all = comp + ["lain"]
for c in comp_all:
    A["l_" + c] = g[c].shift()
A["l_tot"] = g["tkdd_total"].shift()
Zs = np.zeros(len(A))
for t in sorted(A.tahun.unique()):
    for p in A.kode_prov_bps.unique():
        mt = (A.tahun == t)
        out_p = mt & (A.kode_prov_bps != p)
        in_p = mt & (A.kode_prov_bps == p)
        z = 0.0
        for c in comp_all:
            den = A.loc[out_p, "l_" + c].sum()
            gr = (A.loc[out_p, c].sum() / den - 1) if den and den > 0 else 0.0
            z = z + (A.loc[in_p, "l_" + c] / A.loc[in_p, "l_tot"]) * gr
        Zs[np.where(in_p)[0]] = z
A["g_pred"] = Zs
A["Z"] = A.g_pred * A.l_tot / A.pop25 / 1000    # perubahan terprediksi per kapita (ribu rupiah)
S = A[A.lag_ok & A.dT.notna() & A.Z.notna() & A.tahun.between(2021, 2026) & A.dep_l.notna() & np.isfinite(A.dep_l) & A.buf_l.notna() & np.isfinite(A.buf_l)].copy()
print("N obs:", len(S), "| kab/kota:", S.kode_bps.nunique(), "| per tahun:", S.groupby("tahun").size().to_dict())
yd = pd.get_dummies(S.tahun, prefix="y", drop_first=True).astype(float)

def spec(sample, ycol, endog="dT", inst=None):
    s = sample
    ydm = pd.get_dummies(s.tahun, prefix="y", drop_first=True).astype(float).values
    y = s["d" + ycol].values
    if inst is None:     # OLS
        X = np.column_stack([np.ones(len(s)), s[endog].values, ydm])
        b, se, G = reg_cluster(y, X, s.kode_prov_bps.values)
        p = wild_cluster_p(y, X, s.kode_prov_bps.values, 1, B=499)
        return b[1], se[1], p, len(s)
    X = np.column_stack([np.ones(len(s)), s[inst].values, ydm])           # bentuk reduksi: dY pada Z
    b, se, G = reg_cluster(y, X, s.kode_prov_bps.values)
    p = wild_cluster_p(y, X, s.kode_prov_bps.values, 1, B=499)
    return b[1], se[1], p, len(s)

# tahap pertama
Xf = np.column_stack([np.ones(len(S)), S.Z.values, yd.values])
bf, sef, Gf = reg_cluster(S.dT.values, Xf, S.kode_prov_bps.values)
print(f"Tahap pertama: koef={bf[1]:.3f}, t={bf[1]/sef[1]:.2f}, F~{(bf[1]/sef[1])**2:.1f} (kelompok={Gf})")
rows = []
for sam_nm, sam in [("2021-2025", S[S.tahun <= 2025]), ("2021-2026", S)]:
    for nm, yc in YS.items():
        b_ols, se_ols, p_ols, n = spec(sam, yc)
        b_rf, se_rf, p_rf, _ = spec(sam, yc, inst="Z")
        # IV Wald = RF / FS pada sampel yang sama
        ydm = pd.get_dummies(sam.tahun, prefix="y", drop_first=True).astype(float).values
        fs = reg_cluster(sam.dT.values, np.column_stack([np.ones(len(sam)), sam.Z.values, ydm]), sam.kode_prov_bps.values)
        rows.append({"sampel": sam_nm, "luaran": nm, "OLS_koef": b_ols, "OLS_se": se_ols, "OLS_p_wild": p_ols, "RF_koef": b_rf, "RF_se": se_rf, "RF_p_wild": p_rf,
                     "FS_F": (fs[0][1] / fs[1][1]) ** 2, "IV_wald": b_rf / fs[0][1], "N": n})
PT = pd.DataFrame(rows)
PT.to_csv(O / "T1_passthrough.csv", index=False)
print("\nPass-through per Rp1 perubahan TKDD (per kapita):\n", PT.round(3).to_string(index=False))

# ---------------------------------------------------------------- heterogenitas menurut penyangga (tertil buf_l) dan ketergantungan
S["tert_buf"] = pd.qcut(S.buf_l.rank(method="first"), 3, labels=["penyangga_tipis", "penyangga_sedang", "penyangga_tebal"])
S["tert_dep"] = pd.qcut(S.dep_l.rank(method="first"), 3, labels=["dep_rendah", "dep_sedang", "dep_tinggi"])
het = []
for byv, lab in [("tert_buf", "penyangga"), ("tert_dep", "ketergantungan")]:
    Gs = S[byv].cat.categories
    for nm, yc in [("Belanja modal", "Ymod"), ("Belanja barang-jasa", "Ybj"), ("Belanja pegawai", "Ypeg"), ("Belanja total", "Ytot")]:
        ydm = pd.get_dummies(S.tahun, prefix="y", drop_first=True).astype(float).values
        gd = np.column_stack([(S[byv] == k).astype(float).values for k in Gs])
        X = np.column_stack([gd, S.dT.values[:, None] * gd, ydm])    # intersep per kelompok + lereng per kelompok
        y = S["d" + yc].values
        b, se, G = reg_cluster(y, X, S.kode_prov_bps.values)
        sl = b[3:6]; sl_se = se[3:6]
        # beda tebal - tipis (atau tinggi - rendah)
        cov = None
        V = np.diag(se ** 2)   # pendekatan: tanpa kovarians silang (konservatif bila positif)
        diff = sl[0] - sl[2]; diff_se = np.sqrt(sl_se[0] ** 2 + sl_se[2] ** 2)
        for k, kk in enumerate(Gs):
            het.append({"dimensi": lab, "luaran": nm, "kelompok": kk, "koef": sl[k], "se": sl_se[k], "N": int((S[byv] == kk).sum())})
        het.append({"dimensi": lab, "luaran": nm, "kelompok": f"selisih {Gs[0]} - {Gs[2]}", "koef": diff, "se": diff_se, "N": len(S)})
H = pd.DataFrame(het)
H["t"] = H.koef / H.se
H.to_csv(O / "T2_heterogenitas_penyangga.csv", index=False)
print("\nPass-through menurut penyangga/ketergantungan:\n", H.round(3).to_string(index=False))

# ---------------------------------------------------------------- DML: residualisasi LightGBM, lipatan per provinsi
feat = ["buf_l", "dep_l", "lnpop", "V", "l_tot"] + ["l_" + c for c in comp_all]
S["kota"] = (S.jenis_wilayah == "Kota").astype(float)
feat += ["kota"]
Xm = S[feat].copy(); Xm["tahun"] = S.tahun.values
provs = S.kode_prov_bps.unique(); rng = np.random.default_rng(1)
fold_of = dict(zip(provs, rng.permutation(len(provs)) % 5))
fold = S.kode_prov_bps.map(fold_of).values
def crossfit(target):
    r = np.zeros(len(S)); y = S[target].values
    for k in range(5):
        tr, te = fold != k, fold == k
        m = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=8, min_child_samples=20, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1, random_state=1)
        m.fit(Xm[tr], y[tr]); r[te] = y[te] - m.predict(Xm[te])
    return r
rT = crossfit("dT")
dm = []
for nm, yc in [("Belanja modal", "dYmod"), ("Belanja barang-jasa", "dYbj"), ("Belanja pegawai", "dYpeg"), ("Belanja total", "dYtot")]:
    rY = crossfit(yc)
    for byv, lab in [("tert_buf", "penyangga"), ("tert_dep", "ketergantungan")]:
        for kk in S[byv].cat.categories:
            m = (S[byv] == kk).values
            b, se, G = reg_cluster(rY[m], np.column_stack([rT[m]]), S.kode_prov_bps.values[m])
            dm.append({"dimensi": lab, "luaran": nm, "kelompok": kk, "koef_DML": b[0], "se": se[0], "N": int(m.sum())})
    b, se, G = reg_cluster(rY, np.column_stack([rT]), S.kode_prov_bps.values)
    dm.append({"dimensi": "semua", "luaran": nm, "kelompok": "semua", "koef_DML": b[0], "se": se[0], "N": len(S)})
DM = pd.DataFrame(dm)
DM.to_csv(O / "T3_dml_heterogenitas.csv", index=False)
print("\nDML:\n", DM.round(3).to_string(index=False))

# ---------------------------------------------------------------- asimetri: potongan vs kenaikan
asi = []
for nm, yc in [("Belanja modal", "Ymod"), ("Belanja barang-jasa", "Ybj"), ("Belanja pegawai", "Ypeg"), ("Belanja total", "Ytot")]:
    ydm = pd.get_dummies(S.tahun, prefix="y", drop_first=True).astype(float).values
    neg = (S.dT < 0).astype(float).values
    X = np.column_stack([np.ones(len(S)), np.minimum(S.dT.values, 0), np.maximum(S.dT.values, 0), ydm])
    b, se, G = reg_cluster(S["d" + yc].values, X, S.kode_prov_bps.values)
    asi.append({"luaran": nm, "koef_saat_potongan": b[1], "se_potongan": se[1], "koef_saat_kenaikan": b[2], "se_kenaikan": se[2]})
AS = pd.DataFrame(asi); AS.to_csv(O / "T4_asimetri.csv", index=False)
print("\nAsimetri:\n", AS.round(3).to_string(index=False))

# ---------------------------------------------------------------- proyeksi tutup 2026 menurut kuartil kerentanan (memakai lereng kelompok penyangga, skenario bersyarat)
S26 = A[(A.tahun == 2026)].merge(U[["kode_bps"]], on="kode_bps")
print("selesai:", O)
