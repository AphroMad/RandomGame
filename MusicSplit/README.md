# Fake Bandle - Pierre Marsaa

A MIDI instrument group player that splits a song into its instrument families and lets you listen to each one separately.

## Files

### `index.html`
The main app. Opens in any browser and lets you play each instrument group (Bass, Brass/Wind, Strings, Drums, etc.) independently with a progress bar and seek functionality. No backend needed — works on GitHub Pages.

### `generate.py`
Run this locally whenever you add new `.mid` files to the `midi/` folder. It scans the folder and generates `midi/index.json`, which the HTML uses to know which files are available.
```bash
python generate.py
```

### `details_midi.py`
A utility script to inspect a MIDI file and print all its instruments. Useful for debugging or understanding the structure of a new file before adding it.
```bash
python details_midi.py
```

### `utils.js`
Contains the instrument grouping logic — maps General MIDI program numbers to role categories (Bass, Guitar, Strings, Choir, Brass/Wind, Drums, etc.). Used by the HTML to sort tracks into groups.

### `player.js`
*(legacy — no longer used)*
An older version of the audio playback logic using Tone.js. The playback code has since been moved directly into `index.html` using raw Web Audio API. Kept for reference.

## Setup

1. Drop `.mid` files into the `midi/` folder
2. Run `python generate.py`
3. Open `index.html` via a local server (`python -m http.server 8000`) or deploy to GitHub Pages
