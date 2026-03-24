from dataclasses import dataclass
from typing import ClassVar
from pathlib import Path
from enum import IntEnum

from bier.serialization import (
    BinarySerializable,
    u32,
    u16,
    u8,
    i32,
    custom,
    static_length,
)
from bier.EndianedBinaryIO import EndianedReaderIOBase, EndianedFileIO, EndianedBytesIO

from .. import _crypto


@dataclass(frozen=True)
class PackEncryptInfo(BinarySerializable):
    unknown0: u8
    encrypt_info: custom[bytes, static_length[3]]


@dataclass(frozen=True)
class PackMetaHeader(BinarySerializable):
    checksum: u32
    count: u16
    unknown0: u16
    encrypt_info: PackEncryptInfo


@dataclass(frozen=True)
class PackMetaChunk(BinarySerializable):
    id: u32
    checksum: u32
    size: u32


@dataclass(frozen=True)
class PackMetaDirectory(BinarySerializable):
    name_checksum: u32
    name_offset: i32
    file_start_index: u32
    file_count: u32


class PackMetaFileCompression(IntEnum):
    NONE = 0
    PARTIAL = 1
    LZ4 = 2
    ZLIB = 3
    QUICKLZ = 4


class PackMetaFileCrypto(IntEnum):
    NONE = 0
    ICE = 1
    AES = 2
    CHACHA20 = 3


@dataclass(frozen=True)
class PackMetaFileFlags(BinarySerializable):
    compression: PackMetaFileCompression
    crypto: PackMetaFileCrypto
    is_partial: bool

    @classmethod
    def read_from(cls, reader, context=None):
        value = reader.read_u8()
        compression = PackMetaFileCompression(value & 0xF)
        crypto = PackMetaFileCrypto(value >> 4)

        if compression == PackMetaFileCompression.PARTIAL:
            compression = PackMetaFileCompression.NONE
            is_partial = True
        else:
            is_partial = False

        return cls(compression, crypto, is_partial)


@dataclass(frozen=True)
class PackMetaFile(BinarySerializable):
    name_offset: u32
    chunk_offset: u32
    compressed_size: u32
    uncompressed_size: u32
    chunk_id: u16
    flags: PackMetaFileFlags
    unknown0: u8


@dataclass(slots=True)
class TrieStringBuffer:
    _cache: dict[int, str]
    _data: bytes

    def __init__(self, data: bytes):
        self._cache = {}
        self._data = data

    def _read_entry(self, offset: int) -> tuple[int, str]:
        next_offset = int.from_bytes(
            self._data[offset : offset + 4], "little", signed=True
        )
        string_length = self._data[offset + 4]
        return (
            next_offset,
            self._data[offset + 5 : offset + 5 + string_length].decode(),
        )

    def get_string(self, offset: int) -> str:
        if offset == -1:
            return ""

        if (cached_value := self._cache.get(offset, None)) is None:
            next_offset, value = self._read_entry(offset)
            value = self.get_string(next_offset) + value

            self._cache[offset] = cached_value = value

        return cached_value


@dataclass(slots=True)
class PackMeta:
    FILE_EXTENSION: ClassVar[str] = ".pamt"

    _header: PackMetaHeader
    _chunks: dict[int, PackMetaChunk]

    _directory_names: TrieStringBuffer
    _file_names: TrieStringBuffer

    directories: dict[str, dict[str, PackMetaFile]]
    encrypt_data: bytes

    def __init__(
        self,
        reader: EndianedReaderIOBase,
        expected_crc: int,
        pack_group_path: Path | None = None,
    ):
        self._header = PackMetaHeader.read_from(reader)
        self.encrypt_data = self._header.encrypt_info.encrypt_info

        assert self._header.unknown0 == 0, self._header

        data = reader.read()
        _crypto.validate_checksum(data, expected_crc)

        with EndianedBytesIO(data) as data_reader:
            chunks = [
                PackMetaChunk.read_from(data_reader) for _ in range(self._header.count)
            ]

            if pack_group_path is not None:
                for chunk in chunks:
                    chunk_path = pack_group_path / f"{chunk.id}.paz"
                    assert chunk_path.exists(), chunk

                    # the checks below are also needed, but are skipped for performance
                    # chunk_data = chunk_path.read_bytes()
                    # assert len(chunk_data) == chunk.size
                    # assert _crypto.calculate_checksum(chunk_data) == chunk.checksum

            self._chunks = {x.id: x for x in chunks}

            directory_name_buffer = data_reader.read_bytes(data_reader.read_u32_le())
            self._directory_names = TrieStringBuffer(directory_name_buffer)

            file_name_buffer = data_reader.read_bytes(data_reader.read_u32_le())
            self._file_names = TrieStringBuffer(file_name_buffer)

            directories = [
                PackMetaDirectory.read_from(data_reader)
                for _ in range(data_reader.read_u32_le())
            ]

            files = [
                PackMetaFile.read_from(data_reader)
                for _ in range(data_reader.read_u32_le())
            ]

            self.directories = {}

            for directory in directories:
                directory_files = files[
                    directory.file_start_index : directory.file_start_index
                    + directory.file_count
                ]

                directory_path = self._directory_names.get_string(directory.name_offset)
                assert (
                    _crypto.calculate_checksum(directory_path)
                    == directory.name_checksum
                )

                files_in_directory = {}
                for file in directory_files:
                    assert file.unknown0 == 0, file
                    assert file.chunk_id in self._chunks, file
                    assert self._chunks[file.chunk_id].size >= (
                        file.chunk_offset + file.compressed_size
                    ), file

                    file_name = self._file_names.get_string(file.name_offset)
                    files_in_directory[file_name] = file

                self.directories[directory_path] = files_in_directory

    @classmethod
    def from_file(cls, path: Path, expected_crc: int):
        with EndianedFileIO(path, "rb") as f:
            return cls(f, expected_crc)
