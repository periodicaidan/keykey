from .parser import MidiMessageType, MidiMessage, RawMidiMessage
from .device import MidiDevice
from .messages import *


def parse_message(device: MidiDevice) -> MidiMessage:
    raw = RawMidiMessage.from_bytes(device)
    if raw.status_code & 0xF0 == 0x90:
        return NoteOn.from_raw(raw)
    if raw.status_code & 0xF0 == 0x80:
        return NoteOff.from_raw(raw)
    if raw.status_code & 0xF0 == 0xB0:
        if raw.args[0] < 120:
            return ControlChange.from_raw(raw)
        else:
            return ChannelMode.from_raw(raw)
