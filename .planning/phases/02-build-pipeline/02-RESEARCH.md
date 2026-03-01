# Phase 2: Build Pipeline - Research

**Researched:** 2026-03-01
**Domain:** Python MIDI processing, FluidSynth rendering, ffmpeg audio conversion
**Confidence:** HIGH — all tools verified locally, CLI flags tested, code patterns validated

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **MIDI sourcing:** Files in `MusicSplit/midi/`, named `Artist - Title.mid`
- **6 instrument groups (fixed order):**
  1. Drums + Percussion — MIDI channel 10 (is_drum) + programs 47, 55
  2. Bass — programs 32-39
  3. Brass/Wind — programs 56-71
  4. Keys/Piano + Synth — programs 0-23 + 80-95 (+ "Other" fallback)
  5. Guitar — programs 24-31
  6. Ensemble + Choir + Strings — programs 40-54 (excluding 47, 55 already in group 1)
- **Cumulative MP3s** rendered in addition to per-group MP3s (both required)
- **Audio spec:** 192kbps MP3, 44100 Hz, stereo, trimmed to ~60 seconds
- **Render chain:** FluidSynth (MIDI → WAV) then ffmpeg (WAV → MP3)
- **Soundfont:** GeneralUser GS (~30MB .sf2), NOT committed to repo; build.py checks known locations then errors with instructions
- **Output directory:** `MusicSplit/audio/<song-id>/`
- **Files per song:** `group-1-drums.mp3`, `group-2-bass.mp3`, ..., `layer-1.mp3`, `layer-2.mp3`, ...
- **Manifest:** `songs.js` with `const SONGS = [...]` format (matches Music01s pattern)
- **Manifest entry shape:** `{ title, artist, id, groups: [{ name, file, present }], layers: [file1, file2, ...] }`
- **Empty groups:** Skip in cumulative layers; `present: false` in manifest
- **Song ID:** Sanitized filename (lowercase, hyphens)
- **Follow `Music01s/build.py` pattern:** scan → process each file → generate manifest
- **Re-use `details_midi.py` pattern:** pretty_midi usage for instrument/group detection

### Claude's Discretion

- Exact FluidSynth CLI invocation flags
- Temp file handling during rendering
- Whether to render MIDI per-track or per-channel
- Error handling for malformed MIDI files
- Progress reporting format (print statements vs progress bar)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| BUILD-01 | Python script parses MIDI files and groups tracks into 6 instrument groups | pretty_midi detects is_drum + program; mido writes filtered per-group MIDI files by channel |
| BUILD-02 | Script renders each instrument group to a separate MP3 using FluidSynth + soundfont | FluidSynth 2.4.5 verified on machine with `-ni -F out.wav -T wav -r 44100 sf2 midi` pattern |
| BUILD-03 | Script generates cumulative MP3 files (layer N = groups 1 through N mixed together) | ffmpeg `amix=inputs=N:duration=longest:normalize=0` filter verified for combining WAV inputs |
| BUILD-04 | Script generates songs.js manifest with song title, artist, and per-layer file paths | Music01s/build.py pattern verified; `const SONGS = [...]` written with json.dumps |

</phase_requirements>

---

## Summary

The pipeline reads MIDI files, filters channels into 6 instrument groups, renders each group to WAV via FluidSynth, trims/converts to MP3 via ffmpeg, builds cumulative layers by mixing group WAVs, then writes a songs.js manifest. All tooling is already installed on the development machine (FluidSynth 2.4.5, ffmpeg 7.1.1, Python 3.13). The key libraries are `mido` (MIDI read/filter/write) and `pretty_midi` (program/channel introspection), both installed and verified.

The implementation strategy is: use pretty_midi to detect which channels map to which instrument group, then use mido to write per-group MIDI files (filtered by channel), then render each group MIDI with FluidSynth to WAV, then use ffmpeg to trim all WAVs to 60s and convert to MP3. Cumulative layers are built by mixing per-group WAVs with ffmpeg before MP3 conversion. Duration alignment is automatic: FluidSynth renders each group MIDI to the same total length as the source MIDI, and all are trimmed to the same 60s target.

