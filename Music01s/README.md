# EARWORM

Guess the song from a tiny clip. Each round reveals a bit more: 0.1s → 0.5s → 2s → 4s → 8s → 16s.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The game itself. Open this in a browser. |
| `build.py` | Trims silence from `original/` → `music/`, then generates `songs.js`. Requires ffmpeg. |
| `songs.js` | Auto-generated song list. Don't edit manually. |
| `original/` | Drop your MP3s here. Never modified. |
| `music/` | Processed files (trimmed silence). Auto-generated. |

## Usage

```bash
# 1. add MP3s to original/

# 2. build
python build.py

# 3. play
python -m http.server 8000
# open http://localhost:8000
```

## GitHub Pages

Run `python build.py` locally, commit everything, then enable Pages in your repo settings.
