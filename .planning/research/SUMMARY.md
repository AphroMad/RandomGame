# Project Research Summary

**Project:** MusicSplit v1.1 — Instrument-Layering Music Guessing Game
**Domain:** MIDI-to-MP3 build pipeline + cumulative audio guessing game (static, GitHub Pages)
**Researched:** 2026-03-01
**Confidence:** MEDIUM-HIGH — stack and architecture grounded in direct codebase audit; game mechanic patterns from training knowledge of bandle.app; audio API behavior from Web Audio spec

## Executive Summary

MusicSplit v1.1 transforms an existing MIDI instrument visualizer into a bandle.app-style guessing game. The player hears only the first instrument layer (Drums), guesses the song, and on each failure receives a cumulative new layer (Drums + Bass, then + Brass, etc.) over 6 rounds. The foundational requirement that makes everything else possible is a Python build pipeline: MIDI files are parsed by `pretty_midi`, split into 6 instrument-group MIDI files, rendered to WAV via FluidSynth + a General MIDI soundfont, then encoded to MP3 via ffmpeg. The existing oscillator synthesis is entirely replaced — it produces tones players cannot recognize, making the game unplayable without real audio.

The recommended implementation reuses heavily from the existing Music01s codebase. The guess/skip flow, autocomplete, attempt rows, win/lose states, and Next Song button are all direct ports from Music01s. The key difference is that instead of one audio element pointing to a clip, the game manages up to 6 `AudioBufferSourceNode` objects (one per instrument group), all driven from the same `AudioContext` clock for sample-accurate synchronization. Using plain `HTMLAudioElement` for multi-track playback is explicitly identified as a critical pitfall: multiple audio elements drift apart audibly within seconds, making the layered mechanic feel broken.

The biggest risks cluster around two areas: (1) the build pipeline — drum channel assignment, per-group MIDI file creation, soundfont quality, and duration normalization across groups all require careful implementation before any UI work; and (2) the game runtime — audio synchronization using Web Audio API, mobile AudioContext unlock behavior, and dynamic round rendering (as opposed to hardcoded 6-row HTML) are the highest-risk UI decisions. Build the pipeline first, validate audio output quality per group, then build the game UI against real MP3 files.

---

## Key Findings

### Recommended Stack

The stack is almost entirely zero-new-dependency: `pretty_midi` (already imported in `details_midi.py`), `ffmpeg` (already used in `Music01s/build.py`), and FluidSynth (a system CLI binary, not pip-installable). The only new Python dependency is `midi2audio==0.1.1`, a thin wrapper that eliminates FluidSynth subprocess boilerplate. The soundfont is a data asset — GeneralUser GS (~30 MB) is recommended for its full GM coverage and consistent quality across all 6 instrument groups. The soundfont is NOT committed to the repo; it lives in `MusicSplit/soundfonts/` and is a build-only local asset.

**Core technologies:**
- `pretty_midi 0.2.10`: Parse MIDI tracks, split by group, write per-group `.mid` files — already in the project
- `FluidSynth 2.3.x` (CLI): Render group MIDI + soundfont to WAV — installed via `brew install fluidsynth`
- `midi2audio 0.1.1`: Python wrapper for FluidSynth CLI — eliminates subprocess boilerplate
- `ffmpeg 6.x/7.x` (CLI): WAV to MP3 at 192k — already used in Music01s build pipeline
- `GeneralUser GS.sf2`: Full General MIDI soundfont — downloaded separately, never committed to repo

### Expected Features

The game mechanic is well-defined and directly mirrors bandle.app. Research identified a clear separation between P1 launch requirements, P2 polish, and features to defer.

**Must have (table stakes — P1):**
- Pre-rendered per-group MP3 audio pipeline — without real soundfont audio the game is unplayable
- Cumulative audio layer playback via Web Audio API, not HTMLAudioElement — core mechanic
- 6-round guess/skip progression with fixed layer order: Drums, Bass, Brass, Keys, Guitar, Ensemble
- Autocomplete guess input against songs.json manifest
- Attempt rows with correct/wrong/skipped/revealed states — reuse Music01s CSS
- Layer name indicator showing which instrument groups are currently audible
- Win/Lose end state with song reveal and Next Song button

