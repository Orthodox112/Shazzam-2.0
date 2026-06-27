"""
peaks.py
========
Extracts the "constellation map": a sparse set of (time_bin, freq_bin)
local maxima from a spectrogram. These are the standout time-frequency
points described in Q3A -- the ones that survive EQ, volume changes, and
mild noise because they're defined by *relative* prominence, not absolute
level.

Algorithm
---------
1. Slide a 2-D maximum filter over the dB spectrogram. A point survives if
   it equals the max of its own neighborhood (i.e. it IS the loudest point
   nearby) and it's louder than a noise floor.
2. To avoid one loud passage hogging the whole fingerprint, we cap the
   number of peaks kept per second of audio, keeping the loudest ones.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter

from . import config


def extract_peaks(
    S_db: np.ndarray,
    freq_axis: np.ndarray,
    time_axis: np.ndarray,
    neighborhood_freq: int = config.PEAK_NEIGHBORHOOD_FREQ_BINS,
    neighborhood_time: int = config.PEAK_NEIGHBORHOOD_TIME_BINS,
    min_amp_db: float = config.MIN_PEAK_AMP_DB,
    max_peaks_per_second: int = config.MAX_PEAKS_PER_SECOND,
):
    """
    Returns
    -------
    peaks : list[tuple[int, int, float]]
        Each tuple is (time_bin_index, freq_bin_index, amplitude_db),
        sorted by time then frequency.
    """
    size = (2 * neighborhood_freq + 1, 2 * neighborhood_time + 1)
    local_max = maximum_filter(S_db, size=size, mode="constant", cval=-np.inf)
    is_peak = (S_db == local_max) & (S_db > min_amp_db)

    freq_idx, time_idx = np.where(is_peak[:, :])  # rows=freq, cols=time
    amps = S_db[freq_idx, time_idx]

    candidates = list(zip(time_idx.tolist(), freq_idx.tolist(), amps.tolist()))

    # Density cap: keep only the loudest N peaks per second of audio.
    duration_s = time_axis[-1] if len(time_axis) else 1.0
    budget = max(1, int(max_peaks_per_second * max(duration_s, 1.0)))
    if len(candidates) > budget:
        candidates.sort(key=lambda c: c[2], reverse=True)
        candidates = candidates[:budget]

    candidates.sort(key=lambda c: (c[0], c[1]))
    return candidates


def peaks_to_hz_sec(peaks, freq_axis, time_axis):
    """Convert (time_bin, freq_bin, amp) peaks to (time_sec, freq_hz, amp)
    for plotting on a constellation scatter plot."""
    out = []
    for t_idx, f_idx, amp in peaks:
        out.append((time_axis[t_idx], freq_axis[f_idx], amp))
    return out
