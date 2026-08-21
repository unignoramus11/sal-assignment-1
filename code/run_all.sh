#!/usr/bin/env bash
# Regenerates every result and figure from the recordings and TextGrids.
set -e
cd "$(dirname "$0")/.."

PY=.venv/bin/python
# Praat: use $PRAAT if set, else whatever is on PATH, else the usual macOS location.
if [ -z "${PRAAT:-}" ]; then
  if command -v praat >/dev/null 2>&1; then
    PRAAT=$(command -v praat)
  elif [ -x "/Applications/Praat.app/Contents/MacOS/Praat" ]; then
    PRAAT="/Applications/Praat.app/Contents/MacOS/Praat"
  fi
fi
if [ ! -x "${PRAAT:-}" ]; then
  echo "Praat not found. Install it, or point at the executable:" >&2
  echo "  PRAAT=/path/to/praat bash code/run_all.sh" >&2
  exit 1
fi
if [ ! -x "$PY" ]; then
  echo "No virtual environment at $PY. Create one first:" >&2
  echo "  uv venv --python 3.12 .venv" >&2
  echo "  uv pip install --python .venv/bin/python numpy scipy matplotlib soundfile praat-parselmouth" >&2
  exit 1
fi

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
