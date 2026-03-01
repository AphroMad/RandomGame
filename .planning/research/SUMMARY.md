# Project Research Summary

**Project:** RandomGame — Static Mini-Game Collection
**Domain:** Multi-page static game portal (vanilla HTML/CSS/JS, GitHub Pages)
**Researched:** 2026-03-01
**Confidence:** HIGH

## Executive Summary

RandomGame is a personal static web portal hosting three independent mini-games (Music01s, MusicSplit, PokeGuess) on GitHub Pages. This milestone is explicitly a polish and unification effort — not a greenfield build. The tech stack is fully locked by constraints: vanilla HTML/CSS/JS, no build step, raw files served by GitHub Pages. The primary problem to solve is visual incoherence: two competing color palettes exist in the codebase (purple/pink/blue on the homepage and Music01s vs. lime green on MusicSplit and PokeGuess), each game reinvents shared structural CSS (noise overlay, orbs, reset), and mobile layouts are broken on at least two games due to `height: 100vh` + `overflow: hidden` traps.

The recommended approach is a three-phase normalization: first consolidate the design token layer (`themes.css` as single source of truth, eliminating all per-game `:root` overrides and duplicate theme files), then fix mobile responsiveness game by game, then standardize navigation and cosmetic consistency across all three games. This order is dictated by hard dependencies — the mobile CSS fixes and color corrections in MusicSplit are meaningless until `themes.css` is actually imported, and navigation polish only makes sense on a visually coherent product.

The key risks are deceptively invisible: MusicSplit uses the same CSS variable names as `themes.css` but defines different values inline, so the game will appear to work but render the wrong colors until the inline `:root` block is removed and the import is added. Orb colors are hardcoded RGBA values that survive a theme migration unless explicitly hunted down. The Music01s mobile layout requires structural surgery (`100vh` + `overflow: hidden` must be removed), not just media queries applied on top of a broken base.

---

## Key Findings

### Recommended Stack

The stack requires no changes. Vanilla HTML5, CSS Custom Properties via `:root` variables, and vanilla ES Modules (where already in use) are the correct tools. The `themes.css` file at the repo root is the design token system — it is partially functional today and must be enforced as the single source of truth across all games. No libraries should be added. The one external dependency (Tone.js MIDI via jsDelivr CDN in MusicSplit) stays as-is.

The only tooling consideration is local development: because PokeGuess uses ES modules (`type="module"`), a local dev server (VS Code Live Server or `python -m http.server`) is required — `file://` protocol breaks ES modules. This should be documented and standardized across all games.

**Core technologies:**
- Vanilla HTML5: per-game page structure — no framework, GitHub Pages serves raw files directly
- CSS Custom Properties (`themes.css`): design token system — already partially in use, must be enforced consistently
- CSS `clamp()` + `min-height: 100svh`: responsive layout — replace broken `100vh` + `overflow:hidden` pattern
- Vanilla ES Modules: shared utilities if needed — PokeGuess already uses this, adopt for any new shared code
- Google Fonts CDN (Bebas Neue, DM Mono, DM Sans): typography — already loaded on all pages, keep as-is

### Expected Features

This milestone is a polish milestone. All deliverables are table stakes (things users expect from a coherent product), not new functionality. No new game features are in scope.

**Must have (table stakes) — this milestone:**
- MusicSplit adopts `../themes.css` (remove inline `:root`, add `<link>` tag) — prerequisite for all color work
- Consistent accent palette across all games (purple/cyan, not lime) — visual coherence
- Noise overlay and ambient orbs present and correctly colored in all 3 games — visual signature consistency
- Mobile layout functional at 375px width — no horizontal scroll, no clipped controls
- Touch targets minimum 44px on all primary action buttons — usability on mobile
- Standardized logo/header markup and back-navigation across all 3 games
- Consistent `<title>` format and `lang="fr"` attribute on all pages

**Should have (v1.x polish, after core is stable):**
- Page entry fade-in animation (pure CSS, low cost)
- Keyboard navigation improvements for PokeGuess (number keys 1-4) and MusicSplit (spacebar play/stop)
- Semantic HTML pass (`<main>`, `<header>`, `<nav>`)

**Defer (v2+):**
- Game template pattern extraction — only valuable when adding a 4th game
- Light theme completion — not needed for current use case
- PWA / Service Worker — games load remote assets, offline caching is complex and unnecessary

### Architecture Approach

The architecture is a flat directory structure with a shared CSS token layer. Each game is a self-contained directory (`GameName/index.html`) that imports `../themes.css` to inherit design tokens, then adds its own game-specific CSS and JS. The critical architectural fix for this milestone is eliminating the two instances of divergence from this model: MusicSplit has its own inline `:root` instead of importing `themes.css`, and PokeGuess has a conflicting local copy of `themes.css` with different values. The optional `shared.css` at root (for noise overlay, orbs, CSS reset, scrollbar) would eliminate ~30 lines of duplicated CSS per game and is worth introducing during the normalization pass.

