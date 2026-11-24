"""34_aturan_alokasi.py â€” Analisis 4: aturan pembagian potongan yang melindungi paling baik, dan pertukaran antarprinsip konstitusional.

Keadaan layanan: X = -V (satuan simpangan baku; tinggi = baik). Dasar 2028 X0 = proyeksi tren EB (33_risiko_layanan, tanpa efek anggaran).
Potongan wilayah i: c_i = r_i * TKDD_2025_i, jumlah tetap = potongan nasional aktual 2026 (unit Tingkat A).
Efek potongan: X_i = X0_i - d * k_i * c_i, k_i = absorb_i / (pop_i * ikk_rel_i) dinormalkan agar rata2 tertimbang penduduk efek aktual = -d. d TIDAK teridentifikasi
dari data (lihat 33) maka d, penyangga (absorb), dan kecuraman keadilan (epsilon) dijadikan himpunan skenario dan aturan dinilai atas seluruh himpunan.
Kerugian: sum_i w_i [ max(0, F - X_i)^(1+eps) + rho * max(0, X25_i - X_i - tol)^2 ]  (lantai minimum dan non-retrogresi).
Aturan: aktual, proporsional, per kapita sama, berbasis kebutuhan (lembut/tegas), optimal-per-skenario, optimal-robust (minimax regret relatif lewat bobot multiplikatif).
"""
import itertools
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

from util_siap import out, plt, unit_tabel, wmean

O = out("34_aturan_alokasi")
U = unit_tabel()
R6 = pd.read_csv(Path(O).parent / "33_risiko_layanan" / "T6_risiko_per_kabkota.csv", dtype={"kode_bps": str}).set_index("kode_bps")
U = U.set_index("kode_bps").join(R6[[c for c in R6.columns if c.startswith(("proyeksi2028_", "peluang_lantai_", "sekarang_di_bawah_lantai_"))]]).reset_index()
n = len(U)
pop = U["pop"].values; T25 = U.tkdd_2025.values; T26 = U.tkdd_2026.values
cut_act = T25 - T26
BUDGET = cut_act.sum()
rbar = BUDGET / T25.sum()
print(f"unit={n}, potongan nasional Tingkat A = Rp{BUDGET/1e12:.1f} T ({rbar*100:.1f}% dari TKDD 2025)")

# ---- keadaan layanan
raw25 = (lambda z: (z(U.p0) - z(U.uhh) - z(U.hls) - z(U.rls)) / 4)(lambda s: (s - s.mean()) / s.std(ddof=0))
sd_raw = raw25.std(ddof=0)
def zproj(var, mu, sd): return (U[f"proyeksi2028_{var}"] - mu) / sd
proj = (zproj("p0", U.p0.mean(), U.p0.std(ddof=0)) - zproj("uhh", U.uhh.mean(), U.uhh.std(ddof=0)) - zproj("hls", U.hls.mean(), U.hls.std(ddof=0)) - zproj("rls", U.rls.mean(), U.rls.std(ddof=0))) / 4 / sd_raw
X25 = -U.V.values
X0 = -proj.values
print(f"X25 rata2={X25.mean():.2f}; X0 (2028 tren) rata2={X0.mean():.2f}; perbaikan rata2={np.mean(X0-X25):.2f} SD")
ikk_rel = (U.ikk_konstruksi / U.ikk_konstruksi.mean()).values
buf = U.buf.clip(0, 0.5).fillna(0).values
V = U.V.values
pctV = pd.Series(V).rank(pct=True).values

# ---- skenario
TOL = 0.05
RHO = 2.0
D_SET, E_SET, A_SET = (0.05, 0.10, 0.20), (0, 2, 6), ("tanpa_penyangga", "dengan_penyangga")
SC = list(itertools.product(D_SET, E_SET, A_SET))
def kvec(absorb):
    a = np.ones(n) if absorb == "tanpa_penyangga" else (1 - buf)
    k = a / (pop * ikk_rel)
    return k / wmean(cut_act * k, pop) * 1.0      # rata2 tertimbang penduduk dari k*c aktual = 1 (jadi efek rata2 aktual = -d)
