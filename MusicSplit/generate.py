import os
import json

midi_files = [f for f in os.listdir('midi/') if f.endswith('.mid')]

with open('midi/index.json', 'w') as f:
    json.dump(midi_files, f)

print(f"Generated index.json with {len(midi_files)} files")