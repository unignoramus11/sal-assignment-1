"""Fit the known phone sequence to the acoustics to produce a first-pass segmentation.

This is a starting point for hand correction in Praat, not a finished segmentation.
The phone order is fixed and known, so the only thing to decide is where the
boundaries go. Frame-level features are scored against a template for each manner
class, a duration prior is applied per class, and dynamic programming picks the
boundary set with the lowest total cost.

Features are taken from the high-pass filtered audio, which is sample-aligned with
the raw recording, so the boundaries apply to both.

usage: python q1a_prealign.py <wav> <out.TextGrid> [--whisper]
"""

import os
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phone_classes as pc
from textgrid_io import TextGrid, Tier, Interval, write_textgrid

WIN_MS = 25.0
HOP_MS = 5.0

# target feature values per manner class, and how much each feature matters.
# features: energy(0-1), zcr(0-1), voicing(0-1), high-frequency fraction(0-1)
TEMPLATES = {
    "sil":     dict(energy=0.10, zcr=0.05, voicing=0.5, hifrac=0.02),
    "vowel":   dict(energy=0.88, zcr=0.05, voicing=1.0, hifrac=0.01),
    "nasal":   dict(energy=0.60, zcr=0.04, voicing=1.0, hifrac=0.00),
    "vstop":   dict(energy=0.25, zcr=0.10, voicing=0.5, hifrac=0.10),
    "ustop":   dict(energy=0.15, zcr=0.06, voicing=0.5, hifrac=0.03),
    "sfric":   dict(energy=0.60, zcr=0.40, voicing=0.4, hifrac=0.80),
    "wfric":   dict(energy=0.25, zcr=0.12, voicing=0.5, hifrac=0.12),
    "vfric":   dict(energy=0.38, zcr=0.12, voicing=0.4, hifrac=0.70),
}
WEIGHTS = dict(energy=3.0, zcr=1.6, voicing=2.2, hifrac=1.4)

# Whispering removes the glottal source, so vowels lose their energy advantage and
# fricatives become comparably loud. Energy is therefore a poor cue here and the
# high-frequency fraction does most of the work.
TEMPLATES_WHISPER = {
    "sil":     dict(energy=0.12, zcr=0.04, hifrac=0.01),
    "vowel":   dict(energy=0.70, zcr=0.14, hifrac=0.03),
    "nasal":   dict(energy=0.40, zcr=0.10, hifrac=0.01),
    "vstop":   dict(energy=0.25, zcr=0.07, hifrac=0.03),
    "ustop":   dict(energy=0.20, zcr=0.08, hifrac=0.05),
    "sfric":   dict(energy=0.75, zcr=0.40, hifrac=0.85),
    "wfric":   dict(energy=0.40, zcr=0.15, hifrac=0.28),
    "vfric":   dict(energy=0.45, zcr=0.15, hifrac=0.12),
}
WEIGHTS_WHISPER = dict(energy=1.2, zcr=2.0, hifrac=4.5)

# duration prior per class, milliseconds (mean, sd)
DURATION = {
    "sil": (200.0, 200.0), "vowel": (150.0, 80.0), "nasal": (90.0, 45.0),
    "vstop": (80.0, 45.0), "ustop": (110.0, 60.0), "sfric": (140.0, 60.0),
    "wfric": (70.0, 40.0), "vfric": (55.0, 30.0),
}

PHONE_CLASS = {
    "b": "vstop", "ɡ": "vstop",
    "p": "ustop", "t": "ustop", "k": "ustop",
    "s": "sfric", "ʃ": "sfric",
    "θ": "wfric",
    "ð": "vfric",
    "n": "nasal",
}


def phone_to_class(p):
    if p == pc.SIL:
        return "sil"
    if pc.is_vowel(p):
        return "vowel"
    return PHONE_CLASS[p]


def state_sequence():
    """Phone states in order, with an optional pause after each word.

    The recording has clear pauses between some words. Without somewhere to put
    them they get absorbed into the neighbouring stop closure, which would drag
    that phone's mean energy down in Q1c.
    """
    states, optional, phone_of = [], [], []
    states.append(pc.SIL); optional.append(False); phone_of.append(pc.SIL)
    for wi, wphones in enumerate(pc.WORD_PHONES):
        for ph in wphones:
            states.append(ph); optional.append(False); phone_of.append(ph)
        if wi < len(pc.WORD_PHONES) - 1:
            states.append(pc.SIL); optional.append(True); phone_of.append(pc.SIL)
    states.append(pc.SIL); optional.append(False); phone_of.append(pc.SIL)
    return states, optional


