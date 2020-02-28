from dataclasses import dataclass, field
from typing import *
import os
from os import path
import sys
import time
import re
from io import StringIO

from .midi import MidiDevice, MidiMessage, MidiMessageType, parse_message, NoteOn, NoteOff, ControlChange, ChannelMode


Decorator = Callable[[Callable], Any]

__all__ = (
    "KeyKey",
    MidiDevice,
    MidiMessageType,
    MidiMessageType,
    NoteOn,
    NoteOff,
    ControlChange,
    ChannelMode
)


@dataclass
class KeyKey:
    _driver_path: str
    _events: Dict = field(init=False, default_factory=dict)
    _velocity_threshold: int = 0
    delay: float = 0.01

    def run(self):
        with MidiDevice.open(self._driver_path) as device:
            while True:
                try:
                    message = parse_message(device)
                    if hasattr(message, "velocity") and message.velocity < self.velocity_threshold:
                        continue
                    for matcher, handler in self._events.items():
                        if message.matches(matcher):
                            handler(message)
                    time.sleep(self.delay)
                except OSError as err:
                    print(f"MIDI driver disconnected: {err}")
                    break

    def register_event_handler(self, event, handler):
        self._events[event] = handler

    @staticmethod
    def enumerate_devices() -> Dict[str, str]:
        """
        Enumerates all attached MIDI devices
        """
        if sys.platform == "linux":
            sound_driver_dir = "/dev/snd"
            try:
                device_name_dir = path.join(sound_driver_dir, "by-id")
                device_names = list(filter(path.islink, (path.join(device_name_dir, p) for p in os.listdir(device_name_dir))))
            except FileNotFoundError:
                device_name_dir = path.join(sound_driver_dir, "by-path")
                device_names = list(filter(path.islink, (path.join(device_name_dir, p) for p in os.listdir(device_name_dir))))

            controller_paths = {n: d for n, d in zip(device_names, map(path.realpath, device_names))}

            devices = {path.split(d)[1]: "" for d in device_names}
            driver_prefixes = ("midi", "hw")
            possible_drivers = (d for d in os.listdir(sound_driver_dir) if any(map(d.startswith, driver_prefixes)))
            device_name_format = r"^(:?" + "|".join(driver_prefixes) + r")C{N}D\d+"

            for name, controller in controller_paths.items():
                num = int(controller.split("C")[-1])
                matcher = re.compile(device_name_format.replace("{N}", str(num)))
                matches = [re.fullmatch(matcher, s) for s in possible_drivers]
                if any(matches):
                    devices[path.split(name)[1]] = path.join(
                        sound_driver_dir,
                        next(m.group(0) for m in filter(lambda m: m is not None, matches))
                    )

            return devices

    @classmethod
    def query_user_for_device(cls):
        devices = list(cls.enumerate_devices().items())
        strbuf = StringIO()
        strbuf.write("\n".join([
            "Welcome to KeyKey!",
            "Please select a device:"
        ]))

        strbuf.write("\n\n")

        strbuf.writelines(f"{i + 1}. {name} (-> {file})\n" for i, (name, file) in enumerate(devices))

        selection = int(input(strbuf.getvalue())) - 1

        return cls(devices[selection][1])

    @property
    def velocity_threshold(self):
        return self._velocity_threshold

    @velocity_threshold.setter
    def velocity_threshold(self, new: int):
        self._velocity_threshold = new % 128

    def note_on(self, _func=None, *,
                channel: Optional[int] = None,
                note: Optional[str] = None,
                octave: Optional[int] = None,
                velocity: Optional[int] = None) -> Decorator:
        kwargs = collect_locals(**locals())

        def decorator(handler: Callable[[NoteOn], Any]):
            return NoteOn.wrapper(self, handler, **kwargs)()

        if _func is None:
            return decorator
        else:
            return decorator(_func)

    def note_off(self, _func=None, *,
                 channel: Optional[int] = None,
                 note: Optional[str] = None,
                 octave: Optional[int] = None,
                 velocity: Optional[int] = None) -> Decorator:
        kwargs = collect_locals(**locals())

        def decorator(handler: Callable[[NoteOff], Any]):
            return NoteOff.wrapper(self, handler, **kwargs)()

        if _func is None:
            return decorator
        else:
            return decorator(_func)

    def control_change(self, _func=None, *,
                       channel: Optional[int] = None,
                       controller: Optional[int] = None,
                       value: Optional[int] = None) -> Decorator:
        kwargs = collect_locals(**locals())

        def decorator(handler: Callable[[ControlChange], Any]):
            return ControlChange.wrapper(self, handler, **kwargs)()

        if _func is None:
            return decorator
        else:
            return decorator(_func)

    def channel_mode(self, _func=None, *,
                     channel: Optional[int] = None,
                     mode: Optional[int] = None,
                     value: Optional[int] = None) -> Decorator:
        kwargs = collect_locals(**locals())

        def decorator(handler: Callable[[ChannelMode], Any]):
            return ChannelMode.wrapper(self, handler, **kwargs)()

        if _func is None:
            return decorator
        else:
            return decorator(_func)


def collect_locals(**locals):
    return {k: v for k, v in locals.items() if k not in ("self", "*")}
