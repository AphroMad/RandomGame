# Pitfalls Research

**Domain:** MIDI-to-MP3 build pipeline + cumulative audio guessing game (MusicSplit v1.1)
**Researched:** 2026-03-01
**Confidence:** HIGH — all claims grounded in codebase inspection, established FluidSynth behavior, and Web Audio API specifications

---

## Critical Pitfalls

### Pitfall 1: MIDI Channel 10 Is Always Drums — Group Assignment Goes Silent

**What goes wrong:**
FluidSynth maps General MIDI channel 10 (index 9 in zero-based) to percussion unconditionally, regardless of what program number is assigned to it. When you try to mute channel 10 for a "no drums" render, you must mute it specifically by channel number — not by program number. Conversely, when rendering the drums-only group, if you mute by program instead of channel, any non-percussion tracks accidentally on channel 10 in malformed MIDIs get treated as drums and bleed into the wrong group. This causes either silence in the drums group or unexpected percussion sounds in other groups.

**Why it happens:**
The existing `getRole()` function in `utils.js` correctly uses `isPercussion` (a boolean from the MIDI parser), which maps to the channel 10 flag. But FluidSynth's command-line API operates at the channel level, not the track level. Developers confuse the MIDI parser's "instrument.number" (program) with the channel that FluidSynth uses to decide percussion routing. They try to mute `program >= 32 && program <= 39` for Bass and accidentally include a timpani (program 47) that was placed on channel 10 — which FluidSynth ignores the program for and plays as drums anyway.

**How to avoid:**
- In the Python pipeline, always identify percussion tracks by checking if the MIDI track's `channel == 9` (zero-indexed), not by program number.
- Use `pretty_midi`'s `instrument.is_drum` flag (which already checks channel 9) — this is what `details_midi.py` already does correctly.
- When writing a track-filtered MIDI for FluidSynth input, physically remove non-target tracks from a copy of the MIDI file (using `pretty_midi`) rather than trying to mute via FluidSynth flags. This is the reliable approach because FluidSynth's channel muting CLI options are inconsistent across versions.

**Warning signs:**
- The drums group renders silence even though the original song has clear percussion.
- A "Bass" render has a faint snare or hi-hat sound underneath.
- Any code that mutes tracks via FluidSynth's `-R` or channel flags rather than by writing a filtered `.mid` file first.

**Phase to address:** Build pipeline phase (before any game UI work)

---

### Pitfall 2: Per-Group MIDI Copies Must Zero Out Program Gaps or FluidSynth Picks Wrong Soundfont Patch

**What goes wrong:**
When you write a filtered MIDI (only drums + perc tracks) using `pretty_midi`, tracks belonging to other groups are deleted from the file. FluidSynth then loads the remaining tracks and may encounter channel numbers 1-9 with no notes — but if any bank-select or program-change event exists on those channels in the original, FluidSynth will initialize those channels and consume soundfont polyphony. More critically: if you write a per-group MIDI that retains channel assignments from the original (e.g., bass on channel 3), FluidSynth renders correctly. But if you re-number channels for simplicity (e.g., packing all guitar tracks to channel 1 and 2), you risk remapping a track that was originally on channel 9 to a melodic channel, causing the soundfont to play that track as a pitched instrument instead of percussion.

**Why it happens:**
`pretty_midi` instruments store their channel. If you create a new `PrettyMIDI()` object and copy instruments naively, the channel assignment is preserved. But if you filter by role and reconstruct the instrument list, the library may re-assign channels sequentially starting from 0, skipping the percussion channel 9 convention. A bass instrument that was on channel 2 might get reassigned to channel 0 in the filtered file — harmless. But a drums instrument originally on channel 9 that gets reassigned to channel 0 will play as a pitched instrument from the soundfont.

**How to avoid:**
- When copying instruments into a filtered MIDI, explicitly set `instrument.is_drum = True` and ensure the channel stays at 9 for any percussion track.
- Use `pretty_midi`'s `is_drum` parameter when constructing `Instrument` objects: `Instrument(program=0, is_drum=True)`.
- After writing the filtered `.mid`, verify with `pretty_midi` that percussion instruments have `is_drum == True` before passing to FluidSynth.

