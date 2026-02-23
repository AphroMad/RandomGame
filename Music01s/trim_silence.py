#!/usr/bin/env python3
"""
trim_silence.py — Trims leading silence from all files in /music/ using ffmpeg.
Creates trimmed copies, replaces originals in-place.

Requirements: ffmpeg installed (brew install ffmpeg / apt install ffmpeg)
Run: python trim_silence.py
"""

import os
import re
import subprocess
import shutil

MUSIC_DIR       = "music"
EXTENSIONS      = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"}
SILENCE_DB      = -40    # dB threshold — quieter than this = silence
SILENCE_MIN_DUR = 0.05   # minimum silence duration to detect (seconds)
MAX_TRIM        = 10.0   # never trim more than 10s (safety cap)


def find_silence_end(filepath):
    """
    Runs ffmpeg silencedetect and returns the timestamp where
    the first silence ends (i.e. where real audio begins).
    Returns 0.0 if no leading silence found.
    """
    cmd = [
        "ffmpeg", "-i", filepath,
        "-af", f"silencedetect=noise={SILENCE_DB}dB:d={SILENCE_MIN_DUR}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    output = result.stderr.decode("utf-8", errors="ignore")

    matches = re.findall(r"silence_end:\s*([\d.]+)", output)
    if matches:
        offset = float(matches[0])
        return min(offset, MAX_TRIM)
    return 0.0


def trim_file(filepath, offset):
    """
    Uses ffmpeg to cut `offset` seconds from the start of the file.
    Writes to a temp file, then replaces the original.
    """
    ext      = os.path.splitext(filepath)[1].lower()
    tmp_path = filepath + ".tmp" + ext

    # -ss before -i = fast seek (re-encoded cleanly after)
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(offset),
        "-i", filepath,
        "-c", "copy",        # no re-encode, just cut
        tmp_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

    if result.returncode != 0:
        print(f"    ⚠ ffmpeg trim failed:\n{result.stderr.decode()}")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False

    os.replace(tmp_path, filepath)  # atomic replace
    return True


def main():
    if not os.path.isdir(MUSIC_DIR):
        print(f"❌ Folder '{MUSIC_DIR}' not found.")
        return

    files = sorted(
        f for f in os.listdir(MUSIC_DIR)
        if os.path.splitext(f)[1].lower() in EXTENSIONS
    )

    if not files:
        print(f"❌ No audio files found in '{MUSIC_DIR}/'")
        return

    print(f"🎵 {len(files)} files found — scanning for leading silence...\n")

    trimmed = 0
    skipped = 0

    for i, filename in enumerate(files):
        filepath = os.path.join(MUSIC_DIR, filename)
        print(f"  [{i+1}/{len(files)}] {filename}")

        try:
            offset = find_silence_end(filepath)
        except Exception as e:
            print(f"    ⚠ Error scanning: {e}")
            skipped += 1
            continue

        if offset < 0.05:
            print(f"    ✓ No leading silence (starts at {offset:.3f}s) — skipping")
            skipped += 1
            continue

        print(f"    ✂ Trimming {offset:.3f}s of silence...")
        ok = trim_file(filepath, offset)
        if ok:
            print(f"    ✅ Done")
            trimmed += 1
        else:
            print(f"    ❌ Failed — file untouched")
            skipped += 1

    print(f"\n{'─'*40}")
    print(f"✅ Trimmed:  {trimmed} files")
    print(f"⏭  Skipped:  {skipped} files (no silence or error)")
    print(f"\nRun python generate.py next to rebuild songs.js")


if __name__ == "__main__":
    main()
