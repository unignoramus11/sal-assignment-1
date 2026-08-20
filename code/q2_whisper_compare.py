"""Q2: what survives from normal speech to whisper, measured.

Compares q1_normal.wav and q2_whisper.wav on voicing, formants, duration,
intensity and spectral balance, and measures the release-to-vowel interval for
the /p/ of "pig" against the /b/ of "big" in both conditions.

usage: python q2_whisper_compare.py
"""

import csv
import os
import sys

import numpy as np
import parselmouth
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phone_classes as pc
from textgrid_io import read_textgrid
from q1b_energy_zcr import load_mono, frame

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REC = os.path.join(ROOT, "recordings")
TG = os.path.join(ROOT, "textgrids")
RESULTS = os.path.join(ROOT, "results")
PLOTS = os.path.join(ROOT, "plots")

CASES = [("normal", "q1_normal"), ("whisper", "q2_whisper")]


def voicing_report(snd, floor=60, ceiling=500):
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=floor, pitch_ceiling=ceiling)
    f0 = pitch.selected_array["frequency"]
    voiced = f0[f0 > 0]
    return dict(
        frames=len(f0),
        voiced_frames=int(len(voiced)),
        voiced_fraction=round(float(len(voiced) / len(f0)), 4),
        mean_f0=round(float(voiced.mean()), 1) if len(voiced) else None,
    )


def spectral_balance(x, fs):
    """Centroid and the low/high energy split, both of which shift when the
    glottal source is replaced by turbulence."""
    frames, times, win, hop = frame(x, fs)
    w = np.hamming(win)
    mag = np.abs(np.fft.rfft(frames * w, axis=1))
    freqs = np.fft.rfftfreq(win, 1.0 / fs)
    power = mag ** 2
    total = power.sum(axis=1)
    keep = total > total.max() * 1e-4  # ignore the silences
    centroid = (power[keep] * freqs).sum(axis=1) / total[keep]
    low = power[keep][:, freqs < 1000].sum(axis=1)
    high = power[keep][:, freqs >= 1000].sum(axis=1)
    return dict(
        centroid_hz=round(float(centroid.mean()), 1),
        low_over_high_db=round(float(10 * np.log10(low.sum() / high.sum())), 2),
    )


def burst_time(x, fs, iv, hop_ms=1.0, win_ms=5.0):
    """Locate a stop release as the sharpest energy rise inside the interval."""
    a, b = int(iv.xmin * fs), int(iv.xmax * fs)
    seg = x[a:b]
    win = int(win_ms * fs / 1000.0)
    hop = int(hop_ms * fs / 1000.0)
    if len(seg) < win * 2:
        return None
    n = 1 + (len(seg) - win) // hop
    e = np.array([np.sum(seg[i * hop:i * hop + win] ** 2) for i in range(n)])
    e = np.log10(e + 1e-12)
    rise = np.diff(e)
    if len(rise) == 0:
        return None
    k = int(np.argmax(rise))
    return iv.xmin + (k * hop + win / 2.0) / fs


def stop_measures(x, fs, grid, label, occurrence):
    """Release-to-vowel interval for the nth occurrence of a stop label."""
    phones = [iv for iv in grid["phone"]]
    hits = [i for i, iv in enumerate(phones) if iv.text.strip() == label]
    if len(hits) <= occurrence:
        return None
    i = hits[occurrence]
    iv = phones[i]
    bt = burst_time(x, fs, iv)
    if bt is None:
        return None
    return dict(
        phone=label,
        interval_start_s=round(iv.xmin, 4),
        interval_end_s=round(iv.xmax, 4),
        interval_ms=round(1000 * iv.duration, 1),
        burst_s=round(bt, 4),
        release_to_vowel_ms=round(1000 * (iv.xmax - bt), 1),
    )


