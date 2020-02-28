from dataclasses import dataclass, field
from typing import *


@dataclass
class NoteOnEvent:
    status: int
    key: int
    velocity: int

    @classmethod
    def from_raw(cls, raw: bytes):
        pass