**Should have (polish — P2, add after core loop validated):**
- Layer name in attempt row text (e.g. "Skipped — Drums + Bass")
- Visual layer badge strip below audio controls
- Timeline repurposed as 6-segment round indicator (reuse Music01s `.tl-track` CSS)

**Defer (v2+):**
- Mobile responsive layout (inherited debt from v1.0)
- Keyboard navigation (spacebar/enter shortcuts)
- Score persistence or leaderboard (explicitly out of scope in PROJECT.md)

### Architecture Approach

The system has two distinct phases: a local Python build pipeline that runs before deployment, and a browser runtime that plays the pre-rendered results. `build.py` reads MIDI files, groups tracks by GM program range using a canonical 6-group mapping, writes per-group MIDI files, renders them through FluidSynth to WAV, converts via ffmpeg to MP3, and generates `songs.json`. The browser loads `songs.json` via `fetch()`, creates one `AudioBufferSourceNode` per group MP3, and starts all active nodes from the same `AudioContext.currentTime` on each play event. State management is minimal: a round counter and an array of decoded `AudioBuffer` objects.

**Major components:**
1. `MusicSplit/build.py` — MIDI-to-per-group-MP3 render pipeline; replaces `generate.py`; generates `songs.json`
2. `MusicSplit/audio/<song-id>/group-N-<name>.mp3` — pre-rendered group audio; committed to repo; approximately 1-3 MB each
3. `MusicSplit/songs.json` — machine-readable song manifest with group paths; generated by build.py
4. `MusicSplit/index.html` (rewritten) — game UI; uses Music01s flow; new Web Audio engine replaces oscillator player
5. New audio engine (inline or separate file) — `AudioContext` + `AudioBufferSourceNode` per group; no Tone.js

**Files to delete after pipeline is confirmed working:** `generate.py`, `player.js`, `utils.js`, `midi/index.json`

### Critical Pitfalls

1. **Multiple HTMLAudioElement drift** — Never use `<audio>` elements for multi-layer sync. Use Web Audio API `AudioBufferSourceNode` driven from one `AudioContext` clock. Audible drift appears within 10-30 seconds with `HTMLAudioElement`. This is the single highest-impact pitfall with the highest recovery cost.

2. **MIDI Channel 10 drum routing** — FluidSynth unconditionally treats channel 10 as percussion. Always filter tracks using `pretty_midi`'s `instrument.is_drum` flag; never use FluidSynth channel-muting flags. Write a filtered `.mid` per group; never pass the full MIDI with channel flags.

3. **Soundfont quality mismatch** — The default FluidR3_GM soundfont (from apt/brew) renders poor guitar and brass. Test the chosen soundfont on all 6 group types before implementing the pipeline. Recommend GeneralUser GS.

4. **Empty groups produce silent rounds** — Many pop MIDIs have no brass or no strings. The pipeline must detect zero-note groups, flag them in the manifest, and the game must skip those rounds dynamically. Hardcoding 6 rounds always is unacceptable.

5. **songs.js global vs songs.json fetch** — A `const SONGS = [...]` global via `<script>` tag conflicts with ES module deferred loading needed for `async/await`. Use `songs.json` + `fetch()` from the start. This decision must be made before UI coding begins.

6. **Tone.js conflict with new audio engine** — The existing `player.js` uses Tone.js Transport which can suspend the shared `AudioContext`. The new game must NOT import `player.js` or Tone.js. Write a fresh audio module from scratch.

7. **Group duration mismatch** — FluidSynth renders each group independently; release tails differ by instrument type. Normalize all group MP3s for a song to the same duration using `ffmpeg -t {max_duration}` after rendering.

---

## Implications for Roadmap

Research shows a strict dependency chain: audio pipeline must exist before game UI is built, and the manifest format must be decided before either the pipeline output or the game input is coded. The suggested phase structure follows this dependency order.

