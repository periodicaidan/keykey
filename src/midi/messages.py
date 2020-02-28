from dataclasses import dataclass
from typing import *
from functools import wraps
from collections import namedtuple

from .parser import RawMidiMessage, MidiMessageType, MidiMessage


NOTES = ("C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B")
NOTE_MAPPING = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11
}

@dataclass
class Key:
    _raw: int

    @property
    def note(self):
        return NOTES[self._raw % 12]

    @property
    def octave(self):
        return self._raw // 12

    def matches_octave(self, octave: int):
        return self.octave == octave

    def matches_note(self, note: str):
        return NOTES[NOTE_MAPPING.get(note)] == self.note

    def __repr__(self):
        return f"Key({self.note} {self.octave})"


@dataclass
class NoteOff (MidiMessage):
    channel: int
    key: Key
    velocity: int

    @classmethod
    def from_raw(cls, raw: RawMidiMessage):
        channel = (raw.status_code & 0x0F) + 1
        key = Key(raw.args[0] & 0x7F)
        velocity = raw.args[1] & 0x7F
        return cls(raw, MidiMessageType.NoteOff, channel, key, velocity)


@dataclass
class NoteOn (MidiMessage):
    channel: int
    key: Key
    velocity: int

    @classmethod
    def from_raw(cls, raw: RawMidiMessage):
        channel = (raw.status_code & 0x0F) + 1
        key = Key(raw.args[0] & 0x7F)
        velocity = raw.args[1] & 0x7F
        return cls(raw, MidiMessageType.NoteOn, channel, key, velocity)


@dataclass
class ControlChange (MidiMessage):
    channel: int
    controller: int
    value: int

    @classmethod
    def from_raw(cls, raw: RawMidiMessage):
        channel = (raw.status_code & 0x0F) + 1
        controller = raw.args[0] & 0x7F
        value = raw.args[1] & 0x7F
        return cls(raw, MidiMessageType.ControlChange, channel, controller, value)


@dataclass
class ChannelMode (MidiMessage):
    channel: int
    mode: int
    value: int

    @classmethod
    def from_raw(cls, raw: RawMidiMessage):
        channel = (raw.status_code & 0x0F) + 1
        mode = raw.args[0] & 0x7F
        value = raw.args[1] & 0x7F
        return cls(raw, MidiMessageType.ChannelMode, channel, mode, value)