One conflict exists between STATE.md and CONTEXT.md regarding the manifest format. STATE.md records the decision as `songs.json + fetch()`, while CONTEXT.md (the phase-specific, user-locked decision) says `songs.js` with `const SONGS = [...]` matching the Music01s pattern. CONTEXT.md takes precedence as the direct phase decision document. This conflict should be surfaced to the planner as a flag.

**Primary recommendation:** Implement `MusicSplit/build.py` following the Music01s/build.py structure exactly. Use mido for MIDI filtering (channel-based), FluidSynth `-ni -F` for WAV rendering, ffmpeg for MP3 conversion and amix for cumulative layers.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| mido | 1.3.3 | Read MIDI, filter channels, write per-group MIDI files | Already installed; purpose-built for MIDI I/O; no C deps |
| pretty_midi | 0.2.11 | Detect instrument programs and is_drum per channel | Already used in `details_midi.py`; cleaner API for introspection |
| FluidSynth | 2.4.5 (CLI) | Render MIDI + soundfont to WAV | Already installed via Homebrew; verified working |
| ffmpeg | 7.1.1 (CLI) | Trim WAV, convert to MP3, mix multiple WAVs for layers | Already established in project (Music01s/build.py) |
| Python | 3.13 | Script language | Already in use across the project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| subprocess | stdlib | Call FluidSynth and ffmpeg as child processes | Every render and conversion call |
| tempfile | stdlib | Create temporary directory for intermediate WAV files | Per-song processing, cleanup in finally block |
| os, re, json | stdlib | File operations, sanitize filenames, write manifest | Throughout |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| mido (for filtering) | pretty_midi rewrite tracks | pretty_midi doesn't support writing filtered MIDI files easily; mido is the right tool |
| fluidsynth CLI | pyfluidsynth (Python binding) | CLI is simpler, no extra dep, already works |
| ffmpeg amix filter | sox mix | ffmpeg already in project; sox adds a new dependency |

**Installation (already done on dev machine):**
```bash
brew install fluid-synth ffmpeg
pip install pretty_midi mido
```

---

## Architecture Patterns

### Recommended Project Structure
```
MusicSplit/
├── build.py              # Main build script (new)
├── midi/                 # Input: Artist - Title.mid files
│   ├── test.mid
│   └── ...
├── audio/                # Output: generated by build.py (gitignored via *.mp3)
│   └── <song-id>/
│       ├── group-1-drums.mp3
│       ├── group-2-bass.mp3
│       ├── group-3-brass-wind.mp3
│       ├── group-4-keys-piano-synth.mp3
│       ├── group-5-guitar.mp3
│       ├── group-6-ensemble-choir-strings.mp3
│       ├── layer-1.mp3
│       ├── layer-2.mp3
│       ├── layer-3.mp3
│       ├── layer-4.mp3
│       ├── layer-5.mp3
│       └── layer-6.mp3
├── songs.js              # Output: const SONGS = [...] manifest
├── details_midi.py       # Utility: inspect a MIDI file
├── generate.py           # Legacy: replaced by build.py
└── README.md
```

### Pattern 1: Channel-Based Group Assignment

**What:** Use pretty_midi to detect program numbers per instrument, map each channel to one of 6 groups. Use mido to write a filtered MIDI file containing only the channels for that group.

**When to use:** Always — this is the core grouping approach.