**Warning signs:**
- Drums group renders as a melodic (pitched) instrument sound — piano or string chords instead of kick and snare.
- The filtered MIDI for drums-only has a channel 9 track but FluidSynth renders pitched notes.
- Any reconstruction of `PrettyMIDI.instruments` list that does not explicitly set `is_drum`.

**Phase to address:** Build pipeline phase

---

### Pitfall 3: FluidSynth Soundfont Quality Varies Wildly — GeneralUser GS vs. MuseScore GM

**What goes wrong:**
FluidSynth renders only as well as its soundfont. Using a lightweight soundfont (e.g., `FluidR3_GM.sf2` at ~140MB) produces acceptable piano and strings but thin brass and drums that sound nothing like the original song. Users cannot recognize the song because the rendered audio is too far from the original. The game becomes unplayable with bad soundfonts. Conversely, the highest-quality soundfonts (e.g., Sonatina Symphonic Orchestra) are instrument-family-specific and won't cover all 128 GM programs, causing missing-instrument silence.

**Why it happens:**
Developers install the first soundfont they find (`fluid-soundfont-gm` from apt/brew), run a test render, and judge it acceptable on piano-heavy songs. The test MIDI may happen to use programs the soundfont renders well. When other MIDIs use brass (programs 56-71) or guitar (24-31), the render quality degrades significantly and those groups become unrecognizable.

**How to avoid:**
- Use a single full-GM soundfont that covers all 128 programs with reasonable quality. Recommended: `GeneralUser GS v1.471.sf2` (30MB, permissive license, well-balanced across all groups) or `MuseScore_General.sf3` (compressed, used by MuseScore — good across all groups).
- Test the chosen soundfont on at least one song with representative tracks from each of the 6 groups (drums, bass, brass, keys, guitar, strings) before committing to it.
- Do not use the system default FluidSynth soundfont (often `/usr/share/sounds/sf2/FluidR3_GM.sf2`) without testing — it's good for GM piano/strings but weak on guitar and brass.

**Warning signs:**
- Guitar group renders with a piano-like timbre.
- Brass/Wind group sounds like a very thin synthesized trumpet.
- Test on songs where those groups are the main melodic line — if they are unrecognizable, change the soundfont.

**Phase to address:** Build pipeline phase (soundfont selection before pipeline implementation)

---

### Pitfall 4: Multiple `<audio>` Elements Cannot Be Synchronized — Use Web Audio API Instead

**What goes wrong:**
The naive implementation of "cumulative audio layers" creates one `<audio>` element per group and calls `.play()` on each in sequence (or simultaneously) as rounds progress. The first element plays drums. On round 2, it plays drums + bass simultaneously by calling `.play()` on the second element. In practice, the two `<audio>` elements drift apart within seconds due to buffering differences, OS audio scheduler jitter, and network latency if the MP3 files are not fully cached. By round 5 (5 elements), the drift is audible and the song sounds like a bad karaoke echo.

**Why it happens:**
`HTMLAudioElement.play()` starts playback relative to the system clock at the moment of the call. If element A started at T+0 and element B starts at T+0.005 (5ms later due to JS event loop latency), they will drift. There is no built-in synchronization between multiple `<audio>` elements. Browser autoplay policies also add non-deterministic delays.

**How to avoid:**
- Use the Web Audio API exclusively: decode all group MP3 files into `AudioBuffer` objects, and start all active buffers from the same `AudioContext.currentTime` offset using `BufferSourceNode.start(context.currentTime + startOffset)`. All buffers driven from the same `AudioContext` clock will be sample-accurate.
- The existing `player.js` already uses `AudioContext` — reuse this pattern. Add one `AudioBufferSourceNode` per active group, all started at the same `context.currentTime`.
- Preload all group MP3s for the current song via `fetch()` + `context.decodeAudioData()` before the game starts. This eliminates mid-round buffering stalls.

