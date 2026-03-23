from dataclasses import dataclass
from pathlib import Path
from enum import Flag

from bier.serialization import BinarySerializable, u16, u32, custom, static_length
from bier.EndianedBinaryIO import (
    EndianedFileIO,
    EndianedReaderIOBase,
    EndianedWriterIOBase,
)

from .. import _crypto

import lz4.block


class SaveFileFlags(u32, Flag):
    COMPRESSED = 1 << 1


@dataclass(frozen=True)
class SaveFileHeader(BinarySerializable):
    magic: custom[bytes, static_length[4]]
    version: u16
    header_size: u16
    unknown0: u32
    flags: SaveFileFlags
    unknown2: u16
    decompressed_size: u32
    compressed_size: u32
    encryption_nonce: custom[bytes, static_length[16]]
    save_hmac: custom[bytes, static_length[32]]
    reserved: custom[bytes, static_length[0x80 - 0x4A]]


class SaveFile:
    @staticmethod
    def write_encrypted(data: bytes, writer: EndianedWriterIOBase, version: int = 2):
        compressed_save = lz4.block.compress(data, store_size=False)

        hmac, nonce, encrypted_save = _crypto.chacha20_encrypt_save_file(
            compressed_save, version
        )

        new_header = SaveFileHeader(
            magic=b"SAVE",
            version=version,
            header_size=0x80,
            unknown0=0,
            flags=SaveFileFlags.COMPRESSED,
            unknown2=0,
            decompressed_size=len(data),
            compressed_size=len(compressed_save),
            encryption_nonce=nonce,
            save_hmac=hmac,
            reserved=bytes(0x80 - 0x4A),
        )

        new_header.write_to(writer)
        writer.write(encrypted_save)

    @staticmethod
    def write_encrypted_file(data: bytes, output_path: Path, version: int):
        with EndianedFileIO(output_path, "wb") as writer:
            SaveFile.write_encrypted(data, writer, version)

    @staticmethod
    def from_encrypted(reader: EndianedReaderIOBase) -> bytes:
        header = SaveFileHeader.read_from(reader)
        assert header.magic == b"SAVE", f"Invalid save magic {header.magic}"

        encrypted_data = reader.read_bytes(header.compressed_size)

        data = _crypto.chacha20_decrypt_save_file(
            encrypted_data, header.version, header.encryption_nonce, header.save_hmac
        )

        if header.compressed_size != header.decompressed_size:
            data = lz4.block.decompress(
                data, uncompressed_size=header.decompressed_size
            )

        return data

    @staticmethod
    def from_encrypted_file(path: Path):
        with EndianedFileIO(path, "rb") as reader:
            return SaveFile.from_encrypted(reader)


__all__ = [
    "SaveFile",
]