KV = {a: kvec(a) for a in A_SET}
def F_floor(q): return float(np.quantile(X25, q))
FLOOR = F_floor(0.10)
def state(c, d, a): return X0 - d * KV[a] * c
def loss_parts(c, s, w, floor=None, rho=RHO):
    d, e, a = s; fl = FLOOR if floor is None else floor
    x = state(c, d, a)
    sf = np.maximum(0, fl - x); rt = np.maximum(0, X25 - x - TOL)
    return float((w * sf ** (1 + e)).sum()), float((w * rt ** 2).sum()), x
def metrics(c, s, floor=None):
    d, e, a = s; fl = FLOOR if floor is None else floor
    x = state(c, d, a)
    below = (pop * (x < fl)).sum() / pop.sum() * 100
    short = (pop * np.maximum(0, fl - x)).sum() / pop.sum()
    retro = (pop * (X25 - x > TOL)).sum() / pop.sum() * 100
    return below, short, retro

# ---- aturan
BOX_LO = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
BOX_HI = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
TAG = "" if (BOX_LO, BOX_HI) == (0.5, 1.5) else f"_kotak{BOX_LO}-{BOX_HI}"
print(f"Kotak realokasi: {BOX_LO}-{BOX_HI} x persen potongan rata2")
r_lo, r_hi = BOX_LO * rbar, BOX_HI * rbar
lo = np.minimum(r_lo, 1.0) * np.ones(n); hi = np.minimum(r_hi, 1.0) * np.ones(n)
def fit_budget(raw, lo=lo, hi=hi, total=BUDGET):
    a, b = 0.0, 1e12
    for _ in range(200):
        m = (a + b) / 2
        s = (np.clip(m * raw, lo, hi) * T25).sum()
        a, b = (m, b) if s < total else (a, m)
    return np.clip(a * raw, lo, hi) * T25
RULES = {}
RULES["Aktual 2026"] = cut_act
RULES["Proporsional (sama persen)"] = rbar * T25
RULES["Per kapita sama (dalam kotak)"] = fit_budget(pop / T25 * 1.0)      # kotak sama dengan aturan lain agar sebanding
for nm, a_ in (("Berbasis kebutuhan lembut", 0.5), ("Berbasis kebutuhan tegas", 1.0)):
    z = 2 * pctV - 1
    RULES[nm] = fit_budget(np.maximum(1 - a_ * z, 0.05))

def lagr_solve(M, grid_c, total=BUDGET, iters=60):
    """Penyelesaian dualitas: min_c sum_i M[i,c] + lam*sum c; M (n x G) kerugian per wilayah di tiap titik grid, grid_c (n x G)."""
    scale = max(total, 1.0)
    gcn = grid_c / scale                       # biaya dalam satuan "potongan nasional" agar lambda berorde wajar
    def pick(lam):
        j = np.argmin(M - lam * gcn, axis=1)      # potongan harus menutup anggaran: tiap rupiah potongan "dihargai" lam
        return gcn[np.arange(n), j]
    la_, lb_ = 0.0, 1.0
    while pick(lb_).sum() < 1.0 and lb_ < 1e30: lb_ *= 10
    for _ in range(200):
        mid = (la_ + lb_) / 2
        if pick(mid).sum() < 1.0: la_ = mid
        else: lb_ = mid
    c1, c2 = pick(la_), pick(lb_)               # jumlah c1 < 1 <= c2
    s1, s2 = c1.sum(), c2.sum()
    th = 0.0 if abs(s2 - s1) < 1e-12 else (1.0 - s1) / (s2 - s1)
    th = min(max(th, 0), 1)
    return ((1 - th) * c1 + th * c2) * scale
G = 161
grid_r = lo[:, None] + (hi - lo)[:, None] * np.linspace(0, 1, G)[None, :]
grid_c = grid_r * T25[:, None]
def unit_loss_matrix(s, w, floor=None, rho=RHO):
    d, e, a = s; fl = FLOOR if floor is None else floor
    x = X0[:, None] - d * KV[a][:, None] * grid_c
    return w[:, None] * (np.maximum(0, fl - x) ** (1 + e) + rho * np.maximum(0, X25[:, None] - x - TOL) ** 2)
