# Pitfalls Research

**Domain:** Multi-page static mini-game collection — design normalization milestone
**Researched:** 2026-03-01
**Confidence:** HIGH (all findings verified directly from codebase inspection)

---

## Critical Pitfalls

### Pitfall 1: Shared Variable Name, Different Value — The Silent Theme Mismatch

**What goes wrong:**
MusicSplit defines its own `:root` block with `--accent: #c8f060` (lime green) instead of
importing `themes.css`. When you touch MusicSplit during the normalization pass, you may
believe `var(--accent)` refers to the homepage purple (`#9095FF`) — it does not. Every button
hover, active indicator, progress bar, and playing state in MusicSplit renders lime green.

**Why it happens:**
MusicSplit was built independently with a different visual identity. It never linked to
`themes.css`. The variable *names* (`--bg`, `--s1`, `--border`, `--accent`, `--text`, `--muted`,
`--ff-title`, `--ff-mono`, `--ff-body`) are identical, so the game "works" — just with wrong
colors. The divergence is invisible unless you open both pages side by side.

**How to avoid:**
1. Before touching any game, confirm `<link rel="stylesheet" href="../themes.css">` is present
   in the `<head>`.
2. Delete any inline `:root { }` block that redefines the same variables — do not merge them,
   remove the inline block entirely.
3. After switching MusicSplit to `themes.css`, audit every `var(--accent)` usage: they must now
   point to `var(--purple)` or `var(--accent)` from the shared file. Lime-specific UI intent
   (e.g., playing indicator color) must be explicitly reassigned to the new palette.

**Warning signs:**
- The `<link>` tag for `themes.css` is absent from the game's `<head>`.
- A `:root { }` block inside `<style>` or a `.css` file redefines `--bg`, `--accent`, or font
  variables.
- UI elements glow lime/green instead of purple/cyan after clicking "normalize themes."

**Phase to address:** Shared CSS foundation phase (must be completed before any visual polish work)

---

### Pitfall 2: 100vh + overflow:hidden Traps Mobile Users

**What goes wrong:**
Music01s sets `html, body { height: 100%; overflow: hidden; }` and `.shell { height: 100vh; }`.
On iOS Safari and Android Chrome, `100vh` is calculated including the browser chrome (URL bar,
tab bar). When those bars appear on scroll, the viewport shrinks but the game's layout does not
reflow — the bottom controls (skip button, confirm, input) slide under the browser UI and become
untappable. The game is literally unplayable on mobile without scrolling, which is disabled.

**Why it happens:**
The layout was designed for desktop: 6 fixed-height rows fill the screen, controls sit at the
bottom. `overflow: hidden` was added to prevent scrollbars from appearing. On mobile, this
becomes a trap: the browser chrome steals vertical space, the layout overflows inward, and
nothing is reachable.

**How to avoid:**
- Replace `height: 100vh` with `min-height: 100svh` (small viewport height — does not include
  browser chrome). Supported in all modern mobile browsers as of 2023.
- Remove `overflow: hidden` from `html, body`. Instead, hide overflow only on specific
  containers where needed (e.g., the autocomplete dropdown).
- Test the fix with browser devtools in mobile responsive mode with the device toolbar enabled,
  then verify on an actual iPhone with Safari.

**Warning signs:**
- Bottom input/buttons invisible or unreachable on iPhone Safari.
- The game "looks fine" on Chrome desktop devtools but fails on real devices.
- Any layout using `height: 100vh` + `overflow: hidden` on `body`.

**Phase to address:** Mobile responsiveness phase

---

### Pitfall 3: Hardcoded Orb Colors Survive the Theme Migration

**What goes wrong:**
Ambient orbs (`.orb-a`, `.orb-b`) have hardcoded RGBA color values embedded in their
`background` property. MusicSplit and PokeGuess both use `rgba(200,240,96,.05)` (lime) and
`rgba(96,208,240,.04)` (teal) — not the homepage purple/cyan palette. After you wire up
`themes.css`, the page background (`--bg`) and text colors will align, but the orbs will still
glow the wrong colors. Because orbs are very low-opacity decorative elements, this mismatch is
easy to miss during a quick visual check.

**Why it happens:**
Orbs are copy-pasted decoration. They use literal RGB values, not CSS custom properties. No
linter catches this. The orbs don't "break" anything — they just subtly wrong.

**How to avoid:**
- Add `--orb-a-color` and `--orb-b-color` variables to `themes.css` matching the homepage
  (`rgba(144,149,255,.06)` and `rgba(140,247,255,.04)` respectively).
- Update all orb styles to use those variables.
- Do this in the same phase as themes.css adoption, not as a separate pass.

