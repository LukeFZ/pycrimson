from bier.EndianedBinaryIO import EndianedReaderIOBase, EndianedFileIO
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from .. import _crypto

import io


@dataclass(slots=True)
class LocalizationStrings:
    FILE_EXTENSION: ClassVar[str] = ".paloc"

    values: dict[int, str]

    def __init__(self, reader: EndianedReaderIOBase):
        reader.seek(-4, io.SEEK_END)

        count = reader.read_u32()
        reader.seek(0)

        self.values = {}

        for _ in range(count):
            string_category = reader.read_u64()

            key = reader.read_string(reader.read_u32())
            value = reader.read_string(reader.read_u32())

            assert len(key) > 0
            if all(x in "0123456789-" for x in key):
                key = int(key)
            else:
                key = (string_category & 0x3F) << 4 | (
                    _crypto.calculate_checksum(key) << 32
                )

            assert key not in self.values, key
            self.values[key] = value

    @classmethod
    def from_file(cls, path: Path):
        with EndianedFileIO(path, "rb") as f:
            return cls(f)
