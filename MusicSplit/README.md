# DEPRECATED: This was an early experiment. It's not actually fun to play starting from the midi files so I gave up. 

# MusicSplit

Converts MIDI files into layered WAV files, separating instruments into cumulative layers.

## Layer Structure

Each song is split into 4 cumulative layers:

| Layer | Content |
|-------|---------|
| `layer-1.wav` | Drums + Percussion |
| `layer-2.wav` | + Bass + Piano/Keys |
| `layer-3.wav` | + Brass/Wind + Guitar |
| `layer-4.wav` | + Ensemble/Choir/Strings (full mix) |

## Setup

### Requirements

```bash
pip install mido
brew install fluid-synth
```

Download a soundfont (.sf2) and place it in `MusicSplit/` or a subfolder:
- [GeneralUser GS](https://schristiancollins.com/generaluser.php) (free, ~30MB)

### Usage

```bash
# Convert all MIDI files in midi/ folder
python3.9 test_convert.py

# Convert a specific file
python3.9 test_convert.py midi/mysong.mid
```

### Output

```
wav/
  song-name/
    layer-1.wav
    layer-2.wav
    layer-3.wav
    layer-4.wav
```

## Files

| File | Description |
|------|-------------|
| `test_convert.py` | Main conversion script |
| `generate.py` | Generates `midi/index.json` for the MIDI player |
| `index.html` | MIDI player (real-time synthesis, separate from WAV workflow) |
