#!/usr/bin/env python3
"""
Simple MIDI to layered WAV converter.
Creates 4 cumulative layers from MIDI files.

Requirements:
    pip install mido
    brew install fluid-synth

Layer structure:
    Layer 1: Drums + Percussion
    Layer 2: + Bass + Piano/Keys
    Layer 3: + Brass/Wind + Guitar
    Layer 4: + Ensemble/Choir/Strings (full mix)

Output structure:
    wav/{song_name}/layer-1.wav
    wav/{song_name}/layer-2.wav
    wav/{song_name}/layer-3.wav
    wav/{song_name}/layer-4.wav

Usage:
    python test_convert.py                    # process all MIDI files in midi/
    python test_convert.py midi/specific.mid  # process one file
"""
import os
import re
import glob
import argparse
import subprocess
import tempfile

import mido

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(SCRIPT_DIR, "midi")
WAV_DIR = os.path.join(SCRIPT_DIR, "wav")

# Layer definitions: each layer adds new instrument groups
LAYERS = [
    {"name": "layer-1", "description": "Drums + Percussion"},
    {"name": "layer-2", "description": "+ Bass + Piano/Keys"},
    {"name": "layer-3", "description": "+ Brass/Wind + Guitar"},
    {"name": "layer-4", "description": "+ Ensemble/Choir/Strings (full)"},
]


