#!/usr/bin/env python3
"""
MusicSplit build pipeline.
Converts MIDI files in midi/ into per-instrument-group MP3s,
cumulative layer MP3s, and a songs.js manifest.

Usage:
    python build.py
    python build.py --soundfont /path/to/soundfont.sf2
"""
import os
import re
import json
import glob
import sys
import argparse
import subprocess
import tempfile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIDI_DIR  = "midi"
AUDIO_DIR = "audio"
SONGS_JS  = "songs.js"

GROUP_NAMES = [
    "Drums+Perc",
    "Bass",
    "Brass/Wind",
    "Keys/Piano+Synth",
    "Guitar",
    "Ensemble+Choir+Strings",
]

GROUP_META = [
    {"index": 0, "name": "Drums+Perc",            "slug": "group-1-drums"},
    {"index": 1, "name": "Bass",                   "slug": "group-2-bass"},
    {"index": 2, "name": "Brass/Wind",             "slug": "group-3-brass-wind"},
    {"index": 3, "name": "Keys/Piano+Synth",       "slug": "group-4-keys-piano-synth"},
    {"index": 4, "name": "Guitar",                 "slug": "group-5-guitar"},
    {"index": 5, "name": "Ensemble+Choir+Strings", "slug": "group-6-ensemble-choir-strings"},
]

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SOUNDFONT_SEARCH_PATHS = [
    # Next to build.py (user drops it here)
    os.path.join(_SCRIPT_DIR, "*.sf2"),
    # FluidSynth default
    os.path.expanduser("~/.fluidsynth/default_sound_font.sf2"),
    # Homebrew fluid-synth bundled soundfonts
    "/usr/local/share/soundfonts/*.sf2",
    "/usr/local/Cellar/fluid-synth/*/share/fluid-synth/sf2/*.sf2",
    "/opt/homebrew/share/soundfonts/*.sf2",
    "/opt/homebrew/Cellar/fluid-synth/*/share/fluid-synth/sf2/*.sf2",
    # Linux standard
    "/usr/share/sounds/sf2/*.sf2",
    # pretty_midi bundled soundfont (fallback)
    os.path.join(os.path.dirname(os.path.abspath(
        sys.modules.get("pretty_midi", type("", (), {"__file__": ""})).__file__
        if sys.modules.get("pretty_midi") else "/"
    )), "TimGM6mb.sf2"),
]

SOUNDFONT_ERROR = """
No soundfont (.sf2) found. FluidSynth needs a soundfont to render audio.

Setup:
  1. Download GeneralUser GS: https://schristiancollins.com/generaluser.php
     (free, ~30MB, excellent General MIDI coverage)
  2. Place the .sf2 file in: MusicSplit/  (next to build.py)
  3. Run build.py again

Alternatively, FluidR3_GM.sf2 or any other General MIDI soundfont works.
"""


# ---------------------------------------------------------------------------
# Group mapping
# ---------------------------------------------------------------------------

def get_group_index(program, is_drum):
    """Map GM program number (0-127) to group index 0-5.

    Groups:
      0  Drums+Perc        — is_drum, or program 47 (Timpani), 55 (Orchestra Hit)
      1  Bass              — programs 32-39
      2  Brass/Wind        — programs 56-71
      3  Keys/Piano+Synth  — programs 0-23, 80-95  (also fallback for unmapped)
      4  Guitar            — programs 24-31
      5  Ensemble+Choir+Strings — programs 40-54 (excl. 47, 55 caught above)
    """
    if is_drum:
        return 0
    if program in (47, 55):
        return 0
    if 32 <= program <= 39:
        return 1
    if 56 <= program <= 71:
        return 2
    if (0 <= program <= 23) or (80 <= program <= 95):
        return 3
    if 24 <= program <= 31:
        return 4
    if 40 <= program <= 54:
        return 5
    return 3  # Other -> Keys/Piano fallback


# ---------------------------------------------------------------------------
# Soundfont discovery
# ---------------------------------------------------------------------------

def find_soundfont(override=None):
    """Return path to a .sf2 soundfont file, or raise SystemExit."""
    if override:
        if os.path.isfile(override):
            return override
        raise SystemExit(f"Soundfont not found: {override}")

    for pattern in SOUNDFONT_SEARCH_PATHS:
        if not pattern:
            continue
        if "*" in pattern:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
        elif os.path.isfile(pattern):
            return pattern

    raise SystemExit(SOUNDFONT_ERROR)


# ---------------------------------------------------------------------------
# MIDI analysis
# ---------------------------------------------------------------------------