**Major components:**
1. `themes.css` (root) — canonical design tokens: colors, fonts, gradients; all games reference via `../themes.css`
2. `shared.css` (root, to be created) — structural CSS shared by all games: noise overlay, orbs, CSS reset, scrollbar
3. Game directories (`Music01s/`, `MusicSplit/`, `PokeGuess/`) — self-contained game logic, CSS, and assets; no cross-game dependencies
4. Homepage (`index.html`) — navigation entry point linking to all games

**Build order for normalization (dictated by dependencies):**
1. Lock `themes.css` tokens (confirm all required variables are present and correct)
2. Normalize MusicSplit (highest divergence — own `:root`, wrong accent)
3. Normalize PokeGuess (remove duplicate local `themes.css`)
4. Normalize Music01s (extract inline CSS, add noise overlay + orbs)
5. (Optional) Create `shared.css` and consolidate structural CSS

### Critical Pitfalls

1. **Silent theme mismatch via same variable names** — MusicSplit uses `--accent` but defines it as `#c8f060` (lime) inline; after switching to `themes.css`, every `var(--accent)` now points to purple and lime-specific UI elements (playing indicators, progress) will look wrong if not audited. Prevention: after removing the inline `:root`, audit every `var(--accent)` usage in MusicSplit and verify visually.

2. **`100vh` + `overflow:hidden` traps mobile users in Music01s** — On iOS Safari, `100vh` includes the browser chrome; the layout clips and bottom controls become unreachable. Prevention: replace with `min-height: 100svh` + remove `overflow: hidden` from `body`. Test on a real iOS device, not just Chrome DevTools.

3. **Hardcoded RGBA orb colors survive theme migration** — MusicSplit and PokeGuess orbs use `rgba(200,240,96,...)` (lime) hardcoded in CSS, not CSS variables. These do not change when `themes.css` is adopted. Prevention: add `--orb-a-color` and `--orb-b-color` tokens to `themes.css` and update all orb rules to use them, in the same commit as the theme migration.

4. **Copy-pasted noise overlay creates sync debt** — The `body::after` noise SVG is duplicated across 4 files. Any future change requires updating all 4. Prevention: move the noise rule to `themes.css` in one commit and delete all per-file copies; grep for `feTurbulence` to verify zero inline duplicates remain.

5. **PokeGuess `game.html` has no path back to root homepage** — The in-game back link points to `index.html` (PokeGuess setup), not `../../index.html` (root). Users who share a direct game link cannot find the game list. Prevention: audit all game states (setup, mid-game, result) and confirm the logo/back link reaches root `index.html`.

---

## Implications for Roadmap

Based on research, the phase structure is dictated by hard CSS cascade dependencies. Design tokens must be correct before colors can be fixed; mobile layout surgery must happen before mobile QA is meaningful; navigation polish only makes sense on a visually coherent, working product.

### Phase 1: Shared CSS Foundation

**Rationale:** Every subsequent fix depends on `themes.css` being the single source of truth. MusicSplit's inline `:root` and PokeGuess's local `themes.css` copy actively block all color normalization work. This must come first — it is the unblocking phase.
**Delivers:** A coherent visual baseline across all 3 games — same accent color (purple/cyan), same noise overlay, same orb colors. The product looks like one product for the first time.
**Addresses:** themes.css adoption in MusicSplit, consistent accent palette, noise overlay in Music01s, orb colors in MusicSplit and PokeGuess
**Avoids:** Silent theme mismatch (Pitfall 1), hardcoded orb colors (Pitfall 3), copy-pasted noise sync debt (Pitfall 4)

Tasks:
- Confirm `themes.css` has all required tokens; add `--orb-a-color`, `--orb-b-color` if missing
- MusicSplit: add `<link rel="stylesheet" href="../themes.css">`, remove inline `:root {}`
- MusicSplit: audit all `var(--accent)` usages, update orb background values
- PokeGuess: delete `assets/css/themes.css`, remove duplicate `<link>` from both HTML files
- Music01s: add noise overlay and orbs (copy pattern from homepage, use tokens)
- Consolidate noise overlay into `themes.css`; optionally create `shared.css` for orbs + reset

### Phase 2: Mobile Responsiveness

**Rationale:** Music01s has a structurally broken mobile layout (`100vh` + `overflow: hidden`) that cannot be fixed with media queries alone — it requires removing the layout constraint first. MusicSplit has no responsive rules at all. This phase requires Phase 1 to be complete so that colors are correct when testing on mobile.
**Delivers:** All 3 games playable on 375px-wide screens with no horizontal scroll, no clipped content, and tappable controls.
**Addresses:** Mobile layout for Music01s and MusicSplit, `dvh`/`svh` adoption, touch target minimum 44px enforcement
**Avoids:** `100vh` + `overflow:hidden` mobile trap (Pitfall 2)

