
from __future__ import annotations

import numpy as np
import librosa


def add_white_noise(y: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Add white Gaussian noise at a target signal-to-noise ratio (in dB).
    Lower snr_db = noisier. snr_db of +100 is effectively clean.
    """
    sig_power = np.mean(y ** 2)
    if sig_power < 1e-12:
        return y
    noise_power = sig_power / (10 ** (snr_db / 10))
    noise = np.random.normal(0, np.sqrt(noise_power), size=y.shape).astype(y.dtype)
    return y + noise


def pitch_shift(y: np.ndarray, sr: int, n_steps: float) -> np.ndarray:
    """Shift pitch by n_steps semitones (can be fractional, e.g. 0.5)."""
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)


def time_stretch(y: np.ndarray, rate: float) -> np.ndarray:
    """Stretch/compress in time without changing pitch.
    rate > 1.0 speeds the clip up (shorter); rate < 1.0 slows it down."""
    return librosa.effects.time_stretch(y, rate=rate)


def run_noise_sweep(y, sr, db, match_fn, snr_levels_db=(40, 20, 10, 5, 0, -5)):
    """Run identification at a range of SNRs and report at what point it
    breaks. `match_fn(y, sr, db) -> MatchResult` should be matcher.match_clip
    partially applied, kept as a parameter to avoid circular imports."""
    rows = []
    for snr in snr_levels_db:
        y_noisy = add_white_noise(y, snr)
        res = match_fn(y_noisy, sr, db)
        rows.append({
            "snr_db": snr,
            "predicted": res.best_song_id,
            "score": res.best_score,
            "runner_up_ratio": res.runner_up_ratio,
            "is_match": res.is_match,
        })
    return rows


def run_pitch_sweep(y, sr, db, match_fn, semitone_shifts=(0, 0.25, 0.5, 1, 2, 4)):
    rows = []
    for st in semitone_shifts:
        y_shift = y if st == 0 else pitch_shift(y, sr, st)
        res = match_fn(y_shift, sr, db)
        rows.append({
            "semitones": st,
            "predicted": res.best_song_id,
            "score": res.best_score,
            "runner_up_ratio": res.runner_up_ratio,
            "is_match": res.is_match,
        })
    return rows


def run_stretch_sweep(y, sr, db, match_fn, rates=(1.0, 1.02, 1.05, 1.1, 1.2)):
    rows = []
    for r in rates:
        y_s = y if r == 1.0 else time_stretch(y, r)
        res = match_fn(y_s, sr, db)
        rows.append({
            "rate": r,
            "predicted": res.best_song_id,
            "score": res.best_score,
            "runner_up_ratio": res.runner_up_ratio,
            "is_match": res.is_match,
        })
    return rows
