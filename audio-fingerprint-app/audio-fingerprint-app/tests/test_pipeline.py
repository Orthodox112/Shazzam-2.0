"""
tests/test_pipeline.py
=======================
Lightweight sanity tests for the fingerprinting pipeline, using synthetic
tone-sequence "songs" so they run instantly with no audio files needed.

Run with:
    pytest tests/ -v
or, without pytest installed:
    python tests/test_pipeline.py
"""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import librosa  # noqa: F401  (use the real package if it's installed)
except ImportError:
    from _mock_librosa_for_testing import install as _install_librosa_mock
    _install_librosa_mock()

from fingerprint.database import FingerprintDB
from fingerprint.matcher import match_clip, predicted_label
from fingerprint.robustness import add_white_noise

SR = 22050


def make_synthetic_song(seed: int, duration_s: float = 20.0) -> np.ndarray:
    """A reproducible, song-like signal: a sequence of random tones plus
    a soft harmonic and a little noise, distinct per seed."""
    rng = np.random.RandomState(seed)
    n_samples = int(duration_s * SR)
    t = np.linspace(0, duration_s, n_samples, endpoint=False)
    y = np.zeros_like(t)

    n_notes = int(duration_s * 4)
    note_dur = duration_s / n_notes
    freqs = rng.uniform(200, 2000, n_notes)
    for i, f in enumerate(freqs):
        start = int(i * note_dur * SR)
        end = int((i + 1) * note_dur * SR)
        seg = t[start:end]
        y[start:end] += np.sin(2 * np.pi * f * seg) + 0.3 * np.sin(2 * np.pi * 2 * f * seg)

    y += rng.normal(0, 0.01, size=y.shape)
    return y.astype(np.float32)


def build_test_db(n_songs=5):
    db = FingerprintDB()
    songs = {}
    for i in range(n_songs):
        y = make_synthetic_song(i)
        songs[f"song{i}"] = y
        db.add_song(f"song{i}", f"song{i}.wav", y, SR)
    return db, songs


def test_correct_song_identified():
    db, songs = build_test_db()
    query = songs["song2"][int(8 * SR): int(13 * SR)]
    result = match_clip(query, SR, db)
    assert result.best_song_id == "song2"
    assert result.is_match is True
    assert predicted_label(result, db) == "song2"
    print("test_correct_song_identified: PASS")


def test_pure_noise_rejected():
    db, _ = build_test_db()
    noise = np.random.normal(0, 0.05, size=int(5 * SR)).astype(np.float32)
    result = match_clip(noise, SR, db)
    assert result.is_match is False
    assert predicted_label(result, db) == "none"
    print("test_pure_noise_rejected: PASS")


def test_database_save_and_load(tmp_path_factory=None):
    import tempfile
    db, songs = build_test_db()
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "fp.json")
        db.save(path)
        db2 = FingerprintDB.load(path)
        assert db2.n_songs() == db.n_songs()
        assert db2.total_hashes() == db.total_hashes()

        query = songs["song4"][int(2 * SR): int(7 * SR)]
        result = match_clip(query, SR, db2)
        assert result.best_song_id == "song4"
    print("test_database_save_and_load: PASS")


def test_noise_degrades_score_monotonically_ish():
    db, songs = build_test_db()
    query = songs["song1"][int(5 * SR): int(10 * SR)]
    clean_result = match_clip(query, SR, db)
    noisy_result = match_clip(add_white_noise(query, snr_db=0), SR, db)
    # Heavier noise should never produce a *higher* score than the clean clip.
    assert noisy_result.best_score <= clean_result.best_score
    print("test_noise_degrades_score_monotonically_ish: PASS")


def test_single_peak_hashes_more_collision_prone():
    db, songs = build_test_db()
    query = songs["song3"][int(3 * SR): int(8 * SR)]
    paired_result = match_clip(query, SR, db, use_single_peaks=False)
    single_result = match_clip(query, SR, db, use_single_peaks=True)

    # Regression guard: single-peak querying must find candidates at all
    # (this previously failed silently because the DB only indexed paired
    # hashes -- see database.py's `single_index`).
    assert single_result.best_song_id is not None, (
        "single-peak query found zero candidates; is db.single_index populated?"
    )
    assert single_result.best_song_id == "song3"
    assert paired_result.best_song_id == "song3"

    # Paired-hash runner-up ratio should be at least as decisive as single-peak.
    if single_result.runner_up_ratio != float("inf") and paired_result.runner_up_ratio != float("inf"):
        assert paired_result.runner_up_ratio >= single_result.runner_up_ratio * 0.5
    print("test_single_peak_hashes_more_collision_prone: PASS "
          f"(paired_ratio={paired_result.runner_up_ratio}, single_ratio={single_result.runner_up_ratio})")


if __name__ == "__main__":
    test_correct_song_identified()
    test_pure_noise_rejected()
    test_database_save_and_load()
    test_noise_degrades_score_monotonically_ish()
    test_single_peak_hashes_more_collision_prone()
    print("\nAll tests passed.")
