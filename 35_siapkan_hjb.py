"""35_siapkan_hjb.py — bentuk tabel unit untuk model HJB (skema sama dengan 23_siapkan_analisis.py) dari data siap analisis.

Keadaan: x_h = indeks UHH = (UHH-20)/(85-20)*100; x_e = indeks pendidikan = ((HLS/18)+(RLS/15))/2*100. Dasar 2025 (seluruh unit Tingkat A lengkap 2025).
Transfer = TKDD total (termasuk Dana Desa), per kapita dalam juta rupiah, penduduk 2025.
Deret UHH wilayah yang patah sumber (selisih 2023->2024 > 5 tahun) hanya memakai 2024-2025 untuk simpangan dan rerata jangka panjang.
Keluaran: data/analisis_siap/unit_kab.csv, seri_kab.csv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from util_siap import ROOT, panel

OUT = ROOT / "data" / "analisis_siap"
OUT.mkdir(parents=True, exist_ok=True)
D = panel()
D = D[D.lengkap_A].copy()
D["xh"] = (D.uhh - 20) / 65 * 100
D["xe"] = ((D.hls / 18) + (D.rls / 15)) / 2 * 100
w = D.pivot(index="kode_bps", columns="tahun", values="uhh")
patah = w.index[(w[2024] - w[2023]).abs() > 5]
D.loc[D.kode_bps.isin(patah) & D.tahun.between(2020, 2023), "xh"] = np.nan
D["buffer_abs"] = D.pad.fillna(0) + D.silpa.fillna(0)
g = lambda t: D[D.tahun == t].set_index("kode_bps")
U = g(2025)[["nama_wilayah", "jenis_wilayah", "provinsi", "kode_prov_bps"]].copy()
U["tr25"] = g(2025).tkdd_total; U["tr26"] = g(2026).tkdd_total
U["xh0"] = g(2025).xh; U["xe0"] = g(2025).xe; U["pop0"] = g(2025)["pop"]; U["p00"] = g(2025).p0; U["ikk_konstruksi0"] = g(2025).ikk_konstruksi
U["penyangga"] = g(2025).buffer_abs / g(2025).belanja_total
for c in ("xh", "xe"):
    U[c + "bar"] = D[D.tahun.between(2023, 2025)].groupby("kode_bps")[c].mean()
U["xhbar"] = U.xhbar.fillna(U.xh0); U["xebar"] = U.xebar.fillna(U.xe0)
U["unit_analisis"] = U[["tr25", "tr26", "xh0", "xe0", "pop0"]].notna().all(axis=1) & (U.tr25 > 0) & (U.tr26 > 0)
U["uref"] = U.tr25 / U.pop0 / 1e6; U["uact"] = U.tr26 / U.pop0 / 1e6; U["ract"] = U.uact / U.uref
U.reset_index().to_csv(OUT / "unit_kab.csv", index=False, encoding="utf-8-sig")
D[D.tahun.between(2020, 2025)][["kode_bps", "tahun", "xh", "xe"]].to_csv(OUT / "seri_kab.csv", index=False)
A = U[U.unit_analisis]
print(f"unit HJB: {len(A)}; potongan {A.tr25.sum()/1e12:.1f} T -> {A.tr26.sum()/1e12:.1f} T ({A.tr26.sum()/A.tr25.sum()-1:+.1%}); patahan UHH: {len(patah)} wilayah")
