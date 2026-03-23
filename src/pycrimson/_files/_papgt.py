from dataclasses import dataclass
from typing import ClassVar
from pathlib import Path
from enum import Flag

from bier.serialization import BinarySerializable, u32, u16, u8
from bier.EndianedBinaryIO import EndianedReaderIOBase, EndianedFileIO, EndianedBytesIO

from .. import _crypto


class LanguageType(u16, Flag):
    KOR = 1 << 0
    ENG = 1 << 1
    JPN = 1 << 2
    RUS = 1 << 3
    TUR = 1 << 4
    SPA_ES = 1 << 5
    SPA_MX = 1 << 6
    FRE = 1 << 7
    GER = 1 << 8
    ITA = 1 << 9
    POL = 1 << 10
    POR_BR = 1 << 11
    ZHO_TW = 1 << 12
    ZHO_CN = 1 << 13
    ALL = 0x3FFF


@dataclass(frozen=True)
class PackGroupTreeMetaHeader(BinarySerializable):
    unknown0: u32
    checksum: u32
    entry_count: u8
    unknown1: u8
    unknown2: u16


@dataclass(frozen=True)
class PackGroupTreeMetaEntry(BinarySerializable):
    is_optional: u8
    language: LanguageType
    always_zero: u8
    group_name_offset: u32
    pack_meta_checksum: u32


@dataclass(slots=True)
class PackGroupTreeMeta:
    FILE_EXTENSION: ClassVar[str] = ".papgt"

    _header: PackGroupTreeMetaHeader
    _entries: dict[str, PackGroupTreeMetaEntry]

    def __init__(self, reader: EndianedReaderIOBase):
        self._header = PackGroupTreeMetaHeader.read_from(reader)

        file_data: bytes = reader.read()
        _crypto.validate_checksum(file_data, self._header.checksum)

        self._entries = {}

        with EndianedBytesIO(file_data) as entry_reader:
            entries = [
                PackGroupTreeMetaEntry.read_from(entry_reader)
                for _ in range(self._header.entry_count)
            ]

            group_names_length = entry_reader.read_i32_le()
            group_names_buffer = entry_reader.read_bytes(group_names_length)

            for entry in entries:
                group_name_buf = group_names_buffer[entry.group_name_offset :]
                group_name = group_name_buf[: group_name_buf.index(b"\x00")].decode(
                    "utf-8"
                )
                self._entries[group_name] = entry

    @classmethod
    def from_file(cls, path: Path):
        with EndianedFileIO(path, "rb") as f:
            return cls(f)
