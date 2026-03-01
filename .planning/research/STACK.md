# Stack Research

**Domain:** Static multi-page mini-game collection (vanilla HTML/CSS/JS, GitHub Pages)
**Researched:** 2026-03-01
**Confidence:** HIGH (primary evidence is direct codebase audit; all claims grounded in what already exists or well-established web platform capabilities)

---

## Executive Note

This is a *unification* milestone, not a greenfield project. The tech stack is largely fixed by constraints (GitHub Pages, no build tools, vanilla only). Research focus is: which specific patterns and supporting tools normalize the existing three games without adding a build step.

---

## Recommended Stack

### Core Technologies

| Technology | Version/Status | Purpose | Why Recommended |
|------------|---------------|---------|-----------------|
| Vanilla HTML5 | Living standard | Page structure per game | Already in use; GitHub Pages constraint means no SSG/framework. Single `index.html` per game directory is the correct model for this scale. |
| CSS Custom Properties (`:root` vars) | Baseline 2017 (100% browser support) | Shared design tokens | Already partially in use via `themes.css`. Extend — do NOT replace. The var naming scheme (`--bg`, `--s1`, `--text`, `--accent`, `--cta-gradient`) is already established and working. |
| Vanilla ES Modules (`type="module"`) | Baseline 2018 (universal support) | Shared JS utilities without bundling | PokeGuess already uses this pattern. Adopt for any new shared code (e.g. a nav component loader or utility module). Music01s and MusicSplit use classic scripts — keep them unless refactoring is scoped. |
| CSS `clamp()` + Flexbox/Grid | Baseline 2021 | Responsive layout | Already used on homepage and PokeGuess. Music01s uses `overflow:hidden; height:100vh` which breaks on mobile — replace with a `clamp()`-based min-height flow. |
| Google Fonts (CDN) | Current | Bebas Neue, DM Mono, DM Sans | All pages already load the same URL. Keep it. No version to pin — use `display=swap` which all pages already do. |

### Supporting Libraries (Zero-Dependency Policy — Import Only What Exists)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@tonejs/midi` (CDN) | `build/Midi.js` via jsDelivr | MIDI parsing in MusicSplit | Already in use via `<script src="https://cdn.jsdelivr.net/npm/@tonejs/midi/build/Midi.js">`. Do not change. Avoid upgrading mid-milestone — no regression risk needed. |
| No additional libraries | — | — | Every feature needed (audio playback, fetch, DOM manipulation) is native browser API. Adding even a small library (Lodash, etc.) introduces a dependency with no upside for this scale. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| No build tool (intentional) | GitHub Pages deploys raw files | Do NOT add Vite, Parcel, or Webpack. The constraint is real: the repo is deployed directly. Any tooling must produce output files, not be part of the serving pipeline. |
| Python `build.py` (existing) | Generates `songs.js` for Music01s | Keep as-is. Out of scope for this milestone. |
| Python `generate.py` / `details_midi.py` (existing) | MusicSplit MIDI generation | Keep as-is. Out of scope. |
| Browser DevTools (responsive mode) | Mobile QA | Use Chrome/Firefox responsive simulator to test at 375px (iPhone SE), 390px (iPhone 14), 768px (iPad). No additional tooling needed. |
| Live Server (VS Code extension) or `python -m http.server` | Local dev server | Required because ES modules (`type="module"`) fail over `file://`. PokeGuess already needs this. Standardize across all games. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Any JS framework (React, Vue, Svelte) | Violates project constraint; requires build step; overkill for 3 static game pages | Vanilla JS with ES modules for shared utilities |
| CSS preprocessors (Sass, Less, PostCSS) | Requires build step; GitHub Pages serves raw files | Native CSS custom properties — already sufficient for this design system |
| CSS framework (Tailwind, Bootstrap) | Would conflict with existing hand-crafted design language; Tailwind requires a build step; Bootstrap imposes its own variable names that clash with `--bg`, `--s1` etc. | Extend `themes.css` with shared utility classes |
| npm dependencies in production | No bundler = no tree-shaking = full library loaded; GitHub Pages doesn't run Node | CDN scripts (jsDelivr) for the one library already needed (Tone.js MIDI) |
| Web Components / Custom Elements | Adds complexity without benefit at 3-game scale; Safari had historical quirks (now resolved, but adds cognitive overhead) | ES module pattern for shared logic (see below) |
| `localStorage` for theme persistence | Not needed — dark theme is the only theme for this milestone | Hardcode `data-theme="dark"` or omit (`:root` defaults are already dark) |
| Inline `<style>` blocks inside `<script>` tags | Already used in Music01s (all CSS in `<style>` in `<head>`) — acceptable for game-specific styles, but shared/structural CSS must move to external files | External CSS files per the existing PokeGuess model |

---

## Stack Patterns by Variant