**Example:**
```python
# Source: verified against test.mid in this project
import pretty_midi
import mido

GROUP_NAMES = [
    "Drums+Perc",
    "Bass",
    "Brass/Wind",
    "Keys/Piano+Synth",
    "Guitar",
    "Ensemble+Choir+Strings",
]

def get_group_index(program, is_drum):
    """Map GM program number to group index 0-5."""
    if is_drum:
        return 0                          # Drums+Perc
    if program in (47, 55):
        return 0                          # Timpani + Orchestra Hit -> Drums+Perc
    if 32 <= program <= 39:
        return 1                          # Bass
    if 56 <= program <= 71:
        return 2                          # Brass/Wind
    if (0 <= program <= 23) or (80 <= program <= 95):
        return 3                          # Keys/Piano+Synth
    if 24 <= program <= 31:
        return 4                          # Guitar
    if 40 <= program <= 54:
        return 5                          # Ensemble+Choir+Strings
    return 3                              # Other -> Keys/Piano fallback

def get_channel_to_group(midi_path):
    """Return dict: channel_number -> group_index, and set of non-empty groups."""
    pm = pretty_midi.PrettyMIDI(midi_path)
    channel_to_group = {}
    non_empty = set()
    for instrument in pm.instruments:
        # pretty_midi uses channel numbers starting from 0
        # is_drum instruments are always channel 9 in GM
        ch = 9 if instrument.is_drum else instrument.program  # NOTE: see Pitfall 2
        group = get_group_index(instrument.program, instrument.is_drum)
        channel_to_group[ch] = group
        if instrument.notes:
            non_empty.add(group)
    return channel_to_group, non_empty
```

**Critical correction (see Pitfall 2):** pretty_midi instruments don't expose the raw MIDI channel directly. Use mido to extract channel->program mapping instead.

### Pattern 2: Channel-Program Detection with mido

**What:** Use mido to read program_change messages and map MIDI channel -> program -> group.

**When to use:** The correct approach for channel-based MIDI filtering. pretty_midi is for introspection only.

**Example:**
```python
# Source: verified against test.mid (mido 1.3.3)
import mido

def get_channel_programs(midi_path):
    """Return dict: channel -> program (None for drum channel 9)."""
    mid = mido.MidiFile(midi_path)
    channel_programs = {}
    note_counts = {}  # channel -> note count

    for track in mid.tracks:
        for msg in track:
            if msg.type == 'program_change':
                channel_programs[msg.channel] = msg.program
            if msg.type == 'note_on' and msg.velocity > 0:
                ch = msg.channel
                note_counts[ch] = note_counts.get(ch, 0) + 1

    # Channel 9 is always drums in GM, regardless of program
    channel_programs[9] = None  # sentinel for drums
    return channel_programs, note_counts

def build_group_channels(channel_programs, note_counts):
    """Return dict: group_index -> set of MIDI channels."""
    groups = {i: set() for i in range(6)}
    for ch, prog in channel_programs.items():
        is_drum = (ch == 9 or prog is None)
        group = get_group_index(prog if prog is not None else 0, is_drum)
        groups[group].add(ch)
    return groups, {
        g: sum(note_counts.get(ch, 0) for ch in channels) > 0
        for g, channels in groups.items()
    }
```

### Pattern 3: Write Filtered Group MIDI

**What:** Use mido to write a new MIDI file containing only channels for one group.

**When to use:** Before each FluidSynth render call.

**Example:**
```python
# Source: verified with mido 1.3.3, test.mid
import mido

def write_group_midi(src_path, dst_path, keep_channels):
    """Write a MIDI file containing only the specified MIDI channels."""
    src = mido.MidiFile(src_path)
    dst = mido.MidiFile(type=src.type, ticks_per_beat=src.ticks_per_beat)

    for i, track in enumerate(src.tracks):
        new_track = mido.MidiTrack()
        for msg in track:
            # Keep meta messages (no channel) and messages in keep_channels
            if not hasattr(msg, 'channel') or msg.channel in keep_channels:
                new_track.append(msg)
        # Always keep track 0 (tempo/time signature metadata)
        # Keep other tracks only if they have relevant channel messages
        if i == 0 or any(
            hasattr(m, 'channel') and m.channel in keep_channels
            for m in track
        ):
            dst.tracks.append(new_track)

    dst.save(dst_path)
```