W1 = pop / pop.sum()
LOSS = {s: unit_loss_matrix(s, W1) for s in SC}
def total_loss(c, s, w=W1, floor=None, rho=RHO):
    a_, b_, _ = loss_parts(c, s, w, floor, rho); return a_ + rho * b_
REF = {s: total_loss(RULES["Proporsional (sama persen)"], s) for s in SC}
OPT = {s: lagr_solve(LOSS[s], grid_c) for s in SC}
central = (0.10, 2, "tanpa_penyangga")
RULES["Optimal (skenario tengah)"] = OPT[central]
# robust: bobot multiplikatif atas kerugian relatif terhadap proporsional
wts = np.ones(len(SC)) / len(SC); avg_c = np.zeros(n); eta = 2.0; its = 40
for it in range(its):
    M = sum(wts[j] * LOSS[s] / REF[s] for j, s in enumerate(SC))
    c = lagr_solve(M, grid_c)
    avg_c += c / its
    rel = np.array([total_loss(c, s) / REF[s] for s in SC])
    wts = wts * np.exp(eta * (rel - rel.mean())); wts /= wts.sum()
RULES["Optimal robust (minimax relatif)"] = avg_c
for k, c in RULES.items():
    assert abs(c.sum() / BUDGET - 1) < 2e-3, (k, c.sum() / BUDGET)
    if k != "Aktual 2026":     # pola aktual boleh di luar batas (sebagian wilayah justru naik)
        assert (c >= -1e-6).all() and (c <= T25 + 1).all(), k

# ---- evaluasi atas himpunan skenario
res = []
for nm, c in RULES.items():
    rel, bel, rts = [], [], []
    for s in SC:
        b_, sh_, rt_ = metrics(c, s); bel.append(b_); rts.append(rt_)
        rel.append(total_loss(c, s) / OPT_val if (OPT_val := total_loss(OPT[s], s)) > 0 else 1.0)
    b0, s0, r0 = metrics(c, central)
    q4 = pctV >= 0.75
    res.append({"aturan": nm, "pangsa_potongan_dari_TKDD_pct_Q4rentan": c[q4].sum() / T25[q4].sum() * 100, "pangsa_potongan_dari_TKDD_pct_Q1": c[pctV < 0.25].sum() / T25[pctV < 0.25].sum() * 100,
                "potongan_per_kapita_rb_Q4": c[q4].sum() / pop[q4].sum() / 1000, "potongan_per_kapita_rb_Q1": c[pctV < .25].sum() / pop[pctV < .25].sum() / 1000,
                "tengah_penduduk_di_bawah_lantai_pct": b0, "tengah_penduduk_mundur_pct": r0,
                "rata2_di_bawah_lantai_pct_18skenario": np.mean(bel), "terburuk_di_bawah_lantai_pct": np.max(bel), "rata2_mundur_pct": np.mean(rts),
                "regret_relatif_rata2": np.mean(rel) - 1, "regret_relatif_terburuk": np.max(rel) - 1})
RS = pd.DataFrame(res); RS.to_csv(O / f"T1_perbandingan_aturan{TAG}.csv", index=False)
print(f"\nLantai F = P10 X2025 = {FLOOR:.2f} SD; tolok mundur = {TOL} SD; rho={RHO}")
print("Tanpa potongan tambahan (X0): penduduk di bawah lantai =", round(((pop * (X0 < FLOOR)).sum() / pop.sum()) * 100, 1), "%")
print(RS.round(3).to_string(index=False))

# ---- apakah aturan lebih baik secara tahan di semua skenario? hitung menang/kalah terhadap aktual
win = []
for nm in RULES:
    if nm == "Aktual 2026": continue
    wl = [total_loss(RULES[nm], s) < total_loss(RULES["Aktual 2026"], s) for s in SC]
    win.append({"aturan": nm, "skenario_lebih_baik_dari_aktual": f"{sum(wl)}/{len(SC)}"})
print("\nKalah/menang terhadap pola aktual:\n", pd.DataFrame(win).to_string(index=False))

