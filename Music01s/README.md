# EARWORM

Guess the song from a tiny clip. Each round reveals a bit more: 0.1s → 0.5s → 2s → 4s → 8s → 16s.

## Files

| File | Purpose |
|------|---------|
| `index.html` | The game itself. Open this in a browser. |
| `run.py` | **Start here.** Runs prepare.py then generate.py in one command. |
| `prepare.py` | Trims leading silence + crops each song to 30s → saves to `guess/`. |
| `generate.py` | Scans `guess/` and writes `songs.js` so the game knows your songs. |
| `songs.js` | Auto-generated song list. Don't edit manually, commit it. |
| `music/` | Drop your original MP3s here. Never modified. |
| `guess/` | Processed 30s clips used by the game. Auto-generated, commit it. |

## Usage

```bash
# 1. add MP3s to music/
# 2. process them
python run.py

# 3. play
python -m http.server 8000
# open http://localhost:8000
```

## GitHub Pages

Run `python run.py` locally, commit everything, then enable Pages in your repo settings.
