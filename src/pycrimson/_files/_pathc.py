from dataclasses import dataclass
from typing import ClassVar
from pathlib import Path

from bier.serialization import (
    BinarySerializable,
    u64,
    u32,
    u16,
    u8,
    custom,
    static_length,
)
from bier.EndianedBinaryIO import EndianedReaderIOBase, EndianedFileIO, EndianedBytesIO

from .. import _crypto


@dataclass(frozen=True)
class _PackTextureHeaderCollectionFile(BinarySerializable):
    reserved0: u64
    header_size: u32
    header_count: u32
    entry_count: u32
    collision_entry_count: u32
    filenames_length: u32


@dataclass(frozen=True)
class _PackTextureHeaderCollectionEntry(BinarySerializable):
    texture_header_index: u16
    collision_start_index: u8
    collision_end_index: u8
    compressed_block_infos: custom[bytes, static_length[16]]


@dataclass(frozen=True)
class _PackTextureHeaderCollectionCollisionEntry(BinarySerializable):
    filename_offset: u32
    texture_header_index: u16
    unknown0: u16
    compressed_block_infos: custom[bytes, static_length[16]]


@dataclass(slots=True)
class PackTextureHeaderCollection:
    FILE_EXTENSION: ClassVar[str] = ".pathc"

    _header: _PackTextureHeaderCollectionFile
    _headers: list[bytes]
    _header_offsets: list[int]

    _entries: dict[int, _PackTextureHeaderCollectionEntry]
    _hash_collision_entries: dict[str, _PackTextureHeaderCollectionCollisionEntry]

    def __init__(self, reader: EndianedReaderIOBase):
        self._header = _PackTextureHeaderCollectionFile.read_from(reader)

        self._headers = []
        self._header_offsets = []

        for _ in range(self._header.header_count):
            self._header_offsets.append(reader.tell())
            self._headers.append(reader.read_bytes(self._header.header_size))

        checksums = reader.read_u32_le_array(self._header.entry_count)
        checksum_entries = [
            _PackTextureHeaderCollectionEntry.read_from(reader)
            for _ in range(self._header.entry_count)
        ]
        self._entries = {x: y for x, y in zip(checksums, checksum_entries)}

        entries = [
            _PackTextureHeaderCollectionCollisionEntry.read_from(reader)
            for _ in range(self._header.collision_entry_count)
        ]

        self._hash_collision_entries = {}

        filenames = reader.read_bytes(self._header.filenames_length)
        with EndianedBytesIO(filenames) as filename_reader:
            for entry in entries:
                filename_reader.seek(entry.filename_offset)
                filename = filename_reader.read_cstring()
                self._hash_collision_entries[filename] = entry

    @classmethod
    def from_file(cls, path: Path):
        with EndianedFileIO(path, "rb") as f:
            return cls(f)

    def get_file_header(self, path: str) -> bytes:
        normalized_path = f"/{path}" if not path.startswith("/") else path
        checksum = _crypto.calculate_checksum(normalized_path)

        entry = self._entries.get(checksum)
        assert entry is not None

        if entry.texture_header_index != 0xFFFF:
            header = self._headers[entry.texture_header_index]
            compressed_block_infos = entry.compressed_block_infos
        else:
            collision_entry = self._hash_collision_entries.get(normalized_path)
            assert collision_entry is not None

            header = self._headers[collision_entry.texture_header_index]
            compressed_block_infos = collision_entry.compressed_block_infos

        if self._header.header_size == 0x94:
            return header[:0x20] + compressed_block_infos + header[0x30:]

        return header
