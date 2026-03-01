# Requirements: RandomGame

**Defined:** 2026-03-01
**Core Value:** Every game feels like part of the same polished product — consistent design across all games.

## v1 Requirements

### Theme Unification

- [ ] **THEME-01**: All games link to root `themes.css` and use its CSS custom properties
- [ ] **THEME-02**: MusicSplit adopts `themes.css` (currently has no link) with purple/cyan palette
- [ ] **THEME-03**: PokeGuess uses only root `themes.css` (remove duplicate local copy)
- [ ] **THEME-04**: Per-game `:root` color overrides removed (lime green eliminated)
- [ ] **THEME-05**: Orb background colors use consistent values from themes.css across all games
- [ ] **THEME-06**: Music01s has noise overlay and ambient orbs matching other games

## v2 Requirements

### Mobile Responsiveness

- **MOBILE-01**: Music01s layout fixed for mobile (replace 100vh/overflow:hidden)
- **MOBILE-02**: MusicSplit has responsive media queries
- **MOBILE-03**: All touch targets are at least 44px across all games

### Navigation & Consistency

- **NAV-01**: Consistent back-to-homepage link from every game page
- **NAV-02**: PokeGuess game.html has root homepage link
- **NAV-03**: Standardized `<title>` format across all pages

## Out of Scope

| Feature | Reason |
|---------|--------|
| New games | Polish existing 3 first |
| Per-game accent colors | Keep it simple — one unified palette |
| Shared structural CSS file | Can extract noise/orbs/reset later when adding games |
| User accounts / scores | Personal project, not needed |
| Build tools / bundler | GitHub Pages serves raw files, keep it simple |
| Landscape orientation support | Defer to v2+ |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| THEME-01 | — | Pending |
| THEME-02 | — | Pending |
| THEME-03 | — | Pending |
| THEME-04 | — | Pending |
| THEME-05 | — | Pending |
| THEME-06 | — | Pending |

**Coverage:**
- v1 requirements: 6 total
- Mapped to phases: 0
- Unmapped: 6 ⚠️

---
*Requirements defined: 2026-03-01*
*Last updated: 2026-03-01 after initial definition*
