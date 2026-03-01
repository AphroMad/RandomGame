# Feature Research

**Domain:** Static mini-game collection portal (vanilla HTML/CSS/JS, GitHub Pages)
**Researched:** 2026-03-01
**Confidence:** HIGH (based on direct codebase audit of all 3 games + homepage)

---

## Context: What The Codebase Actually Has Today

Before defining features, a precise audit of current state:

| Area | Homepage | Music01s | MusicSplit | PokeGuess |
|------|----------|----------|------------|-----------|
| Links `themes.css` | YES | YES | NO (inline `:root`) | YES |
| Uses correct CSS variables | YES | YES | NO (own `--accent: #c8f060`) | PARTIAL (orbs use green tints) |
| Separate CSS file | NO (inline) | NO (inline) | NO (inline) | YES |
| `lang` attribute | `fr` | `en` | `en` | `fr` |
| Back-to-homepage nav | — | Logo text link | Logo text link | Logo text link |
| Dedicated back button | — | NO | NO | NO |
| Mobile media queries | NO | NO | NO | 1 rule (420px) |
| Noise overlay | YES | NO | YES | YES (via style.css) |
| Orbs | YES | NO | YES (wrong colors) | YES (wrong colors) |

This audit drives every feature decision below.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Shared theme variables** | All 3 games must read the same color tokens from `themes.css` — without this, colors drift whenever `themes.css` is updated | LOW | MusicSplit has its own inline `:root` with completely different colors (`#c8f060` accent). Must remove and replace with `themes.css` import. |
| **Consistent accent color palette** | Users perceive the games as one product. Purple/pink/blue gradient should appear in all games, not green in MusicSplit and wrong-tint orbs in PokeGuess. | LOW | Fix orb rgba values in MusicSplit and PokeGuess style.css to match homepage (purple `rgba(144,149,255,...)`, cyan `rgba(140,247,255,...)`). |
| **Consistent background treatment** | Noise overlay + blur orbs are the homepage's visual signature. Three of three games should have them. | LOW | Music01s is missing both the noise overlay and orbs entirely. Add both (copy from homepage). |
| **Consistent typography rendering** | All 3 fonts (Bebas Neue, DM Mono, DM Sans) are already loaded in all pages. They must be applied via the same CSS variable names (`var(--ff-title)`, `var(--ff-body)`, `var(--ff-mono)`). | LOW | Already correct in Music01s and PokeGuess. MusicSplit references the variables but defines them locally — will work once themes.css is adopted. |
| **Functional back-navigation** | Users expect a clear, consistent path back to the homepage from any game. Current logo-link works but is visually inconsistent across games. | LOW | Standardize logo markup and position across all 3 games. A consistent logo-as-home-link pattern (already present) just needs visual normalization. |
| **Mobile-readable layout** | Phones are primary devices for casual gaming among friends. A layout that breaks or requires horizontal scrolling at 375px is broken. | MEDIUM | Music01s uses `overflow: hidden` + `height: 100vh` — clips content on short mobile screens. MusicSplit has no responsive rules. Homepage has no responsive rules but centers well by default. Each game needs a mobile pass. |
| **Touch-friendly tap targets** | On mobile, buttons must be at minimum 44px tall to be reliably tappable without zooming. | LOW | Audit each game's action buttons (Skip, Confirm, QCM buttons, Play). Most are already close; some need min-height enforcement on small screens. |
| **Consistent page `<title>` format** | Users with multiple tabs open need to identify games. | LOW | Standardize to e.g. `Music 01s — Random Games`, `PokeGuess — Random Games`. |
| **Consistent `lang` attribute** | Homepage is `lang="fr"`. Games mixing `en`/`fr` is inconsistent and affects screen readers/SEO. | LOW | Music01s and MusicSplit have `lang="en"`. Decide on one value (fr, given the audience) and apply consistently. |

