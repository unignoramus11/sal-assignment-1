"""Q1b: short-time energy and zero-crossing rate, 20 ms window, 10 ms shift.

Both are computed directly from the samples rather than with a library call,
since the point of the question is the framing.

usage: python q1b_energy_zcr.py <wav> [TextGrid] [out.png]
"""

import os
import sys

import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phone_classes as pc
from textgrid_io import read_textgrid

WIN_MS = 20.0
HOP_MS = 10.0


def load_mono(path):
    x, fs = sf.read(path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x.astype(np.float64), fs


def frame(x, fs, win_ms=WIN_MS, hop_ms=HOP_MS):
    """Frames as rows, plus the centre time of each frame."""
    win = int(round(win_ms * fs / 1000.0))
    hop = int(round(hop_ms * fs / 1000.0))
    n = 1 + (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    times = (np.arange(n) * hop + win / 2.0) / fs
    return x[idx], times, win, hop


def short_time_energy(frames, window):
    """Sum of squared windowed samples, one value per frame."""
    return np.sum((frames * window) ** 2, axis=1)


def zero_crossing_rate(frames):
    """Fraction of adjacent sample pairs that change sign.

    Unwindowed on purpose: tapering the frame edges towards zero creates
    sign changes that are an artefact of the window, not of the signal.
    """
    signs = np.sign(frames)
    signs[signs == 0] = 1
    return np.mean(np.abs(np.diff(signs, axis=1)) / 2.0, axis=1)


def analyse(path):
    x, fs = load_mono(path)
    frames, times, win, hop = frame(x, fs)
    window = np.hamming(win)
    ste = short_time_energy(frames, window)
    zcr = zero_crossing_rate(frames)
    return dict(x=x, fs=fs, times=times, ste=ste, zcr=zcr,
                win=win, hop=hop, n_frames=len(times))


def plot(res, tg_path, out_png, title):
    x, fs, times = res["x"], res["fs"], res["times"]
    t = np.arange(len(x)) / fs

    grid = read_textgrid(tg_path) if tg_path and os.path.exists(tg_path) else None

    fig, ax = plt.subplots(3, 1, figsize=(11, 7.5), sharex=True)

    ax[0].plot(t, x, lw=0.3, color="black")
    ax[0].set_ylabel("amplitude")
    ax[0].set_title(title)

    # floor the silence so the log axis keeps those frames on screen
    floor = max(res["ste"][res["ste"] > 0].min(), res["ste"].max() * 1e-7)
    ax[1].plot(times, np.maximum(res["ste"], floor), lw=1.0, color="tab:blue")
    ax[1].set_ylabel("short-time energy")
    ax[1].set_yscale("log")

    ax[2].plot(times, res["zcr"], lw=1.0, color="tab:orange")
    ax[2].set_ylabel("zero-crossing rate")
    ax[2].set_xlabel("time (s)")
    ax[2].set_ylim(0, max(0.5, res["zcr"].max() * 1.05))

    if grid is not None:
        phone = grid["phone"]
        for a in ax:
            for iv in phone:
                a.axvline(iv.xmin, color="grey", lw=0.5, alpha=0.7)
        for iv in phone:
            if iv.text.strip() == pc.SIL:
                continue
            ax[0].text(iv.midpoint, ax[0].get_ylim()[1] * 0.82, iv.text,
                       ha="center", va="top", fontsize=8)
        speech = [iv for iv in phone if iv.text.strip() != pc.SIL]
        if speech:
            pad = 0.12
            ax[0].set_xlim(max(0, speech[0].xmin - pad), min(t[-1], speech[-1].xmax + pad))

    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    wav = sys.argv[1]
    tg = sys.argv[2] if len(sys.argv) > 2 else None
    out = sys.argv[3] if len(sys.argv) > 3 else "plots/q1b_energy_zcr.png"

    res = analyse(wav)
    dur = len(res["x"]) / res["fs"]
    expected = 1 + (len(res["x"]) - res["win"]) // res["hop"]
    print(f"{os.path.basename(wav)}: {dur:.3f} s at {res['fs']} Hz")
    print(f"window {res['win']} samples ({WIN_MS:.0f} ms), hop {res['hop']} samples "
          f"({HOP_MS:.0f} ms)")
    print(f"frames: {res['n_frames']} (expected {expected})")
    print(f"energy range {res['ste'].min():.3e} to {res['ste'].max():.3e}")
    print(f"ZCR range    {res['zcr'].min():.4f} to {res['zcr'].max():.4f}")

    label = os.path.basename(wav).replace(".wav", "")
    plot(res, tg, out, f"{label}: waveform, short-time energy and ZCR "
                       f"({WIN_MS:.0f} ms window, {HOP_MS:.0f} ms shift)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