**Verified:** Produces a correctly-sized MIDI file (8327 bytes for drums-only vs 177K for full file). FluidSynth renders it to same-duration WAV as the full file.

### Pattern 4: FluidSynth Render (Verified CLI)

**What:** Render a MIDI file to WAV using FluidSynth 2.x fast-render mode.

**Example:**
```python
# Source: verified on FluidSynth 2.4.5, macOS
import subprocess

def render_midi_to_wav(midi_path, wav_path, soundfont_path):
    """Render MIDI to WAV using FluidSynth fast-render mode."""
    result = subprocess.run([
        "fluidsynth",
        "-ni",          # -n: no MIDI input driver, -i: no interactive shell
        "-F", wav_path, # fast-render output file
        "-T", "wav",    # audio file type
        "-r", "44100",  # sample rate
        soundfont_path,
        midi_path,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if result.returncode != 0:
        raise RuntimeError(f"FluidSynth failed (exit {result.returncode}): {midi_path}")
```

**Note on stderr:** FluidSynth 2.x emits two "panic: An error occurred while reading from stdin" messages to stderr even with `-i` flag. These are harmless. Use `stderr=subprocess.DEVNULL` to suppress them.

### Pattern 5: ffmpeg WAV-to-MP3 and Cumulative Mixing

**What:** Trim WAV to 60s and convert to 192kbps MP3. Mix multiple WAVs for cumulative layers.

**Example:**
```python
# Source: verified with ffmpeg 7.1.1
import subprocess

def wav_to_mp3(wav_path, mp3_path, duration=60):
    """Trim WAV to duration seconds and encode as 192kbps MP3."""
    subprocess.run([
        "ffmpeg", "-y",
        "-i", wav_path,
        "-t", str(duration),
        "-ar", "44100", "-ac", "2", "-b:a", "192k",
        mp3_path,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def mix_wavs_to_mp3(wav_paths, mp3_path, duration=60):
    """Mix multiple WAV files and encode as 192kbps MP3 (cumulative layer)."""
    inputs = []
    for p in wav_paths:
        inputs += ["-i", p]

    n = len(wav_paths)
    if n == 1:
        # No mixing needed for single input
        wav_to_mp3(wav_paths[0], mp3_path, duration)
        return

    subprocess.run([
        "ffmpeg", "-y",
        *inputs,
        "-t", str(duration),
        "-filter_complex", f"amix=inputs={n}:duration=longest:normalize=0",
        "-ar", "44100", "-ac", "2", "-b:a", "192k",
        mp3_path,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
```

**Verified:** `amix` with `normalize=0` preserves original levels. Duration alignment is automatic — all group WAVs from FluidSynth have the same total length (equal to source MIDI length), and all are trimmed to the same 60s target.

### Pattern 6: songs.js Manifest Generation

**What:** Write the manifest matching the Music01s pattern.