**Warning signs:**
- Multiple `<audio>` elements in DOM with each group's `src` set separately.
- `element.play()` called in a loop or sequence for different groups.
- Audible echo/phasing between layers that worsens over time.

**Phase to address:** Game UI phase

---

### Pitfall 5: AudioContext Suspend/Resume on Mobile Requires User Gesture — Preloading Breaks Silently

**What goes wrong:**
All modern browsers require a user gesture before an `AudioContext` can produce sound. The planned pipeline preloads all group MP3s via `fetch()` and `decodeAudioData()` on page load — but if the `AudioContext` was not created or resumed inside a user gesture handler, `decodeAudioData()` may succeed (the buffer is ready) while `AudioContext.state` remains `"suspended"`. When the first play button is clicked, `context.resume()` is called, but on iOS Safari, the audio starts from the current buffer position (not the beginning) because the clock advanced while suspended. This causes the first playback on mobile to start mid-song.

**Why it happens:**
`decodeAudioData()` decodes into memory without requiring a running context. Developers assume that if decoding succeeded, playback will work. They don't check `context.state` before calling `.start()` on the BufferSourceNode. The existing `player.js` already handles this correctly with `await ctx.resume()` — but the new multi-buffer implementation must replicate this pattern for each group.

**How to avoid:**
- Create the `AudioContext` inside the first user gesture handler (the first "Play" click), not at module load time.
- Call `context.resume()` and `await` it before calling `.start()` on any `AudioBufferSourceNode`.
- Store decoded `AudioBuffer` objects from pre-fetch, but do not call `.start()` until the context is running.
- Test on a real iOS Safari device, not just Chrome devtools mobile simulation — Safari has stricter autoplay policies.

**Warning signs:**
- `AudioContext` created at module scope or `DOMContentLoaded` (before any user gesture).
- `context.state === 'suspended'` when the first play button is clicked.
- Audio works on desktop Chrome but is silent on iPhone Safari.

**Phase to address:** Game UI phase

---

### Pitfall 6: Song Duration Mismatch Between Groups — Render Lengths Must Be Identical

**What goes wrong:**
FluidSynth renders each group's MIDI to WAV/MP3 independently. The drums group may render to 3:12 and the bass group to 3:15 because the bass has a long-release note at the end. When both are played together via Web Audio API using the same `AudioContext` clock, one ends 3 seconds before the other, causing a noticeable click or abrupt silence in one layer while others continue playing. Worse, if the game uses `AudioBuffer.duration` to compute "song finished," the game may end prematurely when the shortest buffer ends.

**Why it happens:**
FluidSynth adds silence padding based on the last note's release envelope. Different soundfont presets have different release times. A strings patch may add 2 seconds of reverb tail; a bass patch ends cleanly. The pipeline renders each group separately, so their durations diverge by the release tail length of the last instrument in each group.

**How to avoid:**
- In the Python pipeline, after rendering all group WAVs, compute the maximum duration across all groups for a given song. Pad all shorter renders to match this maximum using `ffmpeg` with the `-t` flag (trim/pad to exact length): `ffmpeg -i input.wav -t {max_duration} output.wav`.
- Store the canonical song duration in the `songs.json` manifest so the game JS knows when to stop all buffers.
- Alternatively, use the original full-song MIDI duration (from `pretty_midi`) as the authoritative length and trim all renders to it.

**Warning signs:**
- Drums group audio ends noticeably earlier than strings/ensemble group.
- Game end state triggers while some audio layers are still playing.
- `AudioBuffer.duration` values differ across group files for the same song by more than 0.5 seconds.

**Phase to address:** Build pipeline phase

---

### Pitfall 7: Group Classification Gaps — Some Songs Have Zero Notes in a Required Group

**What goes wrong:**
The 6-round structure assumes every song has tracks in every group: Drums+Perc, Bass, Brass/Wind, Keys/Piano+Synth, Guitar, Ensemble+Choir+Strings. Many MIDIs — especially pop songs — have no brass or no strings. If round 3 is supposed to reveal "Brass/Wind" but that group has 0 notes, the rendered MP3 is silence, and the cumulative audio doesn't change between round 2 and round 3. Players hear no new layer and think the game is broken.

