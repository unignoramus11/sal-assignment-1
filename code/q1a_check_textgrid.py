"""Sanity checks on a hand-segmented TextGrid.

Reports anything that needs another look in Praat: labels out of order, intervals
that were never moved off the placeholder grid, implausible durations, and
boundaries that disagree with the acoustics.

usage: python q1a_check_textgrid.py <wav> <TextGrid>
"""

import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phone_classes as pc
from textgrid_io import read_textgrid

# generous bounds; these only catch things that are clearly wrong
MIN_MS = {"stop": 8, "fricative": 20, "nasal": 20, "vowel": 25}
MAX_MS = 400


def check(wav_path, tg_path):
    x, fs = sf.read(wav_path)
    if x.ndim > 1:
        x = x.mean(axis=1)
    grid = read_textgrid(tg_path)
    problems = []

    for tier_name, expected in (("phone", pc.phone_tier_labels()),
                                ("word", pc.word_tier_labels())):
        tier = grid[tier_name]
        got = [iv.text.strip() for iv in tier]
        if got != expected:
            problems.append(f"{tier_name} tier labels changed.\n"
                            f"  expected: {' '.join(expected)}\n"
                            f"  found:    {' '.join(got)}")

    phone = grid["phone"]
    durs = np.array([iv.duration for iv in phone])

    # placeholder detection: the template spaces the 20 phones equally
    inner = durs[1:-1]
    if len(inner) and inner.std() < 1e-6:
        problems.append("phone boundaries are still at the template's even spacing, "
                        "so nothing has been segmented yet")

    for iv in phone:
        lab = iv.text.strip()
        ms = iv.duration * 1000.0
        if ms <= 0:
            problems.append(f"{lab!r} has zero or negative duration ({ms:.1f} ms)")
            continue
        if lab == pc.SIL:
            continue
        floor = MIN_MS.get(pc.MANNER.get(lab, ""), 15)
        if ms < floor:
            problems.append(f"{lab!r} is {ms:.0f} ms, short for a {pc.MANNER.get(lab)} "
                            f"(under {floor} ms)")
        if ms > MAX_MS:
            problems.append(f"{lab!r} is {ms:.0f} ms, long enough to suspect a "
                            f"misplaced boundary")

    # do the labelled silences actually contain silence?
    rms_all = np.sqrt(np.mean(x ** 2))
    for iv in phone:
        if iv.text.strip() != pc.SIL or iv.duration <= 0:
            continue
        seg = x[int(iv.xmin * fs):int(iv.xmax * fs)]
        if len(seg) and np.sqrt(np.mean(seg ** 2)) > 0.5 * rms_all:
            problems.append(f"the {iv.xmin:.2f}-{iv.xmax:.2f} s silence still has "
                            f"speech energy in it")

    speech = [iv for iv in phone if iv.text.strip() != pc.SIL]
    if speech:
        print(f"{os.path.basename(tg_path)}: {len(phone)} phone intervals, "
              f"speech {speech[0].xmin:.3f}-{speech[-1].xmax:.3f} s "
              f"({speech[-1].xmax - speech[0].xmin:.3f} s)")

    if problems:
        print(f"\n{len(problems)} thing(s) to look at:")
        for p in problems:
            print("  - " + p)
        return 1
    print("checks passed")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(check(sys.argv[1], sys.argv[2]))