def make_song_id(filename):
    """Sanitize MIDI filename to a folder-safe song ID."""
    name = re.sub(r"\.midi?$", "", filename, flags=re.IGNORECASE)
    name = name.lower()
    name = re.sub(r"[\s_\.]+", "-", name)
    name = re.sub(r"[^a-z0-9\-]", "", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def get_layer_for_program(program, is_drum):
    """Map GM program number to layer index (0-3).
    
    Layer 0: Drums + Percussion (channel 9, or programs 47, 55, 112-119)
    Layer 1: Bass (32-39) + Piano/Keys/Synth (0-23, 80-95)
    Layer 2: Brass/Wind (56-71) + Guitar (24-31)
    Layer 3: Ensemble/Choir/Strings (40-54, 96-111)
    """
    if is_drum:
        return 0
    if program in (47, 55) or 112 <= program <= 119:  # Timpani, Orchestra Hit, Percussive
        return 0
    if 32 <= program <= 39:  # Bass
        return 1
    if (0 <= program <= 23) or (80 <= program <= 95):  # Piano, Organ, Synth
        return 1
    if 56 <= program <= 71:  # Brass, Wind
        return 2
    if 24 <= program <= 31:  # Guitar
        return 2
    if (40 <= program <= 54) or (96 <= program <= 111):  # Strings, Ensemble, Choir
        return 3
    return 1  # Fallback to rhythm section


def analyze_midi(midi_path):
    """Analyze MIDI file and return channel -> layer mapping."""
    mid = mido.MidiFile(midi_path)
    channel_programs = {}
    
    for track in mid.tracks:
        for msg in track:
            if msg.type == "program_change":
                channel_programs[msg.channel] = msg.program
    
    # Build channel -> layer mapping
    channel_layers = {}
    for ch in range(16):
        is_drum = (ch == 9)
        program = channel_programs.get(ch, 0)
        channel_layers[ch] = get_layer_for_program(program, is_drum)
    
    return channel_layers


def write_filtered_midi(src_path, dst_path, keep_channels):
    """Write a MIDI file containing only specified channels, preserving timing."""
    src = mido.MidiFile(src_path)
    dst = mido.MidiFile(type=src.type, ticks_per_beat=src.ticks_per_beat)
    
    for i, track in enumerate(src.tracks):
        new_track = mido.MidiTrack()
        accumulated_time = 0
        
        for msg in track:
            # Check if we should keep this message
            keep = not hasattr(msg, "channel") or msg.channel in keep_channels
            
            if keep:
                # Add accumulated time from skipped messages
                new_msg = msg.copy(time=msg.time + accumulated_time)
                new_track.append(new_msg)
                accumulated_time = 0
            else:
                # Accumulate the time of skipped messages
                accumulated_time += msg.time
        
        # Always keep track 0 (tempo/time sig); keep others if they have content
        if i == 0 or len(new_track) > 0:
            dst.tracks.append(new_track)
    
    dst.save(dst_path)


def find_soundfont():
    """Find a .sf2 soundfont file in common locations."""
    search_paths = [
        os.path.join(SCRIPT_DIR, "*.sf2"),
        os.path.join(SCRIPT_DIR, "*/*.sf2"),  # subfolders like GeneralUser-GS/
        "/opt/homebrew/share/soundfonts/*.sf2",
        "/opt/homebrew/Cellar/fluid-synth/*/share/fluid-synth/sf2/*.sf2",
        "/usr/local/share/soundfonts/*.sf2",
        "/usr/share/sounds/sf2/*.sf2",
    ]
    
    for pattern in search_paths:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    
    raise SystemExit(
        "No soundfont (.sf2) found!\n\n"
        "Download GeneralUser GS from:\n"
        "  https://schristiancollins.com/generaluser.php\n\n"
        "Then place the .sf2 file in the MusicSplit/ folder."
    )


def midi_to_wav(midi_path, wav_path, soundfont):
    """Render MIDI to WAV using FluidSynth CLI."""
    result = subprocess.run(
        [
            "fluidsynth",
            "-ni",              # no interactive mode
            "-F", wav_path,     # output file
            "-T", "wav",        # file type
            "-r", "44100",      # sample rate
            soundfont,
            midi_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if "command not found" in result.stderr or result.returncode == 127:
            raise SystemExit("FluidSynth not found. Install with: brew install fluid-synth")
        raise RuntimeError(f"FluidSynth failed: {result.stderr}")


def convert_midi_to_wav(midi_path, output_dir, soundfont):
    """Convert MIDI file to layered WAVs."""
    print("  Analyzing MIDI channels...")
    channel_layers = analyze_midi(midi_path)
    
    # Group channels by their layer
    layer_channels = {0: set(), 1: set(), 2: set(), 3: set()}
    for ch, layer in channel_layers.items():
        layer_channels[layer].add(ch)
    
    print(f"    Layer 0 (Drums): channels {sorted(layer_channels[0])}")
    print(f"    Layer 1 (Bass+Keys): channels {sorted(layer_channels[1])}")
    print(f"    Layer 2 (Brass+Guitar): channels {sorted(layer_channels[2])}")
    print(f"    Layer 3 (Ensemble): channels {sorted(layer_channels[3])}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    with tempfile.TemporaryDirectory(prefix="midi2wav_") as tmpdir:
        # Build cumulative channel sets for each layer
        cumulative_channels = set()
        layer_wavs = []
        
        for layer_idx in range(4):
            cumulative_channels = cumulative_channels | layer_channels[layer_idx]
            
            if not cumulative_channels:
                print(f"    Skipping {LAYERS[layer_idx]['name']} (no channels)")
                continue
            
            layer_midi = os.path.join(tmpdir, f"layer-{layer_idx + 1}.mid")
            layer_wav = os.path.join(output_dir, f"{LAYERS[layer_idx]['name']}.wav")
            
            print(f"    Creating {LAYERS[layer_idx]['name']} ({LAYERS[layer_idx]['description']})...")
            
            write_filtered_midi(midi_path, layer_midi, cumulative_channels)
            midi_to_wav(layer_midi, layer_wav, soundfont)
            
            layer_wavs.append(layer_wav)
        
        return layer_wavs


def get_midi_files(path=None):
    """Get list of MIDI files to process."""
    if path and os.path.isfile(path):
        return [path]
    
    # Get all MIDI files in midi/ folder
    midi_files = []
    for ext in ["*.mid", "*.midi", "*.MID", "*.MIDI"]:
        midi_files.extend(glob.glob(os.path.join(MIDI_DIR, ext)))
    
    return sorted(midi_files)


def main():
    parser = argparse.ArgumentParser(description="Convert MIDI to layered WAVs")
    parser.add_argument("midi_file", nargs="?", help="Input MIDI file (default: all files in midi/)")
    args = parser.parse_args()

    soundfont = find_soundfont()
    print(f"Using soundfont: {soundfont}")
    
    midi_files = get_midi_files(args.midi_file)
    
    if not midi_files:
        raise SystemExit(f"No MIDI files found in {MIDI_DIR}/")
    
    print(f"\nFound {len(midi_files)} MIDI file(s) to process")
    print(f"Output directory: {WAV_DIR}/\n")
    
    os.makedirs(WAV_DIR, exist_ok=True)
    
    success = 0
    failed = []
    
    for midi_path in midi_files:
        filename = os.path.basename(midi_path)
        song_id = make_song_id(filename)
        output_dir = os.path.join(WAV_DIR, song_id)
        
        print(f"Processing: {filename} -> {song_id}/")
        
        try:
            layers = convert_midi_to_wav(midi_path, output_dir, soundfont)
            print(f"  ✓ Created {len(layers)} layers\n")
            success += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}\n")
            failed.append((filename, str(e)))
    
    print(f"\n{'='*50}")
    print(f"Done! {success}/{len(midi_files)} files processed successfully")
    print(f"Output: {WAV_DIR}/")
    
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for name, err in failed:
            print(f"  {name}: {err}")


if __name__ == "__main__":
    main()