**Example:**
```python
# Source: Music01s/build.py pattern, adapted for MusicSplit
import json, os, re

def make_song_id(filename):
    """Sanitize MIDI filename to a URL-safe song ID."""
    name = re.sub(r'\.mid$', '', filename, flags=re.IGNORECASE)
    name = name.lower()
    name = re.sub(r'[\s_\.]+', '-', name)
    name = re.sub(r'[^a-z0-9\-]', '', name)
    name = re.sub(r'-+', '-', name)
    return name.strip('-')

def parse_filename(filename):
    """Return (artist, title) from 'Artist - Title.mid' convention."""
    name = os.path.splitext(filename)[0]
    parts = [p.strip() for p in name.split(' - ')]
    if len(parts) >= 2:
        return parts[0], ' - '.join(parts[1:])
    return None, parts[0]

GROUP_META = [
    {"index": 0, "name": "Drums+Perc",              "slug": "group-1-drums"},
    {"index": 1, "name": "Bass",                     "slug": "group-2-bass"},
    {"index": 2, "name": "Brass/Wind",               "slug": "group-3-brass-wind"},
    {"index": 3, "name": "Keys/Piano+Synth",         "slug": "group-4-keys-piano-synth"},
    {"index": 4, "name": "Guitar",                   "slug": "group-5-guitar"},
    {"index": 5, "name": "Ensemble+Choir+Strings",   "slug": "group-6-ensemble-choir-strings"},
]

def build_song_entry(midi_filename, song_id, non_empty_groups):
    artist, title = parse_filename(midi_filename)
    base = f"audio/{song_id}"

    groups = []
    layer_files = []
    layer_num = 0

    for meta in GROUP_META:
        g = meta["index"]
        present = g in non_empty_groups
        groups.append({
            "name": meta["name"],
            "file": f"{base}/{meta['slug']}.mp3",
            "present": present,
        })
        if present:
            layer_num += 1
            layer_files.append(f"{base}/layer-{layer_num}.mp3")

    return {
        "id": song_id,
        "title": title,
        "artist": artist,
        "groups": groups,
        "layers": layer_files,
    }

def write_manifest(songs, output_path="songs.js"):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by build.py\n")
        f.write("const SONGS = " + json.dumps(songs, indent=2, ensure_ascii=False) + ";\n")
```

### Pattern 7: Soundfont Discovery

**What:** Check known locations for soundfont; provide clear error with instructions if not found.

**Example:**
```python
import os, glob

SOUNDFONT_SEARCH_PATHS = [
    # Next to build.py (user drops it here)
    os.path.join(os.path.dirname(__file__), "*.sf2"),
    # FluidSynth default
    os.path.expanduser("~/.fluidsynth/default_sound_font.sf2"),
    # Homebrew fluid-synth bundled soundfonts
    "/usr/local/share/soundfonts/*.sf2",
    "/usr/local/Cellar/fluid-synth/*/share/fluid-synth/sf2/*.sf2",
    # Linux standard
    "/usr/share/sounds/sf2/*.sf2",
]

SOUNDFONT_ERROR = """
No soundfont (.sf2) found. FluidSynth needs a soundfont to render audio.

Setup:
  1. Download GeneralUser GS: https://schristiancollins.com/generaluser.php
     (free, ~30MB, excellent General MIDI coverage)
  2. Place the .sf2 file in: MusicSplit/  (next to build.py)
  3. Run build.py again

Alternatively, any General MIDI soundfont works. FluidR3_GM.sf2 is another
popular choice if you have it.
"""

def find_soundfont():
    for pattern in SOUNDFONT_SEARCH_PATHS:
        if '*' in pattern:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
        elif os.path.isfile(pattern):
            return pattern
    raise SystemExit(SOUNDFONT_ERROR)
```

**Note:** On this dev machine, `FluidR3_GM.sf2` exists at a non-standard path. The discovery pattern above will not find it automatically. The dev should copy/symlink it to `MusicSplit/` or `~/.fluidsynth/`.

### Anti-Patterns to Avoid

- **Using pretty_midi to write filtered MIDI:** pretty_midi doesn't expose raw MIDI write with channel filtering. Use mido for writing.
- **Using pretty_midi channel numbers directly for filtering:** pretty_midi remaps channels internally. Extract channel-to-program mapping with mido's `program_change` messages instead.
- **Rendering all 6 groups even when empty:** Detect empty groups via note count. Still write the per-group MP3 (silence is fine for explorer mode), but skip adding to cumulative layers.
- **Not using `check=True` or `returncode` check on subprocess calls:** Silent failures will produce broken MP3s.
- **Leaving temp WAV files on failure:** Always use try/finally to clean up temp directory.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| MIDI channel filtering | Custom MIDI byte parser | mido | MIDI format has variable-length encoding, running status, tick accumulation — complex to get right |
| WAV mixing for cumulative layers | Python audio mixing loop | ffmpeg amix filter | Sample-accurate sync, handles different WAV lengths, no extra deps |
| MP3 encoding | Python audio encoder | ffmpeg libmp3lame | Licensing, quality, encoder tuning all handled |
| MIDI → audio synthesis | Custom oscillator synth | FluidSynth + soundfont | Soundfont gives real instrument samples; oscillators sound wrong for recognition |
| Filename sanitization | Ad-hoc string replace | re-based sanitizer (pattern above) | Handles unicode, special chars, edge cases |

