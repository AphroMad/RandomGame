# Phase 1: Theme Unification - Research

**Researched:** 2026-03-01
**Domain:** Vanilla HTML/CSS — CSS custom properties, visual theming across multiple static pages
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **MusicSplit Migration:** Switch all interactive elements to purple (`--accent`) — playing indicators, hover states, bottom bar, buttons. Background changes from near-black (`#09090b`) to deep navy (`#03052E`) to match homepage. Remove the inline `:root` block entirely, link `../themes.css` instead. Replace all hardcoded lime-green RGBA values with purple-tinted equivalents from homepage palette.
- **PokeGuess Cleanup:** Delete local `assets/css/themes.css` (the duplicate with lime overrides). Fix hardcoded lime orb colors (`rgba(200,240,96,.05)`) to match homepage purple/cyan orb values. Elements already using `--purple`, `--cta-gradient`, `--blue`, `--pink` tokens will automatically look correct.
- **Music01s Additions:** Add noise overlay and ambient orbs (currently missing entirely). Already links `../themes.css` and uses tokens correctly — minimal changes needed.
- **Logo Styling:** Keep existing back-to-homepage link behavior (logo click = `../index.html`).

### Claude's Discretion

- Logo visual style — pick a consistent pattern across all 3 games that works with the purple/cyan palette
- Bottom bar progress style in MusicSplit — solid purple vs gradient, whatever looks best
- Playing indicator glow treatment — purple glow or other visual treatment
- Whether to centralize noise/orbs/reset into themes.css or keep per-game copies
- Orb implementation for Music01s — HTML divs vs CSS pseudo-elements

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

---

## Summary

This phase is a pure CSS/HTML refactoring task with zero new JavaScript or libraries required. The project is a vanilla static site (no build step, GitHub Pages deployment) with three game pages and a root homepage. The root `themes.css` already defines the complete design token system (purple/cyan palette, all surface/text/border tokens, font family variables). The problem is that two games (MusicSplit and PokeGuess) have competing local `:root` overrides that define a lime-green accent instead of the purple/cyan system.

The work splits into three parallel sub-tasks: (1) MusicSplit — remove the inline `<style>` `:root` block and link `../themes.css`, then update all lime RGBA values and dark near-black background references to the correct tokens; (2) PokeGuess — delete `assets/css/themes.css` (the duplicate with lime overrides) and fix the two hardcoded lime orb RGBA values in `style.css`; (3) Music01s — copy the noise overlay and ambient orb pattern from the homepage into Music01s's inline `<style>`, since it already links `../themes.css` correctly but lacks these visual elements.

There are no external dependencies, no package installs, and no build commands needed. The implementation is a series of targeted HTML/CSS edits following patterns already established by the homepage.

**Primary recommendation:** Work game-by-game in dependency order: PokeGuess (smallest change — delete file, fix 2 RGBA values), then Music01s (add noise+orbs), then MusicSplit (largest change — replace entire `:root` block, update all lime references, update background color). Each game can be verified by opening it in a browser after the edit.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| THEME-01 | All games link to root `themes.css` and use its CSS custom properties | MusicSplit is the only game lacking the `<link>` — adding it and removing the inline `:root` is the core fix. PokeGuess and Music01s already have the link. |
| THEME-02 | MusicSplit adopts `themes.css` (currently has no link) with purple/cyan palette | Confirmed: MusicSplit has no `<link rel="stylesheet" href="../themes.css">`. Has an inline `<style>` block with its own `:root` defining lime accent and near-black background. All purple-palette tokens are missing. |
| THEME-03 | PokeGuess uses only root `themes.css` (remove duplicate local copy) | Confirmed: `PokeGuess/assets/css/themes.css` exists and is not referenced in `index.html` or `game.html` HEAD sections (both already link `../themes.css` first). However the file still exists on disk and creates confusion. Must delete it. |
| THEME-04 | Per-game `:root` color overrides removed (lime green eliminated) | Two locations: MusicSplit inline `<style>` lines 12-25 (full `:root` block), and `PokeGuess/assets/css/themes.css` (entire file is a lime `:root`). |
| THEME-05 | Orb background colors use consistent values from themes.css across all games | MusicSplit orb-a: `rgba(200,240,96,.05)` (lime), orb-b: `rgba(96,208,240,.04)` (cyan-ish but wrong). PokeGuess `style.css` lines 23-24: same lime `rgba(200,240,96,.05)`. Homepage correct values: orb-a `rgba(144,149,255,.06)`, orb-b `rgba(140,247,255,.04)`. |
| THEME-06 | Music01s has noise overlay and ambient orbs matching other games | Confirmed: Music01s body has no `body::after` noise overlay and no `.orb` divs in markup. The CSS for `.orb` classes is also absent. Must add both the CSS rules and the HTML divs, copying from homepage. |
</phase_requirements>

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| CSS Custom Properties | Native browser | Design token system | Already in use; no build step needed; cascade handles inheritance |
| Vanilla HTML/CSS | N/A | All implementation | Project constraint — no build tools, GitHub Pages raw file serving |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| SVG Data URI | N/A | Noise overlay texture | Already used by homepage and PokeGuess — inline SVG in `background-image` avoids extra file fetch |
| Google Fonts | CDN | Font imports | Already present in every HTML file — no change needed |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hardcoded RGBA in orbs | CSS var token | CSS vars can't go inside `rgba()` in older syntax — use the literal values from homepage, or `color-mix()` (not needed, just copy values) |
| Per-game noise/orb CSS | Centralizing into `themes.css` | Claude's discretion — centralizing reduces duplication but is out of scope per REQUIREMENTS.md "Out of Scope" table; keep per-game copies for now |