**Why it happens:**
The group structure is designed for orchestral/full-band MIDIs. Pop/electronic MIDIs may have only drums, bass, synth, and possibly guitar. The pipeline generates an empty (silence-only) MP3 for that group, which is technically valid but creates a bad game experience.

**How to avoid:**
- In the pipeline, after parsing MIDI tracks into groups, flag any group with 0 notes as "empty."
- For each song, write a JSON manifest entry that lists which of the 6 groups are present (non-empty). The game JS reads this and skips empty rounds, merging them into the next non-empty group's reveal.
- Alternative: merge groups differently per-song rather than enforcing a fixed 6-round structure. This is more complex but produces a more natural game flow.
- At minimum: never generate and serve a silence-only MP3 as a game round. The pipeline should log a warning for every empty group.

**Warning signs:**
- A song's manifest has a group with `"hasAudio": false` or similar flag.
- Consecutive rounds produce no audible change when a new layer is added.
- Pipeline generates 0-byte or near-silence (< 1KB) MP3 files for certain groups.

**Phase to address:** Build pipeline phase (manifest design) + Game UI phase (skip-empty-round logic)

---

### Pitfall 8: Adapting Music01s Guess/Skip Flow — Round Count Mismatch Breaks the Attempt Rows

**What goes wrong:**
Music01s has exactly 6 attempt rows hardcoded in HTML (`id="row-0"` through `id="row-5"`), matching its 6 clip durations (0.1s, 0.5s, 2s, 4s, 8s, 16s). MusicSplit has 6 groups — superficially the same count. But MusicSplit rounds are triggered by the player choosing when to play each layer, not by fixed clip durations. If any group is empty (pitfall 7 above) and skipped, the number of playable rounds drops below 6. The Music01s row system assumes exactly 6 rounds always happen; if fewer rounds play, unused rows remain blank (or worse, the JS crashes with `getElementById('row-5')` returning a valid element that never gets populated).

**Why it happens:**
Music01s was built for a fixed game flow: always 6 rounds, always 6 rows. Developers copy the HTML structure and JS logic, then try to adapt by changing the round count, but miss that `CLIPS.length`, the attempt rows, and the timeline segment count are all hardcoded together in three different places (`CLIPS` array, HTML `id` attributes, and the `buildTimeline()` function). Changing one without the others causes visual mismatches.

**How to avoid:**
- In the new MusicSplit game, generate the attempt rows from a JavaScript array of groups, not from hardcoded HTML. The number of rows must match the number of active (non-empty) groups for the current song.
- Build a `renderRounds(groups)` function that creates the row elements dynamically and attaches event handlers.
- Do not copy the Music01s HTML structure for attempt rows verbatim — use it as a CSS/style reference only.

**Warning signs:**
- HTML contains `id="row-0"` through `id="row-5"` hardcoded in the template.
- The JS accesses attempt rows by index using `getElementById('row-' + i)` with a fixed upper bound.
- When a 5-group song is loaded, one row remains blank with no group name or button.

**Phase to address:** Game UI phase

---

### Pitfall 9: The `songs.js` Pattern Must Become `songs.json` — Script Tag Loading Blocks Async

**What goes wrong:**
Music01s loads its song list via `<script src="songs.js">` which exposes a `const SONGS = [...]` global. This works for Music01s because the data is small (a list of filenames) and loaded synchronously before game init. For MusicSplit, each song has 6 group MP3 paths plus metadata (group names, which groups exist, song title, artist). A `songs.js` global works but requires a synchronous script load. If the page tries to preload the MP3s via `fetch()` + `decodeAudioData()` while `songs.js` is still loading (e.g., if the script is deferred), the preloading fails silently because the SONGS global does not yet exist.

**Why it happens:**
The `<script src="songs.js">` pattern works for synchronous access but is incompatible with `defer` or `type="module"` script loading. When the new game JS is written as a module (which it should be, for `async/await` support), it runs after DOM parse but the non-deferred `songs.js` may or may not be available depending on load order.

