# Requirements: RandomGame

**Defined:** 2026-03-01
**Core Value:** Every game feels like part of the same polished product — consistent design, smooth experience, works on any device.

## v1.0 Requirements (Complete)

### Theme Unification

- [x] **THEME-01**: All games link to root `themes.css` and use its CSS custom properties
- [x] **THEME-02**: MusicSplit adopts `themes.css` with purple/cyan palette
- [x] **THEME-03**: PokeGuess uses only root `themes.css` (remove duplicate local copy)
- [x] **THEME-04**: Per-game `:root` color overrides removed (lime green eliminated)
- [x] **THEME-05**: Orb background colors use consistent values from themes.css across all games
- [x] **THEME-06**: Music01s has noise overlay and ambient orbs matching other games

## v1.1 Requirements

Requirements for milestone v1.1: MusicSplit Game. Each maps to roadmap phases.

### Build Pipeline

- [x] **BUILD-01**: Python script parses MIDI files and groups tracks into 6 instrument groups (Drums+Perc, Bass, Brass/Wind, Keys/Piano+Synth, Guitar, Ensemble+Choir+Strings)
- [x] **BUILD-02**: Script renders each instrument group to a separate MP3 using FluidSynth + soundfont
- [x] **BUILD-03**: Script generates cumulative MP3 files (layer N = groups 1 through N mixed together)
- [x] **BUILD-04**: Script generates songs.js manifest with song title, artist, and per-layer file paths

### Game Core

- [ ] **GAME-01**: User plays a 6-round guessing game where each round adds an instrument layer
- [ ] **GAME-02**: User can submit a text guess with autocomplete dropdown filtered from song list
- [ ] **GAME-03**: User can skip a round (costs one attempt, reveals next layer)
- [ ] **GAME-04**: Correct guess shows win state with song title/artist reveal
- [ ] **GAME-05**: Exhausting 6 rounds shows lose state with song reveal
- [ ] **GAME-06**: User advances to next song after win or lose via Next button
- [ ] **GAME-07**: Game ends with Game Over screen after all songs are played

### Audio

- [ ] **AUDIO-01**: User can play and pause the current cumulative audio layer
- [ ] **AUDIO-02**: Audio swaps to the correct cumulative MP3 when a new layer is revealed

### UI Polish

- [ ] **UI-01**: Each round displays as an attempt row with correct/wrong/skipped/revealed visual states
- [ ] **UI-02**: Layer name indicator shows which instruments are currently playing
- [ ] **UI-03**: Attempt rows show layer name on skip or wrong guess
- [ ] **UI-04**: Visual badge strip below audio controls shows accumulated layer names
- [ ] **UI-05**: Timeline with 6 segments serves as round indicator

### Modes

- [ ] **MODE-01**: User can toggle between game mode and free-play explorer mode
- [ ] **MODE-02**: Explorer mode lets user play/stop individual instrument groups independently using pre-rendered MP3s

### Cleanup

- [ ] **CLEAN-01**: Legacy oscillator synthesis code and Tone.js import removed from game page

## Future Requirements

### Mobile

- **MOBILE-01**: MusicSplit game is fully responsive on mobile devices
- **MOBILE-02**: Touch-friendly controls for play/pause and mode toggle

### Navigation

- **NAV-01**: Consistent back-to-homepage link from every game page
- **NAV-02**: Standardized `<title>` format across all pages

## Out of Scope

| Feature | Reason |
|---------|--------|
| AI stem separation (Demucs) | MIDI-to-audio rendering gives clean separation by design |
| Score persistence / leaderboard | Personal project, each session is fresh |
| Daily song mode | No backend — songs play from local shuffled list |
| Share results (emoji grid) | No backend, personal project |
| Real-time multi-track Web Audio mixing | Pre-rendered cumulative MP3s avoid all sync complexity |
| Free-text guessing without autocomplete | Ambiguous matching; autocomplete constrains to valid answers |
| Build tools / bundler | GitHub Pages serves raw files, keep it simple |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BUILD-01 | Phase 2 | Complete |
| BUILD-02 | Phase 2 | Complete |
| BUILD-03 | Phase 2 | Complete |
| BUILD-04 | Phase 2 | Complete |
| GAME-01 | Phase 3 | Pending |
| GAME-02 | Phase 3 | Pending |
| GAME-03 | Phase 3 | Pending |
| GAME-04 | Phase 3 | Pending |
| GAME-05 | Phase 3 | Pending |
| GAME-06 | Phase 3 | Pending |
| GAME-07 | Phase 3 | Pending |
| AUDIO-01 | Phase 3 | Pending |
| AUDIO-02 | Phase 3 | Pending |
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 4 | Pending |
| UI-03 | Phase 4 | Pending |
| UI-04 | Phase 4 | Pending |
| UI-05 | Phase 4 | Pending |
| MODE-01 | Phase 4 | Pending |
| MODE-02 | Phase 4 | Pending |
| CLEAN-01 | Phase 3 | Pending |

**Coverage:**
- v1.1 requirements: 21 total
- Mapped to phases: 21
- Unmapped: 0

---
*Requirements defined: 2026-03-01*
*Last updated: 2026-03-01 after roadmap creation (phases 2-4 assigned)*
