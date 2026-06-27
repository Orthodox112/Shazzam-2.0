"""
make_samples.py
================
Generates a handful of short "query" clips by snipping random ~10-second
windows out of songs already in data/songs/, and saves them into
data/samples/. These power the "OR TRY A SAMPLE" row in the Identify tab
(exactly like sample1..sample5 in the demo video) -- a quick way for
graders to test identification without sourcing their own audio.

Usage
-----
    python make_samples.py                  # 5 samples, default 10s each
    python make_samples.py --n 8 --seconds 6
"""
import argparse
import os
import random

import soundfile as sf
import numpy as np

from fingerprint.audio_io import load_audio
from fingerprint import config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--songs-dir", default=config.SONGS_DIR_DEFAULT)
    parser.add_argument("--out-dir", default="data/samples")
    parser.add_argument("--n", type=int, default=5, help="number of sample clips to generate")
    parser.add_argument("--seconds", type=float, default=10.0, help="length of each sample clip")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    songs = [
        f for f in os.listdir(args.songs_dir)
        if os.path.splitext(f)[1].lower() in config.SUPPORTED_EXTS
    ]
    if not songs:
        print(f"No songs found in {args.songs_dir}. Add audio files first.")
        return

    chosen = random.sample(songs, min(args.n, len(songs)))

    for i, fname in enumerate(chosen, start=1):
        path = os.path.join(args.songs_dir, fname)
        y, sr = load_audio(path)
        clip_len = int(args.seconds * sr)
        if len(y) <= clip_len:
            clip = y
        else:
            start = random.randint(0, len(y) - clip_len)
            clip = y[start: start + clip_len]

        out_path = os.path.join(args.out_dir, f"sample{i}.wav")
        sf.write(out_path, clip, sr)
        print(f"sample{i}.wav  <-  {fname}  ({args.seconds:.0f}s clip)")

    print(f"\nWrote {len(chosen)} sample clips to {args.out_dir}/")


if __name__ == "__main__":
    main()
