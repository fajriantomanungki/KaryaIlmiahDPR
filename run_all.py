"""run_all.py — jalankan seluruh rangkaian dari data mentah sampai hasil, berurutan.

Pemakaian (dari folder proyek):
    python -I code/siap/run_all.py          # semua, termasuk HJB (sekitar 20-40 menit)
    python -I code/siap/run_all.py cepat    # tanpa HJB

Urutan dan keluaran:
  30  code/30_siapkan_data.py       gabung isian pemilik, samakan satuan, pisahkan wilayah lengkap/tidak lengkap  -> Data_Siap_Analisis.xlsx
  37  siap/37_deskriptif.py         analisis deskriptif                                                            -> output/siap/37_deskriptif
  31  siap/31_siapa_menanggung.py   siapa menanggung potongan                                                      -> output/siap/31_siapa_menanggung
  32  siap/32_penyangga_passthrough.py   pass-through ke belanja, peran penyangga                                  -> output/siap/32_penyangga_passthrough
  33  siap/33_risiko_layanan.py     efek pada luaran, uji mundur, risiko per kab/kota                              -> output/siap/33_risiko_layanan
  34  siap/34_aturan_alokasi.py     perbandingan aturan alokasi (tiga lebar kotak realokasi)                       -> output/siap/34_aturan_alokasi
  35  siap/35_siapkan_hjb.py        tabel unit untuk HJB
  36  siap/36_hjb_kabkota.py        HJB dinamis 2026-2028 dan pembandingnya                                         -> output/siap/36_hjb
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "output" / "siap" / "log"
LOG.mkdir(parents=True, exist_ok=True)
LANGKAH = [("30_siapkan_data", ROOT / "code" / "30_siapkan_data.py", []),
           ("37_deskriptif", ROOT / "code" / "siap" / "37_deskriptif.py", []),
           ("31_siapa_menanggung", ROOT / "code" / "siap" / "31_siapa_menanggung.py", []),
           ("32_penyangga_passthrough", ROOT / "code" / "siap" / "32_penyangga_passthrough.py", []),
           ("33_risiko_layanan", ROOT / "code" / "siap" / "33_risiko_layanan.py", []),
           ("34_aturan_alokasi", ROOT / "code" / "siap" / "34_aturan_alokasi.py", []),
           ("34_aturan_alokasi_0.25-1.75", ROOT / "code" / "siap" / "34_aturan_alokasi.py", ["0.25", "1.75"]),
           ("34_aturan_alokasi_0.75-1.25", ROOT / "code" / "siap" / "34_aturan_alokasi.py", ["0.75", "1.25"]),
           ("35_siapkan_hjb", ROOT / "code" / "siap" / "35_siapkan_hjb.py", []),
           ("36_hjb", ROOT / "code" / "siap" / "36_hjb_kabkota.py", ["3"])]
if len(sys.argv) > 1 and sys.argv[1] == "cepat":
    LANGKAH = [x for x in LANGKAH if not x[0].startswith(("35", "36"))]
for nama, f, arg in LANGKAH:
    print(f"== {nama}", flush=True)
    with open(LOG / f"{nama}.txt", "w", encoding="utf-8") as fh:
        r = subprocess.run([sys.executable, "-W", "ignore", "-I", str(f), *arg], stdout=fh, stderr=subprocess.STDOUT, cwd=ROOT)
    print("   selesai" if r.returncode == 0 else f"   GAGAL (kode {r.returncode}); lihat {LOG / (nama + '.txt')}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)
print("semua langkah selesai")
