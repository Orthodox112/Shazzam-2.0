"""
fingerprint package
====================
Core DSP + database logic for the EE200 audio-fingerprinting project (Q3A/Q3B).

Modules
-------
audio_io      : loading / resampling / trimming audio files
spectrogram   : STFT -> spectrogram (with dB scaling)
peaks         : local-maxima ("constellation") extraction from a spectrogram
hashing       : pairing peaks into (f1, f2, dt) hashes
database      : building / saving / loading the song database (JSON-backed)
matcher       : querying a clip against the database (offset-histogram voting)
robustness    : helpers for the noise / pitch-shift / time-stretch experiments
config        : all tunable constants in one place
"""
