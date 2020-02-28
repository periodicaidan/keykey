import os

from dataclasses import dataclass
from typing import *


@dataclass
class MidiDevice:
    path: str
    fd: int

    @classmethod
    def open(cls, path: str):
        return cls(path, os.open(path, os.O_RDONLY))

    def close(self):
        os.close(self.fd)

    def read(self, n: int) -> Iterator[int]:
        return map(int, os.read(self.fd, n))

    def read_byte(self) -> int:
        return next(self.read(1))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
