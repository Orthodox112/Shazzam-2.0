"""
audio_io.py
===========
Loading and basic preprocessing of audio files.

We rely on `librosa.load`, which internally uses `soundfile`/`audioread`
to decode WAV/MP3/FLAC/OGG/M4A and returns a float32 mono (or stereo)
NumPy array. librosa also handles resampling with a proper anti-aliasing
low-pass filter before decimating, so downsampling to SAMPLE_RATE here is
safe and consistent with the Nyquist discussion in Q2(f).
"""
from __future__ import annotations

import io
import numpy as np
import librosa

from . import config


def load_audio(path_or_buffer, sr: int = config.SAMPLE_RATE) -> tuple[np.ndarray, int]:
    """
    Load an audio file (path string, Path, or file-like/bytes buffer) and
    return (signal, sample_rate) as a mono float32 NumPy array.

    Parameters
    ----------
    path_or_buffer : str | Path | bytes | file-like
        Anything librosa.load can consume. Streamlit's `UploadedFile` is
        file-like and works directly; raw `bytes` are wrapped in BytesIO.
    sr : int
        Target sample rate (we resample everything to a common rate so
        database and query fingerprints are directly comparable).
    """
    if isinstance(path_or_buffer, bytes):
        path_or_buffer = io.BytesIO(path_or_buffer)

    y, sr_out = librosa.load(path_or_buffer, sr=sr, mono=config.MONO)
    y = y.astype(np.float32)
    return y, sr_out


def trim_or_pad(y: np.ndarray, sr: int, max_seconds: float | None = None) -> np.ndarray:
    """Optionally cap a signal's length (used to keep query clips short)."""
    if max_seconds is None:
        return y
    max_samples = int(max_seconds * sr)
    return y[:max_samples]


def normalize_peak(y: np.ndarray) -> np.ndarray:
    """Scale signal so its peak absolute amplitude is 1.0 (avoids loudness
    differences between recordings affecting peak-picking thresholds)."""
    peak = np.max(np.abs(y))
    if peak < 1e-9:
        return y
    return y / peak