### Phase 1: Build Pipeline — Group Rendering

**Rationale:** This is the foundational blocker. Nothing else in the project can be validated without real per-group MP3 audio. Oscillator synthesis cannot substitute for testing "does this sound like the song." The pipeline is also the most technically novel part — it involves FluidSynth behavior, drum channel routing, soundfont selection, and duration normalization, all of which need verification before downstream work begins.

**Delivers:** Working `build.py` that takes `midi/*.mid` files and produces `audio/<song-id>/group-N-<name>.mp3` for all 6 groups. Each group file contains only its instrument group, all groups are the same duration, no group is silence-only.

**Addresses:** Pre-rendered MP3 pipeline (P1), `songs.json` manifest format decision

**Avoids:** Drum channel 10 mismatch, per-group MIDI channel reassignment, soundfont quality failure, empty-group silence, duration mismatch between groups

### Phase 2: Song Manifest (songs.json)

**Rationale:** Once pipeline output is verified, the manifest format locks the contract between `build.py` and the game UI. This must be finalized before game UI coding starts, or the UI will need to be reworked when manifest format changes. The manifest must record: song ID, title, artist, per-group file paths, which groups are present (non-empty), and canonical song duration.

**Delivers:** `build.py` writes `songs.json` with full song and group metadata. Format: `[{ id, title, artist, duration, groups: [{ name, file, hasAudio }] }]`.

**Uses:** `songs.json` + `fetch()` pattern — not `songs.js` global, which is incompatible with ES module deferred loading

**Avoids:** songs.js global incompatibility with module loading

### Phase 3: Game UI — Core Game Loop

**Rationale:** With real audio and a manifest in place, the game UI can be built against validated data. The core loop (audio playback, guess/skip, round progression, win/lose) is the main deliverable. Music01s patterns provide approximately 80% of the JS needed; the new audio engine and dynamic round rendering are the novel parts.

**Delivers:** Playable game — audio plays cumulatively per round, guess/skip advances layers, correct/wrong/skipped rows update, win/lose state shown, Next Song resets the game.

**Addresses:** All P1 features — cumulative audio playback, 6-round progression, autocomplete, attempt rows, win/lose state, Next Song

**Avoids:** HTMLAudioElement drift (use Web Audio API), Tone.js conflict (write new audio module), hardcoded 6-round HTML rows (generate dynamically from manifest data), mobile AudioContext unlock failure

### Phase 4: UI Polish and Cleanup

**Rationale:** Once the core loop is confirmed to work with real audio, polish features and file cleanup can proceed without risk of blocking the core mechanic.

**Delivers:** Layer name in attempt row text, visual layer badge strip, round indicator (timeline as 6 segments), deletion of `generate.py`, `player.js`, `utils.js`, `midi/index.json`.

**Addresses:** P2 features — layer name in rows, badge strip, timeline round indicator

**Avoids:** Leaving unused Tone.js and player.js imports in the codebase

### Phase Ordering Rationale

- Pipeline before UI is a hard dependency: the game cannot be tested meaningfully without real audio.
- Manifest format before both: `build.py` output and game `fetch()` input must agree on the schema; deciding it once in Phase 2 prevents rework in both directions.
- Dynamic round rendering (not hardcoded HTML) is coded into Phase 3 by design: the manifest provides the actual group list per song, so the UI generates rows from data, not from hardcoded IDs.
- Polish and cleanup are deferred to Phase 4 explicitly: deleting legacy files before Phase 3 is confirmed working removes the safety net.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1 (Pipeline):** FluidSynth CLI flags for the installed version should be verified with `fluidsynth --help` before implementation; `pretty_midi.PrettyMIDI.write()` behavior for filtered instrument sets, particularly `is_drum` preservation, warrants a quick API check before the full pipeline is coded.
- **Phase 3 (Game UI):** Web Audio API multi-buffer synchronized start pattern should be confirmed against MDN before implementation; iOS Safari `AudioContext` autoplay unlock behavior should be verified on a real device, not Chrome DevTools simulation — Safari restrictions change between OS versions.

