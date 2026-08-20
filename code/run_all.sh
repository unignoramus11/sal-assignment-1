#!/usr/bin/env bash
# Regenerates every result and figure from the recordings and TextGrids.
set -e
cd "$(dirname "$0")/.."

PY=.venv/bin/python
PRAAT="/Applications/Praat.app/Contents/MacOS/Praat"

echo "== hum removal (used for pitch and formants only) =="
$PY code/preprocess_hum.py

echo
echo "== Q1b: energy and ZCR =="
$PY code/q1b_energy_zcr.py recordings/q1_normal.wav textgrids/q1_normal.TextGrid \
    plots/q1b_energy_zcr.png

echo
echo "== Q1c: per-phoneme averages and class comparison =="
$PY code/q1c_segment_stats.py recordings/q1_normal.wav textgrids/q1_normal.TextGrid q1

echo
echo "== Q2: normal against whisper =="
$PY code/q1b_energy_zcr.py recordings/q2_whisper.wav textgrids/q2_whisper.TextGrid \
    plots/q2b_energy_zcr.png
$PY code/q1c_segment_stats.py recordings/q2_whisper.wav textgrids/q2_whisper.TextGrid q2
$PY code/q2_whisper_compare.py

echo
echo "== Q4: formants of beat and bit =="
$PRAAT --run --FULL-TRUST code/q4_formants.praat "$PWD/recordings_hp" "$PWD/results" 5500
$PY code/q4_plot_formants.py results plots recordings_hp

echo
echo "== Q5: pitch contours by emotion =="
$PRAAT --run --FULL-TRUST code/q5_pitch.praat "$PWD/recordings_hp" "$PWD/results" 70 500
$PY code/q5_plot_pitch.py results plots recordings

echo
echo "== Q6: tau from the STFT =="
$PY code/q6_stft_tau.py

echo
echo "done"
