#!/usr/bin/env bash
# Builds the submission zip. Report source, build scripts and working notes stay out.
set -e
cd "$(dirname "$0")/.."

ROLL=2023111021
STAGE=$(mktemp -d)/${ROLL}_A1
mkdir -p "$STAGE"

cp "${ROLL}_A1_report.pdf" "$STAGE"/
cp README.md "$STAGE"/
mkdir -p "$STAGE"/recordings "$STAGE"/textgrids "$STAGE"/code "$STAGE"/results "$STAGE"/plots
cp recordings/*.wav        "$STAGE"/recordings/
cp textgrids/*.TextGrid    "$STAGE"/textgrids/
cp results/*.csv           "$STAGE"/results/
cp plots/*.png             "$STAGE"/plots/

# analysis code only
for f in textgrid_io.py phone_classes.py preprocess_hum.py \
         q1a_make_template.py q1a_check_textgrid.py \
         q1b_energy_zcr.py q1c_segment_stats.py q2_whisper_compare.py \
         q4_formants.praat q4_plot_formants.py \
         q5_pitch.praat q5_plot_pitch.py q6_stft_tau.py run_all.sh; do
  cp "code/$f" "$STAGE"/code/
done

rm -f "${ROLL}_A1.zip"
( cd "$(dirname "$STAGE")" && zip -qr "$OLDPWD/${ROLL}_A1.zip" "${ROLL}_A1" -x '*.DS_Store' )
rm -rf "$(dirname "$STAGE")"

echo "wrote ${ROLL}_A1.zip"
unzip -l "${ROLL}_A1.zip" | tail -3
