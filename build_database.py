import argparse
import time
from fingerprint.database import FingerprintDB
from fingerprint import config


def main():
    parser = argparse.ArgumentParser(description="Index a song library into a fingerprint database.")
    parser.add_argument("--songs-dir", default=config.SONGS_DIR_DEFAULT,
                         help="Folder containing the 50 song audio files.")
    parser.add_argument("--out", default=config.DB_PATH_DEFAULT,
                         help="Where to save the resulting fingerprints.json")
    args = parser.parse_args()

    print(f"Indexing songs from: {args.songs_dir}")
    db = FingerprintDB()

    def progress(i, total, name):
        print(f"  [{i}/{total}] {name}")

    t0 = time.perf_counter()
    n = db.build_from_folder(args.songs_dir, progress_callback=progress)
    t1 = time.perf_counter()

    db.save(args.out)

    print(f"\nIndexed {n} songs, {db.total_hashes()} total hashes in {t1 - t0:.1f}s")
    print(f"Database saved to: {args.out}")


if __name__ == "__main__":
    main()