Phases with standard patterns (skip research-phase):
- **Phase 2 (Manifest):** JSON schema design with no external dependencies. No research needed.
- **Phase 4 (Polish):** Pure CSS/DOM manipulation. Established patterns. No research needed.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | `pretty_midi` and `midi2audio` are confirmed tools; versions reflect Aug 2025 training cutoff — verify on PyPI before pinning. `ffmpeg` and FluidSynth confirmed present via direct codebase audit. |
| Features | MEDIUM-HIGH | Core game mechanic based on training knowledge of bandle.app (cited in MusicSplit source). Music01s reuse patterns based on direct code reading (HIGH). Competitor feature details MEDIUM. |
| Architecture | HIGH | Based entirely on direct codebase audit of Music01s and MusicSplit source files. HTML5 Audio API patterns are well-established spec-level behavior. |
| Pitfalls | HIGH | Grounded in codebase inspection, General MIDI spec (channel 10 rule), and Web Audio API specification. FluidSynth rendering behavior from training knowledge confirmed by spec. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Exact FluidSynth CLI flags for rendering:** `fluidsynth -ni <sf> <mid> -F <wav> -r 44100` is the expected form but should be verified with `fluidsynth --help` on the actual installed version before the pipeline is coded. Flags differ slightly between FluidSynth 1.x and 2.x.
- **pretty_midi channel 9 preservation on write:** The drum channel preservation behavior when copying instruments into a new `PrettyMIDI` object should be tested with a small script before the full pipeline is written. If `is_drum` is not preserved on copy, an explicit assertion must be added.
- **Soundfont availability and license:** GeneralUser GS is recommended but must be manually downloaded. Verify current version URL at https://schristiancollins.com/generaluser.php; license permits use in games.
- **Repo size budget:** At 192k MP3, a 3-minute song produces approximately 26 MB of group files. The current MIDI library size is unknown — if more than 10-15 songs are planned, 128k bitrate or clip trimming (render only first 60 seconds) may be needed. Decide before running the full pipeline on the whole library.
- **iOS Safari AudioContext policy:** Safari's autoplay restrictions evolve with OS versions. The research identifies the correct pattern (create AudioContext in user gesture, `await context.resume()` before `.start()`) but the specific behavior should be tested on a real device.

---

## Sources

### Primary (HIGH confidence)
- Direct codebase audit — `MusicSplit/index.html`, `MusicSplit/player.js`, `MusicSplit/utils.js`, `MusicSplit/details_midi.py`, `MusicSplit/generate.py`, `Music01s/build.py`, `Music01s/index.html`, `Music01s/songs.js` (2026-03-01)
- `PROJECT.md` — layer order, pipeline scope, anti-features explicitly excluded
- `STATE.md` — v1.1 active milestone, decisions logged
- General MIDI specification — Channel 10 percussion routing, GM program number ranges
- Web Audio API specification — `AudioContext`, `AudioBufferSourceNode`, mobile autoplay policy

### Secondary (MEDIUM confidence)
- Training knowledge: `pretty_midi` API (`instrument.is_drum`, `PrettyMIDI.write`), `midi2audio` wrapper behavior, FluidSynth 2.3.x CLI flags, GeneralUser GS soundfont quality — stable and long-established tools; verify versions on PyPI and official sites before pinning
- Training knowledge: bandle.app game mechanics — cumulative layer reveal over 6 rounds with autocomplete; cited in MusicSplit source as direct inspiration
- FluidSynth project (https://www.fluidsynth.org/) — version 2.3.x current as of Aug 2025 training cutoff; verify current version before installing

### Tertiary (LOW confidence)
- iOS Safari specific AudioContext autoplay behavior — documented restriction pattern is stable, but exact behavior in newer Safari versions should be validated on a real device before shipping
- GitHub Pages repo size limits — 1 GB soft limit widely cited; verify if repo audio assets grow beyond 10 songs

---
*Research completed: 2026-03-01*
*Ready for roadmap: yes*