**For game-specific styles:**
- Keep them in an external `style.css` per game directory (PokeGuess model).
- If a game currently has all CSS inline in `<head>` (Music01s, MusicSplit), move shared/structural CSS to a separate `style.css`. Game-logic CSS can stay inline or move — team preference.

**For shared navigation:**
- Do NOT reach for a JS framework's router. Use a lightweight ES module (`shared/nav.js`) that injects the back-to-homepage link via `document.getElementById`. Each game's HTML has an empty `<div id="nav"></div>` placeholder.
- Alternative (simpler): hardcode the `<a href="../index.html">` in each page — no JS needed. Given only 3 games, this is defensible.
- Recommendation: **hardcode it**. The nav is one link. An ES module for one link is over-engineering.

**For shared structural CSS (noise overlay, orbs, scrollbar):**
- Move duplicated structural CSS (the `body::after` noise SVG, `.orb` styles, scrollbar rules) into `themes.css`. Every page already imports it. This is the highest-leverage refactor.

**For mobile responsiveness:**
- Use `min-height: 100dvh` (dynamic viewport height) instead of `height: 100vh` where fullscreen layout is needed — `dvh` accounts for mobile browser chrome. Baseline support: 2023 (Chrome 108+, Safari 15.4+, Firefox 101+).
- Use `clamp()` for font sizes (already in homepage and PokeGuess — standardize across Music01s and MusicSplit).
- Use `flex-wrap` on button/control rows that currently overflow on narrow screens.

---

## Critical Palette Conflict (Action Required)

This is the most important finding from the codebase audit.

| Game | Accent color | Theme source |
|------|-------------|-------------|
| Homepage | `--purple: #9095FF`, `--pink: #DBA1FF`, `--blue: #8CF7FF` | Root `themes.css` |
| Music01s | Imports root `themes.css` — uses `var(--purple)` | Correct |
| PokeGuess (game.html) | Imports root `themes.css` — uses `var(--purple)` | Correct |
| PokeGuess (index.html) | Imports root `themes.css` AND `assets/css/themes.css` | Conflict: local overrides root |
| PokeGuess `assets/css/themes.css` | `--accent: #c8f060` (lime green), different `--bg: #09090b` | Diverged palette |
| MusicSplit `index.html` | Inline `:root` with `--accent: #c8f060` (lime green), no import of root `themes.css` | Fully diverged |

**Resolution:** Delete `PokeGuess/assets/css/themes.css`. Update MusicSplit to import `../themes.css`. Remove the inline `:root` block from MusicSplit. All games then inherit the root `themes.css` purple/pink/blue palette. This is the primary deliverable of the design normalization milestone.

---

## Version Compatibility

| Asset | Compatible With | Notes |
|-------|----------------|-------|
| `@tonejs/midi` (CDN, current) | Native `AudioContext` API | No known conflicts. Do not upgrade during this milestone. |
| ES Modules (`type="module"`) | Chrome 61+, Firefox 60+, Safari 10.1+ | Universal in 2025. PokeGuess already uses this. |
| CSS `dvh` unit | Chrome 108+, Safari 15.4+, Firefox 101+ | Safe to use; covers effectively all active mobile browsers as of 2025. |
| CSS `clamp()` | Chrome 79+, Firefox 75+, Safari 13.1+ | Baseline 2020 — fully safe. |
| CSS `mask-composite: exclude` (gradient border trick) | Chrome 96+, Firefox 53+, Safari 15.4+ | Used in homepage and PokeGuess `.start-btn`. Safe. `-webkit-mask-composite: xor` fallback already present. |

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|------------------------|
| Extend root `themes.css` | Per-game CSS files for all theming | Never for this project — defeats the unification goal |
| Hardcode nav link per page | ES module nav injector | Only when nav becomes complex (multiple items, active states) — not now |
| No build tool | Vite in dev only, raw files committed | Acceptable only if the team wants HMR during development; output files still need to be committed. For 3 static games, the complexity overhead is not worth it. |
| `dvh` for viewport height | `100vh` | Use `100vh` only as a fallback; prefer `dvh` for mobile correctness |

---

## Sources

- Direct codebase audit (HIGH confidence) — `/themes.css`, `/index.html`, `/Music01s/index.html`, `/MusicSplit/index.html`, `/PokeGuess/index.html`, `/PokeGuess/game.html`, `/PokeGuess/assets/css/themes.css`, `/PokeGuess/assets/css/style.css`
- MDN Web Docs (training data, HIGH confidence for CSS custom properties and ES modules — both are established standards since 2017-2018 with 100% baseline support)
- Can I Use baseline data (training data, MEDIUM confidence — `dvh` unit confirmed ~2023 baseline; verify at caniuse.com if critical)

---

*Stack research for: RandomGame — static mini-game collection unification milestone*
*Researched: 2026-03-01*