**How to avoid:**
- Use `songs.json` (a static JSON file) loaded via `fetch()` inside the game JS. This makes the load order explicit and `async/await`-friendly.
- The pipeline's Python script writes `songs.json` instead of `songs.js`. The game JS starts with `const songs = await fetch('songs.json').then(r => r.json())`.
- This also makes the data available to any future tooling (other scripts, build verification scripts) without requiring a browser JS runtime.

**Warning signs:**
- The pipeline generates a `.js` file with `const SONGS = ...` syntax.
- The game JS accesses `window.SONGS` or a global `SONGS` variable.
- Any `DOMContentLoaded` handler that accesses `SONGS` before the songs script tag has executed.

**Phase to address:** Build pipeline phase (manifest format decision made before game UI is coded)

---

### Pitfall 10: Existing `player.js` WebAudio Model Is Incompatible — It Cannot Layer Multiple AudioBufferSources

**What goes wrong:**
The existing `player.js` uses Tone.js's Transport and Part system for scheduling synthesized notes. The new game needs raw `AudioBufferSourceNode` playback of decoded MP3s. These are fundamentally different audio models. Developers attempt to reuse `player.js` by adding a "load MP3" mode alongside the existing oscillator synthesis mode. This creates a hybrid that is hard to debug: Tone.js Transport and Web Audio `AudioBufferSourceNode` share the same `AudioContext` but Tone.js may reset the context state unexpectedly when `Transport.stop()` or `Transport.cancel()` is called, which disconnects any manually added `AudioBufferSourceNode` graphs.

**Why it happens:**
`player.js` is imported in `index.html` as a module. Developers try to extend it rather than replace it to avoid "touching working code." Tone.js wraps the `AudioContext` internally — its `Transport.stop()` calls `context.suspend()` in some versions, which also suspends manually added raw Web Audio nodes.

**How to avoid:**
- Write a new `audio-player.js` that does not use Tone.js. It handles only `AudioBuffer` loading and playback via raw Web Audio API.
- Keep `player.js` as-is for the current MIDI visualizer mode (if that mode is preserved at all). Do not modify it.
- The new game JS imports only `audio-player.js`. The game does not depend on Tone.js at all.
- `audio-player.js` exposes: `preloadSong(groups)`, `playCumulative(activeGroupCount)`, `pause()`, `resume()`, `seek(fraction)`, `on('tick', fn)`, `on('end', fn)`.

**Warning signs:**
- Any `import` of `Tone` or `player.js` in the new game JS files.
- The game JS calling `Tone.Transport.stop()` alongside its own `AudioBufferSourceNode` management.
- Audio cuts out unexpectedly mid-playback or on mobile when switching between rounds.

