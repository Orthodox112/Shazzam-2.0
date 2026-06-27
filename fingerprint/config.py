SAMPLE_RATE = 22_050
MONO = True                  
N_FFT = 4096                  
HOP_LENGTH = 1024              
WINDOW = "hann"
MIN_FREQ_HZ = 80
MAX_FREQ_HZ = 5_000


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
