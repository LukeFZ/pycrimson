from bier.EndianedBinaryIO import EndianedReaderIOBase, EndianedFileIO
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import io

# this table will be moved at some point, but for now we need it here

_UINT_COUNT_TABLES: set[str] = {
    "characterappearanceindexinfo",
    "globalstagesequencerinfo",
    "sequencerspawninfo",
    "sheetmusicinfo",
    "spawningpoolautospawninfo",
    "itemuseinfo",
    "terrainregionautospawninfo",
    "textguideinfo",
    "validscheduleactioninfo",
    "stageinfo",
    "questinfo",
    "gimmickeventtableinfo",
    "fieldreviveinfo",
    "aidialogstringinfo",
    "dialogsetinfo",
    "vibratepatterninfo",
    "platformachievementinfo",
    "levelgimmicksceneobjectinfo",
    "fieldlevelnametableinfo",
    "gamelevelinfo",
    "boardinfo",
    "gameplaytriggerinfo",
    "characterchangeinfo",
    "materialrelationinfo",
}


@dataclass(slots=True)
class BinaryGameHeader:  # not actually sure if this is the correct name
    FILE_EXTENSION: ClassVar[str] = ".pabgh"

    value_offsets: dict[int, int]

    def __init__(self, reader: EndianedReaderIOBase, count_size: int = 2):
        self.value_offsets = {}

        # we don't actually know how big each key is, as we don't know the schemas (yet).
        # so we have to use heuristics to find them

        count = int.from_bytes(reader.read_bytes(count_size), "little")

        reader.seek(0, io.SEEK_END)
        file_size = reader.tell()

        total_key_size = file_size - (count_size + count * 4)
        key_size = total_key_size // count
        assert (key_size * count) == total_key_size, "failed to determine key size"

        reader.seek(count_size)

        for _ in range(count):
            key = int.from_bytes(reader.read_bytes(key_size), "little")
            offset = reader.read_u32()
            self.value_offsets[key] = offset

    @classmethod
    def from_file(cls, path: Path):
        filename = path.name.rsplit(".", 1)[0].lower()
        count_size = 4 if filename in _UINT_COUNT_TABLES else 2

        with EndianedFileIO(path, "rb") as f:
            return cls(f, count_size)