**Phase to address:** Game UI phase (design new audio module first, before building game flow)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Render one MP3 per group using full MIDI duration | Simple pipeline — no duration matching needed | Silence padding at end of short groups; groups end at different times causing sync issues | Never — always normalize durations |
| Use `<audio>` elements instead of Web Audio API for sync | Familiar API, less code | Layers drift apart within 10-30 seconds; audible phasing makes game unplayable | Never for multi-layer sync |
| Hardcode 6 rounds always | Matches Music01s structure exactly | Empty rounds are silence; game feels broken for 4-group songs | Never — always skip empty groups |
| Use `songs.js` global instead of `songs.json` + fetch | No async code needed | Incompatible with ES module deferred loading; blocks page parse | Only acceptable during initial development prototype, not shipping |
| Reuse `player.js` with Tone.js for MP3 playback | Less new code to write | Tone.js Transport conflicts with raw AudioBufferSourceNode management; debugging is very hard | Never — separate the audio models |
| Use low-quality free soundfont (fluid-soundfont-gm) | Easy to install via package manager | Guitar and brass groups unrecognizable; game fails for non-piano-heavy songs | Acceptable only as a first test render before switching to a better soundfont |
| Mute tracks via FluidSynth channel flags | No need to write filtered MIDI files | Channel muting flags differ between FluidSynth versions; behavior is undefined for some channels | Never — always write filtered MIDI files |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| FluidSynth + pretty_midi | Passing the original `.mid` to FluidSynth and trying to mute channels via CLI flags | Write a filtered `.mid` per group using `pretty_midi`, then pass each to FluidSynth |
| FluidSynth + ffmpeg | Rendering to WAV with FluidSynth then converting to MP3 with ffmpeg in a separate step, but forgetting to normalize volume | Add `-af loudnorm` to the ffmpeg conversion step so all groups have consistent perceived loudness |
| Web Audio API + GitHub Pages | Fetching MP3s cross-origin assumes same-origin; GitHub Pages serves from the same origin, so no CORS issue — but `file://` local dev fails | Always use `python -m http.server` or similar for local dev; never open `index.html` directly as a file |
| Web Audio API `decodeAudioData` | Reusing the same `ArrayBuffer` for multiple `decodeAudioData()` calls — it's consumed (neutered) after the first call | `fetch()` each MP3 once, store the decoded `AudioBuffer`, never re-decode from the same buffer |
| pretty_midi channel 9 | Setting `is_drum=False` on a track that was originally on channel 9 in the source MIDI | Always preserve the original `is_drum` flag from the parsed instrument; never override it unless certain |
| songs.json path | Game JS fetches `songs.json` with a relative path — works from the server root but fails if the game is opened at a different path depth | Always use `fetch('songs.json')` (relative, no leading slash) from within the `MusicSplit/` directory |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Decoding all group MP3s at page load | 3-6 second blank page before game starts (decoding 6 MP3s × N songs) | Only preload the current song's groups; decode remaining songs lazily in the background | With more than 3 songs if groups are large (>30s) |
| Storing `AudioBuffer` objects for all songs | Memory spikes; Safari may terminate the page on mobile | Keep only the current song's `AudioBuffer`s in memory; release previous song's buffers by setting references to `null` | 5+ songs with full-duration renders; less of an issue for 30s clips |
| Creating new `AudioContext` per round | Each round creates a new context; iOS limits concurrent AudioContext instances to 6 | Create one `AudioContext` at game start, reuse it throughout the session | After 6 round restarts on iOS |
| Fetching MP3s without error handling | Network failure causes silent game (no audio, no error message) | Always `try/catch` `fetch()` + `decodeAudioData()`; show "Audio failed to load" state in UI | On slow connections or when MP3 files are missing from repo |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No loading indicator while decoding group MP3s | User clicks Play and nothing happens for 2-3 seconds — looks broken | Show "Loading audio..." spinner before first play; hide it once all group buffers are decoded |
| Revealing group names before the round | Naming "Guitar" before the player hears the guitar layer removes the guessing element | Show group name only after round is completed (skipped or guessed), like Bandle.app |
| Allowing guess submission before listening | Player submits a random guess without playing the audio | Require at least one play before enabling the guess input (disable input until first `play()` call) |
| No visual indication that a new layer was added | Player clicks "Next round" and has no feedback that new audio was added | Flash or animate the new group row when it joins the cumulative audio; highlight the newly active layer |
| Progress bar width mapping to "current clip" not "song position" | Music01s maps the progress bar to clip duration (0-16s). For MusicSplit, each round plays the full song from the start — the bar should show song position, not round number | Use a single progress bar showing `currentTime / songDuration`; separate round indicators for the 6 groups |

---

## "Looks Done But Isn't" Checklist

