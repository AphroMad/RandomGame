# RandomGame

## What This Is

A GitHub Pages website that hosts a collection of mini-games — quizzes, guessing games, and more. Users land on a homepage listing all available games and pick one to play. Built as a personal project shared with friends.

## Core Value

Every game feels like part of the same polished product — consistent design, smooth experience, works on any device.

## Requirements

### Validated

- ✓ Homepage with game list — existing
- ✓ Music 01s game (guess the song from 1s clip) — existing
- ✓ Music Split game (separate instruments) — existing
- ✓ PokeGuess game (Pokémon quiz) — existing
- ✓ Dark theme with gradient accents — existing (themes.css)

### Active

- [ ] Unified visual design across all 3 games matching homepage style
- [ ] Shared code structure and patterns across games
- [ ] Mobile-responsive design for all games
- [ ] Consistent navigation between games and homepage

### Out of Scope

- New games — focus on polishing existing 3 first
- User accounts or score tracking — personal/friends project
- Backend/server — GitHub Pages static hosting only
- Game template system — not needed until adding new games

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

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dark theme for all games | Match homepage, unified feel | — Pending |
| Vanilla HTML/CSS/JS | Already in use, no build step needed for GitHub Pages | — Pending |
| No new games in this milestone | Polish first, expand later | — Pending |

---
*Last updated: 2026-03-01 after initialization*
