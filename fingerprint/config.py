"""
config.py
=========
All tunable constants for the fingerprinting pipeline live here, so the
Streamlit app, the indexing script and the notebook in the report can all
import the *same* numbers. Tune these if you change the song dataset.
"""

# ---------------------------------------------------------------------------
# Audio loading
# ---------------------------------------------------------------------------
SAMPLE_RATE = 22_050          # Hz. Music fingerprints don't need hi-fi audio;
                              # most energy that matters for ID is < 5 kHz,
                              # so we downsample everything to this rate first.
                              # (This *is* deliberate decimation -> see Q1A/Q2f
                              # discussion on anti-aliasing: librosa low-pass
                              # filters before downsampling, so no aliasing.)
MONO = True                   # collapse stereo to mono (average channels)

# ---------------------------------------------------------------------------
# Spectrogram (STFT) parameters
# ---------------------------------------------------------------------------
N_FFT = 4096                  # samples per STFT window (~186 ms at 22050 Hz)
HOP_LENGTH = 1024             # samples between successive frames (~46 ms)
                              # -> 4x overlap, smooth time axis, good peaks.
WINDOW = "hann"

# Frequency band we keep peaks from. Below MIN_FREQ is mostly rumble / DC,
# above MAX_FREQ is rarely diagnostic and is the first thing noise destroys.
MIN_FREQ_HZ = 80
MAX_FREQ_HZ = 5_000

# ---------------------------------------------------------------------------
# Peak picking ("constellation map")
# ---------------------------------------------------------------------------
# We split the spectrogram into rectangular neighborhoods and keep a bin only
# if it's the loudest point in its own neighborhood (a local max filter),
# AND it's above a noise floor. This gives a sparse, repeatable fingerprint.
PEAK_NEIGHBORHOOD_FREQ_BINS = 14   # neighborhood half-height in freq bins
PEAK_NEIGHBORHOOD_TIME_BINS = 10   # neighborhood half-width in time bins
MIN_PEAK_AMP_DB = -55              # ignore peaks quieter than this (dB, after
                                   # per-clip normalization to 0 dB max)
MAX_PEAKS_PER_SECOND = 30          # cap fingerprint density so very loud /
                                   # busy songs don't dominate hash counts

# ---------------------------------------------------------------------------
# Hashing (peak-pairing, "fan-out")
# ---------------------------------------------------------------------------
# Each anchor peak is paired with several peaks that follow it within a
# target zone. This is what makes a hash "two frequencies + a time gap"
# (see Q3A) instead of a single, easily-confused frequency bin.
FAN_OUT = 6                # how many partner peaks each anchor pairs with
MIN_TIME_DELTA = 1         # frames; partners must be at least this far ahead
MAX_TIME_DELTA = 90        # frames (~4.1 s); partners must be within this
FREQ_QUANTIZE_HZ = 0       # 0 = no extra quantization beyond FFT bin width

# ---------------------------------------------------------------------------
# Matching / scoring
# ---------------------------------------------------------------------------
# A query hash "votes" for (song, query_time - song_time) whenever it matches
# a database hash. A true match produces one huge spike at a single offset;
# wrong songs spread votes thinly across many offsets.
MIN_VOTES_FOR_MATCH = 5          # cluster score below this -> "no match"
MIN_RUNNER_UP_RATIO = 1.5        # best score must beat 2nd place by this
                                  # factor, otherwise we report "no match"
OFFSET_BIN_TOLERANCE = 0          # 0 = exact-frame offset bins (no merging)

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
DB_PATH_DEFAULT = "data/db/fingerprints.json"
SONGS_DIR_DEFAULT = "data/songs"
SUPPORTED_EXTS = (".wav", ".mp3", ".flac", ".ogg", ".m4a")
