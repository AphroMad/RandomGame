# Phase 1: Theme Unification - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Make all 3 games (Music01s, MusicSplit, PokeGuess) visually match the homepage — same purple/cyan palette from root `themes.css`, same noise overlay, same ambient orbs. Eliminate all competing color definitions (lime green `:root` overrides, duplicate themes.css files, hardcoded orb RGBA values).

</domain>

<decisions>
## Implementation Decisions

### MusicSplit Migration
- Switch all interactive elements to purple (`--accent`) — playing indicators, hover states, bottom bar, buttons
- Background changes from near-black (`#09090b`) to deep navy (`#03052E`) to match homepage
- Remove the inline `:root` block entirely, link `../themes.css` instead
- Replace all hardcoded lime-green RGBA values with purple-tinted equivalents from homepage palette

### PokeGuess Cleanup
- Delete local `assets/css/themes.css` (the duplicate with lime overrides)
- Fix hardcoded lime orb colors (`rgba(200,240,96,.05)`) to match homepage purple/cyan orb values
- Elements already using `--purple`, `--cta-gradient`, `--blue`, `--pink` tokens will automatically look correct

### Music01s Additions
- Add noise overlay and ambient orbs (currently missing entirely)
- Already links `../themes.css` and uses tokens correctly — minimal changes needed

### Logo Styling
- Keep existing back-to-homepage link behavior (logo click = `../index.html`)

### Claude's Discretion
- Logo visual style — pick a consistent pattern across all 3 games that works with the purple/cyan palette
- Bottom bar progress style in MusicSplit — solid purple vs gradient, whatever looks best
- Playing indicator glow treatment — purple glow or other visual treatment
- Whether to centralize noise/orbs/reset into themes.css or keep per-game copies
- Orb implementation for Music01s — HTML divs vs CSS pseudo-elements

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `themes.css` (root): Complete token system with `--accent`, `--accent-alt`, `--accent-third`, `--cta-gradient`, surface/border/text tokens. Already has dark + light theme support.
- Homepage `index.html`: Reference implementation for orb colors (`rgba(144,149,255,.06)` purple, `rgba(140,247,255,.04)` cyan), noise overlay, and gradient title styling.

### Established Patterns
- CSS custom properties for all colors — games should use tokens, not hardcoded values
- Noise overlay: SVG filter via `body::after` with `z-index: 9999`
- Orbs: Two fixed-position divs (`.orb-a` top-left, `.orb-b` bottom-right) with `blur(130px)`
- Scrollbar: Thin 3px style with `--border2` color
- Font imports: Google Fonts link for Bebas Neue, DM Mono, DM Sans (duplicated in every HTML file)

### Integration Points
- MusicSplit: `<style>` block lines 10-25 contain the rogue `:root`, lines 34-36 contain lime orb colors
- PokeGuess: `assets/css/themes.css` is the duplicate file to delete; `assets/css/style.css` lines 23-24 have hardcoded lime orb values
- Music01s: `<style>` block needs noise overlay and orb additions
- All games: Logo elements use varying patterns (`.logo` class in all, but different color approaches)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. User wants all games to feel like "the same product" with the homepage's purple/cyan aesthetic.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-theme-unification*
*Context gathered: 2026-03-01*