# ---- pertukaran lantai vs non-retrogresi (varian rho) pada skenario tengah
fr = []
for rho in (0, 0.5, 1, 2, 5, 20, 100):
    M = unit_loss_matrix(central, W1, rho=rho)
    c = lagr_solve(M, grid_c)
    b_, sh_, rt_ = metrics(c, central)
    fr.append({"rho_non_retrogresi": rho, "penduduk_di_bawah_lantai_pct": b_, "kekurangan_rata2_SD": sh_, "penduduk_mundur_pct": rt_})
for nm in ("Aktual 2026", "Proporsional (sama persen)"):
    b_, sh_, rt_ = metrics(RULES[nm], central); fr.append({"rho_non_retrogresi": nm, "penduduk_di_bawah_lantai_pct": b_, "kekurangan_rata2_SD": sh_, "penduduk_mundur_pct": rt_})
FR = pd.DataFrame(fr); FR.to_csv(O / f"T2_pertukaran_lantai_vs_nonretrogresi{TAG}.csv", index=False)
print("\nPertukaran lantai vs non-retrogresi (skenario tengah):\n", FR.round(3).to_string(index=False))
# pertukaran di bawah lantai lebih tinggi / efek lebih besar: apakah ada trade-off nyata?
fr2 = []
for fq in (0.10, 0.20, 0.30):
    for d_ in (0.10, 0.20, 0.40):
        sc_ = (d_, 2, "tanpa_penyangga")
        flv = F_floor(fq)
        for rho in (0, 2, 20):
            Mx = unit_loss_matrix(sc_, W1, floor=flv, rho=rho); cx = lagr_solve(Mx, grid_c)
            b_, sh_, rt_ = metrics(cx, sc_, flv)
            fr2.append({"lantai_persentil": int(fq * 100), "d": d_, "rho": rho, "di_bawah_lantai_pct": b_, "kekurangan_SD": sh_, "mundur_pct": rt_})
        b_, sh_, rt_ = metrics(cut_act, sc_, flv); fr2.append({"lantai_persentil": int(fq * 100), "d": d_, "rho": "aktual", "di_bawah_lantai_pct": b_, "kekurangan_SD": sh_, "mundur_pct": rt_})
FR2 = pd.DataFrame(fr2); FR2.to_csv(O / f"T2b_pertukaran_menurut_lantai_dan_efek{TAG}.csv", index=False)
print("\nPertukaran menurut tinggi lantai dan besar efek:\n", FR2.round(3).to_string(index=False))
atb = np.isclose(RULES["Optimal robust (minimax relatif)"], lo * T25, rtol=1e-3) | np.isclose(RULES["Optimal robust (minimax relatif)"], hi * T25, rtol=1e-3)
print(f"Aturan robust: {atb.sum()} dari {n} wilayah di batas kotak ({atb.mean()*100:.0f}%)")

# ---- ketahanan terhadap pembobotan wilayah dan lantai
rob = []
for kap_name, kap in (("penduduk", 1.0), ("akar_penduduk", 0.5), ("wilayah_sama", 0.0)):
    w = pop ** kap; w = w / w.sum()
    LM = unit_loss_matrix(central, w)
    c = lagr_solve(LM, grid_c)
    rob.append({"bobot": kap_name, "alokasi": c, **dict(zip(["di_bawah_lantai_pct", "kekurangan", "mundur_pct"], metrics(c, central)))})
base_diff = None
dfr = pd.DataFrame({r["bobot"]: (r["alokasi"] / T25 - cut_act / T25) for r in rob})
dfr.index = U.kode_bps
print("\nKorelasi arah perubahan (optimal - aktual, poin persen) antar pembobotan:\n", dfr.corr().round(2).to_string())
same = ((np.sign(dfr) == np.sign(dfr.iloc[:, [0]].values)).all(axis=1) & (dfr.abs() > 0.5 * 0.01).all(axis=1))
print("Wilayah dengan arah koreksi sama di ketiga pembobotan:", int(same.sum()), "dari", n)
pd.DataFrame([{k: v for k, v in r.items() if k != "alokasi"} for r in rob]).to_csv(O / f"T3_ketahanan_bobot{TAG}.csv", index=False)
for fl_q in (0.05, 0.10, 0.20):
    fl = F_floor(fl_q)
    Mf = unit_loss_matrix(central, W1, floor=fl); c = lagr_solve(Mf, grid_c)
    ba = metrics(RULES["Aktual 2026"], central, fl)[0]; bo = metrics(c, central, fl)[0]
    print(f"lantai P{int(fl_q*100):02d}: aktual {ba:.2f}% -> optimal {bo:.2f}% penduduk di bawah lantai")

