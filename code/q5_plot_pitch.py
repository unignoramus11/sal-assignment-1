"""Q5: pitch contours of "Did you miss the exam?" across four emotions.

Reads the per-frame CSVs written by q5_pitch.praat, overlays the contours on a
normalised time axis, and tabulates the numbers the discussion needs.

usage: python q5_plot_pitch.py <results dir> <plots dir>
"""

import csv
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, filtfilt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ORDER = ["q5_neutral", "q5_happy", "q5_angry", "q5_sad", "q5_surprised"]
NICE = {"q5_neutral": "neutral", "q5_happy": "happy", "q5_angry": "angry",
        "q5_sad": "sad", "q5_surprised": "surprised"}
COLOURS = {"neutral": "grey", "happy": "tab:orange", "angry": "tab:red",
           "sad": "tab:blue", "surprised": "tab:green"}


def speech_region(wav_path, frame_ms=20.0, thresh_frac=0.08):
    """Start and end of speech, measured on a 300-4000 Hz band so that the
    low-frequency mains component does not register as speech."""
    x, fs = sf.read(wav_path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    b, a = butter(4, [300.0 / (fs / 2), min(4000.0, fs / 2 - 1) / (fs / 2)], btype="band")
    xb = filtfilt(b, a, x)
    n = int(frame_ms * fs / 1000.0)
    nf = len(xb) // n
    rms = np.array([np.sqrt(np.mean(xb[i * n:(i + 1) * n] ** 2)) for i in range(nf)])
    loud = rms > thresh_frac * rms.max()
    if not loud.any():
        return 0.0, len(x) / fs
    first, last = np.argmax(loud), nf - 1 - np.argmax(loud[::-1])
    return first * n / fs, (last + 1) * n / fs


def drop_short_runs(f, min_frames=3):
    """Remove isolated voiced frames, which are tracking errors rather than speech."""
    f = f.copy()
    voiced = ~np.isnan(f)
    i = 0
    while i < len(voiced):
        if voiced[i]:
            j = i
            while j < len(voiced) and voiced[j]:
                j += 1
            if j - i < min_frames:
                f[i:j] = np.nan
            i = j
        else:
            i += 1
    return f


def read_pitch(path):
    t, f = [], []
    for r in csv.DictReader(open(path)):
        v = r["f0_hz"].strip()
        t.append(float(r["time_s"]))
        f.append(float(v) if v and v != "--undefined--" else np.nan)
    return np.array(t), np.array(f)


def semitones(hz, ref):
    return 12.0 * np.log2(hz / ref)


def final_slope(t, f, frac=0.25):
    """Least-squares slope in Hz/s over the last `frac` of the voiced part."""
    ok = ~np.isnan(f)
    if ok.sum() < 4:
        return np.nan
    tv, fv = t[ok], f[ok]
    cut = tv[-1] - frac * (tv[-1] - tv[0])
    sel = tv >= cut
    if sel.sum() < 3:
        return np.nan
    return float(np.polyfit(tv[sel], fv[sel], 1)[0])


def main():
    res_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    plot_dir = sys.argv[2] if len(sys.argv) > 2 else "plots"
    rec_dir = sys.argv[3] if len(sys.argv) > 3 else "recordings"

    tracks, rows = {}, []
    for key in ORDER:
        path = os.path.join(res_dir, f"{key}_pitch.csv")
        if not os.path.exists(path):
            print(f"skipping {key}, no {path}")
            continue
        t, f = read_pitch(path)
        wav = os.path.join(rec_dir, f"{key}.wav")
        if os.path.exists(wav):
            t0, t1 = speech_region(wav)
            f[(t < t0) | (t > t1)] = np.nan
        f = drop_short_runs(f)
        ok = ~np.isnan(f)
        if ok.sum() == 0:
            print(f"{key}: no voiced frames found")
            continue
        tv = t[ok]
        name = NICE[key]
        tracks[name] = (t, f)
        rows.append(dict(
            emotion=name,
            duration_s=round(float(tv[-1] - tv[0]), 3),
            voiced_frames=int(ok.sum()),
            voiced_fraction=round(float(ok.sum() / len(f)), 3),
            mean_f0_hz=round(float(np.nanmean(f)), 1),
            min_f0_hz=round(float(np.nanmin(f)), 1),
            max_f0_hz=round(float(np.nanmax(f)), 1),
            range_hz=round(float(np.nanmax(f) - np.nanmin(f)), 1),
            range_semitones=round(float(semitones(np.nanmax(f), np.nanmin(f))), 2),
            sd_f0_hz=round(float(np.nanstd(f, ddof=1)), 1),
            final_slope_hz_per_s=round(final_slope(t, f), 1),
        ))

    if not rows:
        sys.exit("no pitch data found; run the Praat pitch script first")

    hdr = (f"{'emotion':<10} {'dur s':>6} {'mean':>7} {'min':>7} {'max':>7} "
           f"{'range':>7} {'st':>6} {'sd':>6} {'final slope':>12}")
    print(hdr); print("-" * len(hdr))
    for r in rows:
        print(f"{r['emotion']:<10} {r['duration_s']:>6.2f} {r['mean_f0_hz']:>7.1f} "
              f"{r['min_f0_hz']:>7.1f} {r['max_f0_hz']:>7.1f} {r['range_hz']:>7.1f} "
              f"{r['range_semitones']:>6.2f} {r['sd_f0_hz']:>6.1f} "
              f"{r['final_slope_hz_per_s']:>12.1f}")

    base = next((r for r in rows if r["emotion"] == "neutral"), None)
    if base:
        print("\nagainst the neutral baseline:")
        for r in rows:
            if r["emotion"] == "neutral":
                continue
            dm = 12 * np.log2(r["mean_f0_hz"] / base["mean_f0_hz"])
            print(f"  {r['emotion']:<10} mean F0 {dm:+.1f} semitones, "
                  f"range {r['range_semitones'] - base['range_semitones']:+.2f} st, "
                  f"duration {r['duration_s'] - base['duration_s']:+.2f} s")

    out_csv = os.path.join(res_dir, "q5_pitch_summary.csv")
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))

    for name, (t, f) in tracks.items():
        ok = ~np.isnan(f)
        ax[0].plot(t[ok] - t[ok][0], f[ok], ".", ms=3,
                   color=COLOURS.get(name, "black"), label=name)
    ax[0].set_xlabel("time from voicing onset (s)")
    ax[0].set_ylabel("F0 (Hz)")
    ax[0].set_title("pitch contours, real time")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)

    for name, (t, f) in tracks.items():
        ok = ~np.isnan(f)
        tv = t[ok]
        norm = (tv - tv[0]) / (tv[-1] - tv[0])
        ax[1].plot(norm, f[ok], ".", ms=3, color=COLOURS.get(name, "black"), label=name)
    ax[1].set_xlabel("normalised position in utterance")
    ax[1].set_ylabel("F0 (Hz)")
    ax[1].set_title("same contours, time-normalised")
    ax[1].grid(alpha=0.3)

    fig.suptitle('Q5: "Did you miss the exam?" across four emotions plus a neutral baseline',
                 fontsize=12)
    fig.tight_layout()
    out_png = os.path.join(plot_dir, "q5_pitch_contours.png")
    fig.savefig(out_png, dpi=160)
    plt.close(fig)

    # range and mean at a glance
    fig, ax = plt.subplots(figsize=(7.5, 4))
    names = [r["emotion"] for r in rows]
    y = np.arange(len(names))
    for i, r in enumerate(rows):
        c = COLOURS.get(r["emotion"], "black")
        ax.plot([r["min_f0_hz"], r["max_f0_hz"]], [i, i], lw=6, color=c, alpha=0.45,
                solid_capstyle="round")
        ax.plot(r["mean_f0_hz"], i, "o", color=c, ms=9, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(names)
    ax.set_xlabel("F0 (Hz)")
    ax.set_title("F0 range (bar) and mean (dot) by emotion")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    out_png2 = os.path.join(plot_dir, "q5_pitch_ranges.png")
    fig.savefig(out_png2, dpi=160)
    plt.close(fig)

    print(f"\nwrote {out_csv}\n      {out_png}\n      {out_png2}")


if __name__ == "__main__":
    main()
