from __future__ import annotations

from collections import defaultdict

from . import config


def generate_hashes(
    peaks,
    fan_out: int = config.FAN_OUT,
    min_dt: int = config.MIN_TIME_DELTA,
    max_dt: int = config.MAX_TIME_DELTA,
):
    """
    Parameters
    ----------
    peaks : list[tuple[int, int, float]]
        (time_bin, freq_bin, amp_db), already sorted by time.

    Returns
    -------
    hashes : list[tuple[hash_key, anchor_time_bin]]
        hash_key = (freq_anchor, freq_partner, delta_time)
    """
    hashes = []
    n = len(peaks)
    for i in range(n):
        t1, f1, _ = peaks[i]
        partners_found = 0
        for j in range(i + 1, n):
            t2, f2, _ = peaks[j]
            dt = t2 - t1
            if dt < min_dt:
                continue
            if dt > max_dt:
                break  # peaks are time-sorted, so nothing further qualifies
            hash_key = (f1, f2, dt)
            hashes.append((hash_key, t1))
            partners_found += 1
            if partners_found >= fan_out:
                break
    return hashes


def generate_single_peak_hashes(peaks):
    """
    The 'single peaks on their own' baseline mentioned in Q3A, used only
    for the comparison experiment. Each peak becomes its own (trivial)
    hash key = its frequency bin; far more collision-prone than pairs.
    """
    return [((f,), t) for (t, f, _amp) in peaks]


def hashes_to_dict(hashes):
    """Group a list of (hash_key, anchor_time) into {hash_key: [times...]}.
    Used when building the per-song fingerprint record stored in the DB."""
    d = defaultdict(list)
    for key, t in hashes:
        d[key].append(t)
    return dict(d)
