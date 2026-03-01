# Roadmap: RandomGame

## Milestones

- ✅ **v1.0 Theme Unification** - Phase 1 (shipped 2026-03-01)
- 🚧 **v1.1 MusicSplit Game** - Phases 2-4 (in progress)

## Phases

<details>
<summary>✅ v1.0 Theme Unification (Phase 1) - SHIPPED 2026-03-01</summary>

### Phase 1: Theme Unification
**Goal**: All three games look like the same product — same accent palette (purple/cyan), same noise overlay, same orb colors, zero competing color definitions
**Depends on**: Nothing (first phase)
**Requirements**: THEME-01, THEME-02, THEME-03, THEME-04, THEME-05, THEME-06
**Success Criteria** (what must be TRUE):
  1. Opening any of the three game pages shows the purple/cyan accent palette — no lime green visible anywhere
  2. The noise overlay texture and ambient orb blobs are present and consistently colored on all three game pages
  3. Inspecting the page source of MusicSplit shows a `<link>` to `../themes.css` and no inline `:root {}` block
  4. Inspecting PokeGuess shows no local `assets/css/themes.css` file and no duplicate theme `<link>` tags
  5. Music01s has the noise overlay and ambient orbs matching the homepage visual signature
**Plans:** 3/3 plans complete
- [x] 01-01-PLAN.md — PokeGuess cleanup (delete duplicate themes.css, fix orb colors) + Music01s additions (noise overlay, ambient orbs)
- [x] 01-02-PLAN.md — MusicSplit full migration (remove inline :root, link themes.css, replace all lime values with purple/cyan)
- [x] 01-03-PLAN.md — Cross-game automated verification + visual checkpoint

</details>

### 🚧 v1.1 MusicSplit Game (In Progress)

**Milestone Goal:** Transform MusicSplit from a MIDI visualizer into a real guessing game where players hear cumulative instrument layers across 6 rounds and guess the song

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 2: Build Pipeline** - Python script renders MIDI files to per-instrument-group MP3s and generates the songs.js manifest
- [ ] **Phase 3: Game Core** - Playable 6-round guessing game with cumulative audio, autocomplete guessing, win/lose states, and legacy code removed
- [ ] **Phase 4: UI Polish + Explorer Mode** - Layer name indicators, badge strip, round timeline, and free-play explorer mode

## Phase Details

### Phase 2: Build Pipeline
**Goal**: A local Python build pipeline converts MIDI files into per-instrument-group MP3s and a machine-readable songs.js manifest, giving the game real audio assets to play
**Depends on**: Phase 1
**Requirements**: BUILD-01, BUILD-02, BUILD-03, BUILD-04
**Success Criteria** (what must be TRUE):
  1. Running `build.py` on a MIDI file produces 6 MP3 files (one per instrument group: Drums+Perc, Bass, Brass/Wind, Keys/Piano+Synth, Guitar, Ensemble+Choir+Strings) in `MusicSplit/audio/<song-id>/`
  2. Each group MP3 contains only its assigned instruments and all group MP3s for a song share the same total duration
  3. Running `build.py` produces a `songs.js` file listing each song's title, artist, and all per-group file paths with flags indicating which groups are non-empty
  4. Playing a group MP3 in a browser or audio player sounds like recognizable instruments from the original song (not oscillator tones)
**Plans:** 1 plan
Plans:
- [x] 02-01-PLAN.md — Build complete MIDI-to-MP3 pipeline (build.py + .gitignore + end-to-end verification)

### Phase 3: Game Core
**Goal**: A fully playable MusicSplit guessing game where the player hears cumulative instrument layers, submits guesses with autocomplete, skips rounds, and receives a win or lose outcome — with all legacy oscillator/Tone.js code gone
**Depends on**: Phase 2
**Requirements**: GAME-01, GAME-02, GAME-03, GAME-04, GAME-05, GAME-06, GAME-07, AUDIO-01, AUDIO-02, UI-01, CLEAN-01
**Success Criteria** (what must be TRUE):
  1. Opening MusicSplit plays the first instrument layer (Drums) automatically; the player can pause and resume playback with a single button
  2. Typing in the guess input shows an autocomplete dropdown filtered to matching song titles; submitting a correct guess shows the win screen with song title and artist
  3. Clicking Skip advances to the next round, adds one more instrument layer to the audio, and marks the row as skipped; exhausting all 6 rounds shows the lose screen with the song revealed
  4. Each played round is shown as an attempt row with a visual state (correct, wrong, skipped, or revealed) reflecting what happened
  5. Clicking Next after a win or lose loads the next song; after all songs are exhausted the Game Over screen is shown
  6. Viewing the page source shows no Tone.js import and no oscillator synthesis code
**Plans**: TBD

### Phase 4: UI Polish + Explorer Mode
**Goal**: The game gains layer-name context in its UI (which instruments are playing at each round) and an explorer mode where the player can freely play individual instrument groups to study them
**Depends on**: Phase 3
**Requirements**: UI-02, UI-03, UI-04, UI-05, MODE-01, MODE-02
**Success Criteria** (what must be TRUE):
  1. Below the audio controls a strip of badges shows the names of all instrument groups currently audible, updated on each round
  2. Each attempt row displays the name of the layer that was revealed on that round (e.g. "Skipped — Drums + Bass")
  3. A 6-segment timeline below the audio player serves as a round indicator, with each segment filling as the corresponding round is revealed
  4. A toggle button switches between game mode and explorer mode; in explorer mode the player can independently start and stop each instrument group's MP3
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 2 → 3 → 4

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Theme Unification | v1.0 | 3/3 | Complete | 2026-03-01 |
| 2. Build Pipeline | v1.1 | 1/1 | Complete | 2026-03-01 |
| 3. Game Core | v1.1 | 0/? | Not started | - |
| 4. UI Polish + Explorer Mode | v1.1 | 0/? | Not started | - |