**Key insight:** The hard parts of this pipeline (MIDI parsing, audio synthesis, format conversion) are all solved by existing tools. The build script is primarily orchestration glue, not algorithmic work.

---

## Common Pitfalls

### Pitfall 1: FluidSynth CLI Flags Differ Between 1.x and 2.x

**What goes wrong:** Documentation and blog posts often show FluidSynth 1.x syntax. Using `-a` audio driver flags or `--fast-render` (long form) may behave differently.

**Why it happens:** Major version change between 1.x and 2.x.

**How to avoid:** Use the verified 2.x command (tested on 2.4.5 on this machine):
```bash
fluidsynth -ni -F output.wav -T wav -r 44100 soundfont.sf2 input.mid
```

**Warning signs:** Exit code non-zero; WAV file not created; empty WAV file.

### Pitfall 2: pretty_midi Does Not Expose Raw MIDI Channel Numbers

**What goes wrong:** `pretty_midi.PrettyMIDI` instruments have an internal `channel` attribute, but it's assigned by pretty_midi's parsing logic, not always equal to the raw MIDI channel number in the file.

**Why it happens:** pretty_midi normalizes track/channel handling internally.

**How to avoid:** Use mido to read `program_change` messages directly and build channel->program mapping. Use pretty_midi only for high-level introspection (is_drum, program, note count).

**Correct approach:**
```python
# Use mido for channel->program mapping
mid = mido.MidiFile(midi_path)
for track in mid.tracks:
    for msg in track:
        if msg.type == 'program_change':
            channel_programs[msg.channel] = msg.program
```

### Pitfall 3: Empty Groups Still Render to Full-Length Silent WAV

**What goes wrong:** A group MIDI with zero notes still produces a 16-minute WAV (full MIDI length) filled with silence. This is correct behavior and not a bug, but developers may mistake it for a render failure.

**Why it happens:** FluidSynth renders the MIDI's full time range, even if no notes play.

**How to avoid:** After rendering, detect empty groups via note count (from mido analysis), not by WAV file size. Use `present: false` in manifest for empty groups. Still keep the per-group MP3 (empty/silent is fine for explorer mode; the manifest tells the game not to use it in layers).

**Detection pattern:**
```python
# -90.3 dB mean volume = effectively silence
# Use note_counts from mido analysis, not audio analysis
is_present = note_counts.get(group_index, 0) > 0
```

### Pitfall 4: Duration Misalignment Between Groups

**What goes wrong:** If groups are trimmed independently, floating-point duration differences (~30ms from MP3 encoding) cause visible drift when the game switches layers.

**Why it happens:** MP3 frame alignment adds a small start offset (~25ms) and rounding.

**How to avoid:** All group WAVs from FluidSynth render to the same byte length (verified: all show `Duration: 00:16:48.98` for the test MIDI). Trimming all with `ffmpeg -t 60` produces identical duration MP3s. The game's Web Audio API handling (Phase 3) will handle the ~25ms MP3 start offset identically for all files.

### Pitfall 5: songs.js vs songs.json Manifest Format Conflict

**What goes wrong:** STATE.md records a decision "songs.json + fetch() — NOT songs.js global", but CONTEXT.md (the phase decision document) locks in `songs.js` with `const SONGS = [...]`.

**Why it happens:** STATE.md may have been updated before the detailed phase discussion, which overrode it.

**Resolution:** CONTEXT.md is the authoritative phase decision. Output `songs.js` with `const SONGS = [...]`. The Phase 3 game code will load it via `<script src="songs.js">` and access `window.SONGS`. If Phase 3 uses ES modules with deferred loading, this will need revisiting — flag it for the Phase 3 planner.

