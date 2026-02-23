import pretty_midi

midi = pretty_midi.PrettyMIDI('midi/test.mid')
for instrument in midi.instruments:
    if instrument.is_drum:
        print(f"Drums: {instrument.name}")
    else:
        print(f"{pretty_midi.program_to_instrument_name(instrument.program)}: {instrument.name}")

