# Stack Research

**Domain:** MIDI-to-per-instrument-group MP3 rendering pipeline (Python build script)
**Researched:** 2026-03-01
**Confidence:** MEDIUM — FluidSynth/pretty_midi are well-established tools confirmed by training knowledge and codebase evidence (pretty_midi already imported in details_midi.py). Version numbers sourced from training data (cutoff Aug 2025); verify on PyPI before pinning.

---

## Executive Note

This is an **additive** milestone. The existing Python scripts (`generate.py`, `details_midi.py`, `build.py`) and the frontend (vanilla JS, Web Audio API) are not replaced. The only new component is a Python build script that renders MIDI files to per-instrument-group MP3s. The frontend game UI then plays those pre-rendered MP3s via `<audio>` tags — replacing the current Web Audio API oscillator synthesis with real soundfont audio.

**Pipeline in one sentence:** MIDI file → pretty_midi splits tracks by GM program group → FluidSynth renders each group to WAV → ffmpeg encodes WAV to MP3 → MP3s committed to repo for GitHub Pages serving.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `pretty_midi` | 0.2.10 (latest as of Aug 2025) | MIDI parsing, per-track manipulation, writing per-group MIDI files | Already used in `details_midi.py` — zero new dependency cost. Provides clean Python objects for instruments, notes, program numbers. Native support for drum tracks (`is_drum` flag). The `PrettyMIDI.write()` method is what enables writing per-group temp MIDI files. |
| `FluidSynth` | 2.3.x (system package) | MIDI-to-WAV rendering using a soundfont | The canonical open-source General MIDI synthesizer. Renders MIDI to audio via a soundfont file. Available as a system package (`brew install fluidsynth` / `apt install fluidsynth`). Does NOT install via pip — it is a C binary. |
| `midi2audio` | 0.1.1 | Python wrapper that calls FluidSynth CLI | Eliminates `subprocess` boilerplate for FluidSynth calls. One-liner: `FluidSynth().midi_to_audio('in.mid', 'out.wav')`. Thin and stable — has not needed updates since FluidSynth's CLI interface is stable. |
| `ffmpeg` (CLI) | 6.x or 7.x | WAV-to-MP3 encoding, bitrate control | Already used in `Music01s/build.py` via `subprocess.run(["ffmpeg", ...])`. Reuse the same pattern. No new dependency. Produces the final MP3 files that GitHub Pages serves. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `midiutil` | 1.2.1 | Write MIDI files programmatically | Only if per-group MIDI files need to be constructed from scratch. If pretty_midi's `PrettyMIDI.write()` is sufficient (it should be), skip this entirely. **Tentatively: do not add.** |
| `numpy` | 1.x / 2.x | Array operations on audio data | Only if WAV post-processing (normalization, silence trimming) is needed. FluidSynth output is usually already normalized. pretty_midi already depends on numpy — it will be present transitively. Do not add explicitly unless needed. |
| `soundfile` | 0.12.x | Read/write WAV files in Python | Only if audio inspection or normalization is added to the pipeline. ffmpeg already handles the WAV-to-MP3 step. **Do not add for the initial pipeline.** |

### Soundfont Files (Data Assets — Not Python Libraries)

| Soundfont | Size | Quality | Why |
|-----------|------|---------|-----|
| **GeneralUser GS** | ~30 MB | High — clean General MIDI | Best balance of size and quality for General MIDI. All 128 GM programs covered. Actively maintained by S. Christian Collins. Download from the official site (not pip). Recommended. |
| FluidR3_GM.sf2 | ~140 MB | Very high — reference quality | Ships with `fluid-soundfont-gm` on Ubuntu/Debian (`apt install fluid-soundfont-gm`). Excellent quality but 140 MB is large to commit to the repo. Use if quality is the priority. |
| TimGM6mb.sf2 | ~6 MB | Acceptable | Ships with some FluidSynth packages. Very small — acceptable if file size is a hard constraint. Noticeably lower quality on strings and choir. |