### Pitfall 6: Malformed MIDI Files from Free MIDI Sites

**What goes wrong:** MIDI files from the internet may have: no program_change messages (uses default program 0), multiple program changes per channel, tempo track embedded in a non-zero track, type 0 (single-track) format instead of type 1.

**Why it happens:** MIDI is a loose standard; DAWs export in different ways.

**How to avoid:**
- `mido` handles Type 0 and Type 1 correctly (both use channel-based filtering)
- If no `program_change` found for a channel, assume program 0 (acoustic grand piano → group 3, Keys)
- Wrap each song's processing in a try/except; log errors and continue to the next song
- Print a summary of which songs failed and why

**Error handling pattern:**
```python
for midi_file in midi_files:
    try:
        process_song(midi_file, ...)
        print(f"  OK: {midi_file}")
    except Exception as e:
        print(f"  FAILED: {midi_file}: {e}")
        failed.append((midi_file, str(e)))

if failed:
    print(f"\n{len(failed)} song(s) failed:")
    for name, err in failed:
        print(f"  {name}: {err}")
```

---

## Code Examples

Verified patterns from local testing:

### Complete FluidSynth Render and Convert Pipeline

```python
# Source: verified locally (FluidSynth 2.4.5, ffmpeg 7.1.1)
import subprocess, tempfile, os

def render_group(midi_path, mp3_path, soundfont_path, duration=60):
    """Render one group MIDI to a trimmed 192kbps MP3."""
    with tempfile.TemporaryDirectory(prefix="musicsplit_") as tmpdir:
        wav_path = os.path.join(tmpdir, "render.wav")

        # Step 1: MIDI -> WAV
        subprocess.run([
            "fluidsynth", "-ni",
            "-F", wav_path, "-T", "wav", "-r", "44100",
            soundfont_path, midi_path,
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Step 2: WAV -> MP3 (trim to duration)
        subprocess.run([
            "ffmpeg", "-y", "-i", wav_path,
            "-t", str(duration),
            "-ar", "44100", "-ac", "2", "-b:a", "192k",
            mp3_path,
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
```

### Cumulative Layer from Multiple WAV Files

```python
# Source: verified locally (ffmpeg 7.1.1 amix filter)
def render_cumulative_layer(wav_paths, mp3_path, duration=60):
    """Mix multiple WAV files into one cumulative layer MP3."""
    n = len(wav_paths)
    inputs = []
    for p in wav_paths:
        inputs += ["-i", p]

    subprocess.run([
        "ffmpeg", "-y", *inputs,
        "-t", str(duration),
        "-filter_complex", f"amix=inputs={n}:duration=longest:normalize=0",
        "-ar", "44100", "-ac", "2", "-b:a", "192k",
        mp3_path,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
```

### Main Build Loop Structure

