"""36_hjb_kabkota.py — HJB sebagai satu opsi metode: kebijakan dinamis 2026-2028 (dekomposisi Lagrangian, harga bayangan lambda_t) pada 508 kab/kota.

Memakai mesin HJB tahap sebelumnya (hjb_core/hjb_kab/hjb_jobs) pada data siap analisis (35_siapkan_hjb.py).
Dunia (parameter perilaku yang tak teridentifikasi) dibuat beberapa: phi (kepekaan layanan terhadap transfer), bentuk respons rupiah/persen.
Pembanding statis: pangkas merata, per kapita sama, pola aktual 2026, berbobot kebutuhan, aturan r_i (parameter terkalibrasi tahap sebelumnya).
Keluaran: output/siap/36_hjb/*.csv, hjb_jobs.pkl
Pemakaian: python -I code/siap/36_hjb_kabkota.py [pekerja=3]
"""
import multiprocessing as mp
import os
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["HJB_DATA_DIR"] = str(ROOT / "data" / "analisis_siap")
sys.path.insert(0, str(ROOT / "code")); sys.path.insert(0, str(HERE))
import numpy as np
import pandas as pd

import hjb_jobs as J

OUT = ROOT / "output" / "siap" / "36_hjb"
OUT.mkdir(parents=True, exist_ok=True)
PRM = dict(eps=6, alpha=1.0, beta=0.5, gamma=1)       # aturan r_i terkalibrasi pada tahap sebelumnya (output/kab_aturan_param.json)
WORLDS = [dict(nama="tengah|phi=1.0|rho=0.4|rupiah", phi_h=1.0, rho=0.4, resp="rupiah"),
          dict(nama="lemah|phi=0.5|rho=0.4|rupiah", phi_h=0.5, rho=0.4, resp="rupiah"),
          dict(nama="kuat|phi=2.3|rho=0.4|rupiah", phi_h=2.3, rho=0.4, resp="rupiah"),
          dict(nama="persen|phi=1.0|rho=0.4|persen", phi_h=1.0, rho=0.4, resp="persen"),
          dict(nama="lambat|phi=1.0|rho=0.7|rupiah", phi_h=1.0, rho=0.7, resp="rupiah")]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    nw = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    t0 = time.time()
    S0 = J.make_S({})
    print(f"unit={S0.P}; lantai UHH-idx={S0.floor[0]:.2f}, pendidikan={S0.floor[1]:.2f}; B2025={S0.Bref/1e6:.1f} T, B2026={S0.B26/1e6:.1f} T ({S0.B26/S0.Bref-1:+.1%})", flush=True)
    jobs = [dict(sp, eps=6, prm=PRM) for sp in WORLDS] + [dict(nama="robust|theta=0.1", phi_h=1.0, rho=0.4, resp="rupiah", eps=6, theta=0.1, prm=None)]
    RES = {}
    with ProcessPoolExecutor(max_workers=nw, mp_context=mp.get_context("spawn")) as ex:
        fut = {ex.submit(J.job, sp): sp["nama"] for sp in jobs}
        for f in as_completed(fut):
            nm = fut[f]
            try:
                RES[nm] = f.result()
                print(f"selesai {len(RES)}/{len(jobs)}: {nm} [{time.time()-t0:.0f}s] HJB U={RES[nm].get('HJB', {}).get('U', float('nan')):.3f}", flush=True)
            except Exception as e:
                print(f"GAGAL {nm}: {e!r}", flush=True)
            pickle.dump(RES, open(OUT / "hjb_jobs.pkl", "wb"))
    # ringkasan
    rows = []
    for nm, r in RES.items():
        for pol, m in r.items():
            if isinstance(m, dict) and "U" in m:
                rows.append({"dunia": nm, "kebijakan": pol, "penduduk_di_bawah_lantai_pct(U)": m["U"], "lantai_kesehatan_pct": m["floor_h"], "lantai_pendidikan_pct": m["floor_e"],
                             "Q4_rentan_lantai_kesehatan_pct": m["Q4_floor_h"], "mundur_kesehatan_pct": m["retro_h"], "x_kesehatan_2028": m["x_h_2028"],
                             "unit_di_batas_bawah": m["n_rmin"], "pangsa_unit_dipotong": m["share_potong_unit"], "J6": m["J6"]})
    T = pd.DataFrame(rows); T.to_csv(OUT / "T1_hjb_vs_aturan.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(T.round(3).to_string(index=False))
    # regret: selisih terhadap dunia-terbaik
    best = T.groupby("dunia")["penduduk_di_bawah_lantai_pct(U)"].transform("min")
    T["selisih_vs_terbaik"] = T["penduduk_di_bawah_lantai_pct(U)"] - best
    print("\nrata-rata selisih terhadap kebijakan terbaik di tiap dunia (poin persen penduduk di bawah lantai):")
    print(T.groupby("kebijakan")["selisih_vs_terbaik"].agg(["mean", "max"]).sort_values("mean").round(3).to_string())
    # peta potongan HJB tengah vs aktual
    cen = RES.get("tengah|phi=1.0|rho=0.4|rupiah")
    if cen:
        S0 = J.make_S({})
        P = pd.DataFrame({"kode_bps": S0.provs, "r26_HJB": cen["HJB"]["r26"], "r26_aktual": S0.ract, "V_P0": S0.V, "pop": S0.pop})
        P["potongan_HJB_pct"] = (1 - P.r26_HJB) * 100; P["potongan_aktual_pct"] = (1 - P.r26_aktual) * 100
        P.to_csv(OUT / "T2_peta_potongan_HJB.csv", index=False)
        print("\nkorelasi (Spearman) potongan HJB vs P0:", round(P.potongan_HJB_pct.corr(P.V_P0, method="spearman"), 3), "| aktual vs P0:", round(P.potongan_aktual_pct.corr(P.V_P0, method="spearman"), 3))
    print(f"selesai total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    mp.freeze_support(); main()
