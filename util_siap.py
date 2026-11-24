"""util_siap.py — modul bersama analisis tahap 2 (memakai data siap analisis hasil 30_siapkan_data.py)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "data" / "siap_analisis" / "panel_gabungan.csv"
OUT = ROOT / "output" / "siap"
OUT.mkdir(parents=True, exist_ok=True)
RNG_SEED = 20261123


def out(nama):
    d = OUT / nama
    d.mkdir(parents=True, exist_ok=True)
    return d


def plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as p
    p.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 130})
    return p


def panel():
    D = pd.read_csv(CSV, dtype={"kode_bps": str, "kode_prov_bps": str, "kode_djpk": str})
    D["pop"] = D.penduduk_bps.fillna(D.penduduk_turunan_susenas)
    D["pop_dari_bps"] = D.penduduk_bps.notna()
    D["buf"] = (D.pad + D.silpa) / D.belanja_total
    D["dep"] = D.tkdd_apbd / D.pend_total
    return D


def zs(x):
    return (x - x.mean()) / x.std(ddof=0)


def unit_tabel(D=None):
    """Satu baris per kab/kota Tingkat A (481). Kerentanan V = rata-rata z (P0, -UHH, -HLS, -RLS) 2025; tinggi = rentan."""
    D = panel() if D is None else D
    A = D[D.lengkap_A]
    s = A[A.tahun == 2025].set_index("kode_bps")
    U = s[["nama_wilayah", "jenis_wilayah", "provinsi", "kode_prov_bps", "pop", "pop_dari_bps", "p0", "uhh", "hls", "rls", "ppk",
           "ikk_konstruksi", "buf", "dep", "pend_total", "belanja_total", "pad", "silpa"]].copy()
    U["V"] = (zs(U.p0) - zs(U.uhh) - zs(U.hls) - zs(U.rls)) / 4
    U["V"] = U.V / U.V.std(ddof=0)
    for t in range(2019, 2027):
        z = A[A.tahun == t].set_index("kode_bps")
        U[f"tkdd_{t}"] = z.tkdd_total
        U[f"pop_{t}"] = z["pop"]
    for c in ["dau", "dbh", "dak_fisik", "dak_nonfisik", "dana_desa", "otsus", "transfer_daerah"]:
        for t in (2025, 2026):
            U[f"{c}_{t}"] = A[A.tahun == t].set_index("kode_bps")[c]
    U["bobot"] = U["pop"]
    return U.reset_index()


def wmean(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    m = np.isfinite(x) & np.isfinite(w)
    return float((x[m] * w[m]).sum() / w[m].sum())


def wcov_rank_index(L, V, w):
    """Indeks konsentrasi (Kakwani-Wagstaff) beban L dengan peringkat kerentanan V (tinggi = rentan), tertimbang w."""
    L, V, w = map(lambda a: np.asarray(a, float), (L, V, w))
    o = np.argsort(V, kind="stable")
    L, w = L[o], w[o]
    W = w.sum()
    r = (np.cumsum(w) - 0.5 * w) / W
    mu = (L * w).sum() / W
    cov = (w * (L - mu) * (r - 0.5)).sum() / W
    return float(2 * cov / mu)


def reg_cluster(y, X, cl):
    """OLS dengan galat baku terkelompok (CR1); mengembalikan koefisien, galat baku, jumlah kelompok."""
    X = np.asarray(X, float); y = np.asarray(y, float); n, k = X.shape
    XtXi = np.linalg.pinv(X.T @ X); b = XtXi @ X.T @ y; e = y - X @ b
    cls = pd.Series(cl).astype("category").cat.codes.values; G = cls.max() + 1
    meat = np.zeros((k, k))
    for g in range(G):
        m = cls == g; s = X[m].T @ e[m]; meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G / (G - 1)) * ((n - 1) / max(n - k, 1))
    return b, np.sqrt(np.diag(V)), G


def wild_cluster_p(y, X, cl, j, B=1999, seed=RNG_SEED):
    """Nilai-p wild cluster bootstrap (bobot Rademacher, hipotesis nol dipaksakan) untuk koefisien kolom j; statistik-t terkelompok."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y, float); X = np.asarray(X, float)
    b, se, G = reg_cluster(y, X, cl)
    t0 = b[j] / se[j]
    Xr = np.delete(X, j, axis=1)
    br = np.linalg.pinv(Xr.T @ Xr) @ Xr.T @ y
    fit_r = Xr @ br; e_r = y - fit_r
    cls = pd.Series(cl).astype("category").cat.codes.values
    cnt = 0
    for _ in range(B):
        w = rng.choice([-1.0, 1.0], size=G)[cls]
        ys = fit_r + e_r * w
        bb, ss, _ = reg_cluster(ys, X, cl)
        if abs(bb[j] / ss[j]) >= abs(t0):
            cnt += 1
    return (cnt + 1) / (B + 1)