```python
# Source: Music01s/build.py pattern, adapted
import os, glob

MIDI_DIR = "midi"
AUDIO_DIR = "audio"
SONGS_JS  = "songs.js"

def main():
    soundfont = find_soundfont()  # raises SystemExit if not found

    os.makedirs(AUDIO_DIR, exist_ok=True)

    midi_files = sorted(
        f for f in os.listdir(MIDI_DIR)
        if f.lower().endswith('.mid') or f.lower().endswith('.midi')
    )

    songs = []
    failed = []

    for midi_filename in midi_files:
        midi_path = os.path.join(MIDI_DIR, midi_filename)
        song_id = make_song_id(midi_filename)
        out_dir = os.path.join(AUDIO_DIR, song_id)
        os.makedirs(out_dir, exist_ok=True)

        print(f"Processing: {midi_filename}")

        try:
            entry = process_song(midi_path, midi_filename, song_id, out_dir, soundfont)
            songs.append(entry)
            print(f"  Done ({len(entry['layers'])} layers)")
        except Exception as e:
            print(f"  FAILED: {e}")
            failed.append((midi_filename, str(e)))

    write_manifest(songs, SONGS_JS)
    print(f"\n{len(songs)} song(s) written to {SONGS_JS}")

    if failed:
        print(f"\n{len(failed)} failed:")
        for name, err in failed:
            print(f"  {name}: {err}")

if __name__ == "__main__":
    main()
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| MIDI playback via Tone.js oscillators | Pre-rendered MP3 via FluidSynth+soundfont | Phase 2 (this phase) | Real instrument timbres; no synthesis in browser |
| Flat `midi/index.json` list | `songs.js` with full manifest | Phase 2 (this phase) | Game knows group names, file paths, which groups are present |
| Single MIDI playback | Per-group + cumulative MP3s | Phase 2 (this phase) | Enables layer-reveal game mechanic |

**Deprecated/outdated:**
- `generate.py`: will be replaced by `build.py`; old script only generates `midi/index.json` flat list
- `midi/index.json`: replaced by `songs.js` manifest
- Tone.js oscillator synthesis (`player.js`): removed in Phase 3 (CLEAN-01)

---

## Open Questions

1. **Manifest format conflict: songs.js vs songs.json**
   - What we know: CONTEXT.md says `songs.js` (locked decision); STATE.md says `songs.json + fetch()` (project-level note)
   - What's unclear: Whether the Phase 3 game code can load a `<script src="songs.js">` global safely, or whether ES module deferred loading will require fetch()
   - Recommendation: Build `songs.js` as CONTEXT.md specifies. Flag for Phase 3 planner that if they use `type="module"` or deferred loading, they'll need to switch to `songs.json + fetch()`.

2. **Soundfont for dev machine**
   - What we know: FluidR3_GM.sf2 exists at a non-standard path on this machine. The `~/.fluidsynth/default_sound_font.sf2` symlink is broken.
   - What's unclear: Should the README document FluidR3_GM as the alternative to GeneralUser GS, or just GeneralUser GS?
   - Recommendation: Document both. FluidR3_GM is higher quality (~142MB); GeneralUser GS is lighter (~30MB). Both produce good results.

3. **Per-group MP3 for truly empty groups**
   - What we know: FluidSynth renders silence correctly (verified: -90.3 dB). A `present: false` group still gets a file.
   - What's unclear: Does the explorer mode (Phase 4) need a silent MP3 for unplayed groups, or should the file be omitted?
   - Recommendation: Always write the per-group MP3 (even if silent). Keeps the file manifest consistent. The game uses `present` flag to decide whether to show/use the group.

---

## Sources

### Primary (HIGH confidence)
- Local verification: FluidSynth 2.4.5 CLI tested against `MusicSplit/midi/test.mid`
- Local verification: mido 1.3.3 MIDI filtering tested and files written
- Local verification: ffmpeg 7.1.1 WAV→MP3 and amix filter tested
- `Music01s/build.py` — exact pattern to follow for scan→process→manifest
- `MusicSplit/utils.js:getRole()` — authoritative source for GM program→group mapping
- `MusicSplit/details_midi.py` — established pretty_midi usage pattern

### Secondary (MEDIUM confidence)
- pretty_midi 0.2.11 documentation (installed locally, API verified via test script)
- FluidSynth 2.x `--help` output (read directly from installed binary)

### Tertiary (LOW confidence)
- GeneralUser GS download URL: https://schristiancollins.com/generaluser.php — not fetched, documented from memory; verify before writing README

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all tools installed and verified locally with the actual project MIDI file
- Architecture: HIGH — patterns tested end-to-end (MIDI → WAV → MP3 with real output)
- Pitfalls: HIGH for tools-specific (verified); MEDIUM for MIDI edge cases (extrapolated from test file)

**Research date:** 2026-03-01
**Valid until:** 2026-09-01 (stable tools; FluidSynth and ffmpeg APIs very stable)