def features(x, fs, whisper=False):
    win = int(WIN_MS * fs / 1000.0)
    hop = int(HOP_MS * fs / 1000.0)
    n = 1 + (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    fr = x[idx]
    w = np.hamming(win)

    energy = np.log10(np.sum((fr * w) ** 2, axis=1) + 1e-12)
    lo, hi = np.percentile(energy, 2), np.percentile(energy, 98)
    energy = np.clip((energy - lo) / max(hi - lo, 1e-9), 0, 1)

    sg = np.sign(fr)
    sg[sg == 0] = 1
    zcr = np.mean(np.abs(np.diff(sg, axis=1)) / 2.0, axis=1)
    zcr = np.clip(zcr / 0.5, 0, 1)

    mag = np.abs(np.fft.rfft(fr * w, axis=1))
    freqs = np.fft.rfftfreq(win, 1.0 / fs)
    power = mag ** 2
    total = power.sum(axis=1) + 1e-20
    hifrac = power[:, freqs >= 2500].sum(axis=1) / total

    # voicing from the normalised autocorrelation peak in the plausible F0 range
    if whisper:
        voicing = np.zeros(n)
    else:
        voicing = np.empty(n)
        lag_lo, lag_hi = int(fs / 300.0), int(fs / 70.0)
        for i in range(n):
            seg = fr[i] - fr[i].mean()
            denom = np.sum(seg ** 2) + 1e-20
            ac = np.correlate(seg, seg, mode="full")[win - 1:]
            band = ac[lag_lo:min(lag_hi, len(ac))]
            voicing[i] = np.clip(band.max() / denom, 0, 1) if len(band) else 0.0
        voicing = np.clip(voicing / 0.45, 0, 1)

    times = (np.arange(n) * hop + win / 2.0) / fs
    return dict(energy=energy, zcr=zcr, voicing=voicing, hifrac=hifrac,
                times=times, n=n, hop=hop, win=win)


def frame_costs(feat, classes, whisper=False):
    """cost[k, i] = how badly frame i fits the class of phone k."""
    n = feat["n"]
    templates = TEMPLATES_WHISPER if whisper else TEMPLATES
    weights = WEIGHTS_WHISPER if whisper else WEIGHTS
    cost = np.empty((len(classes), n))
    for k, cls in enumerate(classes):
        c = np.zeros(n)
        for name, target in templates[cls].items():
            c += weights[name] * (feat[name] - target) ** 2
        cost[k] = c
    return cost


def speech_span(x, fs, frame_ms=20.0, thresh_frac=0.06):
    """Rough speech start and end from a 300-4000 Hz band."""
    from scipy.signal import butter, filtfilt
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


def align(feat, phones, whisper=False, optional=None, span=None):
    if optional is None:
        optional = [False] * len(phones)
    classes = [phone_to_class(p) for p in phones]
    fc = frame_costs(feat, classes, whisper)
    cum = np.concatenate([np.zeros((len(classes), 1)), np.cumsum(fc, axis=1)], axis=1)

    n = feat["n"]
    P = len(classes)
    hop_ms = HOP_MS
    # per-class floors; a vowel is never 15 ms, a stop closure can be brief
    MIN_MS = {"vowel": 45.0, "nasal": 35.0, "sfric": 40.0, "wfric": 25.0,
              "vfric": 25.0, "vstop": 20.0, "ustop": 20.0, "sil": 5.0}
    max_fr = int(round(700.0 / hop_ms))

    INF = 1e18
    dp = np.full((P + 1, n + 1), INF)
    back = np.zeros((P + 1, n + 1), dtype=int)
    dp[0, 0] = 0.0

    for k in range(1, P + 1):
        cls = classes[k - 1]
        mu, sd = DURATION[cls]
        lo_fr = 1 if cls == "sil" else max(1, int(round(MIN_MS[cls] / hop_ms)))
        hi_fr = n if cls == "sil" else max_fr
        if optional[k - 1]:
            lo_fr = 0          # a pause may be absent entirely
        # keep the leading and trailing silence consistent with the detected span
        lo_end, hi_end = 0, n
        if span is not None:
            t0, t1 = span
            if k == 1:
                lo_end = max(0, int((t0 - 0.10) / (hop_ms / 1000.0)))
                hi_end = min(n, int((t0 + 0.12) / (hop_ms / 1000.0)))
            elif k == P:
                lo_end = hi_end = n
            elif k == P - 1:
                lo_end = max(0, int((t1 - 0.12) / (hop_ms / 1000.0)))
                hi_end = min(n, int((t1 + 0.10) / (hop_ms / 1000.0)))
        for end in range(0, n + 1):
            if end < lo_end or end > hi_end:
                continue
            best, arg = INF, -1
            d_min = lo_fr
            d_max = min(hi_fr, end)
            for d in range(d_min, d_max + 1):
                start = end - d
                prev = dp[k - 1, start]
                if prev >= INF:
                    continue
                seg = cum[k - 1, end] - cum[k - 1, start]
                dur_ms = d * hop_ms
                if d == 0:
                    dcost = 0.0        # no penalty for omitting an optional pause
                else:
                    dcost = ((dur_ms - mu) / sd) ** 2
                tot = prev + seg + 1.2 * dcost
                if tot < best:
                    best, arg = tot, start
            dp[k, end] = best
            back[k, end] = arg

    bounds = [n]
    cur = n
    for k in range(P, 0, -1):
        cur = back[k, cur]
        bounds.append(cur)
    bounds.reverse()
    return bounds, dp[P, n]


def build(wav_path, out_path, whisper=False):
    d, base = os.path.split(os.path.abspath(wav_path))
    hp = os.path.join(os.path.dirname(d), "recordings_hp", base)
    src = hp if os.path.exists(hp) else wav_path
    x, fs = sf.read(src)
    if x.ndim > 1:
        x = x.mean(axis=1)

    total = len(x) / fs
    states, optional = state_sequence()
    feat = features(x, fs, whisper)
    span = speech_span(x, fs)
    bounds, cost = align(feat, states, whisper, optional, span)

    hop, win = feat["hop"], feat["win"]

    def frame_to_time(f):
        if f <= 0:
            return 0.0
        if f >= feat["n"]:
            return total
        return (f * hop + win / 2.0) / fs

    times = [0.0] + [frame_to_time(b) for b in bounds[1:-1]] + [total]

    # drop optional pauses the aligner chose not to use
    kept = [(states[i], times[i], times[i + 1])
            for i in range(len(states))
            if not (optional[i] and times[i + 1] - times[i] < 1e-6)]

    grid = TextGrid(0.0, total)
    phone_tier = Tier("phone", 0.0, total)
    for lab, a, b in kept:
        phone_tier.intervals.append(Interval(a, b, lab))
    grid.tiers.append(phone_tier)

    # word tier: spans from the first to the last phone of each word
    word_tier = Tier("word", 0.0, total)
    idx, edges = 1, []
    for wphones in pc.WORD_PHONES:
        start = times[idx]
        idx += len(wphones)
        end = times[idx]
        edges.append((start, end))
        if idx < len(states) and optional[idx]:
            idx += 1
    word_tier.intervals.append(Interval(0.0, edges[0][0], pc.SIL))
    for i, (w, (a, b)) in enumerate(zip(pc.WORDS, edges)):
        word_tier.intervals.append(Interval(a, b, w))
        nxt = edges[i + 1][0] if i + 1 < len(edges) else total
        if nxt - b > 1e-6:
            word_tier.intervals.append(Interval(b, nxt, pc.SIL))
    grid.tiers.append(word_tier)

    write_textgrid(grid, out_path)

    speech = [iv for iv in phone_tier if iv.text != pc.SIL]
    npause = sum(1 for iv in phone_tier if iv.text == pc.SIL) - 2
    print(f"{os.path.basename(wav_path)}  (features from {os.path.basename(os.path.dirname(src))}/)")
    print(f"  speech {speech[0].xmin:.3f}-{speech[-1].xmax:.3f} s, "
          f"{npause} inter-word pause(s), cost {cost:.1f}")
    for iv in phone_tier:
        tag = "  (pause)" if iv.text == pc.SIL else ""
        print(f"  {iv.text:<4} {iv.xmin:>7.3f} {iv.xmax:>7.3f} {1000 * iv.duration:>7.1f} ms{tag}")
    print(f"  wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2], whisper="--whisper" in sys.argv)