**Installation:** None required.

---

## Architecture Patterns

### Recommended Project Structure

```
RandomGame/
├── themes.css              # Single source of truth for all tokens (already exists)
├── index.html              # Homepage — reference implementation for orb/noise pattern
├── Music01s/
│   └── index.html          # Add noise overlay CSS + orb divs; already links ../themes.css
├── MusicSplit/
│   └── index.html          # Remove inline :root; add <link ../themes.css>; fix RGBA values
└── PokeGuess/
    ├── index.html           # Already correct (links ../themes.css, no local overrides)
    ├── game.html            # Already correct (links ../themes.css, no local overrides)
    └── assets/css/
        ├── style.css        # Fix 2 hardcoded orb RGBA values (lines 23-24)
        └── themes.css       # DELETE THIS FILE
```

### Pattern 1: CSS Token Link Order

**What:** Every game page must link `../themes.css` before any per-game stylesheet. The per-game stylesheet can then safely use all `var(--token)` names without re-declaring them.
**When to use:** Every HTML file in the project.
**Example:**
```html
<!-- Correct order -->
<link rel="stylesheet" href="../themes.css">
<link rel="stylesheet" href="assets/css/style.css">

<!-- Wrong — per-game stylesheet linked before tokens are defined -->
<link rel="stylesheet" href="assets/css/style.css">
<link rel="stylesheet" href="../themes.css">
```

### Pattern 2: Noise Overlay (body::after)

**What:** SVG fractal noise applied as a fixed full-viewport pseudo-element at `z-index: 9999`.
**When to use:** Every game page — provides the "grain" texture that unifies the visual signature.
**Example (from homepage, confirmed working):**
```css
body::after {
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 9999;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
}
```

### Pattern 3: Ambient Orbs

**What:** Two fixed-position divs with radial gradients and heavy blur, placed at viewport corners.
**When to use:** Every game page — the orbs are the primary visual signature of the purple/cyan palette.
**Example (from homepage, confirmed correct values):**
```css
/* CSS */
.orb { position: fixed; border-radius: 50%; filter: blur(130px); pointer-events: none; z-index: 0; }
.orb-a { width: 700px; height: 700px; top: -250px; left: -200px; background: radial-gradient(circle, rgba(144,149,255,.06) 0%, transparent 70%); }
.orb-b { width: 500px; height: 500px; bottom: -150px; right: -150px; background: radial-gradient(circle, rgba(140,247,255,.04) 0%, transparent 70%); }
```
```html
<!-- HTML — place immediately after <body> opening tag, before .shell -->
<div class="orb orb-a"></div>
<div class="orb orb-b"></div>
```

### Pattern 4: Logo Consistent Style

**What:** Claude's discretion area — choose one visual treatment for logo across all 3 games.
**Recommendation:** Use the gradient text treatment from the homepage `h1` for visual consistency. This means `background: var(--cta-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;` on the logo element, replacing the current `color: var(--accent)` approach used in MusicSplit and PokeGuess style.css.
**Alternative:** Keep `color: var(--accent)` (purple) with an `<em>` in a contrasting token — simpler and Music01s already does this (`color: var(--text)` with `<em>` in `var(--purple)`). Either is valid.

