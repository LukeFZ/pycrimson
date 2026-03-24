from bier.EndianedBinaryIO import EndianedReaderIOBase, EndianedFileIO
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from ._pabgh import BinaryGameHeader

import io


@dataclass(slots=True)
class BinaryGameBlob:
    FILE_EXTENSION: ClassVar[str] = ".pabgb"

    _pabgh: BinaryGameHeader
    entries: dict[int, bytes]

    def __init__(self, reader: EndianedReaderIOBase, pabgh: BinaryGameHeader):
        self._pabgh = pabgh
        self.entries = {}

        reader.seek(0, io.SEEK_END)
        total_size = reader.tell()

        sorted_offsets = sorted(self._pabgh.value_offsets.values()) + [total_size]
        for _, offset in self._pabgh.value_offsets.items():
            entry_size = sorted_offsets[sorted_offsets.index(offset) + 1]
            reader.seek(offset)
            entry = reader.read_bytes(entry_size)
            self.entries[offset] = entry

    @classmethod
    def from_file(cls, path: Path):
        pabgb_path = path.with_suffix(".pabgh")
        pabgh = BinaryGameHeader.from_file(pabgb_path)

        with EndianedFileIO(path, "rb") as f:
            return cls(f, pabgh)