**Recommendation: GeneralUser GS.** ~30 MB committed to `MusicSplit/soundfonts/` is reasonable. It is NOT committed to the GitHub Pages output — it only lives in the repo as a build asset used locally.

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `brew install fluidsynth` (macOS) | Install FluidSynth system binary | Required on developer machines. Not pip-installable. Document in README. |
| `apt install fluidsynth` (Linux/CI) | Same, for Linux environments | If a GitHub Actions CI pipeline is added later. |
| `pip install pretty_midi midi2audio` | Install Python wrappers | Pin versions in `requirements.txt` in `MusicSplit/`. |
| `python -m pip install -r requirements.txt` | Reproduce environment | Standard Python practice. Add `MusicSplit/requirements.txt`. |

---

## Installation

```bash
# System dependency (macOS) — must be installed before pip packages
brew install fluidsynth

# Python packages
pip install pretty_midi==0.2.10 midi2audio==0.1.1

# Download soundfont (one-time, manual step)
# GeneralUser GS: https://schristiancollins.com/generaluser.php
# Place at: MusicSplit/soundfonts/GeneralUser.sf2
```

```
# MusicSplit/requirements.txt
pretty_midi==0.2.10
midi2audio==0.1.1
```

---

## How This Integrates with Existing Scripts

The new build script (`MusicSplit/build.py`) follows the same pattern as `Music01s/build.py`:

```python
# Pattern already established in Music01s/build.py:
subprocess.run(["ffmpeg", "-y", "-i", src, ...], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# New build.py adds:
import pretty_midi
from midi2audio import FluidSynth

def render_group(midi_obj, track_indices, out_path, soundfont):
    # 1. Write per-group MIDI to temp file
    group_midi = pretty_midi.PrettyMIDI()
    for i in track_indices:
        group_midi.instruments.append(midi_obj.instruments[i])
    group_midi.write("/tmp/group.mid")

    # 2. Render to WAV via FluidSynth
    FluidSynth(soundfont).midi_to_audio("/tmp/group.mid", "/tmp/group.wav")

    # 3. Encode to MP3 via ffmpeg (existing pattern)
    subprocess.run(["ffmpeg", "-y", "-i", "/tmp/group.wav",
                    "-ar", "44100", "-ac", "2", "-b:a", "192k",
                    out_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```

The instrument grouping logic already exists in `MusicSplit/utils.js` (General MIDI program → role mapping). The new Python build script must replicate that mapping — use `pretty_midi`'s `instrument.program` and `instrument.is_drum` to reproduce the same 6-group categorization (`Drums+Perc`, `Bass`, `Brass/Wind`, `Keys/Piano+Synth`, `Guitar`, `Ensemble+Choir+Strings`).