**Warning signs:**
- Orbs glow greenish/lime on any page other than the homepage.
- The `background: radial-gradient(...)` on `.orb-a` or `.orb-b` contains hardcoded `rgba`
  values with 200, 240, 96 (lime) or 96, 208, 240 (teal).

**Phase to address:** Shared CSS foundation phase

---

### Pitfall 4: Copy-Pasted Noise Overlay Creates Silent Sync Risk

**What goes wrong:**
The grain/noise SVG overlay (`body::after { background-image: url("data:image/svg+xml,...") }`)
is copy-pasted verbatim into: `index.html`, `Music01s/index.html`, `MusicSplit/index.html`, and
`PokeGuess/assets/css/style.css`. If you ever need to change the noise texture (different
frequency, different opacity, dark/light variant), you must update 4 files. During the
normalization milestone, updating only 2 out of 4 leaves the project in a mixed state.

**Why it happens:**
No shared component system exists. Each page is a standalone HTML file. Copy-paste is the only
tool available without a build step.

**How to avoid:**
- Move the `body::after` noise rule into `themes.css`. It applies globally and belongs there.
- Remove the identical rule from each game's inline `<style>` and from
  `PokeGuess/assets/css/style.css`.
- Do this in one commit — don't partially migrate it.

**Warning signs:**
- Grep for `feTurbulence` shows matches in more than one file.
- After an update to `themes.css`, the noise looks different on some pages.

**Phase to address:** Shared CSS foundation phase

---

### Pitfall 5: Navigation Inconsistency Breaks the "One Product" Feel

**What goes wrong:**
Each game has a different approach to navigation back to the homepage. Music01s and MusicSplit
use the game logo as a link to `../index.html`. PokeGuess's `game.html` links to `index.html`
(within PokeGuess, not the root). There is no consistent "back to lobby" affordance — no
breadcrumb, no nav bar, no universal element. Users who start from a shared game link have no
obvious path back to the game list.

**Why it happens:**
Games were built independently. Each developer solved navigation in isolation without an agreed
pattern.

**How to avoid:**
- Define a canonical navigation pattern: a small back-arrow or "Random Games" text link in the
  top-left corner that always links to `../index.html` (the root).
- Add this element in the same location on every page, using the same class name and style from
  `themes.css`.
- PokeGuess already has a `.logo` -> `.header` pattern — standardize this across all games.

**Warning signs:**
- User opens a game directly (via shared URL) and cannot find the homepage.
- `game.html` in PokeGuess links to `index.html` without `../` prefix — it loops back to
  PokeGuess setup, not the homepage.

**Phase to address:** Navigation and consistency phase

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Inline `<style>` blocks in each HTML file | No separate CSS file to manage | Cannot share rules across games; any global change requires touching every file | Never, for rules that should be shared |
| Copy-paste orb/noise CSS | Fast to add ambiance to a new game | 4 files diverge independently; normalization requires auditing all 4 | Never, now that `themes.css` exists |
| Hardcoded `rgba()` for brand colors | Quick to write | Palette change requires grep-and-replace across all files, easy to miss half | Never — brand colors should be CSS variables |
| `height: 100vh` on body/shell | Simple full-screen layouts on desktop | Completely broken on iOS Safari without `svh` fallback | Never for mobile-intended layouts |
| `overflow: hidden` on body | Prevents scrollbar flash | Traps content when viewport shrinks (mobile browser chrome) | Only acceptable in fullscreen kiosk contexts |
| Game-specific `:root {}` override | Easy to customize per game | Makes shared `themes.css` useless; variables mean different things on different pages | Never — use game-specific class or data-theme instead |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Google Fonts | Loading all 3 font families on every page even if unused | Already correct — all 3 fonts are always loaded; don't optimize this unless fonts cause real perf issues |
| GitHub Pages paths | Relative path `../themes.css` assumes correct directory depth | Always verify depth from each game's `index.html`: `Music01s/index.html` is one level deep, so `../themes.css` is correct |
| GitHub Pages paths | `PokeGuess/game.html` linking to `index.html` without `../` | The within-folder link to `index.html` is correct for "back to PokeGuess setup" — but there is no path back to root homepage from `game.html` |
| CSS custom properties | Adding a new variable to `themes.css` and expecting it to work in MusicSplit | MusicSplit doesn't import `themes.css` — any new variable is invisible there until the import is added |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Large orb blur on mobile | Janky scrolling, battery drain, dropped frames | Reduce `filter: blur(130px)` to `blur(60px)` on screens under 768px via media query | Any mid-range mobile device |
| `requestAnimationFrame` progress loop in Music01s | Fine with one audio clip; could stack if `loadSong()` is called before previous RAF stops | Always call `stopClip()` before starting a new clip (already done, but verify during refactor) | If navigation logic changes during mobile refactor |
| Loading all MIDI files sequentially in MusicSplit | Page appears to load but is actually fetching all MIDI files before showing anything | Already uses `async/await` per file — acceptable for personal project scale | Not a concern at this scale |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No "back to menu" from PokeGuess game screen | User finishes a game and must use the browser Back button to return | Add a nav link in `.header` on `game.html` pointing to `../../index.html` or at minimum to `index.html` (PokeGuess setup) |
| Music01s input has no mobile keyboard handling | On iOS, the soft keyboard pushes the layout up, potentially covering the autocomplete dropdown | Add `inputmode="search"` to the input; test that the autocomplete opens upward (it already does via `bottom: calc(100% + 6px)`) |
| MusicSplit has no "current song name" revealed | User listens and has no way to know what they're hearing | This is intentional game design — do not add it during normalization pass |
| `lang="en"` on Music01s and MusicSplit | Screen readers and search engines get wrong language hint for French-language UIs | Set `lang="fr"` on all pages to match the homepage and PokeGuess |