- [ ] **Pipeline produces correct group files:** Run the pipeline on a song with ALL 6 group types present, verify each MP3 contains only instruments from that group — listen to each file separately before building the game UI.
- [ ] **Duration normalization:** Verify all 6 group MP3s for a given song have identical duration (within 10ms) — use `ffprobe` to print duration of each file.
- [ ] **Silence detection:** Confirm no group MP3 is silence-only — add a loudness check in the pipeline and warn on empty groups.
- [ ] **Mobile audio unlock:** Play the game on a real iOS Safari device (not just Chrome devtools) — confirm audio plays on the first button click.
- [ ] **Layer sync:** Play a song with 6 layers active, then seek to 2 minutes — confirm all 6 layers are still in sync (no audible drift or echo).
- [ ] **Skip-empty-round logic:** Load a song that has no Guitar tracks — confirm round 5 is skipped and the game advances to the final round correctly, without a blank/silent round.
- [ ] **Autocomplete sources:** The guess input must source song names from the same list regardless of how many songs are loaded — verify the autocomplete lists all songs, not just the current one.
- [ ] **Old player.js not imported:** Verify `index.html` does not import `player.js` or reference Tone.js in the new game build.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| FluidSynth drum channel mismatch | MEDIUM | Rewrite the group-filter step in the pipeline to use `instrument.is_drum` from pretty_midi; re-render all songs |
| Wrong soundfont — groups unrecognizable | MEDIUM | Swap soundfont in pipeline config, re-render all songs; no game JS changes needed if path convention is stable |
| Audio layers drift | HIGH | Replace all `<audio>` elements with `AudioBufferSourceNode`; requires rewriting the audio engine entirely |
| Hardcoded 6-round HTML rows | MEDIUM | Rewrite round rendering to be dynamic (JS-generated DOM); update CSS to not rely on fixed row count |
| `songs.js` global incompatible with module loading | LOW | Convert pipeline output to `songs.json`; update game JS fetch call |
| Tone.js conflicts with raw AudioBufferSource | HIGH | Extract all audio logic into a new `audio-player.js` that does not import Tone.js; rewrite from scratch |
| Empty-group silence rounds | MEDIUM | Add empty-group detection to pipeline; add skip logic to game JS |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Drum channel 10 mismatch | Build pipeline phase | Listen to each group MP3 in isolation; drums must not appear in other groups |
| Percussion channel reassignment in filtered MIDI | Build pipeline phase | Check `is_drum` flag of all tracks in filtered MIDI after writing |
| Soundfont quality | Build pipeline phase (before pipeline coding) | Test render on a guitar-heavy and brass-heavy MIDI |
| Multiple `<audio>` drift | Game UI phase | Play 6-layer song for 3 minutes; verify no audible phasing or echo |
| Mobile AudioContext suspension | Game UI phase | Test first-click playback on real iOS Safari |
| Song duration mismatch between groups | Build pipeline phase | Run `ffprobe` on all group files for one song; compare durations |
| Empty groups in fixed 6-round structure | Build pipeline phase (manifest) + Game UI phase (skip logic) | Load a 4-group song; verify game has only 4 rounds |
| Music01s hardcoded row structure | Game UI phase | Load a song with 5 groups; confirm 5 rows render, not 6 |
| `songs.js` global vs `songs.json` | Build pipeline phase (manifest format) | Game JS must not reference `window.SONGS`; use `fetch()` |
| Tone.js conflict with new audio engine | Game UI phase | Confirm `player.js` and Tone.js are not imported in new game files |

---

## Sources

- Direct codebase inspection: `MusicSplit/player.js`, `MusicSplit/utils.js`, `MusicSplit/index.html`, `MusicSplit/details_midi.py`, `Music01s/index.html`, `Music01s/build.py` (2026-03-01)
- General MIDI specification: Channel 10 percussion mapping, program number ranges for instrument families
- Web Audio API specification (MDN, training knowledge): `AudioContext`, `AudioBufferSourceNode`, synchronization behavior, mobile autoplay policies
- FluidSynth behavior (training knowledge, HIGH confidence): WAV rendering quality depends on soundfont, channel 10 percussion override is per-spec
- `pretty_midi` Python library (training knowledge, HIGH confidence): `Instrument.is_drum` maps to channel 9; `PrettyMIDI` write behavior preserves instrument channels
- iOS Safari Web Audio autoplay policy: documented Apple developer restriction — requires user gesture before `AudioContext` produces output

---
*Pitfalls research for: MusicSplit v1.1 — MIDI-to-MP3 build pipeline + cumulative audio guessing game*
*Researched: 2026-03-01*