def get_channel_programs(midi_path):
    """Parse MIDI file and return (channel_programs, note_counts).

    channel_programs: dict channel -> program (None for drum channel 9)
    note_counts:      dict channel -> number of note_on events (velocity > 0)
    """
    import mido
    mid = mido.MidiFile(midi_path)
    channel_programs = {}
    note_counts = {}

    for track in mid.tracks:
        for msg in track:
            if msg.type == "program_change":
                channel_programs[msg.channel] = msg.program
            if msg.type == "note_on" and msg.velocity > 0:
                ch = msg.channel
                note_counts[ch] = note_counts.get(ch, 0) + 1

    # Channel 9 is always drums in GM regardless of program_change
    channel_programs[9] = None  # sentinel for drums
    return channel_programs, note_counts


def build_group_channels(channel_programs, note_counts):
    """Return (groups, non_empty).

    groups:    dict group_index -> set of MIDI channels
    non_empty: dict group_index -> bool (True if any channel in group has notes)
    """
    groups = {i: set() for i in range(6)}
    for ch, prog in channel_programs.items():
        is_drum = (ch == 9 or prog is None)
        effective_prog = prog if prog is not None else 0
        group = get_group_index(effective_prog, is_drum)
        groups[group].add(ch)

    non_empty = {
        g: sum(note_counts.get(ch, 0) for ch in channels) > 0
        for g, channels in groups.items()
    }
    return groups, non_empty


# ---------------------------------------------------------------------------
# MIDI filtering
# ---------------------------------------------------------------------------

def write_group_midi(src_path, dst_path, keep_channels):
    """Write a MIDI file containing only the specified MIDI channels."""
    import mido
    src = mido.MidiFile(src_path)
    dst = mido.MidiFile(type=src.type, ticks_per_beat=src.ticks_per_beat)

    for i, track in enumerate(src.tracks):
        new_track = mido.MidiTrack()
        for msg in track:
            # Keep meta messages (no channel attr) and messages for keep_channels
            if not hasattr(msg, "channel") or msg.channel in keep_channels:
                new_track.append(msg)
        # Always keep track 0 (tempo/time sig); keep others only if relevant
        if i == 0 or any(
            hasattr(m, "channel") and m.channel in keep_channels
            for m in track
        ):
            dst.tracks.append(new_track)

    dst.save(dst_path)


# ---------------------------------------------------------------------------
# Audio rendering
# ---------------------------------------------------------------------------

