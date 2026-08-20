"""Q4: compare the vowels of "beat" and "bit" from the Praat formant tracks.

Locates the vowel as the loudest contiguous stretch of the word, measures F1-F3
at the midpoint and averaged over the middle third (the steady state), and draws
the tracks plus an F1/F2 vowel-space plot.

usage: python q4_plot_formants.py <results dir> <plots dir>
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

WORDS = {"q4_beat": ("beat", "iː"), "q4_bit": ("bit", "ɪ")}


def read_track(path):
    t, f1, f2, f3, db = [], [], [], [], []
    for r in csv.DictReader(open(path)):
        def num(k):
            v = r[k].strip()
            if not v or v == "--undefined--":
                return np.nan
            return float(v)
        t.append(float(r["time_s"]))
        f1.append(num("f1_hz")); f2.append(num("f2_hz"))
        f3.append(num("f3_hz")); db.append(num("intensity_db"))
    return (np.array(t), np.array(f1), np.array(f2), np.array(f3), np.array(db))


def band_energy_db(wav_path, times, lo=300.0, hi=3500.0, frame_ms=20.0):
    """Energy in a speech band at each formant-frame time.

    Praat's own intensity contour includes the low-frequency mains component,
    which is loud enough here to swamp a short isolated word, so the vowel is
    located from band-limited energy instead.
    """
    x, fs = sf.read(wav_path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    b, a = butter(4, [lo / (fs / 2), min(hi, fs / 2 - 1) / (fs / 2)], btype="band")
    xb = filtfilt(b, a, x)
    half = int(frame_ms * fs / 2000.0)
    out = []
    for tt in times:
        c = int(tt * fs)
        seg = xb[max(0, c - half):c + half]
        out.append(10 * np.log10(np.sum(seg ** 2) + 1e-20) if len(seg) else -200.0)
    return np.array(out)


def vowel_region(t, db, drop_db=10.0):
    """Longest run of frames within drop_db of the energy peak."""
    ok = db > (np.nanmax(db) - drop_db)
    best, cur_start, best_len = None, None, 0
    for i, v in enumerate(ok):
        if v and cur_start is None:
            cur_start = i
        elif not v and cur_start is not None:
            if i - cur_start > best_len:
                best, best_len = (cur_start, i), i - cur_start
            cur_start = None
    if cur_start is not None and len(ok) - cur_start > best_len:
        best = (cur_start, len(ok))
    return best


def main():
    res_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    plot_dir = sys.argv[2] if len(sys.argv) > 2 else "plots"
    rec_dir = sys.argv[3] if len(sys.argv) > 3 else "recordings"

    data, summary = {}, []
    for key, (word, ipa) in WORDS.items():
        path = os.path.join(res_dir, f"{key}_formants.csv")
        if not os.path.exists(path):
            sys.exit(f"missing {path}; run the Praat formant script first")
        t, f1, f2, f3, _praat_db = read_track(path)
        wav = os.path.join(rec_dir, f"{key}.wav")
        db = band_energy_db(wav, t) if os.path.exists(wav) else _praat_db
        a, b = vowel_region(t, db)
        mid = (a + b) // 2
        third_a, third_b = a + (b - a) // 3, a + 2 * (b - a) // 3

        def steady(arr):
            return float(np.nanmean(arr[third_a:third_b]))

        row = dict(
            file=key, word=word, ipa=ipa,
            vowel_start_s=round(float(t[a]), 4),
            vowel_end_s=round(float(t[b - 1]), 4),
            vowel_duration_ms=round(1000 * float(t[b - 1] - t[a]), 1),
            f1_mid_hz=round(float(f1[mid]), 1),
            f2_mid_hz=round(float(f2[mid]), 1),
            f3_mid_hz=round(float(f3[mid]), 1),
            f1_steady_hz=round(steady(f1), 1),
            f2_steady_hz=round(steady(f2), 1),
            f3_steady_hz=round(steady(f3), 1),
        )
        row["f2_minus_f1_hz"] = round(row["f2_steady_hz"] - row["f1_steady_hz"], 1)
        summary.append(row)
        data[key] = (t, f1, f2, f3, db, a, b)

    for r in summary:
        print(f"{r['word']:>5} /{r['ipa']}/  vowel {r['vowel_duration_ms']:>6.1f} ms   "
              f"F1 {r['f1_steady_hz']:>6.1f}  F2 {r['f2_steady_hz']:>7.1f}  "
              f"F3 {r['f3_steady_hz']:>7.1f}  F2-F1 {r['f2_minus_f1_hz']:>7.1f}")

    beat, bit = summary[0], summary[1]
    print(f"\nF1 difference (bit - beat): {bit['f1_steady_hz'] - beat['f1_steady_hz']:+.1f} Hz")
    print(f"F2 difference (bit - beat): {bit['f2_steady_hz'] - beat['f2_steady_hz']:+.1f} Hz")
    print(f"duration ratio beat/bit:    "
          f"{beat['vowel_duration_ms'] / bit['vowel_duration_ms']:.2f}")

    warn = []
    for r in summary:
        if not (r["f1_steady_hz"] < r["f2_steady_hz"] < r["f3_steady_hz"]):
            warn.append(f"{r['word']}: formants are not in ascending order, "
                        f"the tracker probably mislabelled one")
        if not (200 <= r["f1_steady_hz"] <= 900):
            warn.append(f"{r['word']}: F1 of {r['f1_steady_hz']:.0f} Hz is outside the "
                        f"usual range, try a different maximum formant setting")
    if warn:
        print("\ncheck these:")
        for w in warn:
            print("  - " + w)

    out_csv = os.path.join(res_dir, "q4_vowel_formants.csv")
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0].keys()))
        w.writeheader(); w.writerows(summary)

    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
    for a_i, (key, (word, ipa)) in enumerate(WORDS.items()):
        t, f1, f2, f3, db, a, b = data[key]
        axx = ax[a_i]
        for arr, lab, c in ((f1, "F1", "tab:blue"), (f2, "F2", "tab:orange"),
                            (f3, "F3", "tab:green")):
            axx.plot(t, arr, ".", ms=2.5, color=c, label=lab)
        axx.axvspan(t[a], t[b - 1], color="grey", alpha=0.18)
        axx.set_title(f'"{word}"  /{ipa}/', fontsize=11)
        axx.set_xlabel("time (s)"); axx.set_ylim(0, 4000)
        axx.set_xlim(t[a] - 0.25, t[b - 1] + 0.25)
        axx.legend(fontsize=8, loc="upper right")
    ax[0].set_ylabel("frequency (Hz)")

    axx = ax[2]
    f2s = [r["f2_steady_hz"] for r in summary]
    f1s = [r["f1_steady_hz"] for r in summary]
    padx = max(0.38 * (max(f2s) - min(f2s)), 220)
    pady = max(0.45 * (max(f1s) - min(f1s)), 80)
    axx.set_xlim(max(f2s) + padx, min(f2s) - padx)   # F2 decreasing to the right
    axx.set_ylim(max(f1s) + pady, min(f1s) - pady)   # F1 decreasing upwards
    for r, c in zip(summary, ["tab:blue", "tab:red"]):
        axx.scatter(r["f2_steady_hz"], r["f1_steady_hz"], s=90, color=c, zorder=3)
        # Push each label towards the middle of the panel. Both axes are inverted,
        # so a high-F2 point sits on the left and needs a rightward offset.
        dx = 34 if r["f2_steady_hz"] > np.mean(f2s) else -34
        dy = 22 if r["f1_steady_hz"] > np.mean(f1s) else -22
        axx.annotate(f'{r["word"]} /{r["ipa"]}/',
                     (r["f2_steady_hz"], r["f1_steady_hz"]),
                     textcoords="offset points", xytext=(dx, dy), fontsize=10,
                     ha="center", va="center", color=c)
    axx.set_xlabel("F2 (Hz)"); axx.set_ylabel("F1 (Hz)")
    axx.set_title("vowel space (front is right, high is up)", fontsize=10)
    axx.grid(alpha=0.3)

    fig.suptitle("Q4: formants of the vowels in \"beat\" and \"bit\"", fontsize=12)
    fig.tight_layout()
    out_png = os.path.join(plot_dir, "q4_formants.png")
    fig.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"\nwrote {out_csv}\n      {out_png}")


if __name__ == "__main__":
    main()