---

## "Looks Done But Isn't" Checklist

- [ ] **themes.css adoption:** Each game has `<link rel="stylesheet" href="../themes.css">` AND has no conflicting inline `:root { }` block — verify both conditions are true simultaneously.
- [ ] **Orb colors:** After switching to `themes.css`, orbs are purple/cyan, not lime/teal — do a visual check on all 3 games, not just the one you just edited.
- [ ] **Mobile Music01s:** Removing `overflow: hidden` from body makes the layout scrollable — verify the 6 attempt rows still fill the screen correctly and don't collapse to `min-content` on small screens.
- [ ] **Navigation:** From every page and every game state (setup, mid-game, results), there is a visible path back to the homepage — test `game.html` in PokeGuess specifically.
- [ ] **Noise overlay:** After moving `body::after` to `themes.css`, the rule no longer exists in any inline `<style>` block — search for `feTurbulence` across all files to confirm.
- [ ] **Font loading:** All 3 Google Fonts (Bebas Neue, DM Mono, DM Sans) are loaded on every page — do not remove the `<link>` tag even if a specific game only uses 2 of 3 fonts.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| MusicSplit wrong theme after migration | MEDIUM | Restore the MusicSplit `:root` values, identify which `var(--accent)` usages need game-specific overrides, then re-migrate carefully |
| Mobile layout broken after removing overflow:hidden | LOW | Revert only the height/overflow change; apply `100svh` fix on a separate branch and test properly |
| Noise overlay missing on one page | LOW | Search all HTML files for `body::after` or `feTurbulence`; ensure `themes.css` contains the rule and the per-file copies are deleted |
| Navigation loop (game.html -> PokeGuess index instead of root) | LOW | Fix the href to `../../index.html` or restructure the back link to always use `../index.html` from the PokeGuess directory root |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| MusicSplit wrong accent color | Shared CSS foundation (Phase 1) | Open all 3 games, confirm primary interactive color is purple, not lime |
| 100vh + overflow:hidden mobile trap | Mobile responsiveness (Phase 2) | Test Music01s on iOS Safari real device or BrowserStack — bottom controls must be tappable |
| Hardcoded orb RGBA colors | Shared CSS foundation (Phase 1) | Grep for `rgba(200,240,96` — zero results expected |
| Copy-pasted noise overlay | Shared CSS foundation (Phase 1) | Grep for `feTurbulence` — exactly one match in `themes.css`, zero elsewhere |
| Inconsistent navigation | Navigation and consistency phase (Phase 3) | From every game's result/end state, click the logo — confirm it lands on root `index.html` |
| lang="en" on French pages | Navigation and consistency phase (Phase 3) | Check `<html lang="...">` attribute on all files — all should be `lang="fr"` |
| PokeGuess game.html has no root nav | Navigation and consistency phase (Phase 3) | Open `game.html` directly, verify a path back to homepage exists |

---

## Sources

- Direct codebase inspection: `/Music01s/index.html`, `/MusicSplit/index.html`, `/PokeGuess/index.html`, `/PokeGuess/game.html`, `/PokeGuess/assets/css/style.css`, `/themes.css`, `/index.html`
- MDN Web Docs: CSS Viewport units (`svh`, `dvh`, `lvh`) — large/small/dynamic viewport height behavior on mobile browsers
- Known issue: iOS Safari `100vh` including browser chrome has been a documented problem since 2017; `svh` unit was introduced in 2022 as the standard fix

---
*Pitfalls research for: Static multi-page mini-game collection — design normalization*
*Researched: 2026-03-01*
