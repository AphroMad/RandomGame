---
phase: 01-theme-unification
plan: "01"
subsystem: CSS / HTML theme consistency
tags: [theme, orbs, noise-overlay, pokeguess, music01s]
dependency_graph:
  requires: []
  provides: [unified-orb-colors, music01s-noise-overlay, music01s-orbs]
  affects: [PokeGuess/assets/css/style.css, Music01s/index.html]
tech_stack:
  added: []
  patterns: [CSS custom properties via var(--)-, SVG fractal noise overlay, radial-gradient ambient orbs]
key_files:
  created: []
  modified:
    - PokeGuess/assets/css/style.css
    - Music01s/index.html
  deleted:
    - PokeGuess/assets/css/themes.css
decisions:
  - "Deleted orphaned PokeGuess/assets/css/themes.css — zero references found, safe to remove"
  - "Orb colors unified to purple rgba(144,149,255,.06) and cyan rgba(140,247,255,.04) across all pages"
metrics:
  duration: "5 minutes"
  completed: "2026-03-01"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 2
  files_deleted: 1
---

# Phase 1 Plan 01: PokeGuess Cleanup and Music01s Visual Parity Summary

**One-liner:** Deleted orphaned PokeGuess/assets/css/themes.css and replaced lime-green orbs with purple/cyan; added SVG fractal noise overlay and ambient orbs to Music01s matching homepage visual signature.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | PokeGuess — delete duplicate themes.css and fix lime orb RGBA values | c2840e0 | PokeGuess/assets/css/themes.css (deleted), PokeGuess/assets/css/style.css |
| 2 | Music01s — add noise overlay and ambient orbs | 5e260f6 | Music01s/index.html |

## Verification Results

1. `PokeGuess/assets/css/themes.css` — does not exist on disk. PASS
2. `PokeGuess/assets/css/style.css` — contains `rgba(144,149,255,.06)` for orb-a and `rgba(140,247,255,.04)` for orb-b. PASS
3. No occurrence of `200,240,96` or `c8f060` in any PokeGuess CSS file. PASS
4. `Music01s/index.html` contains `body::after` noise overlay CSS. PASS
5. `Music01s/index.html` contains `.orb-a` and `.orb-b` CSS rules with correct RGBA values. PASS
6. `Music01s/index.html` contains `<div class="orb orb-a">` and `<div class="orb orb-b">` HTML elements. PASS

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- PokeGuess/assets/css/themes.css: DELETED (confirmed)
- PokeGuess/assets/css/style.css: MODIFIED (confirmed, contains rgba(144,149,255))
- Music01s/index.html: MODIFIED (confirmed, contains body::after and orb divs)
- Commits c2840e0 and 5e260f6: exist in git log
