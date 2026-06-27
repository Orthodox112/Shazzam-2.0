
from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

from . import config
from .audio_io import load_audio
from .pipeline import fingerprint_signal


def _key_to_str(key: tuple) -> str:
    return "_".join(str(x) for x in key)


def _str_to_key(s: str) -> tuple:
    parts = s.split("_")
    return tuple(int(p) for p in parts)


class FingerprintDB:
    """In-memory fingerprint database with JSON persistence.

    Two parallel inverted indices are kept:
      - `index`         : paired (f1, f2, dt) hashes -> [(song_id, time), ...]
      - `single_index`  : single-peak (f,) hashes    -> [(song_id, time), ...]

    The single-peak index exists ONLY to power the Q3A comparison
    experiment ("repeat the matching using single peaks on their own").
    It is intentionally far more collision-prone, which is the point.
    """

    def __init__(self):
        self.songs: dict[str, dict] = {}      # song_id -> metadata
        self.index: dict[tuple, list] = defaultdict(list)  # hash_key -> [(song_id, time), ...]
        self.single_index: dict[tuple, list] = defaultdict(list)  # single-peak hash_key -> [(song_id, time), ...]

    # ------------------------------------------------------------------ #
    # Building
    # ------------------------------------------------------------------ #
    def add_song(self, song_id: str, filename: str, y, sr) -> int:
        """Fingerprint one song's audio and add it to the index.
        Returns the number of (paired) hashes added."""
        result = fingerprint_signal(y, sr, use_single_peaks=True)
        for hash_key, anchor_time in result.hashes:
            self.index[hash_key].append((song_id, anchor_time))
        for hash_key, anchor_time in result.single_peak_hashes:
            self.single_index[hash_key].append((song_id, anchor_time))

        duration_s = float(result.time_axis[-1]) if len(result.time_axis) else 0.0
        self.songs[song_id] = {
            "filename": filename,
            "n_hashes": len(result.hashes),
            "n_peaks": len(result.peaks),
            "duration_s": duration_s,
        }
        return len(result.hashes)

    def build_from_folder(self, folder: str, progress_callback=None):
        """Index every supported audio file in `folder`. song_id is the
        filename without extension (matches the results.csv convention
        required by the project spec)."""
        folder = Path(folder)
        files = sorted(
            p for p in folder.iterdir()
            if p.suffix.lower() in config.SUPPORTED_EXTS
        )
        for i, path in enumerate(files):
            song_id = path.stem
            y, sr = load_audio(str(path))
            self.add_song(song_id, path.name, y, sr)
            if progress_callback:
                progress_callback(i + 1, len(files), path.name)
        return len(files)

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def save(self, path: str = config.DB_PATH_DEFAULT):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {
            "songs": self.songs,
            "index": {
                _key_to_str(k): v for k, v in self.index.items()
            },
            "single_index": {
                _key_to_str(k): v for k, v in self.single_index.items()
            },
        }
        with open(path, "w") as fh:
            json.dump(payload, fh)

    @classmethod
    def load(cls, path: str = config.DB_PATH_DEFAULT) -> "FingerprintDB":
        db = cls()
        if not os.path.exists(path):
            return db
        with open(path, "r") as fh:
            payload = json.load(fh)
        db.songs = payload.get("songs", {})
        raw_index = payload.get("index", {})
        db.index = defaultdict(list)
        for k_str, postings in raw_index.items():
            db.index[_str_to_key(k_str)] = [tuple(p) for p in postings]

        raw_single = payload.get("single_index", {})
        db.single_index = defaultdict(list)
        for k_str, postings in raw_single.items():
            db.single_index[_str_to_key(k_str)] = [tuple(p) for p in postings]
        return db

    def exists_on_disk(self, path: str = config.DB_PATH_DEFAULT) -> bool:
        return os.path.exists(path)

    # ------------------------------------------------------------------ #
    # Stats
    # ------------------------------------------------------------------ #
    def total_hashes(self) -> int:
        return sum(len(v) for v in self.index.values())

    def n_songs(self) -> int:
        return len(self.songs)
