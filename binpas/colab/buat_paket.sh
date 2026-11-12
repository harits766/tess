#!/bin/bash
# Susun ulang paket Colab (inatrade_colab.zip). Data mentah tidak ada di repo, jadi harus disediakan.
# Pakai: bash binpas/colab/buat_paket.sh <Non_PAW_dari_nol.xlsm> <folder keluaran ambil_bps.py> <folder cache json BPS> <folder hasil Tahap 0> <folder tujuan>
set -e
XLSM=$1; BPS=$2; CACHE=$3; T0=$4; OUT=$5
R=$(cd "$(dirname "$0")/../.." && pwd)
P=$OUT/inatrade_colab
rm -rf "$P"; mkdir -p "$P"/data/inatrade "$P"/data/bps "$P"/data/bps_cache "$P"/hasil_tahap0 "$P"/binpas \
  "$P"/beras_colab/data_raw/inatrade "$P"/beras_colab/data_raw/bps "$P"/beras_colab/data_raw/publik
cp "$R"/binpas/colab/03_tahap0.ipynb "$R"/binpas/colab/04_adu_versi_beras.ipynb "$R"/binpas/colab/BACA_DULU.txt "$R"/SERAH_TERIMA.md "$P"/
cp "$R"/binpas/*.py "$R"/binpas/*.md "$P"/binpas/
cp -r "$R"/beras_stok "$P"/beras_stok; cp -r "$R"/stok_komoditas "$P"/stok_komoditas
cp "$XLSM" "$P"/data/inatrade/Non_PAW_dari_nol.xlsm; cp "$BPS"/*.csv "$P"/data/bps/; cp "$CACHE"/*.json "$P"/data/bps_cache/
[ -d "$T0" ] && cp "$T0"/*.csv "$P"/hasil_tahap0/ || true
cp "$R"/beras_stok/colab/* "$P"/beras_colab/; cp "$XLSM" "$P"/beras_colab/data_raw/inatrade/Non_PAW_dari_nol.xlsm
cp "$CACHE"/*.json "$P"/beras_colab/data_raw/bps/; cp "$R"/beras_stok/jangkar_publik.csv "$P"/beras_colab/data_raw/publik/
find "$P" -name "__pycache__" -prune -exec rm -rf {} +
(cd "$OUT" && rm -f inatrade_colab.zip && python3 -c "import shutil; shutil.make_archive('inatrade_colab', 'zip', '.', 'inatrade_colab')")
echo "paket: $OUT/inatrade_colab.zip (berisi data INATRADE internal; jangan di-commit)"