Tasks:
- Music01s: replace `height: 100vh` with `min-height: 100svh`; remove `overflow: hidden` from `html, body`; add `flex-wrap` on control rows; test on iOS Safari
- MusicSplit: add mobile media queries; ensure controls are reachable at 375px
- Homepage: verify centered layout holds at 375px (likely already OK)
- All games: audit primary action buttons for `min-height: 44px`
- Add `inputmode="search"` to Music01s text input for iOS keyboard handling

### Phase 3: Navigation and Consistency

**Rationale:** With colors and mobile layouts correct, the final phase addresses the "one product" feel at the navigation and metadata level. These are lower-severity issues (broken navigation still works via browser back button) but are required for the product to feel finished.
**Delivers:** Consistent navigation pattern across all games, correct HTML metadata, standardized header markup.
**Addresses:** Inconsistent back-navigation, PokeGuess `game.html` missing root nav, `lang` attribute, `<title>` format
**Avoids:** Navigation inconsistency (Pitfall 5)

Tasks:
- Define canonical navigation pattern: logo-as-link in top-left, always pointing to `../index.html`
- Apply pattern consistently across all 3 games (Music01s, MusicSplit, PokeGuess index + game.html)
- Fix PokeGuess `game.html` back link to reach root `index.html`
- Set `lang="fr"` on all pages (currently `en` on Music01s and MusicSplit)
- Standardize `<title>` format: `[Game Name] — Random Games`

### Phase Ordering Rationale

- Phase 1 before Phase 2: MusicSplit's color fixes are impossible until `themes.css` is imported; fixing mobile layout on top of wrong colors wastes a test cycle
- Phase 1 before Phase 3: Navigation styling references CSS tokens — tokens must be stable
- Phase 2 before Phase 3: No point polishing navigation chrome until the core game layout is mobile-functional
- Phase 3 last: It is the least blocking and most cosmetic — safe to defer if time is limited

### Research Flags

Phases with standard patterns (no additional research needed):
- **Phase 1:** CSS Custom Properties cascade is a thoroughly documented, stable web standard. The specific changes (add `<link>`, remove `:root {}`) are mechanical and low-risk.
- **Phase 2:** `min-height: 100svh` has documented browser support (2022+, all modern mobile browsers). The pattern is established.
- **Phase 3:** Metadata and HTML attribute changes are trivial. No research needed.

No phases require additional research. All implementation patterns are either already established in the codebase or are well-documented web platform features.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Based on direct codebase audit; stack is already fixed by project constraints — no speculation required |
| Features | HIGH | Feature scope defined by direct gap analysis between current codebase state and target coherent product; no guessing |
| Architecture | HIGH | Direct file inspection; all findings are concrete file-level issues with specific fixes |
| Pitfalls | HIGH | Every pitfall is a real bug or pattern observed directly in existing files, not theoretical risk |

**Overall confidence:** HIGH

### Gaps to Address

- **`svh` vs `dvh` unit choice:** Research recommends `min-height: 100svh` (small viewport height — most conservative, ensures content is never clipped by browser chrome). `dvh` (dynamic) would also work but reflows on scroll. Decision: use `svh` for fixed-layout games (Music01s), verify during implementation if `dvh` is more appropriate for scroll-friendly layouts.
- **MusicSplit lime color intent:** Several MusicSplit UI states (playing row highlight, progress indicator) use `--accent` which was lime (#c8f060). After migration to purple, these elements may need design review to confirm purple reads correctly in context. Not a blocker, but requires a visual QA pass after Phase 1.
- **`shared.css` decision:** Whether to create a `shared.css` for orbs, noise, and reset is left optional in research. Recommendation is to create it — the noise overlay consolidation is required (Pitfall 4) and doing orbs + reset at the same time is low-overhead. Confirm during Phase 1 planning.

---

## Sources

### Primary (HIGH confidence)
- Direct codebase audit (2026-03-01): `/index.html`, `/themes.css`, `/Music01s/index.html`, `/MusicSplit/index.html`, `/PokeGuess/index.html`, `/PokeGuess/game.html`, `/PokeGuess/assets/css/themes.css`, `/PokeGuess/assets/css/style.css` — all findings grounded in actual file contents

### Secondary (MEDIUM confidence)
- MDN Web Docs (training data): CSS viewport units (`svh`, `dvh`), CSS Custom Properties cascade behavior, ES module browser support
- Can I Use baseline data (training data): `svh`/`dvh` 2022 baseline, `clamp()` 2020 baseline, `dvh` 2023 baseline

### Tertiary (noted for validation)
- Browser behavior of `100vh` on iOS Safari with browser chrome: well-documented community issue since 2017; `svh` introduced as the standard fix in 2022; verify on real device during Phase 2 QA

---

*Research completed: 2026-03-01*
*Ready for roadmap: yes*
