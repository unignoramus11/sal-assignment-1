"""Q6: recover the switching time tau from the STFT of s(t).

s(t) = sin(2*pi*f1*t) for 0 <= t <= tau
       sin(2*pi*f2*t) for tau < t <= 2
       0 otherwise
with tau = 1 s, f1 = 100 Hz, f2 = 300 Hz.

The point is to find tau from the spectrum alone, without looking at the
definition, so both estimators below only see the STFT magnitudes.
"""

import csv
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 8000
F1, F2 = 100.0, 300.0
TRUE_TAU = 1.0
DURATION = 2.0
WIN_MS = 20.0
HOP_MS = 1.0

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLOTS = os.path.join(ROOT, "plots")
RESULTS = os.path.join(ROOT, "results")


def make_signal(fs=FS, tau=TRUE_TAU, dur=DURATION):
    t = np.arange(0, dur, 1.0 / fs)
    s = np.where(t <= tau, np.sin(2 * np.pi * F1 * t), np.sin(2 * np.pi * F2 * t))
    return t, s


def stft(x, fs, win_ms, hop_ms, nfft=None):
    """Magnitude STFT. Returns (freqs, times, magnitude[freq, frame])."""
    win_len = int(round(win_ms * fs / 1000.0))
    hop = int(round(hop_ms * fs / 1000.0))
    if nfft is None:
        nfft = win_len
    window = np.hamming(win_len)
    n_frames = 1 + (len(x) - win_len) // hop
    mag = np.empty((nfft // 2 + 1, n_frames))
    for i in range(n_frames):
        seg = x[i * hop: i * hop + win_len] * window
        mag[:, i] = np.abs(np.fft.rfft(seg, n=nfft))
    freqs = np.fft.rfftfreq(nfft, 1.0 / fs)
    # timestamp each frame at its centre
    times = (np.arange(n_frames) * hop + win_len / 2.0) / fs
    return freqs, times, mag


def tau_from_peak_track(freqs, times, mag):
    """Where the peak-magnitude bin crosses the midpoint between f1 and f2."""
    peak = freqs[np.argmax(mag, axis=0)]
    midpoint = 0.5 * (F1 + F2)
    above = peak > midpoint
    idx = np.argmax(above)  # first frame at the higher tone
    if not above[idx]:
        return None, peak
    return times[idx], peak


def band_energy(freqs, mag, centre, halfwidth=50.0):
    sel = np.abs(freqs - centre) <= halfwidth
    return mag[sel, :].sum(axis=0)


def tau_from_band_crossover(freqs, times, mag):
    """Where energy near f2 overtakes energy near f1."""
    e1 = band_energy(freqs, mag, F1)
    e2 = band_energy(freqs, mag, F2)
    crossed = e2 > e1
    idx = np.argmax(crossed)
    if not crossed[idx]:
        return None, e1, e2
    # linear interpolation between the two straddling frames
    if idx == 0:
        return times[0], e1, e2
    d_prev = e2[idx - 1] - e1[idx - 1]
    d_now = e2[idx] - e1[idx]
    frac = -d_prev / (d_now - d_prev)
    t_cross = times[idx - 1] + frac * (times[idx] - times[idx - 1])
    return t_cross, e1, e2


def main():
    os.makedirs(PLOTS, exist_ok=True)
    os.makedirs(RESULTS, exist_ok=True)

    t, s = make_signal()
    freqs, times, mag = stft(s, FS, WIN_MS, HOP_MS)

    tau_peak, peak_track = tau_from_peak_track(freqs, times, mag)
    tau_band, e1, e2 = tau_from_band_crossover(freqs, times, mag)

    win_len = int(round(WIN_MS * FS / 1000.0))
    bin_width = FS / win_len

    print(f"window {WIN_MS} ms = {win_len} samples, hop {HOP_MS} ms")
    print(f"FFT bin spacing {bin_width:.1f} Hz")
    print(f"cycles of f1 inside the window: {F1 * WIN_MS / 1000.0:.1f}")
    print(f"tau from peak-frequency track : {tau_peak:.4f} s "
          f"(error {1000 * (tau_peak - TRUE_TAU):+.1f} ms)")
    print(f"tau from band-energy crossover: {tau_band:.4f} s "
          f"(error {1000 * (tau_band - TRUE_TAU):+.1f} ms)")

    with open(os.path.join(RESULTS, "q6_tau.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "value", "unit"])
        w.writerow(["sampling_rate", FS, "Hz"])
        w.writerow(["window_length", WIN_MS, "ms"])
        w.writerow(["window_length_samples", win_len, "samples"])
        w.writerow(["hop", HOP_MS, "ms"])
        w.writerow(["fft_bin_spacing", round(bin_width, 2), "Hz"])
        w.writerow(["true_tau", TRUE_TAU, "s"])
        w.writerow(["tau_peak_track", round(tau_peak, 4), "s"])
        w.writerow(["tau_band_crossover", round(tau_band, 4), "s"])
        w.writerow(["error_peak_track", round(1000 * (tau_peak - TRUE_TAU), 2), "ms"])
        w.writerow(["error_band_crossover", round(1000 * (tau_band - TRUE_TAU), 2), "ms"])

    # figure 1: signal, spectrogram, peak track, band energies
    fig, ax = plt.subplots(4, 1, figsize=(9, 10), sharex=True)

    ax[0].plot(t, s, lw=0.4, color="black")
    ax[0].set_ylabel("amplitude")
    ax[0].set_title(f"s(t), {F1:.0f} Hz then {F2:.0f} Hz, true $\\tau$ = {TRUE_TAU} s")
    ax[0].set_xlim(0, DURATION)

    show = freqs <= 600
    ax[1].imshow(20 * np.log10(mag[show, :] + 1e-12), origin="lower", aspect="auto",
                 extent=[times[0], times[-1], 0, freqs[show][-1]], cmap="magma")
    ax[1].set_ylabel("frequency (Hz)")
    ax[1].set_title(f"STFT magnitude (dB), {WIN_MS:.0f} ms window, {HOP_MS:.0f} ms hop")

    ax[2].plot(times, peak_track, lw=1.0, color="tab:blue")
    ax[2].axhline(0.5 * (F1 + F2), ls=":", color="grey", lw=0.8)
    ax[2].axvline(tau_peak, ls="--", color="tab:red", lw=1.0)
    ax[2].set_ylabel("peak bin (Hz)")
    ax[2].set_title(f"peak-magnitude frequency, crossing at {tau_peak:.3f} s")

    ax[3].plot(times, e1, label=f"energy near {F1:.0f} Hz", lw=1.0)
    ax[3].plot(times, e2, label=f"energy near {F2:.0f} Hz", lw=1.0)
    ax[3].axvline(tau_band, ls="--", color="tab:red", lw=1.0)
    ax[3].set_ylabel("band magnitude")
    ax[3].set_xlabel("time (s)")
    ax[3].set_title(f"band-energy crossover at {tau_band:.3f} s")
    ax[3].legend(loc="center right", fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "q6_tau_estimation.png"), dpi=160)
    plt.close(fig)

    # figure 2: what the window length costs you
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.6))
    for a, wms in zip(ax, [5.0, 20.0, 100.0]):
        f2_, t2_, m2_ = stft(s, FS, wms, HOP_MS, nfft=2048)
        sel = f2_ <= 600
        a.imshow(20 * np.log10(m2_[sel, :] + 1e-12), origin="lower", aspect="auto",
                 extent=[t2_[0], t2_[-1], 0, f2_[sel][-1]], cmap="magma")
        wl = int(round(wms * FS / 1000.0))
        a.set_title(f"{wms:.0f} ms window\n{FS / wl:.0f} Hz resolution", fontsize=9)
        a.set_xlabel("time (s)")
    ax[0].set_ylabel("frequency (Hz)")
    fig.suptitle("Time and frequency resolution trade-off (same signal, three window lengths)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "q6_window_tradeoff.png"), dpi=160)
    plt.close(fig)

    # figure 3: zoom on the transition, where the window length is visible
    fig, ax = plt.subplots(figsize=(7, 3.6))
    zoom = (times >= TRUE_TAU - 0.05) & (times <= TRUE_TAU + 0.05)
    ax.plot(times[zoom], e1[zoom], label=f"energy near {F1:.0f} Hz", lw=1.4)
    ax.plot(times[zoom], e2[zoom], label=f"energy near {F2:.0f} Hz", lw=1.4)
    ax.axvline(TRUE_TAU, ls="-", color="grey", lw=0.8, label="true $\\tau$")
    ax.axvline(tau_band, ls="--", color="tab:red", lw=1.0, label="estimate")
    ax.axvspan(TRUE_TAU - WIN_MS / 2000.0, TRUE_TAU + WIN_MS / 2000.0,
               color="grey", alpha=0.15, label=f"{WIN_MS:.0f} ms window span")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("band magnitude")
    ax.set_title("Transition region: the swap takes one window length to complete")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "q6_transition_zoom.png"), dpi=160)
    plt.close(fig)

    # how long the crossover actually takes, as a check on the resolution claim
    both = np.where((e1 > 0.1 * e1.max()) & (e2 > 0.1 * e2.max()))[0]
    if len(both):
        print(f"frames where both tones are present: "
              f"{1000 * (times[both[-1]] - times[both[0]]):.1f} ms wide")

    print("wrote plots/q6_tau_estimation.png, plots/q6_window_tradeoff.png, "
          "plots/q6_transition_zoom.png, results/q6_tau.csv")


if __name__ == "__main__":
    main()
