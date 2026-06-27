"""
matcher.py
==========
Identifies a query clip against the database using the classic
"offset histogram" voting scheme (Q3A: "look at the time offsets at which
its hashes match: a true match lines them all up at a single offset,
while a wrong song gives only scattered, random matches").

How it works
------------
For every hash in the query clip, we look up which (song_id, db_time)
pairs share that exact hash in the database. For each match we compute

    offset = db_time - query_time

If the query really is a snippet of that song (possibly starting partway
through), then for *every* correctly matched hash pair, db_time and
query_time differ by the SAME constant offset (the position in the song
where the clip starts). So correct matches pile up into one tall spike
in the offset histogram, while coincidental hash collisions with the
wrong song land at essentially random offsets and stay low and spread out.

We track per-song offset histograms in a single pass with a dict of
Counters, then take, for each song, the tallest bin as that song's score
(the "cluster score"), and rank songs by that score.
"""
from __future__ import annotations

import time
from collections import defaultdict, Counter

from . import config
from .pipeline import fingerprint_signal


class MatchResult:
    def __init__(self):
        self.fingerprint = None          # FingerprintResult for the query
        self.candidate_scores = []       # list of (song_id, score) sorted desc
        self.best_song_id = None
        self.best_score = 0
        self.best_offset = None
        self.runner_up_score = 0
        self.runner_up_ratio = float("inf")
        self.is_match = False
        self.n_hashes_matched_total = 0
        self.timings_ms = {}


def match_clip(y, sr, db, use_single_peaks: bool = False) -> MatchResult:
    """
    Fingerprint `y` and match it against `db` (a FingerprintDB).
    Returns a MatchResult with the full pipeline breakdown, ready for the
    Streamlit app to render step-by-step (mirrors the demo video's
    spectrogram -> constellation -> hashing -> DB lookup -> scoring chips).
    """
    result = MatchResult()

    fp = fingerprint_signal(y, sr, use_single_peaks=use_single_peaks)
    result.fingerprint = fp
    result.timings_ms.update(fp.timings_ms)

    query_hashes = fp.single_peak_hashes if use_single_peaks else fp.hashes
    lookup_index = db.single_index if use_single_peaks else db.index

    t0 = time.perf_counter()
    # song_id -> Counter(offset -> votes)
    offset_histograms: dict[str, Counter] = defaultdict(Counter)
    n_matched = 0
    for hash_key, q_time in query_hashes:
        postings = lookup_index.get(hash_key)
        if not postings:
            continue
        for song_id, db_time in postings:
            offset = db_time - q_time
            offset_histograms[song_id][offset] += 1
            n_matched += 1
    t1 = time.perf_counter()
    result.timings_ms["db_lookup"] = (t1 - t0) * 1000
    result.n_hashes_matched_total = n_matched

    t0 = time.perf_counter()
    scored = []
    best_offsets = {}
    for song_id, hist in offset_histograms.items():
        if not hist:
            continue
        best_offset, best_count = hist.most_common(1)[0]
        scored.append((song_id, best_count))
        best_offsets[song_id] = best_offset
    scored.sort(key=lambda x: x[1], reverse=True)
    t1 = time.perf_counter()
    result.timings_ms["scoring"] = (t1 - t0) * 1000

    result.candidate_scores = scored
    if scored:
        result.best_song_id, result.best_score = scored[0]
        result.best_offset = best_offsets[result.best_song_id]
        result.runner_up_score = scored[1][1] if len(scored) > 1 else 0
        result.runner_up_ratio = (
            result.best_score / result.runner_up_score
            if result.runner_up_score > 0
            else float("inf")
        )
        result.is_match = (
            result.best_score >= config.MIN_VOTES_FOR_MATCH
            and result.runner_up_ratio >= config.MIN_RUNNER_UP_RATIO
        )

    return result


def predicted_label(match_result: MatchResult, db) -> str:
    """Returns the matched song's filename WITHOUT extension (the label
    format required by results.csv), or 'none' if no candidate clears the
    confidence threshold."""
    if not match_result.is_match or match_result.best_song_id is None:
        return "none"
    return match_result.best_song_id
