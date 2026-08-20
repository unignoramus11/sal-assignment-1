"""Remove the 100 Hz mains hum before pitch analysis.

The recordings carry a steady mains component at 100.0 Hz (the second harmonic
of 50 Hz), present in the silences as well as during speech. It falls inside the
speaker's F0 range, so Praat reports spurious voiced frames and octave errors if
pitch is measured on the raw signal.

A 4th-order Butterworth high-pass at 150 Hz removes it. Autocorrelation pitch
tracking is unaffected by losing the fundamental itself, because the waveform
still repeats at the same period once the harmonics above 150 Hz remain.

Energy and ZCR (Q1) are NOT computed from these filtered files, since filtering
would change the quantity the question asks about.

usage: python preprocess_hum.py
"""

import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, filtfilt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "recordings")
DST = os.path.join(ROOT, "recordings_hp")

CUTOFF = 150.0


def main():
    os.makedirs(DST, exist_ok=True)
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".wav"):
            continue
        x, fs = sf.read(os.path.join(SRC, name))
        if x.ndim > 1:
            x = x.mean(axis=1)
        b, a = butter(4, CUTOFF / (fs / 2), btype="high")
        y = filtfilt(b, a, x)
        sf.write(os.path.join(DST, name), y, fs)

        def hum(sig):
            n = 1 << 16
            seg = sig[:int(0.3 * fs)]
            mag = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), n=n))
            fr = np.fft.rfftfreq(n, 1.0 / fs)
            band = (fr > 90) & (fr < 110)
            return 20 * np.log10(mag[band].max() + 1e-12)

        print(f"{name:<20} hum in leading silence {hum(x):6.1f} -> {hum(y):6.1f} dB")
    print(f"\nwrote {DST}")


if __name__ == "__main__":
    main()
