"""
_mock_librosa_for_testing.py
=============================
DEV-ONLY helper. This sandbox has no network access to `pip install
librosa`, so this stub lets us exercise the pure NumPy/SciPy logic
(spectrogram, peaks, hashing, database, matcher) without the real
decoder. It is NOT part of the shipped app -- the deployed app's
requirements.txt installs the real librosa, which is what actually
decodes MP3/WAV/etc. Do not import this from app code.
"""
import sys
import types
import numpy as np


def install():
    if "librosa" in sys.modules and getattr(sys.modules["librosa"], "_is_real", True) is True \
            and hasattr(sys.modules["librosa"], "__file__"):
        # real librosa already imported elsewhere; don't clobber it
        return

    librosa_mock = types.ModuleType("librosa")

    def load(path_or_buf, sr=22050, mono=True):
        # Only used in tests that pass raw arrays around directly;
        # real file loading is exercised on the deployed app, not here.
        raise NotImplementedError("audio_io.load_audio file decoding is not exercised in this sandbox")

    def pitch_shift(y, sr, n_steps):
        return y  # identity stub; robustness logic itself isn't under test here

    def time_stretch(y, rate):
        if rate == 1.0:
            return y
        n = int(len(y) / rate)
        idx = np.linspace(0, len(y) - 1, n)
        return np.interp(idx, np.arange(len(y)), y).astype(y.dtype)

    effects_mock = types.ModuleType("librosa.effects")
    effects_mock.pitch_shift = pitch_shift
    effects_mock.time_stretch = time_stretch

    librosa_mock.load = load
    librosa_mock.effects = effects_mock

    sys.modules["librosa"] = librosa_mock
    sys.modules["librosa.effects"] = effects_mock