### Anti-Patterns to Avoid

- **Inline `:root` block overrides:** Any per-game `:root { }` block defined after `themes.css` silently wins the cascade. There must be zero `:root` blocks in game HTML or per-game CSS files.
- **Hardcoded RGBA colors for orbs:** Cannot be overridden by theme tokens. Must use the literal values from the homepage reference (`rgba(144,149,255,.06)` purple, `rgba(140,247,255,.04)` cyan).
- **Leaving `PokeGuess/assets/css/themes.css` on disk:** Even if not linked, its existence is confusing and a future risk if ever accidentally linked again. Delete it entirely.
- **Adding `<link>` to themes.css without removing the competing `:root`:** In MusicSplit, simply adding the link is not enough — the inline `<style>` block's `:root` will still override the file because inline `<style>` comes later in parse order.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Noise texture | Custom canvas noise, JS-generated grain | SVG data URI in `body::after` (already used) | Zero JS, no extra file fetch, already proven working in this project |
| Design tokens | Per-file CSS variable declarations | Root `themes.css` with single import | Cascade guarantees correctness; any token change propagates everywhere automatically |

**Key insight:** The entire phase is about removing custom per-game solutions (the hand-rolled `:root` override blocks) and replacing them with the already-existing central `themes.css`.

---

## Common Pitfalls

### Pitfall 1: CSS Cascade Order for Inline Styles

**What goes wrong:** Developer adds `<link rel="stylesheet" href="../themes.css">` to MusicSplit but keeps the inline `<style>` block. The inline `<style>` block containing `:root { --accent: #c8f060; }` comes after the `<link>` in the HTML, so it wins the cascade — lime green stays.
**Why it happens:** CSS specificity for `:root` is equal; source order determines the winner. Inline `<style>` always comes after linked stylesheets in the HTML parse order if placed in the same `<head>` section after the link.
**How to avoid:** Remove the entire inline `:root { ... }` block from MusicSplit's `<style>` tag when adding the `<link>`. The `<style>` tag itself can remain for game-specific rules.
**Warning signs:** After the edit, inspect the page in DevTools → Computed → `--accent`. If it shows `#c8f060`, the old `:root` block is still present.

### Pitfall 2: `PokeGuess/assets/css/themes.css` Is Not Linked But Still Dangerous

**What goes wrong:** The duplicate `themes.css` in PokeGuess is not referenced in `index.html` or `game.html` right now — both already link `../themes.css` first. But the file on disk could be accidentally linked in the future, or cause confusion during code review.
**Why it happens:** The file was likely an early copy before the root `themes.css` was established.
**How to avoid:** Delete the file. Verify neither `index.html` nor `game.html` in PokeGuess has a `<link>` pointing to `assets/css/themes.css` before deleting.
**Warning signs:** Run `grep -r "assets/css/themes.css" PokeGuess/` before deleting — should return zero results.

### Pitfall 3: Orb Lime Colors Remain After `:root` Swap

**What goes wrong:** In MusicSplit, even after removing the `:root` block, the orb divs still have inline `background: radial-gradient(circle, rgba(200,240,96,.05) ...)` baked into the CSS rules. These RGBA values are not driven by CSS tokens — they are hardcoded and will not change when `themes.css` is loaded.
**Why it happens:** The original developer used literal RGBA values instead of CSS token references for the orb colors.
**How to avoid:** After removing the `:root` block, do a full-text search for `200,240,96` and `96,208,240` (the lime RGB triplets) and replace every occurrence with the correct homepage values (`144,149,255` for purple orb-a, `140,247,255` for cyan orb-b).
**Warning signs:** Page renders purple in general but orbs still glow lime/yellow-green in the top-left corner.

### Pitfall 4: MusicSplit Background Color Token Mismatch

**What goes wrong:** After removing the inline `:root`, MusicSplit's `background: var(--bg)` now resolves to `#03052E` (deep navy from `themes.css`) instead of the old `#09090b` (near-black). The bottom bar background is hardcoded as `rgba(9,9,11,.92)` — this is the RGB expansion of the OLD `#09090b`. It will look wrong against the new navy background.
**Why it happens:** `rgba(9,9,11,.92)` was hand-calculated from the old `--bg` value and not tied to a token.
**How to avoid:** Update the bottom bar `background: rgba(9,9,11,.92)` to `rgba(3,5,46,.92)` — the RGB expansion of `#03052E` — or better, use a CSS variable if one is defined. In the current `themes.css`, `--bg` is `#03052E` which is rgb(3,5,46).
**Warning signs:** Bottom bar looks like a dark grey stripe floating over a navy background instead of blending with it.

