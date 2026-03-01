# RandomGame

## What This Is

A GitHub Pages website that hosts a collection of mini-games — quizzes, guessing games, and more. Users land on a homepage listing all available games and pick one to play. Built as a personal project shared with friends.

## Core Value

Every game feels like part of the same polished product — consistent design, smooth experience, works on any device.

## Requirements

### Validated

- ✓ Homepage with game list — v1.0
- ✓ Music 01s game (guess the song from 1s clip) — v1.0
- ✓ Music Split game (separate instruments) — v1.0
- ✓ PokeGuess game (Pokémon quiz) — v1.0
- ✓ Dark theme with gradient accents — v1.0 (themes.css)
- ✓ Unified visual design across all 3 games — v1.0 (Theme Unification)

### Active

- [ ] Python build pipeline: MIDI → per-instrument-group MP3 rendering
- [ ] MusicSplit game UI: Music01s-style guess/skip flow with cumulative audio layers
- [ ] 6-round instrument reveal: Drums+Perc → Bass → Brass/Wind → Keys/Piano+Synth → Guitar → Ensemble+Choir+Strings

### Out of Scope

- Other games changes — focus on MusicSplit transformation
- User accounts or score tracking — personal/friends project
- Backend/server — GitHub Pages static hosting only
- Real audio stem separation (e.g. Demucs) — using MIDI-to-audio rendering instead

## Context

- Hosted on GitHub Pages (static HTML/CSS/JS only)
- 3 games already functional: Music01s, MusicSplit, PokeGuess
- Each game lives in its own directory with its own index.html
- Homepage uses themes.css with CSS custom properties for theming
- Current design language: dark background, gradient accents (purple/cyan), Bebas Neue + DM Mono + DM Sans fonts, subtle noise overlay, blur orbs
- Some games may not use themes.css yet — need to adopt it
- French language (lang="fr" on homepage)

## Constraints

- **Hosting**: GitHub Pages — static files only, no server-side code
- **Tech stack**: Vanilla HTML/CSS/JS — no build tools or frameworks (keep it simple)
- **Design**: Must match existing homepage aesthetic (dark theme, gradient accents, same fonts)

## Current Milestone: v1.1 MusicSplit Game

**Goal:** Transform MusicSplit from a MIDI visualizer into a real guessing game with cumulative instrument layers

**Target features:**
- Python build pipeline rendering MIDI files to per-instrument-group MP3s via FluidSynth/soundfonts
- Music01s-style game UI with guess/skip flow and autocomplete
- 6-round cumulative instrument reveal (Drums+Perc → Bass → Brass/Wind → Keys/Piano+Synth → Guitar → Ensemble+Choir+Strings)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dark theme for all games | Match homepage, unified feel | ✓ Good |
| Vanilla HTML/CSS/JS | Already in use, no build step needed for GitHub Pages | ✓ Good |
| No new games in v1.0 | Polish first, expand later | ✓ Good |
| MIDI → MP3 via soundfonts | Better audio quality than oscillator synthesis, simpler playback | — Pending |
| Merge Strings/Synth/Other into closest groups | Keep exactly 6 rounds, avoid sparse groups | — Pending |
| Python build pipeline before game UI | Get audio assets right first, then build the game | — Pending |

---
*Last updated: 2026-03-01 after milestone v1.1 start*
