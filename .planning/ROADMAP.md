# Roadmap: RandomGame

## Overview

This milestone is a polish and unification effort across the three existing games (Music01s, MusicSplit, PokeGuess). All six v1 requirements are theme normalization tasks — they are tightly coupled and must ship together as one coherent visual unification phase. When complete, every game will share the same design token layer, visual signature (noise overlay, orbs, accent palette), and look like one product.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Theme Unification** - Make all three games share `themes.css` as the single source of truth for colors, noise overlay, and ambient orbs

## Phase Details

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
**Plans:** 3 plans
- [x] 01-01-PLAN.md — PokeGuess cleanup (delete duplicate themes.css, fix orb colors) + Music01s additions (noise overlay, ambient orbs)
- [x] 01-02-PLAN.md — MusicSplit full migration (remove inline :root, link themes.css, replace all lime values with purple/cyan)
- [x] 01-03-PLAN.md — Cross-game automated verification + visual checkpoint

## Progress

**Execution Order:**
Phases execute in numeric order: 1

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Theme Unification | 3/3 | Complete | 2026-03-01 |