The output structure for each MIDI file `song.mid` would be:
```
MusicSplit/audio/song/drums.mp3
MusicSplit/audio/song/bass.mp3
MusicSplit/audio/song/brass_wind.mp3
MusicSplit/audio/song/keys_piano.mp3
MusicSplit/audio/song/guitar.mp3
MusicSplit/audio/song/ensemble.mp3
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|------------------------|
| `midi2audio` wrapper | Direct `subprocess.run(["fluidsynth", ...])` | When you need non-default FluidSynth CLI flags (e.g. custom sample rate, gain). For this project, defaults are fine — use `midi2audio`. |
| `pretty_midi` for MIDI parsing | `mido` library | Use `mido` when you need raw byte-level MIDI manipulation. `pretty_midi` is higher-level and already in the project. |
| `pretty_midi` for MIDI parsing | `music21` library | `music21` is a full music analysis suite (~10 MB install, multiple sub-dependencies). Overkill for splitting tracks. |
| `ffmpeg` for WAV→MP3 | `pydub` library | Use `pydub` if you need Python-native audio manipulation (trim, normalize). For a pure encode step, `ffmpeg` CLI is already present and sufficient. |
| GeneralUser GS soundfont | Musescore General.sf3 (SF3 compressed) | SF3 is smaller but FluidSynth support varies by version. SF2 is universally supported. Stick with SF2. |
| Per-group MIDI → FluidSynth | Real stem separation (Demucs, Spleeter) | Out of scope per PROJECT.md. Neural stem separation requires GPU, produces imperfect results, and is overkill for MIDI-sourced songs. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `pyfluidsynth` (Python bindings) | Direct C bindings — more complex setup, version-sensitive, harder to install cross-platform. Overkill when all we need is "render this MIDI to a WAV." | `midi2audio` (wraps FluidSynth CLI — simpler, more portable) |
| `music21` | Heavy dependency (~25 MB, pulls in matplotlib and more). Designed for music theory analysis, not audio rendering. | `pretty_midi` (already in project, purpose-built for MIDI manipulation) |
| `pydub` | Adds an extra dependency when ffmpeg is already available and sufficient for WAV→MP3 encoding. | `subprocess.run(["ffmpeg", ...])` (already established pattern in build.py) |
| `sounddevice` / `pygame.midi` | Real-time playback libraries — not for offline rendering pipelines. | FluidSynth (renders to file, not real-time) |
| Demucs / Spleeter (ML stem separation) | Requires PyTorch (~2 GB), GPU for practical speed, and produces imperfect results on songs that already have MIDI stems. Explicitly out of scope in PROJECT.md. | FluidSynth + soundfonts (deterministic, fast, produces perfect per-instrument isolation from MIDI) |
| Committing WAV files to the repo | WAV is uncompressed — a single song's 6 instrument groups would be ~50–100 MB. GitHub Pages has a 1 GB soft limit. | Encode to MP3 (192k) via ffmpeg as the final output; delete temp WAVs. |
| Committing the soundfont to the `docs/` or output directory | The soundfont is a LOCAL build tool — it must not be served on GitHub Pages. | Keep soundfont in `MusicSplit/soundfonts/` and add `*.sf2` to `.gitignore` OR document that it is a build-only asset not deployed. |

---

## Stack Patterns by Variant

**If a MIDI file has no tracks in a group (e.g. no guitar tracks):**
- Skip rendering that group entirely — do not produce an empty MP3.
- The game UI must handle missing groups gracefully (skip that round).

**If FluidSynth is not installed (developer machine setup):**
- The script should detect the missing binary and print a clear error: `"FluidSynth not found. Install with: brew install fluidsynth"`.
- Do NOT silently produce empty files.

**If a song's per-group MP3s already exist and the MIDI has not changed:**
- Skip re-rendering (check mtime or existence). Mirrors how `Music01s/build.py` skips nothing (always rebuilds) — but for MusicSplit re-rendering is expensive (FluidSynth is slow), so a skip-if-exists check is worthwhile.

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|----------------|-------|
| `pretty_midi==0.2.10` | Python 3.8+ | Depends on `numpy`, `mido`, `six`. All stable. |
| `midi2audio==0.1.1` | FluidSynth 1.x and 2.x CLI | The wrapper calls `fluidsynth` binary directly; both major versions use the same CLI flags for basic rendering. |
| `FluidSynth 2.3.x` | GeneralUser GS SF2, FluidR3_GM SF2, TimGM6mb SF2 | All major SF2 soundfonts work with FluidSynth 2.x. SF3 format requires FluidSynth 1.1.6+. |
| `ffmpeg 6.x / 7.x` | WAV input, MP3 output via libmp3lame | The same flags used in `Music01s/build.py` (`-ar 44100 -ac 2 -b:a 192k`) work identically. |
| Python 3.10+ | All above packages | Recommended minimum. macOS 13+ ships Python 3.x; Linux CI defaults to 3.10+. |

---

## Sources

- Codebase audit (HIGH confidence) — `MusicSplit/details_midi.py` confirms `pretty_midi` is already used; `Music01s/build.py` confirms `ffmpeg` via `subprocess` is the established pattern; `MusicSplit/utils.js` defines the 6-group GM program mapping that Python must replicate.
- Training knowledge for `pretty_midi`, `midi2audio`, `FluidSynth` (MEDIUM confidence — these are stable, long-established tools; version numbers reflect Aug 2025 training cutoff; verify `pretty_midi` and `midi2audio` on PyPI before pinning).
- `FluidSynth` project (MEDIUM confidence — well-established C synthesizer, version 2.3.x is current as of Aug 2025; verify at https://www.fluidsynth.org/).
- GeneralUser GS soundfont (MEDIUM confidence — active project by S. Christian Collins; verify current version at https://schristiancollins.com/generaluser.php).

---

*Stack research for: MusicSplit — MIDI-to-per-instrument-group MP3 rendering pipeline*
*Researched: 2026-03-01*