### Pitfall 5: MusicSplit Hover State Uses `color: #09090b` (Text-on-Lime)

**What goes wrong:** The `.group-row.playing .btn:hover` rule has `color: #09090b` — this was designed as dark text on a lime-green button background. After switching to purple, the background is still `var(--accent)` but the text color must be `#fff` or a light token.
**Why it happens:** Lime green is light enough to need dark text; purple is dark enough to need light text.
**How to avoid:** Change `color: #09090b` to `color: #fff` (or `color: var(--bg)`) on that hover rule.
**Warning signs:** Button text is invisible (black on dark purple) when hovering a playing row's stop button.

---

## Code Examples

### MusicSplit: Before and After the `:root` Block Removal

**Before (lines 9-25 in MusicSplit/index.html):**
```html
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #09090b;
    --s1:       #111114;
    --s2:       #17171c;
    --border:   #222228;
    --border2:  #2e2e38;
    --accent:   #c8f060;
    --text:     #e2e2ee;
    --muted:    #52526a;
    --muted2:   #38384a;
    --ff-title: 'Bebas Neue', sans-serif;
    --ff-mono:  'DM Mono', monospace;
    --ff-body:  'DM Sans', sans-serif;
  }
  ...
```

**After:**
```html
<link rel="stylesheet" href="../themes.css">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  /* :root block removed — tokens come from ../themes.css */
  ...
```

### MusicSplit: Orb Color Fix

**Before:**
```css
.orb-a { ... background: radial-gradient(circle, rgba(200,240,96,.05) 0%, transparent 70%); }
.orb-b { ... background: radial-gradient(circle, rgba(96,208,240,.04) 0%, transparent 70%); }
```

**After (matching homepage values):**
```css
.orb-a { ... background: radial-gradient(circle, rgba(144,149,255,.06) 0%, transparent 70%); }
.orb-b { ... background: radial-gradient(circle, rgba(140,247,255,.04) 0%, transparent 70%); }
```

### MusicSplit: Bottom Bar Background Fix

**Before:**
```css
#bottom-bar {
  background: rgba(9,9,11,.92);
  ...
}
```

**After:**
```css
#bottom-bar {
  background: rgba(3,5,46,.92);
  ...
}
```

### MusicSplit: Playing Row Background Fix

**Before:**
```css
.group-row.playing { border-color: var(--accent); background: rgba(200,240,96,.04); }
```

**After:**
```css
.group-row.playing { border-color: var(--accent); background: rgba(144,149,255,.04); }
```

### MusicSplit: Button Hover Text Color Fix

**Before:**
```css
.group-row.playing .btn:hover { background: var(--accent); color: #09090b; }
```

**After:**
```css
.group-row.playing .btn:hover { background: var(--accent); color: #fff; }
```

### PokeGuess: Orb Color Fix in style.css (lines 23-24)

**Before:**
```css
.orb-a { width: 700px; height: 700px; top: -250px; left: -200px; background: radial-gradient(circle, rgba(200,240,96,.05) 0%, transparent 70%); }
.orb-b { width: 500px; height: 500px; bottom: -150px; right: -150px; background: radial-gradient(circle, rgba(96,208,240,.04) 0%, transparent 70%); }
```

**After:**
```css
.orb-a { width: 700px; height: 700px; top: -250px; left: -200px; background: radial-gradient(circle, rgba(144,149,255,.06) 0%, transparent 70%); }
.orb-b { width: 500px; height: 500px; bottom: -150px; right: -150px; background: radial-gradient(circle, rgba(140,247,255,.04) 0%, transparent 70%); }
```

### Music01s: Add Noise Overlay and Orbs

**Add to Music01s/index.html `<style>` block** (after the reset rule, before `.shell`):
```css
body::after {
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 9999;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
}

.orb { position: fixed; border-radius: 50%; filter: blur(130px); pointer-events: none; z-index: 0; }
.orb-a { width: 700px; height: 700px; top: -250px; left: -200px; background: radial-gradient(circle, rgba(144,149,255,.06) 0%, transparent 70%); }
.orb-b { width: 500px; height: 500px; bottom: -150px; right: -150px; background: radial-gradient(circle, rgba(140,247,255,.04) 0%, transparent 70%); }
```