def main():
    out_rows, spectro = [], {}
    per_phone = {}

    for cond, stem in CASES:
        wav = os.path.join(REC, f"{stem}.wav")
        tg = os.path.join(TG, f"{stem}.TextGrid")
        if not os.path.exists(wav):
            sys.exit(f"missing {wav}")
        if not os.path.exists(tg):
            sys.exit(f"missing {tg}; segment it in Praat first")

        hp_wav = os.path.join(ROOT, "recordings_hp", f"{stem}.wav")
        x, fs = load_mono(wav)
        xhp, _ = load_mono(hp_wav)
        snd = parselmouth.Sound(wav)
        snd_hp = parselmouth.Sound(hp_wav)
        grid = read_textgrid(tg)

        # Voicing is reported both ways on purpose. The raw figure is inflated by
        # the 100 Hz mains component, which sits inside the pitch search range; the
        # filtered figure is the one that reflects phonation.
        v_raw = voicing_report(snd)
        v = voicing_report(snd_hp)
        sb = spectral_balance(xhp, fs)

        speech = [iv for iv in grid["phone"] if iv.text.strip() != pc.SIL]
        span = speech[-1].xmax - speech[0].xmin
        seg = x[int(speech[0].xmin * fs):int(speech[-1].xmax * fs)]
        rms = float(np.sqrt(np.mean(seg ** 2)))

        row = dict(condition=cond, speech_duration_s=round(span, 3),
                   rms=round(rms, 5), rms_db=round(20 * np.log10(rms), 2),
                   voiced_fraction_raw=v_raw["voiced_fraction"], **v, **sb)
        out_rows.append(row)

        per_phone[cond] = {iv.text.strip(): 1000 * iv.duration for iv in speech}
        spectro[cond] = (snd, grid)

        print(f"\n{cond}:")
        print(f"  speech duration     {span:.3f} s")
        print(f"  voiced frames       {v['voiced_frames']} / {v['frames']} "
              f"({100 * v['voiced_fraction']:.1f}%)   "
              f"[before hum removal: {100 * v_raw['voiced_fraction']:.1f}%]")
        print(f"  mean F0             {v['mean_f0'] if v['mean_f0'] else 'none detected'}")
        print(f"  RMS                 {row['rms_db']:.1f} dB")
        print(f"  spectral centroid   {sb['centroid_hz']:.0f} Hz")
        print(f"  low/high balance    {sb['low_over_high_db']:+.1f} dB")

        for label, occ, word in (("b", 0, "big"), ("p", 0, "pig")):
            m = stop_measures(x, fs, grid, label, occ)
            if m:
                print(f"  /{label}/ in \"{word}\": interval {m['interval_ms']:.0f} ms, "
                      f"release to vowel {m['release_to_vowel_ms']:.0f} ms")
                m.update(condition=cond, word=word)
                out_rows.append({"condition": f"{cond}_stop_{word}", **m})

    with open(os.path.join(RESULTS, "q2_whisper_comparison.csv"), "w", newline="") as fh:
        keys = sorted({k for r in out_rows for k in r})
        w = csv.DictWriter(fh, fieldnames=["condition"] + [k for k in keys if k != "condition"])
        w.writeheader(); w.writerows(out_rows)

    # per-phone durations, normal against whisper
    common = [p for p in per_phone["normal"] if p in per_phone["whisper"]]
    with open(os.path.join(RESULTS, "q2_phone_durations.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["phone", "normal_ms", "whisper_ms", "whisper_minus_normal_ms", "ratio"])
        for p in common:
            n, wh = per_phone["normal"][p], per_phone["whisper"][p]
            w.writerow([p, round(n, 1), round(wh, 1), round(wh - n, 1), round(wh / n, 3)])

    fig, ax = plt.subplots(2, 1, figsize=(12, 7.5))
    for a, (cond, stem) in zip(ax, CASES):
        snd, grid = spectro[cond]
        spec = snd.to_spectrogram(window_length=0.005, maximum_frequency=8000)
        X, Y = spec.x_grid(), spec.y_grid()
        db = 10 * np.log10(spec.values + 1e-12)
        a.pcolormesh(X, Y, db, vmin=db.max() - 65, vmax=db.max(), cmap="Greys", shading="auto")
        phones = [iv for iv in grid["phone"] if iv.text.strip() != pc.SIL]
        for iv in phones:
            a.axvline(iv.xmin, color="tab:red", lw=0.6, alpha=0.8)
            a.text(iv.midpoint, 7400, iv.text, ha="center", fontsize=8, color="tab:red")
        a.axvline(phones[-1].xmax, color="tab:red", lw=0.6, alpha=0.8)
        a.set_xlim(phones[0].xmin - 0.08, phones[-1].xmax + 0.08)
        a.set_ylim(0, 8000)
        a.set_ylabel("frequency (Hz)")
        a.set_title(f"{cond}: {pc.SENTENCE}", fontsize=10)
    ax[1].set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "q2_spectrograms.png"), dpi=160)
    plt.close(fig)

    print(f"\nwrote results/q2_whisper_comparison.csv")
    print(f"      results/q2_phone_durations.csv")
    print(f"      plots/q2_spectrograms.png")


if __name__ == "__main__":
    main()
