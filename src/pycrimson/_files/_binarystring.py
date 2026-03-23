from bier.EndianedBinaryIO import EndianedReaderIOBase, EndianedFileIO
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass(slots=True)
class StringBinary:
    FILE_EXTENSION: ClassVar[str] = ".binarystring"

    values: list[str]

    def __init__(self, reader: EndianedReaderIOBase):
        self.values = []

        for _ in range(reader.read_u16()):
            size = reader.read_u8()
            data = reader.read_string(size)
            assert reader.read_u8() == 0, hex(reader.tell())
            self.values.append(data)

    @classmethod
    def from_file(cls, path: Path):
        with EndianedFileIO(path, "rb") as f:
            return cls(f)
