from src import KeyKey, NoteOn, NoteOff


if __name__ == "__main__":
    keykey = KeyKey("/dev/snd/midiC1D0")

    @keykey.note_on
    def test_key_on(e: NoteOn):
        print(f"{e.key.note}{e.key.octave} pressed")

    @keykey.note_off
    def test_key_off(e: NoteOff):
        print(f"{e.key.note}{e.key.octave} released")

    keykey.run()