---

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Polished inter-game transitions** | Clicking a game from the homepage feels like a deliberate entry into a distinct experience rather than just a page load. A subtle fade or slide entry on game load costs almost nothing and adds perceptual quality. | LOW | CSS `@keyframes` fade-in on `.shell`/`.wrap` on page load. Pure CSS, no JS needed. |
| **Standardized game header component** | Currently each game invents its own header markup. A unified pattern (logo left, optional subtitle right, consistent sizing) would make the portal feel like a product family. | LOW | Not a JS component — just a documented HTML+CSS pattern applied consistently. |
| **Viewport-unit safety for mobile** (`dvh` instead of `vh`) | `100vh` is broken on mobile browsers due to address bar height. `100dvh` (dynamic viewport height) is now widely supported and fixes layouts that clip on mobile. | LOW | Music01s uses `height: 100vh` and `overflow: hidden`. Replacing with `min-height: 100dvh` + scroll would fix the clip. |
| **Keyboard navigation support** | Power users (and accessibility) benefit from keyboard controls. Music01s already has keyboard support for autocomplete. | MEDIUM | Music01s is already good. PokeGuess QCM could support number keys (1-4). MusicSplit could support spacebar for play/stop. |
| **Semantic HTML cleanup** | Using `<header>`, `<main>`, `<nav>` properly improves accessibility and screen reader flow without any visual change. | LOW | Currently all games use `<div class="shell">` or `<div class="wrap">` as the root container. |

---

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **JavaScript component system / framework** | "Reuse the header across all pages cleanly" | Requires build tooling, breaks the "static files only" constraint, GitHub Pages cannot run Node.js. Even vanilla JS `fetch()` for HTML partials has CORS issues when opened as `file://` locally. | Document a copy-paste HTML pattern for the header. Three copies of 5 lines is fine for 3 games. |
| **CSS preprocessor (Sass/Less)** | "Avoid duplication in CSS variables" | Requires a build step. The whole project is deliberately no-build-step. | `themes.css` with CSS custom properties already solves the variable duplication problem. This is the right approach and is already in use. |
| **Local storage score persistence** | "Remember my high score" | Adds state management, score display UI, and reset UI — significant scope expansion for a friends-group game that rotates through songs/pokemon randomly each session | Out of scope per PROJECT.md. Not needed for the current use case. |
| **Animated theme switcher (light/dark toggle)** | `themes.css` already has a light theme stub | Adding UI toggle adds a settings panel or button to every page, complicates styling, and the light theme stub is incomplete. The dark theme is the product's identity. | Keep dark theme only. The light theme stub in `themes.css` can stay as scaffolding for later but no toggle UI. |
| **Service Worker / PWA** | "Make it installable / work offline" | Games load audio and Pokémon images from remote sources (PokeAPI, local mp3s). Offline caching is complex and not needed for the use case. | Don't build. GitHub Pages already has fast CDN. |
| **Game template generator** | "Make it easy to add the 4th game" | PROJECT.md explicitly calls this out of scope for this milestone. Building the template before patterns are solidified leads to a bad template. | Polish the 3 existing games first, then extract the pattern as a template in a future milestone. |

---

## Feature Dependencies

```
[themes.css adoption in MusicSplit]
    └──enables──> [Consistent accent color palette across all games]
                      └──enables──> [Consistent background treatment (correct orb tints)]

[Mobile layout audit per game]
    └──requires first──> [dvh viewport unit adoption] (low-hanging fix)

[Standardized game header component]
    └──enhances──> [Consistent back-navigation]
    └──enhances──> [Consistent page <title> format]

[Consistent lang attribute]
    └──independent of everything else, do it first]
```

### Dependency Notes

- **themes.css adoption in MusicSplit requires doing before color work:** MusicSplit's inline `:root` overrides any themes.css variables. Until the inline block is removed and replaced with `<link rel="stylesheet" href="../themes.css">`, no color fixes will take effect there.
- **dvh viewport fix unblocks the mobile layout audit:** Music01s's `overflow: hidden` + `100vh` approach must be restructured before mobile CSS rules are meaningful — adding media queries on top of a broken layout won't help.
- **Header standardization enhances but doesn't block:** Games are already navigable. The header pattern can be applied incrementally.

---

