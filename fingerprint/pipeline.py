
from __future__ import annotations

import time
import numpy as np

from . import config
from .spectrogram import compute_spectrogram, restrict_band
from .peaks import extract_peaks, peaks_to_hz_sec
from .hashing import generate_hashes, generate_single_peak_hashes


class FingerprintResult:
    """Container for every intermediate artifact, so the Streamlit app can
    display each pipeline stage (spectrogram, constellation, hashes,
    timings) exactly like the demo video's step-by-step breakdown."""

    def __init__(self):
        self.freq_axis = None
        self.time_axis = None
        self.S_db = None
        self.peaks = None            # list of (t_bin, f_bin, amp_db)
        self.peaks_hz_sec = None     # list of (t_sec, f_hz, amp_db)
        self.hashes = None           # list of (hash_key, anchor_time_bin)
        self.single_peak_hashes = None
        self.timings_ms = {}         # stage_name -> milliseconds
        self.shape = None            # (n_freq_bins, n_time_bins)


def fingerprint_signal(y: np.ndarray, sr: int, use_single_peaks: bool = False) -> FingerprintResult:
    """Run the full pipeline on an already-loaded mono signal."""
    result = FingerprintResult()

    t0 = time.perf_counter()
    f, t, S_db = compute_spectrogram(y, sr)
    f, S_db = restrict_band(f, S_db)
    t1 = time.perf_counter()
    result.timings_ms["spectrogram"] = (t1 - t0) * 1000
    result.freq_axis, result.time_axis, result.S_db = f, t, S_db
    result.shape = S_db.shape

    t0 = time.perf_counter()
    peaks = extract_peaks(S_db, f, t)
    t1 = time.perf_counter()
    result.timings_ms["constellation"] = (t1 - t0) * 1000
    result.peaks = peaks
    result.peaks_hz_sec = peaks_to_hz_sec(peaks, f, t)

    t0 = time.perf_counter()
    result.hashes = generate_hashes(peaks)
    if use_single_peaks:
        result.single_peak_hashes = generate_single_peak_hashes(peaks)
    t1 = time.perf_counter()
    result.timings_ms["hashing"] = (t1 - t0) * 1000

    return result
