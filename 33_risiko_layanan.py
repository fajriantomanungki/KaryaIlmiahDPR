"""33_risiko_layanan.py — Analisis 3: seberapa besar risiko layanan turun, dan apa yang bisa dikatakan data?

(a) Proyeksi lokal (local projections): luaran t+h - t-1 pada potongan TKDD tahun t (dan eksposur komposisi), dengan uji pra-tren, daya uji (efek minimum terdeteksi)
    dan sensitivitas pra-tren sederhana ala Rambachan-Roth (batas relatif M x |pra-tren| terbesar).
(b) Uji mundur bergulir: apakah fitur anggaran menambah akurasi ramalan luaran dibanding "tanpa perubahan" dan tren terkerutkan; selang prediksi.
(c) Risiko per kab/kota: peluang jatuh di bawah lantai 2028 dari model tren hierarkis empiris-Bayes (kerutan ke provinsi).
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
warnings.filterwarnings("ignore")
import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy.stats import norm

from util_siap import RNG_SEED, out, panel, plt, reg_cluster, unit_tabel, wild_cluster_p, wmean

O = out("33_risiko_layanan")
D = panel()
U = unit_tabel(D)
A = D[D.lengkap_A & D.tahun.between(2020, 2026)].copy()
Y = ["uhh", "hls", "rls", "p0"]
LAB = {"uhh": "UHH (tahun)", "hls": "HLS (tahun)", "rls": "RLS (tahun)", "p0": "Kemiskinan P0 (poin %)"}
W = {v: A.pivot(index="kode_bps", columns="tahun", values=v) for v in Y + ["tkdd_total", "dbh", "dak_fisik", "dana_desa", "buf", "dep"]}
# patahan sumber UHH: wilayah dengan selisih 2023->2024 lebih dari 5 tahun (Papua pegunungan: nilai 2020-2023 dari tabel induk, 2024+ dari isian pemilik).
# Deret 2020-2023 wilayah itu tidak dipakai dalam model deret waktu; nilai 2024-2025 tetap dipakai.
_u = W["uhh"]
patah = _u.index[((_u[2024] - _u[2023]).abs() > 5)]
pd.DataFrame({"kode_bps": patah, "nama_wilayah": U.set_index("kode_bps").loc[patah, "nama_wilayah"].values, "uhh_2023": _u.loc[patah, 2023].values,
              "uhh_2024": _u.loc[patah, 2024].values}).to_csv(O / "T0_patahan_uhh.csv", index=False, encoding="utf-8-sig")
print("Patahan sumber UHH, deret 2020-2023 dikeluarkan:", len(patah), "wilayah")
W["uhh"].loc[patah, [2020, 2021, 2022, 2023]] = np.nan
prov = U.set_index("kode_bps").kode_prov_bps
pop = U.set_index("kode_bps")["pop"]
idx = W["uhh"].index
# eksposur dan potongan (tahun t, persen; positif = potong)
cut = {t: -(W["tkdd_total"][t] / W["tkdd_total"][t - 1] - 1) * 100 for t in range(2021, 2027)}
expo = {t: (W["dbh"][t - 1].fillna(0) + W["dak_fisik"][t - 1].fillna(0) + W["dana_desa"][t - 1].fillna(0)) / W["tkdd_total"][t - 1] * 100 for t in range(2021, 2027)}

# ---------------------------------------------------------------- (a) proyeksi lokal
rows = []
for var in Y:
    for h in (0, 1, 2):
        for tag, X_ in (("potongan_nyata", cut), ("eksposur_komposisi", expo)):
            recs = []
            for t in range(2021, 2026 - h):
                yfut = W[var][t + h] - W[var][t - 1]
                d = pd.DataFrame({"y": yfut, "x": X_[t] / 10, "lvl": W[var][t - 1], "tahun": t, "prov": prov})
                recs.append(d.dropna(subset=["y", "x", "lvl"]))
            S = pd.concat(recs)
            yd = pd.get_dummies(S.tahun, drop_first=True).astype(float).values
            Xm = np.column_stack([np.ones(len(S)), S.x, S.lvl, yd])
            b, se, G = reg_cluster(S.y.values, Xm, S.prov.values)
            p = wild_cluster_p(S.y.values, Xm, S.prov.values, 1, B=499)
            rows.append({"luaran": var, "horizon_h": h, "ukuran_paparan": tag, "koef_per_10pp": b[1], "se": se[1], "p_wild": p, "MDE_80pct_daya": 2.8 * se[1], "N": len(S), "provinsi": G})
LP = pd.DataFrame(rows)
LP.to_csv(O / "T1_proyeksi_lokal.csv", index=False)
print("Efek paparan 10 poin persen potongan TKDD pada perubahan luaran:\n", LP.round(4).to_string(index=False))

# uji pra-tren (lead): perubahan luaran sebelum t pada potongan t
pre = []
for var in Y:
    for tag, X_ in (("potongan_nyata", cut), ("eksposur_komposisi", expo)):
        recs = []
        for t in range(2022, 2026):
            lead = W[var][t - 1] - W[var][t - 2]
            if var == "uhh" and t - 2 < 2020: continue
            d = pd.DataFrame({"y": lead, "x": X_[t] / 10, "tahun": t, "prov": prov}).dropna()
            recs.append(d)
        S = pd.concat(recs); yd = pd.get_dummies(S.tahun, drop_first=True).astype(float).values
        Xm = np.column_stack([np.ones(len(S)), S.x, yd]); b, se, G = reg_cluster(S.y.values, Xm, S.prov.values)
        pre.append({"luaran": var, "ukuran_paparan": tag, "koef_pra_tren": b[1], "se": se[1], "t": b[1] / se[1], "N": len(S)})
PR = pd.DataFrame(pre); PR.to_csv(O / "T2_uji_pra_tren.csv", index=False)
print("\nUji pra-tren:\n", PR.round(4).to_string(index=False))
# sensitivitas: selang dilebarkan sebesar M x |pra-tren|
sens = []
for r in LP[(LP.horizon_h == 1) & (LP.ukuran_paparan == "potongan_nyata")].itertuples():
    pt = PR[(PR.luaran == r.luaran) & (PR.ukuran_paparan == "potongan_nyata")].iloc[0]
    for M in (0, 0.5, 1, 2):
        sens.append({"luaran": r.luaran, "M": M, "lo": r.koef_per_10pp - 1.96 * r.se - M * abs(pt.koef_pra_tren), "hi": r.koef_per_10pp + 1.96 * r.se + M * abs(pt.koef_pra_tren)})
SN = pd.DataFrame(sens); SN.to_csv(O / "T3_sensitivitas_pratren.csv", index=False)
print("\nSelang 95% (h=1) bila pelanggaran tren sejajar sebesar M x |pra-tren|:\n", SN.round(4).to_string(index=False))

# ---------------------------------------------------------------- (b) uji mundur bergulir, h=1
def eb_trend_forecast(Wv, origin, h, start):
    """tren per wilayah (OLS dari start..origin) dikerutkan ke tren provinsi; keluarkan ramalan dan simpangan prediksi."""
    yrs = np.arange(start, origin + 1)
    Z = Wv[yrs].values
    ok = np.isfinite(Z).sum(axis=1) >= 3
    tt = yrs - origin
    slope = np.full(len(Z), np.nan); sd_res = np.full(len(Z), np.nan); lvl = np.full(len(Z), np.nan)
    for i in range(len(Z)):
        m = np.isfinite(Z[i])
        if m.sum() >= 3:
            c = np.polyfit(tt[m], Z[i][m], 1); slope[i], lvl[i] = c[0], c[1]
            r = Z[i][m] - np.polyval(c, tt[m]); sd_res[i] = r.std(ddof=2) if m.sum() > 2 else np.nan
    # wilayah dengan <3 titik: tingkat = nilai terakhir (di asal), kemiringan = rata2 provinsi
    for i in range(len(Z)):
        m = np.isfinite(Z[i])
        if 1 <= m.sum() < 3 and m[-1]:
            lvl[i] = Z[i][-1]
    s = pd.Series(slope, index=Wv.index)
    pm = s.groupby(prov.reindex(Wv.index)).transform("mean")
    s = s.fillna(pm).fillna(np.nanmean(slope))
    pm = pm.fillna(np.nanmean(slope))
    sd_res = np.where(np.isfinite(sd_res), sd_res, np.nanmean(sd_res))
    var_w = np.nanmean(sd_res ** 2) / np.nansum((tt - tt.mean()) ** 2) * 1.0         # varians kemiringan dari galat dalam-wilayah
    var_b = max(np.nanvar(s - pm) - var_w, 1e-6)
    lam = var_b / (var_b + var_w)
    sh = lam * s + (1 - lam) * pm
    f = pd.Series(lvl, index=Wv.index) + sh * h
    sd = pd.Series(np.sqrt(np.nanmean(sd_res ** 2) + (var_w * (1 - lam)) * h ** 2), index=Wv.index)
    return f, sd, lam

bt = []
cover = []
for var in Y:
    for origin in (2023, 2024):
        h = 1; target = origin + h
        start = 2020
        f, sd, lam = eb_trend_forecast(W[var], origin, h, start)
        naive = W[var][origin]
        act = W[var][target]
        m = act.notna() & f.notna() & naive.notna()
        # model fitur anggaran: prediksi perubahan t->t+1 dari fitur t (pelatihan: pasangan t'+1<=origin)
        feats = []
        for t in range(2021, origin + 1):
            d = pd.DataFrame({"dy_next": W[var][t + 1] - W[var][t] if t + 1 <= origin else np.nan, "lvl": W[var][t], "dy_prev": W[var][t] - W[var][t - 1],
                              "cut": cut[t], "expo": expo[t], "buf": W["buf"][t], "dep": W["dep"][t], "tahun": t, "prov": prov})
            feats.append(d)
        Fm = pd.concat(feats)
        tr = Fm[(Fm.tahun < origin)].dropna(subset=["dy_next", "lvl", "dy_prev"]); te = Fm[Fm.tahun == origin]
        cols = ["lvl", "dy_prev", "cut", "expo", "buf", "dep"]
        g1 = lgb.LGBMRegressor(n_estimators=150, learning_rate=0.05, num_leaves=6, min_child_samples=25, verbose=-1, random_state=1).fit(tr[cols], tr.dy_next)
        pred_fisk = W[var][origin] + pd.Series(g1.predict(te[cols]), index=te.index)
        cols0 = ["lvl", "dy_prev"]
        g0 = lgb.LGBMRegressor(n_estimators=150, learning_rate=0.05, num_leaves=6, min_child_samples=25, verbose=-1, random_state=1).fit(tr[cols0], tr.dy_next)
        pred_nofisk = W[var][origin] + pd.Series(g0.predict(te[cols0]), index=te.index)
        mm = m & pred_fisk.notna() & pred_nofisk.notna()
        e = {"naif": (naive - act)[mm], "tren_EB": (f - act)[mm], "GBM_tanpa_anggaran": (pred_nofisk - act)[mm], "GBM_dengan_anggaran": (pred_fisk - act)[mm]}
        for k, v in e.items():
            bt.append({"luaran": var, "asal": origin, "model": k, "RMSE": float(np.sqrt((v ** 2).mean())), "MAE": float(v.abs().mean()), "N": int(mm.sum())})
        z = norm.ppf(0.9)
        lo, hi = f - z * sd, f + z * sd
        cover.append({"luaran": var, "asal": origin, "cakupan_selang80_nominal80": float(((act >= lo) & (act <= hi))[mm].mean()), "lebar_rata2": float((hi - lo)[mm].mean())})
BT = pd.DataFrame(bt); CV = pd.DataFrame(cover)
# kalibrasi simpangan prediksi dari galat uji mundur (selang bawaan model terlalu sempit untuk HLS/RLS/P0): RMSE_h dari tren EB, h=1 (asal 2023, 2024) dan h=2 (asal 2023)
CAL = {}
for var in Y:
    r1 = BT[(BT.luaran == var) & (BT.model == "tren_EB")].RMSE.mean()
    f2, _, _ = eb_trend_forecast(W[var], 2023, 2, 2020)
    e2 = (f2 - W[var][2025]).dropna()
    r2 = float(np.sqrt((e2 ** 2).mean()))
    kappa = float(np.clip(np.log2(r2 / r1), 0.5, 1.0))
    CAL[var] = (r1, r2, kappa)
print("\nKalibrasi galat tren EB (RMSE_1, RMSE_2, kappa):", {k: tuple(round(x, 3) for x in v) for k, v in CAL.items()})
BT.to_csv(O / "T4_uji_mundur.csv", index=False); CV.to_csv(O / "T5_cakupan_selang.csv", index=False)
agg = BT.pivot_table(index=["luaran"], columns="model", values="RMSE", aggfunc="mean")
agg["rasio_anggaran_vs_tanpa"] = agg["GBM_dengan_anggaran"] / agg["GBM_tanpa_anggaran"]
agg["rasio_EB_vs_naif"] = agg["tren_EB"] / agg["naif"]
print("\nUji mundur h=1 (rata2 RMSE asal 2023 dan 2024):\n", agg.round(4).to_string())
print("\nCakupan selang 80%:\n", CV.round(3).to_string(index=False))

# ---------------------------------------------------------------- (c) risiko per kab/kota 2028 (tanpa efek anggaran)
risk = pd.DataFrame(index=idx)
for var in Y:
    f, sd, lam = eb_trend_forecast(W[var], 2025, 3, 2020)
    sd = pd.Series(CAL[var][0] * 3 ** CAL[var][2], index=f.index)       # simpangan terkalibrasi uji mundur (seragam antarwilayah)
    L25 = W[var][2025]
    floor = L25.quantile(0.10) if var != "p0" else L25.quantile(0.90)
    if var == "p0":
        pr = 1 - norm.cdf((floor - f) / sd)
    else:
        pr = norm.cdf((floor - f) / sd)
    risk[f"batas_{var}"] = floor; risk[f"proyeksi2028_{var}"] = f; risk[f"sd_{var}"] = sd; risk[f"peluang_lantai_{var}"] = pr
    risk[f"sekarang_di_bawah_lantai_{var}"] = (L25 < floor) if var != "p0" else (L25 > floor)
    print(f"{var}: lantai/ambang(P10|P90)={floor:.2f}, lambda kerutan={lam:.2f}")
risk["risiko_maks"] = risk[[f"peluang_lantai_{v}" for v in Y]].max(axis=1)
risk["risiko_rata2"] = risk[[f"peluang_lantai_{v}" for v in Y]].mean(axis=1)
risk = risk.join(U.set_index("kode_bps")[["nama_wilayah", "provinsi", "pop", "V"]])
risk.to_csv(O / "T6_risiko_per_kabkota.csv", encoding="utf-8-sig")
print("\nRisiko: kab/kota dengan peluang>0,5 di salah satu luaran:", int((risk.risiko_maks > .5).sum()), "| penduduk (juta):", round(risk.loc[risk.risiko_maks > .5, "pop"].sum() / 1e6, 1))
print("Korelasi risiko_rata2 dengan V:", round(risk.risiko_rata2.corr(risk.V, method="spearman"), 3))
top = risk.sort_values("risiko_rata2", ascending=False).head(15)[["nama_wilayah", "provinsi", "risiko_rata2", "risiko_maks", "V"]]
print(top.round(3).to_string())
print("selesai:", O)