## MVP Definition

This milestone is a polish milestone, not a feature milestone. MVP = all table stakes delivered for all 3 games.

### Launch With (this milestone)

- [x] `themes.css` adopted in MusicSplit (remove inline `:root`, add link tag)
- [x] Accent color palette consistent across all games (fix orb rgba values, MusicSplit accent)
- [x] Noise overlay + orbs added to Music01s
- [x] `lang` attribute unified to `fr` across all pages
- [x] Mobile layout functional on 375px width for all 3 games (no horizontal scroll, no clipped content)
- [x] Touch targets minimum 44px on all primary action buttons
- [x] Standardized logo/header markup across all 3 games
- [x] Consistent `<title>` format

### Add After Validation (v1.x polish)

- [ ] Fade-in animation on page entry — add only after core layout is stable
- [ ] Keyboard navigation improvements for PokeGuess and MusicSplit
- [ ] Semantic HTML (`<main>`, `<header>`, `<nav>`) pass

### Future Consideration (v2+)

- [ ] Game template pattern extraction — only valuable when adding a 4th game
- [ ] Light theme completion — only if explicitly requested

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| MusicSplit adopts themes.css | HIGH (visual coherence) | LOW | P1 |
| Fix orb colors in PokeGuess + MusicSplit | HIGH (brand consistency) | LOW | P1 |
| Add noise overlay + orbs to Music01s | HIGH (visual coherence) | LOW | P1 |
| Mobile layout — Music01s (overflow/vh fix) | HIGH (usability) | MEDIUM | P1 |
| Mobile layout — MusicSplit | HIGH (usability) | MEDIUM | P1 |
| Mobile layout — Homepage | MEDIUM (already centered OK) | LOW | P1 |
| Touch targets audit | HIGH (usability on mobile) | LOW | P1 |
| Unified lang attribute | LOW (UX) | LOW | P1 (trivial, do it) |
| Consistent page `<title>` | LOW | LOW | P1 (trivial, do it) |
| Standardized header markup | MEDIUM | LOW | P2 |
| Page entry fade animation | MEDIUM | LOW | P2 |
| Keyboard nav improvements | LOW | MEDIUM | P3 |
| Semantic HTML pass | LOW (accessibility) | LOW | P3 |

**Priority key:**
- P1: Must have for this milestone
- P2: Should have, add when possible
- P3: Nice to have, future consideration

---

## Competitor Feature Analysis

*Note: WebSearch unavailable during research session. Analysis based on direct codebase audit and knowledge of the domain.*

Sites like [wordle.com](https://wordle.com), [heardle](https://heardle.app), and [bandle.app](https://bandle.app) — all in the same genre as the games here — share these patterns:

| Feature | Wordle-class sites | Bandle.app | Our Approach |
|---------|-------------------|------------|--------------|
| Color system | Single CSS file with custom properties | Single design language per game | Use `themes.css` as single source of truth |
| Mobile layout | Full viewport, no horizontal scroll, large tap targets | Scroll-friendly, thumb-reachable controls | Fix overflow/vh, ensure 44px targets |
| Navigation | Browser back, no explicit back button | Back link in header | Logo-as-link is sufficient for 3 games |
| Visual identity | Distinctive palette applied consistently | Green accent throughout | Purple/cyan gradient consistently applied |
| Animations | Minimal, purposeful (tile flip on Wordle) | Minimal | Existing flash-win/flash-lose in Music01s is correct pattern |

---

## Sources

- Direct codebase audit: `/index.html`, `/themes.css`, `/Music01s/index.html`, `/MusicSplit/index.html`, `/PokeGuess/index.html`, `/PokeGuess/assets/css/style.css` (2026-03-01)
- PROJECT.md: explicit scope constraints and existing feature list
- MDN Web Docs (training knowledge): `100dvh` browser support, touch target guidelines (44px from Apple HIG / Material Design)
- Bandle.app referenced in MusicSplit source code (`Inspired by bandle.app`)

---

*Feature research for: static mini-game collection portal (polish milestone)*
*Researched: 2026-03-01*
