# Phase 2: Build Pipeline - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Python build script that converts MIDI files in `midi/` into per-instrument-group MP3s using FluidSynth + a soundfont, then generates a song manifest for the game. No game UI changes in this phase — only the build pipeline and its outputs.

</domain>

<decisions>
## Implementation Decisions

### MIDI File Sourcing
- Input files live in `MusicSplit/midi/` (current location)
- Naming convention: `Artist - Title.mid` — script parses title/artist from filename, same pattern as `Music01s/build.py`
- Files downloaded from free MIDI sites — script should be resilient to varied MIDI quality/format
- Small-to-medium collection (5-50 songs)

### Instrument Grouping
- 6 groups, derived from existing `utils.js` `getRole()` mapping, with merges:
  1. **Drums + Percussion** — MIDI channel 10 (is_drum) + programs 47, 55
  2. **Bass** — programs 32-39
  3. **Brass/Wind** — programs 56-71
  4. **Keys/Piano + Synth** — programs 0-23 + 80-95
  5. **Guitar** — programs 24-31
  6. **Ensemble + Choir + Strings** — programs 40-54
- "Other" instruments (unmapped programs) → merge into Keys/Piano group as fallback
- This is the layer reveal order in the game (group 1 first, group 6 last)

### Audio Rendering
- Render cumulative MP3s: layer-1 = drums only, layer-2 = drums+bass, layer-3 = drums+bass+brass, etc.
- Also render separate per-group MP3s (needed for explorer mode in Phase 4)
- All MP3s for a given song must have the same total duration (pad shorter groups)
- Trim audio to ~60 seconds — enough to guess, keeps file sizes manageable
- MP3 quality: 192kbps (matches Music01s)
- FluidSynth renders to WAV first, then ffmpeg converts to MP3 (ffmpeg already established in project)

### Empty Group Handling
- If a MIDI file has no tracks for a group, skip that layer in the cumulative rendering
- Manifest flags which groups are present so the game can adjust round count per song

### Manifest Format
- Output: `songs.js` — `const SONGS = [...]` (matches Music01s pattern, simple script-tag loading)
- Each song entry: `{ title, artist, id, groups: [{ name, file, present }], layers: [file1, file2, ...] }`
- `groups` array: 6 entries, one per group, with `present: true/false` and path to individual group MP3
- `layers` array: cumulative MP3 paths in reveal order (only for present groups)

### Soundfont Setup
- Recommended: GeneralUser GS (~30MB .sf2 file)
- Soundfont file is NOT committed to repo (too large) — goes in .gitignore
- Build script checks known locations, then falls back to a clear error message with download instructions
- README documents setup: `brew install fluid-synth` + soundfont download link

### Claude's Discretion
- Exact FluidSynth CLI invocation flags
- Temp file handling during rendering
- Whether to render MIDI per-track or per-channel
- Error handling for malformed MIDI files
- Progress reporting format (print statements vs progress bar)

</decisions>

<specifics>
## Specific Ideas

- Follow `Music01s/build.py` pattern closely: scan input dir → process each file → generate manifest
- The existing `details_midi.py` already shows `pretty_midi` usage with `instrument.is_drum` and `instrument.program` — reuse that pattern for group assignment
- Output directory: `MusicSplit/audio/<song-id>/` with files like `group-1-drums.mp3`, `group-2-bass.mp3`, `layer-1.mp3`, `layer-2.mp3`, etc.
- Song ID derived from sanitized filename (lowercase, hyphens)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `utils.js:getRole()` — exact GM program-to-group mapping, needs Python translation + 3 merges
- `details_midi.py` — `pretty_midi` usage pattern (PrettyMIDI, instrument.is_drum, instrument.program)
- `Music01s/build.py` — canonical build script pattern (scan → process → generate manifest)
- `generate.py` — will be replaced by new build.py

### Established Patterns
- Build scripts use `subprocess.run()` for ffmpeg calls with `stdout=DEVNULL, stderr=DEVNULL`
- Manifest format: `const SONGS = [...]` in a .js file loaded via script tag
- File naming: parsed from `"Artist - Title"` pattern in filename

### Integration Points
- Output MP3s go in `MusicSplit/audio/` (new directory)
- `songs.js` replaces current `midi/index.json` as the data source for the game
- Soundfont file location needs documentation (README or setup script)
- `.gitignore` needs `*.sf2` entry

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-build-pipeline*
*Context gathered: 2026-03-01*
