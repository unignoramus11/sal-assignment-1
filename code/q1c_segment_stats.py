"""Q1c: average energy and ZCR inside each hand-marked phoneme segment,
then compare vowel against non-vowel and voiced against unvoiced.

usage: python q1c_segment_stats.py <wav> <TextGrid> [tag]
"""

import csv
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phone_classes as pc
from textgrid_io import read_textgrid
from q1b_energy_zcr import analyse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def per_segment(res, grid):
    """Mean STE and mean ZCR over the frames whose centre falls in each interval."""
    times, ste, zcr = res["times"], res["ste"], res["zcr"]
    rows = []
    for iv in grid["phone"]:
        lab = iv.text.strip()
        if lab == pc.SIL:
            continue
        sel = (times >= iv.xmin) & (times < iv.xmax)
        if not sel.any():  # segment shorter than the hop, take the nearest frame
            sel = np.zeros_like(times, dtype=bool)
            sel[np.argmin(np.abs(times - iv.midpoint))] = True
        rows.append(dict(
            phone=lab,
            start=iv.xmin,
            end=iv.xmax,
            duration_ms=1000.0 * iv.duration,
            n_frames=int(sel.sum()),
            mean_energy=float(ste[sel].mean()),
            mean_zcr=float(zcr[sel].mean()),
            vowel_class=pc.vowel_class(lab),
            voicing=pc.voicing(lab),
            manner=pc.MANNER.get(lab, ""),
        ))
    return rows


def summarise(rows, key):
    out = {}
    for group in sorted({r[key] for r in rows}):
        sub = [r for r in rows if r[key] == group]
        out[group] = dict(
            n=len(sub),
            energy_mean=float(np.mean([r["mean_energy"] for r in sub])),
            energy_sd=float(np.std([r["mean_energy"] for r in sub], ddof=1)) if len(sub) > 1 else 0.0,
            zcr_mean=float(np.mean([r["mean_zcr"] for r in sub])),
            zcr_sd=float(np.std([r["mean_zcr"] for r in sub], ddof=1)) if len(sub) > 1 else 0.0,
        )
    return out


def print_table(rows):
    print(f"{'phone':<5} {'dur ms':>7} {'frames':>7} {'energy':>11} {'ZCR':>7}  {'class':<9} {'voicing':<8}")
    for r in rows:
        print(f"{r['phone']:<5} {r['duration_ms']:>7.1f} {r['n_frames']:>7d} "
              f"{r['mean_energy']:>11.4e} {r['mean_zcr']:>7.4f}  "
              f"{r['vowel_class']:<9} {r['voicing']:<8}")


def print_summary(name, s):
    print(f"\n{name}:")
    for g, v in s.items():
        print(f"  {g:<10} n={v['n']:<3} energy {v['energy_mean']:.4e} "
              f"(sd {v['energy_sd']:.2e})   ZCR {v['zcr_mean']:.4f} (sd {v['zcr_sd']:.4f})")


def plot_groups(rows, out_png, tag):
    fig, ax = plt.subplots(2, 2, figsize=(11, 7))

    for col, (key, order) in enumerate([("vowel_class", ["vowel", "non-vowel"]),
                                        ("voicing", ["voiced", "unvoiced"])]):
        s = summarise(rows, key)
        groups = [g for g in order if g in s]
        for row, (metric, label) in enumerate([("energy", "mean short-time energy"),
                                               ("zcr", "mean zero-crossing rate")]):
            a = ax[row][col]
            means = [s[g][f"{metric}_mean"] for g in groups]
            sds = [s[g][f"{metric}_sd"] for g in groups]
            bars = a.bar(groups, means, yerr=sds, capsize=5,
                         color=["tab:blue", "tab:orange"][:len(groups)], alpha=0.85)
            # the individual phones behind the group means
            for k, g in enumerate(groups):
                pts = [r[f"mean_{metric}"] for r in rows if r[key] == g]
                a.scatter(np.full(len(pts), k) + np.random.default_rng(1).uniform(-0.12, 0.12, len(pts)),
                          pts, s=14, color="black", zorder=3, alpha=0.6)
            a.set_ylabel(label)
            if metric == "energy":
                a.set_yscale("log")
            a.set_title(f"{label} by {key.replace('_', ' ')}", fontsize=10)

    fig.suptitle(f"{tag}: per-phoneme averages grouped by class "
                 f"(bars are group means with SD, dots are individual phonemes)", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    wav, tg = sys.argv[1], sys.argv[2]
    tag = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(wav).replace(".wav", "")

    res = analyse(wav)
    grid = read_textgrid(tg)
    rows = per_segment(res, grid)

    print_table(rows)
    v = summarise(rows, "vowel_class")
    c = summarise(rows, "voicing")
    print_summary("vowel vs non-vowel", v)
    print_summary("voiced vs unvoiced", c)

    if "vowel" in v and "non-vowel" in v:
        print(f"\nvowel/non-vowel energy ratio: "
              f"{v['vowel']['energy_mean'] / v['non-vowel']['energy_mean']:.1f}x")
        print(f"non-vowel/vowel ZCR ratio:   "
              f"{v['non-vowel']['zcr_mean'] / v['vowel']['zcr_mean']:.1f}x")
    if "voiced" in c and "unvoiced" in c:
        print(f"voiced/unvoiced energy ratio: "
              f"{c['voiced']['energy_mean'] / c['unvoiced']['energy_mean']:.1f}x")
        print(f"unvoiced/voiced ZCR ratio:    "
              f"{c['unvoiced']['zcr_mean'] / c['voiced']['zcr_mean']:.1f}x")

    csv_path = os.path.join(ROOT, "results", f"{tag}_phoneme_stats.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    sum_path = os.path.join(ROOT, "results", f"{tag}_class_summary.csv")
    with open(sum_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["grouping", "group", "n", "mean_energy", "sd_energy", "mean_zcr", "sd_zcr"])
        for name, s in (("vowel_class", v), ("voicing", c)):
            for g, val in s.items():
                w.writerow([name, g, val["n"], f"{val['energy_mean']:.6e}",
                            f"{val['energy_sd']:.6e}", f"{val['zcr_mean']:.6f}",
                            f"{val['zcr_sd']:.6f}"])

    png = os.path.join(ROOT, "plots", f"{tag}_class_comparison.png")
    plot_groups(rows, png, tag)
    print(f"\nwrote {csv_path}\n      {sum_path}\n      {png}")


if __name__ == "__main__":
    main()
