from dataclasses import dataclass
from typing import *
import enum
from collections import namedtuple
from functools import wraps

from src.midi.device import MidiDevice


@enum.unique
class MidiMessageType (enum.IntFlag):
    NoteOff = enum.auto()
    NoteOn = enum.auto()
    ControlChange = enum.auto()
    ChannelMode = enum.auto()


@dataclass
class RawMidiMessage:
    status_code: int
    valence: int
    args: List[int]

    @classmethod
    def from_bytes(cls, device: MidiDevice):
        status_code = device.read_byte()
        if status_code & 0xF0 == 0x80:
            # NoteOff
            valence = 2
        elif status_code & 0xF0 == 0x90:
            # NoteOn
            valence = 2
        else:
            valence = 0
        args = list(device.read(valence))

        return cls(status_code, valence, args)


@dataclass
class MidiMessage:
    _raw: RawMidiMessage
    type: MidiMessageType

    @classmethod
    def wrapper(cls, keykey, handler, **kwargs):
        @wraps(handler)
        def register():
            kwargs["type"] = MidiMessageType.__members__[cls.__name__]
            pattern = namedtuple(f"{cls.__name__}Pattern", kwargs.keys())
            keykey.register_event_handler(pattern(**kwargs), handler)

        return register

    def matches(self, pattern: NamedTuple):
        for k, v in pattern._asdict().items():
            if v is None:
                continue
            if k == "octave" and not self.key.matches_octave(v):
                return False
            if k == "note" and not self.key.matches_note(v):
                return False
            if getattr(self, k, v) != v:
                return False

        return True
