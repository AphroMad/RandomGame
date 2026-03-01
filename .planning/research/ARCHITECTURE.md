# Architecture Research

**Domain:** Static multi-game collection website (vanilla HTML/CSS/JS, GitHub Pages)
**Researched:** 2026-03-01
**Confidence:** HIGH — Based on direct codebase audit of all existing files; no speculation required.

---

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Pages Host                       │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────┐ │
│  │ index.html │  │ Music01s/  │  │ MusicSplit/│  │PokeGue │ │
│  │ (homepage) │  │ index.html │  │ index.html │  │ss/     │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └───┬────┘ │
│        │               │               │              │      │
│        └───────────────┴───────────────┴──────────────┘      │
│                               │                              │
├───────────────────────────────┼──────────────────────────────┤
│                    SHARED LAYER                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  themes.css  (root CSS custom properties — tokens)    │   │
│  └───────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Google Fonts CDN (Bebas Neue, DM Mono, DM Sans)      │   │
│  └───────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    GAME-SPECIFIC LAYER                       │
│  ┌──────────────────┐  ┌──────────────────┐                  │
│  │  Game CSS        │  │  Game JS         │                  │
│  │  (styles)        │  │  (logic/data)    │                  │
│  └──────────────────┘  └──────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `themes.css` (root) | Canonical design tokens: colors, fonts, gradients, states | `:root {}` CSS custom properties; game pages load via `../themes.css` |
| `index.html` (root) | Homepage: game list, navigation entry point | Self-contained HTML + inline `<style>` |
| `GameName/index.html` | Game entry point: page structure + game UI | Imports `../themes.css`; game CSS inline or via external file |
| Game CSS file | Game-specific layout and component styles | External `.css` only needed if game spans multiple pages |
| Game JS file(s) | Game logic, data, state management | Vanilla JS, either inline `<script>` or external `.js` |

---

## Current State: What Exists vs. Target State

### Actual File Layout (as audited)

```
RandomGame/
├── index.html              # Homepage — uses themes.css, inline <style>
├── themes.css              # CANONICAL token file (fonts + dark/light themes)
│
├── Music01s/
│   ├── index.html          # All styles inline in <style> tag; links ../themes.css
│   └── songs.js            # Auto-generated song data array (SONGS constant)
│
├── MusicSplit/
│   ├── index.html          # Divergent: has own :root {} inline, no ../themes.css link
│   │                       # Uses different accent (#c8f060 lime vs #9095FF purple)
│   ├── player.js           # (present but content in index.html inline script)
│   └── utils.js            # (present but content in index.html inline script)
│
└── PokeGuess/
    ├── index.html          # Links ../themes.css AND assets/css/themes.css (conflict)
    ├── game.html           # The active game page
    └── assets/
        ├── css/
        │   ├── themes.css  # DUPLICATE token file with different accent color (#c8f060)
        │   └── style.css   # All game CSS; well-organized external file
        └── js/
            ├── data.js     # Pokemon data fetching (PokeAPI)
            ├── setup.js    # Setup page logic (ES module)
            └── game.js     # Game logic (ES module)
```

### Key Divergences Found (Confidence: HIGH)

| Issue | MusicSplit | PokeGuess | Music01s |
|-------|-----------|-----------|----------|
| Links `../themes.css` | No — own `:root` inline | Partially — also has local `assets/css/themes.css` | Yes |
| Accent color | `#c8f060` (lime) | `#c8f060` (lime) in local themes.css | `#9095FF` (purple, from shared) |
| Orb background colors | Lime-tinted `rgba(200,240,96)` | Lime-tinted `rgba(200,240,96)` | Purple-tinted via shared |
| Noise overlay | Inline in `<style>` | In `assets/css/style.css` | Inline in `<style>` |
| Reset CSS | Inline in `<style>` | In `assets/css/style.css` | Inline in `<style>` |
| Font loading | Google Fonts CDN link | Google Fonts CDN link | Google Fonts CDN link |