def render_midi_to_wav(midi_path, wav_path, soundfont_path):
    """Render MIDI to WAV using FluidSynth 2.x fast-render mode."""
    result = subprocess.run([
        "fluidsynth",
        "-ni",           # -n: no MIDI input driver, -i: no interactive shell
        "-F", wav_path,  # fast-render output file
        "-T", "wav",     # audio file type
        "-r", "44100",   # sample rate
        soundfont_path,
        midi_path,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if result.returncode != 0:
        raise RuntimeError(
            f"FluidSynth failed (exit {result.returncode}): {midi_path}"
        )


def wav_to_mp3(wav_path, mp3_path, duration=None):
    """Encode WAV as 192kbps stereo MP3.

    duration: seconds to trim to, or None to encode the full file.
    """
    cmd = ["ffmpeg", "-y", "-i", wav_path]
    if duration is not None:
        cmd += ["-t", str(duration)]
    cmd += ["-ar", "44100", "-ac", "2", "-b:a", "192k", mp3_path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def mix_wavs_to_mp3(wav_paths, mp3_path, duration=None):
    """Mix multiple WAV files and encode as a cumulative layer MP3.

    duration: seconds to trim to, or None to encode the full length.
    Single input: delegates to wav_to_mp3 (no mixing needed).
    Multiple inputs: uses ffmpeg amix filter with normalize=0.
    """
    if len(wav_paths) == 1:
        wav_to_mp3(wav_paths[0], mp3_path, duration)
        return

    inputs = []
    for p in wav_paths:
        inputs += ["-i", p]

    n = len(wav_paths)
    cmd = ["ffmpeg", "-y", *inputs]
    if duration is not None:
        cmd += ["-t", str(duration)]
    cmd += [
        "-filter_complex", f"amix=inputs={n}:duration=longest:normalize=0",
        "-ar", "44100", "-ac", "2", "-b:a", "192k",
        mp3_path,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


# ---------------------------------------------------------------------------
# Filename utilities
# ---------------------------------------------------------------------------

def make_song_id(filename):
    """Sanitize MIDI filename to a URL-safe song ID."""
    name = re.sub(r"\.midi?$", "", filename, flags=re.IGNORECASE)
    name = name.lower()
    name = re.sub(r"[\s_\.]+", "-", name)
    name = re.sub(r"[^a-z0-9\-]", "", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def parse_filename(filename):
    """Return (artist, title) from 'Artist - Title.mid' naming convention.

    If no ' - ' separator found, returns (None, full_name).
    """
    name = os.path.splitext(filename)[0]
    parts = [p.strip() for p in name.split(" - ")]
    if len(parts) >= 2:
        return parts[0], " - ".join(parts[1:])
    return None, parts[0]


# ---------------------------------------------------------------------------
# Song processing
# ---------------------------------------------------------------------------

def process_song(midi_path, midi_filename, song_id, out_dir, soundfont):
    """Process one MIDI file into per-group MP3s, cumulative layers, and a manifest entry.

    Returns a song dict: { id, title, artist, groups, layers }
    """
    artist, title = parse_filename(midi_filename)

    with tempfile.TemporaryDirectory(prefix="musicsplit_") as tmpdir:
        # Step A: Detect channel-to-group mapping
        channel_programs, note_counts = get_channel_programs(midi_path)
        groups, non_empty = build_group_channels(channel_programs, note_counts)

        # Step B: Render each group to WAV in temp dir
        group_wavs = {}  # group_index -> wav_path
        for meta in GROUP_META:
            g = meta["index"]
            keep_channels = groups[g]

            group_midi = os.path.join(tmpdir, f"{meta['slug']}.mid")
            group_wav  = os.path.join(tmpdir, f"{meta['slug']}.wav")

            write_group_midi(midi_path, group_midi, keep_channels)
            render_midi_to_wav(group_midi, group_wav, soundfont)
            group_wavs[g] = group_wav

        # Step C: Convert each per-group WAV to MP3 (even if silent)
        for meta in GROUP_META:
            g = meta["index"]
            mp3_path = os.path.join(out_dir, f"{meta['slug']}.mp3")
            wav_to_mp3(group_wavs[g], mp3_path)

        # Step D: Build cumulative layers (present groups only, in order)
        accumulated_wavs = []
        layer_num = 0
        layer_files = []

        for meta in GROUP_META:
            g = meta["index"]
            if non_empty[g]:
                accumulated_wavs.append(group_wavs[g])
                layer_num += 1
                layer_mp3 = os.path.join(out_dir, f"layer-{layer_num}.mp3")
                mix_wavs_to_mp3(list(accumulated_wavs), layer_mp3)
                layer_files.append(f"audio/{song_id}/layer-{layer_num}.mp3")

        # Step E: Build manifest entry
        groups_manifest = []
        for meta in GROUP_META:
            g = meta["index"]
            groups_manifest.append({
                "name":    meta["name"],
                "file":    f"audio/{song_id}/{meta['slug']}.mp3",
                "present": non_empty[g],
            })

        return {
            "id":     song_id,
            "title":  title,
            "artist": artist,
            "groups": groups_manifest,
            "layers": layer_files,
        }


# ---------------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------------

def write_manifest(songs, output_path):
    """Write songs.js manifest in const SONGS = [...] format."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by build.py\n")
        f.write("const SONGS = " + json.dumps(songs, indent=2, ensure_ascii=False) + ";\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="MusicSplit build pipeline")
    parser.add_argument(
        "--soundfont", metavar="FILE",
        help="Path to a .sf2 soundfont file (overrides auto-discovery)"
    )
    args = parser.parse_args()

    soundfont = find_soundfont(args.soundfont)
    print(f"Using soundfont: {soundfont}")

    # Change to script directory so relative paths (midi/, audio/) work correctly
    os.chdir(_SCRIPT_DIR)
    os.makedirs(AUDIO_DIR, exist_ok=True)

    midi_files = sorted(
        f for f in os.listdir(MIDI_DIR)
        if f.lower().endswith(".mid") or f.lower().endswith(".midi")
    )

    if not midi_files:
        print(f"No MIDI files found in {MIDI_DIR}/")
        return

    songs = []
    failed = []

    for midi_filename in midi_files:
        midi_path = os.path.join(MIDI_DIR, midi_filename)
        song_id   = make_song_id(midi_filename)
        out_dir   = os.path.join(AUDIO_DIR, song_id)
        os.makedirs(out_dir, exist_ok=True)

        print(f"Processing: {midi_filename}")
        try:
            entry = process_song(midi_path, midi_filename, song_id, out_dir, soundfont)
            songs.append(entry)
            present_count = sum(1 for g in entry["groups"] if g["present"])
            print(f"  Done — {present_count} present groups, {len(entry['layers'])} layers")
        except Exception as e:
            print(f"  FAILED: {e}")
            failed.append((midi_filename, str(e)))

    write_manifest(songs, SONGS_JS)
    print(f"\n{len(songs)} song(s) written to {SONGS_JS}")

    if failed:
        print(f"\n{len(failed)} song(s) failed:")
        for name, err in failed:
            print(f"  {name}: {err}")


if __name__ == "__main__":
    main()
