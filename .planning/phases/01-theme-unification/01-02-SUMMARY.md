---
phase: 01-theme-unification
plan: 02
subsystem: MusicSplit
tags: [theme, css, migration, purple-cyan]
dependency_graph:
  requires: [themes.css]
  provides: [MusicSplit themed with shared palette]
  affects: [MusicSplit/index.html]
tech_stack:
  added: []
  patterns: [CSS custom properties via themes.css, shared token system]
key_files:
  created: []
  modified:
    - MusicSplit/index.html
decisions:
  - Logo uses var(--text) for main text and var(--purple) for em, matching Music01s pattern
metrics:
  duration: ~5 minutes
  completed: 2026-03-01
---

# Phase 1 Plan 02: MusicSplit Theme Migration Summary

**One-liner:** Replaced MusicSplit's inline lime-green :root token system with the shared purple/cyan palette from themes.css via full token removal and RGBA value replacement.

## What Was Done

MusicSplit had its own complete `:root {}` CSS block defining lime-green values that competed with themes.css. This plan removed those inline definitions and wired MusicSplit into the shared theme system.

### Changes Made

1. Added `<link rel="stylesheet" href="../themes.css">` before the `<style>` tag
2. Removed the entire inline `:root {}` block (14 declarations, lime-green token definitions)
3. Replaced hardcoded lime orb colors:
   - `orb-a`: `rgba(200,240,96,.05)` → `rgba(144,149,255,.06)` (purple)
   - `orb-b`: `rgba(96,208,240,.04)` → `rgba(140,247,255,.04)` (cyan)
   - Playing row: `rgba(200,240,96,.04)` → `rgba(144,149,255,.04)` (purple)
4. Fixed `#bottom-bar` background: `rgba(9,9,11,.92)` → `rgba(3,5,46,.92)` (navy match)
5. Fixed `.btn:hover` text: `color: #09090b` → `color: #fff` (light text on dark purple)
6. Updated logo: `color: var(--accent)` → `color: var(--text)` with `em` using `var(--purple)`, matching Music01s pattern

### Token Audit

All CSS custom properties used in MusicSplit resolve correctly to themes.css:
- `var(--accent)`, `var(--bg)`, `var(--border)`, `var(--border2)`
- `var(--ff-body)`, `var(--ff-mono)`, `var(--ff-title)`
- `var(--muted)`, `var(--muted2)`, `var(--purple)`, `var(--s1)`, `var(--text)`

## Verification

- themes.css linked: YES
- No `:root {}` block: YES
- No lime hex `#c8f060`: YES
- No old bg `#09090b`: YES
- No lime RGBA `rgba(200,240,96`: YES
- orb-a uses `rgba(144,149,255,.06)`: YES
- orb-b uses `rgba(140,247,255,.04)`: YES
- Bottom bar uses `rgba(3,5,46,.92)`: YES
- Button hover uses `color: #fff`: YES

## Commits

| Task | Description | Commit |
|------|-------------|--------|
| 1+2 | Migrate MusicSplit to themes.css purple/cyan palette | 0353231 |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Logo color updated to match Music01s pattern**
- **Found during:** Task 2 (logo consistency check)
- **Issue:** Logo used `color: var(--accent)` (purple) with `em` using `var(--text)` — visually inverted vs Music01s
- **Fix:** Changed logo to `color: var(--text)` and `em` to `color: var(--purple)`, matching the Music01s styling convention
- **Files modified:** MusicSplit/index.html
- **Commit:** 0353231

## Self-Check: PASSED

- MusicSplit/index.html: EXISTS
- Commit 0353231: EXISTS
- No lime colors remain: CONFIRMED
- themes.css link present: CONFIRMED
