from __future__ import annotations

import numpy as np
from scipy.signal import stft

from . import config


def compute_spectrogram(
    y: np.ndarray,
    sr: int,
    n_fft: int = config.N_FFT,
    hop_length: int = config.HOP_LENGTH,
    window: str = config.WINDOW,
):
    """
    Compute the magnitude spectrogram of a signal.

    Returns
    -------
    f : ndarray, shape (n_freq_bins,)      frequency axis in Hz
    t : ndarray, shape (n_time_frames,)    time axis in seconds
    S_db : ndarray, shape (n_freq_bins, n_time_frames)
        Magnitude spectrogram in dB, normalized so the loudest bin in the
        whole clip is 0 dB (this makes MIN_PEAK_AMP_DB comparable across
        clips of different loudness).
    """
    noverlap = n_fft - hop_length
    f, t, Zxx = stft(
        y, fs=sr, window=window, nperseg=n_fft, noverlap=noverlap, boundary=None
    )
    mag = np.abs(Zxx)
    mag = np.maximum(mag, 1e-10)
    S_db = 20 * np.log10(mag)
    S_db -= S_db.max()  # normalize: loudest point in clip = 0 dB
    return f, t, S_db


def restrict_band(f, S_db, min_hz=config.MIN_FREQ_HZ, max_hz=config.MAX_FREQ_HZ):
    """Crop the spectrogram to the frequency band that matters for ID
    (discards sub-bass rumble and very-high-frequency noise)."""
    mask = (f >= min_hz) & (f <= max_hz)
    return f[mask], S_db[mask, :]
