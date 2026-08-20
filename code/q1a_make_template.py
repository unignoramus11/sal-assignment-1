"""Build the TextGrid template to segment by hand in Praat.

Every interval label is already typed in the right order, so in Praat you only
ever drag boundaries, never retype text. The starting boundaries are placeholders
at even spacing inside the speech region; all of them need moving.

usage: python q1a_make_template.py <wav> <out.TextGrid>
"""

import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, filtfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phone_classes as pc
from textgrid_io import TextGrid, Tier, Interval, write_textgrid


def speech_bounds(x, fs, frame_ms=20.0, thresh_frac=0.08):
    """Rough start and end of speech, so the two silences start near the right place.

    Measured on a 300-4000 Hz band so that low-frequency mains hum, which runs
    through the whole recording, does not read as speech.
    """
    b, a = butter(4, [300.0 / (fs / 2), min(4000.0, fs / 2 - 1) / (fs / 2)], btype="band")
    xb = filtfilt(b, a, x)
    n = int(frame_ms * fs / 1000.0)
    n_frames = len(xb) // n
    rms = np.array([np.sqrt(np.mean(xb[i * n:(i + 1) * n] ** 2)) for i in range(n_frames)])
    loud = rms > thresh_frac * rms.max()
    if not loud.any():
        return 0.0, len(x) / fs
    first, last = np.argmax(loud), n_frames - 1 - np.argmax(loud[::-1])
    return first * n / fs, (last + 1) * n / fs


def spread(labels, start, end):
    """Intervals for `labels` spread evenly between start and end."""
    edges = np.linspace(start, end, len(labels) + 1)
    return [Interval(edges[k], edges[k + 1], lab) for k, lab in enumerate(labels)]


def build(wav_path, out_path):
    x, fs = sf.read(wav_path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    total = len(x) / fs
    t0, t1 = speech_bounds(x, fs)
    # keep a little silence at each end even if the take is tight
    t0 = min(max(t0, 0.0), total * 0.4)
    t1 = max(min(t1, total), total * 0.6)

    grid = TextGrid(0.0, total)

    phone = Tier("phone", 0.0, total)
    phone.intervals = ([Interval(0.0, t0, pc.SIL)]
                       + spread(pc.PHONES, t0, t1)
                       + [Interval(t1, total, pc.SIL)])
    grid.tiers.append(phone)

    word = Tier("word", 0.0, total)
    word.intervals = ([Interval(0.0, t0, pc.SIL)]
                      + spread(pc.WORDS, t0, t1)
                      + [Interval(t1, total, pc.SIL)])
    grid.tiers.append(word)

    write_textgrid(grid, out_path)
    print(f"{os.path.basename(wav_path)}: {total:.3f} s, speech roughly {t0:.3f}-{t1:.3f} s")
    print(f"wrote {out_path}  ({len(phone.intervals)} phone intervals, "
          f"{len(word.intervals)} word intervals)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
