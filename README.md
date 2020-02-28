KeyKey
===

KeyKey is a Python library that lets you use a MIDI controller to control anything.

## Basic Usage

KeyKey exposes a series of decorators (similar to Flask) that allow you to register
callbacks for MIDI messages. All you need to do is instantiate KeyKey, register some
MIDI message handlers, and say go.

```python
from keykey import KeyKey

kk = KeyKey.query_user_for_device()


@kk.note_on(note="C")
def handle_c_press(e):
    """
    This will be called if you press a C key on any octave.
    All handlers are passed the MIDI message they're handling,
    which in this case is a NoteOn event
    """
    print(f"You pressed C{e.key.octave}")


if __name__ == "__main__":
    kk.run()
```

Currently there are events to handle note on, note off, control change,
channel mode, and pitch bend. As well as some logging and error handling
functions for convenience. For about 99% of MIDI controllers this is 
sufficient. As a rule of thumb, keypresses on a MIDI controller trigger
note on/off events on MIDI channel 1. For everything else you'll have to
consult your controller's manual.