**Critical finding:** There are effectively two color schemes in use. Homepage and Music01s use the purple/pink/blue gradient palette from the canonical `themes.css`. MusicSplit and PokeGuess use a lime (#c8f060) accent. Unification is the primary architectural work.

---

## Recommended Project Structure (Target State)

```
RandomGame/
├── index.html              # Homepage
├── themes.css              # Canonical tokens — all games reference this
├── shared.css              # (Optional) Shared structural patterns: orbs, noise, reset, scrollbar
│
├── Music01s/
│   ├── index.html          # Links: ../themes.css [+ ../shared.css if created]
│   ├── style.css           # Game-specific CSS (extracted from inline <style>)
│   └── songs.js            # Game data
│
├── MusicSplit/
│   ├── index.html          # Links: ../themes.css [+ ../shared.css if created]
│   │                       # Remove inline :root{} — use tokens from themes.css
│   ├── style.css           # Game-specific CSS
│   ├── player.js           # Game logic
│   └── utils.js            # Utilities
│
└── PokeGuess/
    ├── index.html          # Links: ../themes.css only (remove local assets/css/themes.css)
    ├── game.html           # Links: ../themes.css only
    └── assets/
        ├── css/
        │   └── style.css   # Game CSS only — no token duplication
        └── js/
            ├── data.js
            ├── setup.js
            └── game.js
```

### Structure Rationale

- **`themes.css` at root:** Single source of truth for all design tokens. All games reference it with `../themes.css`. No game duplicates or overrides it.
- **`shared.css` at root (optional):** If the noise overlay, orb markup, CSS reset, and scrollbar styles are extracted into one file, every game gains them for free with one additional link. This is optional but eliminates ~30 lines of duplicated CSS per game.
- **Game-specific CSS as external files:** Keeps `index.html` readable. Only necessary when the game has enough CSS to warrant it (Music01s currently has it all inline — extracting to `style.css` is the right move for consistency).
- **No shared JS:** Games are fully independent in logic. Shared JS is overkill until a genuine utility (e.g., analytics, keyboard shortcuts) spans multiple games.

---

## Architectural Patterns

### Pattern 1: CSS Custom Property Token Cascade

**What:** A single root-level CSS file defines all design tokens as custom properties. Game pages inherit them by linking `../themes.css` before their own styles.

**When to use:** Always. This is the pattern already started with `themes.css` — the task is to enforce it consistently across all games.

**Trade-offs:** Extremely simple, no build tools needed, easy to theme-swap later via `data-theme` attribute; tokens are global (not scoped), which is fine for a project of this size.

**Example:**
```css
/* themes.css — root level */
:root {
  --bg:             #03052E;
  --accent:         var(--purple);
  --cta-gradient:   linear-gradient(90deg, var(--purple), var(--pink), var(--blue));
  --ff-title:       'Bebas Neue', sans-serif;
}

/* MusicSplit/index.html — after normalizing */
<link rel="stylesheet" href="../themes.css">
<style>
  /* Only game-specific styles here — no :root{} override */
  .group-row.playing { border-color: var(--accent); }
</style>
```

### Pattern 2: Homepage-to-Game Navigation via Relative `href`

**What:** The homepage links each game with `href="GameName/index.html"`. Each game links back with `href="../index.html"` on its logo/title element.

**When to use:** Always — this pattern is already established and correct for GitHub Pages static hosting with no routing.

**Trade-offs:** Simple and reliable; no JavaScript navigation needed; browser back button works natively.

**Example:**
```html
<!-- In any game's index.html — back link -->
<a href="../index.html" class="logo"><em>Music</em> 01s</a>
```

### Pattern 3: Self-Contained Game Pages (No Build Step)

**What:** Each game is a directory with its own `index.html`. Assets (CSS, JS, media) live alongside it. No module bundler, no compilation step.

**When to use:** Appropriate for this project's scale and hosting constraints (GitHub Pages, no server).

**Trade-offs:** No dead-code elimination or minification; manual HTML changes per game; scales well to ~10 games before organization becomes painful.

---

## Data Flow

### Navigation Flow

```
User visits GitHub Pages URL
    |
    v
index.html (homepage)
    |
    +-- click game link --> GameName/index.html
                                |
                                +-- game loads (JS initializes)
                                |
                                +-- user plays game (state in JS memory only)
                                |
                                +-- click logo/back --> ../index.html
```

### Theming Flow (CSS Custom Properties)

```
themes.css loaded first
    |
    v
:root CSS custom properties set (--bg, --text, --accent, etc.)
    |
    v
Game <style> or style.css reads tokens via var(--token-name)
    |
    v
Rendered page uses unified palette
```

### Game State (per-game, no persistence)

```
Page load
    |
    v
JS initializes (reads data file: songs.js / fetch from API)
    |
    v
User interaction --> JS mutates DOM directly
    |
    v
Game ends --> JS shows result UI
    |
    v
Page reload / navigate away --> all state lost (intentional, no backend)
```

---

## Component Boundaries

### What Is Shared vs. Game-Specific

| Element | Shared | Game-Specific | Notes |
|---------|--------|---------------|-------|
| Color tokens (--bg, --text, --accent, etc.) | Yes — `themes.css` | — | Games must not redeclare `:root` tokens |
| Font definitions (--ff-title, --ff-mono, etc.) | Yes — `themes.css` | — | |
| Google Fonts CDN `<link>` | Must be in each page `<head>` | — | No shared `<head>` in static HTML |
| Noise overlay CSS + markup | Candidate for `shared.css` | Currently duplicated | Pattern is identical in all games |
| Blur orb CSS + markup | Candidate for `shared.css` | Currently duplicated | Orb colors differ — need token alignment |
| CSS reset (`*, *::before, *::after`) | Candidate for `shared.css` | Currently duplicated | Identical in all games |
| Scrollbar styles | Candidate for `shared.css` | Currently duplicated | Identical in all games |
| Game layout / UI components | — | Yes — per-game CSS | Each game has unique layout needs |
| Game logic / state | — | Yes — per-game JS | Games are independent |
| Navigation markup | — | Each game embeds its own back link | Consistent pattern, not a shared file |

---

## Build Order for Normalization

The recommended order to normalize the existing three games:

### Step 1: Normalize `themes.css` (the foundation)

Before touching any game, ensure `themes.css` is the correct canonical source:
- Confirm it has all required tokens: `--purple`, `--pink`, `--blue`, `--cta-gradient`, semantic roles, font families.
- Decide on the official accent color (purple/pink/blue gradient vs lime) and commit to it in `themes.css`.

**Why first:** Every subsequent step depends on tokens being stable. Changing tokens after game CSS is updated causes cascading rework.

### Step 2: Normalize MusicSplit (highest divergence)

MusicSplit is the most out-of-sync game:
- Remove the inline `:root {}` block from its `<style>`.
- Add `<link rel="stylesheet" href="../themes.css">` to its `<head>`.
- Replace hardcoded lime color values with the canonical token (`var(--accent)` or appropriate semantic token).
- Update orb colors to match the canonical palette.

**Why second:** It's the biggest gap. Fixing it validates the token system is complete enough to cover all use cases.

### Step 3: Normalize PokeGuess (theme file conflict)

- Remove `PokeGuess/assets/css/themes.css` entirely.
- Ensure `PokeGuess/index.html` and `PokeGuess/game.html` only link `../themes.css`.
- Audit `assets/css/style.css` for any hardcoded color values that should reference tokens.

**Why third:** PokeGuess already links `../themes.css` — the fix is removal of the conflicting local copy, not a rewrite.

### Step 4: Normalize Music01s (extract inline CSS)

Music01s is token-compliant but has all CSS inline. Extract to `Music01s/style.css`:
- Move `<style>` contents to `Music01s/style.css`.
- Replace with `<link rel="stylesheet" href="style.css">`.

**Why fourth:** It's low risk — already using the right tokens, just needs extraction for consistency.

### Step 5: (Optional) Create `shared.css`

If the noise overlay, orbs, reset, and scrollbar are extracted to a root-level `shared.css`, add it to each game's `<head>` after `themes.css`. This is lowest priority — correctness of tokens matters more than eliminating duplicated structural CSS.

---

## Anti-Patterns

### Anti-Pattern 1: Game-Level `:root {}` Overrides

**What people do:** Define a `:root {}` block inside a game's `<style>` or CSS file with game-specific color values.

**Why it's wrong:** Defeats the purpose of `themes.css`. Any future palette change requires visiting every game. Creates inconsistency (MusicSplit currently does this — different accent color than homepage).

**Do this instead:** Use `themes.css` tokens everywhere. If a game needs a specific accent that differs, use a scoped selector on a container element: `.game-shell { --accent: var(--lime); }` — but prefer aligning all games to the same palette first.

### Anti-Pattern 2: Duplicate Theme File Per Game

**What people do:** Copy `themes.css` into each game directory (e.g., `PokeGuess/assets/css/themes.css`).

**Why it's wrong:** The copies immediately diverge. A color change requires updating N files. PokeGuess currently has this — its local copy has `#c8f060` lime while the canonical root has `#9095FF` purple.

**Do this instead:** Always link to `../themes.css` from the game directory. The relative path is the correct pattern for a flat directory structure.

### Anti-Pattern 3: Hardcoding Colors in Game CSS

**What people do:** Write `color: #9095FF` or `background: rgba(144,149,255,.07)` directly in game-specific CSS instead of `color: var(--purple)` or `background: rgba(144,149,255,.07)`.

**Why it's wrong:** A single palette tweak in `themes.css` won't propagate. Also makes the CSS harder to read — semantic token names document intent.

**Do this instead:** Always use the token: `color: var(--purple)`, `border-color: var(--accent)`, etc. The existing `themes.css` already defines the right tokens.

### Anti-Pattern 4: Inline `<style>` Containing Both Reset and Game Styles

**What people do:** Put CSS reset, token redefinition, and all game-specific styles in one large `<style>` block in `index.html`.

**Why it's wrong:** Hard to maintain, impossible to share. Music01s currently does this — 140+ lines of CSS inline makes the HTML hard to read.

**Do this instead:** Separate concerns into files. `themes.css` → reset-level shared styles → game-specific `style.css`.

---

## Scaling Considerations

This is a static personal project, so user-scale is not a concern. The relevant "scaling" is adding new games.

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 3 games (current) | Normalize existing games to token system — no new infrastructure |
| 5-10 games | `shared.css` at root pays off — one change propagates to all games |
| 10+ games | Consider a simple build step (e.g., a Python script that injects shared `<head>` content) — still no bundler needed |

### Scaling Priorities

1. **First bottleneck:** Token drift — without a canonical `themes.css`, each new game invents its own colors. Fix by enforcing the single-source `themes.css` now.
2. **Second bottleneck:** Repeated `<head>` boilerplate (font CDN link, themes.css link, viewport meta) across every new game page. A lightweight Python script that writes the shared `<head>` block could help at 10+ games, but is premature now.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Google Fonts CDN | `<link>` in each page `<head>` | Must be present on every game page — no single shared `<head>` in static HTML |
| PokeAPI (for PokeGuess) | `fetch()` at runtime from `data.js` | Client-side only; no CORS issues |
| Tone.js MIDI CDN (for MusicSplit) | `<script src="cdn...">` in head | External dependency, loaded on demand |
| GitHub Pages | Static file serving | No server-side routing; all navigation is file-path based |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `themes.css` → game pages | CSS cascade (link tag) | One-way: tokens defined in themes.css, consumed by game pages |
| Homepage → games | HTML anchor href | One-way navigation, no state passed between pages |
| Game JS → DOM | Direct DOM manipulation | All games use vanilla `getElementById` / `querySelector`; no virtual DOM |
| Multi-page games (PokeGuess) | `sessionStorage` or URL params | PokeGuess uses `setup.js` → `game.html` flow; state should pass via `sessionStorage` (current implementation — confirmed in `setup.js`) |

---

## Sources

- Direct codebase audit of all HTML, CSS, and JS files (2026-03-01) — HIGH confidence
- CSS Custom Properties specification (MDN): well-established pattern for design token systems
- GitHub Pages static hosting constraints: no server-side code, file-path-based routing only

---

*Architecture research for: RandomGame — static multi-game collection website*
*Researched: 2026-03-01*