# ---- batas potongan aman: besar potongan nasional 0-30%
bs = []
for lvl in (0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
    tot = lvl * T25.sum()
    prop = np.full(n, lvl) * T25
    lo2 = np.minimum(0.5 * lvl, 1.0) * np.ones(n); hi2 = np.minimum(1.5 * lvl, 1.0) * np.ones(n) if lvl > 0 else np.zeros(n)
    if lvl == 0: copt = np.zeros(n)
    else:
        gr = lo2[:, None] + (hi2 - lo2)[:, None] * np.linspace(0, 1, G)[None, :]; gc = gr * T25[:, None]
        xg = X0[:, None] - central[0] * KV[central[2]][:, None] * gc
        Mg = W1[:, None] * (np.maximum(0, FLOOR - xg) ** (1 + central[1]) + RHO * np.maximum(0, X25[:, None] - xg - TOL) ** 2)
        copt = lagr_solve(Mg, gc, total=tot)
    bs.append({"potongan_pct_TKDD": lvl * 100, "proporsional_di_bawah_lantai_pct": metrics(prop, central)[0], "optimal_di_bawah_lantai_pct": metrics(copt, central)[0],
               "proporsional_mundur_pct": metrics(prop, central)[2], "optimal_mundur_pct": metrics(copt, central)[2]})
BS = pd.DataFrame(bs); BS.to_csv(O / f"T4_batas_potongan{TAG}.csv", index=False)
print("\nBatas potongan (skenario tengah):\n", BS.round(2).to_string(index=False))

# ---- siapa yang naik/turun pada aturan robust dibanding aktual
rob_c = RULES["Optimal robust (minimax relatif)"]
DT = pd.DataFrame({"kode_bps": U.kode_bps, "nama_wilayah": U.nama_wilayah, "provinsi": U.provinsi, "pop": pop, "V": V, "persen_potongan_aktual": cut_act / T25 * 100,
                   "persen_potongan_robust": rob_c / T25 * 100})
DT["selisih_poin"] = DT.persen_potongan_robust - DT.persen_potongan_aktual
DT.to_csv(O / f"T5_alokasi_per_kabkota{TAG}.csv", index=False, encoding="utf-8-sig")
print("\nKorelasi (Spearman) persen potongan dengan V: aktual", round(pd.Series(DT.persen_potongan_aktual).corr(pd.Series(V), method="spearman"), 3), "| robust", round(pd.Series(DT.persen_potongan_robust).corr(pd.Series(V), method="spearman"), 3))
print("Provinsi dengan koreksi terbesar (rata2 selisih poin, tertimbang penduduk):")
pv = DT.groupby("provinsi").apply(lambda g: pd.Series({"selisih_poin": wmean(g.selisih_poin, g["pop"]), "pop_juta": g["pop"].sum() / 1e6}), include_groups=False).sort_values("selisih_poin")
print(pd.concat([pv.head(5), pv.tail(5)]).round(2).to_string())

# ---- kategori risiko: sudah di bawah lantai vs rawan jatuh (dari 33)
sk = [c for c in U.columns if c.startswith("sekarang_di_bawah_lantai_")]
pl = [c for c in U.columns if c.startswith("peluang_lantai_")]
below_now = U[sk].any(axis=1); rawan = (~below_now) & (U[pl].max(axis=1) > 0.2)
print(f"\nSudah di bawah lantai pada >=1 luaran: {int(below_now.sum())} kab/kota ({U.loc[below_now,'pop'].sum()/1e6:.1f} juta jiwa); rawan jatuh (>20%): {int(rawan.sum())} ({U.loc[rawan,'pop'].sum()/1e6:.1f} juta)")
U[["kode_bps", "nama_wilayah", "provinsi"]].assign(sudah_di_bawah=below_now.values, rawan_jatuh=rawan.values).to_csv(O / "T6_kategori_risiko.csv", index=False, encoding="utf-8-sig")

# ---- siapa yang mundur dan siapa yang di bawah lantai, menurut kuartil kerentanan dan aturan (skenario tengah)
qv = pd.qcut(pd.Series(V).rank(method="first"), 4, labels=["Q1 paling tidak rentan", "Q2", "Q3", "Q4 paling rentan"])
rows_q = []
for nm in ("Aktual 2026", "Proporsional (sama persen)", "Per kapita sama (dalam kotak)", "Optimal robust (minimax relatif)"):
    x = state(RULES[nm], central[0], central[2])
    for qn in qv.cat.categories:
        m = (qv == qn).values
        rows_q.append({"aturan": nm, "kuartil_V": qn, "pct_penduduk_mundur": (pop[m] * (X25[m] - x[m] > TOL)).sum() / pop[m].sum() * 100,
                       "pct_penduduk_di_bawah_lantai": (pop[m] * (x[m] < FLOOR)).sum() / pop[m].sum() * 100, "rata2_perubahan_SD": wmean(x[m] - X25[m], pop[m])})
KQ = pd.DataFrame(rows_q); KQ.to_csv(O / f"T7_dampak_per_kuartil{TAG}.csv", index=False)
print("\nDampak skenario tengah menurut kuartil kerentanan:\n", KQ.round(2).to_string(index=False))
x_act = state(cut_act, central[0], central[2])
prv = pd.DataFrame({"provinsi": U.provinsi, "mundur": pop * (X25 - x_act > TOL), "pop": pop}).groupby("provinsi").sum()
prv["pct"] = prv.mundur / prv["pop"] * 100
print("Provinsi dengan penduduk mundur terbanyak pada pola aktual (juta jiwa):\n", (prv.mundur / 1e6).sort_values(ascending=False).head(6).round(2).to_string())

# ---- gambar
p = plt()
fig, ax = p.subplots(1, 3, figsize=(15, 4.2))
ax[0].plot(FR.iloc[:7].penduduk_mundur_pct, FR.iloc[:7].penduduk_di_bawah_lantai_pct, "o-", c="#1f6f8b")
for r in FR.iloc[:7].itertuples(): ax[0].annotate(str(r.rho_non_retrogresi), (r.penduduk_mundur_pct, r.penduduk_di_bawah_lantai_pct), fontsize=7)
for r in FR.iloc[7:].itertuples(): ax[0].scatter(r.penduduk_mundur_pct, r.penduduk_di_bawah_lantai_pct, marker="s", label=str(r.rho_non_retrogresi))
ax[0].set_xlabel("penduduk yang layanannya mundur (%)"); ax[0].set_ylabel("penduduk di bawah lantai (%)"); ax[0].set_title("Pertukaran lantai vs non-retrogresi"); ax[0].legend(fontsize=7)
RS2 = RS.set_index("aturan")
ax[1].barh(RS2.index, RS2.rata2_di_bawah_lantai_pct_18skenario, xerr=[RS2.rata2_di_bawah_lantai_pct_18skenario - 0, RS2.terburuk_di_bawah_lantai_pct - RS2.rata2_di_bawah_lantai_pct_18skenario], color="#7aa6c2", alpha=.8)
ax[1].set_title("Penduduk di bawah lantai: rata2 dan terburuk (18 skenario)"); ax[1].set_xlabel("%")
ax[2].plot(BS.potongan_pct_TKDD, BS.proporsional_di_bawah_lantai_pct, "o-", label="proporsional"); ax[2].plot(BS.potongan_pct_TKDD, BS.optimal_di_bawah_lantai_pct, "s-", label="optimal")
ax[2].set_xlabel("potongan TKDD nasional (%)"); ax[2].set_ylabel("penduduk di bawah lantai (%)"); ax[2].set_title("Kurva besar potongan"); ax[2].legend()
p.tight_layout(); p.savefig(O / f"G1_aturan_alokasi{TAG}.png"); p.close()
print("selesai:", O)

