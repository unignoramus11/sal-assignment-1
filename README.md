# Speech Analysis and Linguistics, Assignment 1

Mohit Singh, 2023111021

## Contents

```
recordings/   the nine source recordings (44.1 kHz mono, made in Praat)
textgrids/    hand-marked phoneme and word boundaries for Q1 and Q2
code/         analysis scripts (Python and Praat)
results/      measurement tables written by the scripts
plots/        every figure used in the report
2023111021_A1_report.pdf
```

## Requirements

Praat 7.0 and Python 3.12 with numpy, scipy, matplotlib, soundfile and praat-parselmouth.

```
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python numpy scipy matplotlib soundfile praat-parselmouth
```

## Reproducing everything

```
bash code/run_all.sh
```

This rebuilds every CSV in `results/` and every PNG in `plots/` from the recordings and
TextGrids. Q6 needs no recordings and can be run on its own with
`.venv/bin/python code/q6_stft_tau.py`.

## What each script does

| Script | Question | Purpose |
|---|---|---|
| `q1a_make_template.py` | 1a | Writes a pre-labelled TextGrid to segment by hand in Praat |
| `q1a_check_textgrid.py` | 1a | Consistency checks on a completed segmentation |
| `q1b_energy_zcr.py` | 1b | Short-time energy and ZCR, 20 ms window, 10 ms shift |
| `q1c_segment_stats.py` | 1c | Per-phoneme averages, grouped by vowel and by voicing |
| `q2_whisper_compare.py` | 2 | Normal against whisper: voicing, duration, intensity, spectral balance, stop releases |
| `q4_formants.praat` | 4 | Formant tracks for "beat" and "bit" |
| `q4_plot_formants.py` | 4 | Vowel measurement and the F1/F2 plot |
| `q5_pitch.praat` | 5 | Pitch contours for the five emotion recordings |
| `q5_plot_pitch.py` | 5 | Contour overlay and the F0 statistics table |
| `q6_stft_tau.py` | 6 | Synthesises s(t) and recovers tau from the STFT |
| `textgrid_io.py`, `phone_classes.py` | 1, 2 | TextGrid reading and writing, phoneme inventory and class labels |

## Analysis settings

Short-time analysis uses a 20 ms Hamming window with a 10 ms shift, which at 44100 Hz is an
882-sample window advancing 441 samples. Energy is the sum of squared windowed samples per
frame. Zero-crossing rate is computed on the unwindowed frame, since tapering the frame
edges towards zero introduces sign changes that belong to the window rather than the signal.

Praat scripts are run with `--FULL-TRUST`, which Praat 7 requires before a script may write
files.