**Add to Music01s/index.html `<body>`** (immediately after `<body>` opening tag):
```html
<div class="orb orb-a"></div>
<div class="orb orb-b"></div>
```

Note: Music01s currently has `overflow: hidden` on `html, body`. This is fine — the orbs use `position: fixed` which escapes the overflow context and renders at the viewport level.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Per-game inline `:root` color overrides | Single `themes.css` import | Pre-existing root file; games not migrated yet | Eliminates all token duplication, enables global palette changes from one file |
| Hardcoded RGBA orb values | Literal values matching themes.css tokens | This phase | Visual consistency; would become tokenizable if CSS custom properties inside `rgba()` are ever needed |

---

## Open Questions

1. **Logo visual treatment consistency**
   - What we know: MusicSplit uses `color: var(--accent)` with a `<em>` in `var(--text)`. Music01s uses `color: var(--text)` with `<em>` in `var(--purple)`. PokeGuess `style.css` uses `color: var(--accent)` with `<em>` in `var(--text)`.
   - What's unclear: Which pattern to standardize on — gradient text (like homepage `h1`), or solid purple token, or two-tone token approach.
   - Recommendation: Use the Music01s pattern (`color: var(--text)` with `<em>` colored by `var(--purple)`) as it works without needing the gradient text trick and is already present in one game. Apply to MusicSplit logo CSS and PokeGuess `style.css` `.header .logo` rule. This is Claude's discretion.

2. **`PokeGuess/assets/css/themes.css` link verification before deletion**
   - What we know: Neither `index.html` nor `game.html` in PokeGuess contain a `<link>` to `assets/css/themes.css` in their current state.
   - What's unclear: Whether any other HTML file or future file might reference it.
   - Recommendation: Run `grep -r "assets/css/themes" PokeGuess/` before deleting. Expected: zero results. Confirmed: the duplicate file is orphaned.

---

## Sources

### Primary (HIGH confidence)

- Direct file inspection: `/Users/pierremarsaa/Desktop/Projet/WEB/RandomGame/themes.css` — full token system documented
- Direct file inspection: `/Users/pierremarsaa/Desktop/Projet/WEB/RandomGame/index.html` — homepage reference implementation for orb values and noise overlay pattern
- Direct file inspection: `/Users/pierremarsaa/Desktop/Projet/WEB/RandomGame/MusicSplit/index.html` — confirmed: no themes.css link, full inline `:root` with lime `--accent`, hardcoded lime orb RGBA, hardcoded `rgba(9,9,11,.92)` bottom bar
- Direct file inspection: `/Users/pierremarsaa/Desktop/Projet/WEB/RandomGame/Music01s/index.html` — confirmed: has `<link ../themes.css>`, no noise overlay CSS, no orb CSS, no orb HTML divs
- Direct file inspection: `/Users/pierremarsaa/Desktop/Projet/WEB/RandomGame/PokeGuess/index.html` and `game.html` — confirmed: both link `../themes.css`, neither links `assets/css/themes.css`
- Direct file inspection: `/Users/pierremarsaa/Desktop/Projet/WEB/RandomGame/PokeGuess/assets/css/themes.css` — confirmed: lime `:root` override exists, file is not linked anywhere
- Direct file inspection: `/Users/pierremarsaa/Desktop/Projet/WEB/RandomGame/PokeGuess/assets/css/style.css` — confirmed: hardcoded lime orb RGBA on lines 23-24, all other rules use correct tokens

### Secondary (MEDIUM confidence)

- CSS cascade specification behavior (inline `<style>` after `<link>` wins) — standard browser behavior, verified by developer knowledge of CSS spec

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pure vanilla HTML/CSS, no external dependencies, all verified by direct file inspection
- Architecture: HIGH — all patterns verified from existing homepage code; no speculation
- Pitfalls: HIGH — all pitfalls derived from actual code analysis of specific line numbers in existing files
- Code examples: HIGH — all examples taken directly from existing files or are minimal modifications thereof

**Research date:** 2026-03-01
**Valid until:** 2026-04-01 (stable — no moving dependencies, no framework versions to track)
