from pathlib import Path
import lz4.block

from ._files import (
    PackTextureHeaderCollection,
    PackGroupTreeMeta,
    PackMeta,
    PackMetaFileEntry,
    PackMetaFileCompression,
    PackMetaFileCrypto,
)

from . import _crypto, _dds


class PackageContext:
    _base_path: Path
    _packs: dict[str, PackMeta]
    _paz_handle_cache: dict
    _pack_group_whitelist: list[str] | None

    def __init__(
        self, base_directory: Path, pack_group_whitelist: list[str] | None = None
    ):
        self._base_path = base_directory
        self._packs = {}
        self._paz_handle_cache = {}
        self._pack_group_whitelist = pack_group_whitelist

        self._parse_pack_meta()
        self._parse_texture_header_collection()

    def _parse_texture_header_collection(self):
        pthc_file = self._base_path / "meta" / "0.pathc"
        if pthc_file.exists():
            self._pthc = PackTextureHeaderCollection.from_file(pthc_file)

    def _parse_pack_meta(self):
        papgt_file = self._base_path / "meta" / "0.papgt"
        if papgt_file.exists():
            papgt = PackGroupTreeMeta.from_file(papgt_file)
            for name, entry in papgt._entries.items():
                if (
                    self._pack_group_whitelist is not None
                    and name not in self._pack_group_whitelist
                ):
                    continue

                base_folder_path = self._base_path / name
                pamt_path = base_folder_path / "0.pamt"

                if pamt_path.exists():
                    print("currently parsing", name)
                    pack_meta = PackMeta.from_file(pamt_path, entry.pack_meta_checksum)
                    self._packs[name] = pack_meta

    def _get_entry_by_path(
        self, path: str
    ) -> tuple[str, bytes, PackMetaFileEntry | None]:
        dir_path, file_name = path.rsplit("/", 1)

        for group_id, pack in self._packs.items():
            if (dir := pack.directories.get(dir_path, None)) is None:
                continue

            if (file := dir.get(file_name, None)) is None:
                continue

            return (group_id, pack.encrypt_data, file)

        return ("", b"", None)

    def _handle_partial_texture(self, data: bytes, header: bytes) -> bytes:
        assert header[:4] == b"DDS "
        dds_header = _dds.DDS_HEADER.from_bytes(header[4:])
        dx10_header = _dds.DDS_HEADER_DXT10.from_bytes(header[0x80:])

        is_dx10 = dds_header.ddspf.four_cc == b"DX10"
        header_size = 0x94 if is_dx10 else 0x80

        multi_chunk_supported_0 = (dx10_header.array_size < 2) if is_dx10 else True

        multi_chunk_supported_1 = dds_header.mip_map_count > 5 and (
            dds_header.caps2 == 0 and dds_header.depth < 2
        )

        use_single_chunk = not multi_chunk_supported_0 or not multi_chunk_supported_1
        if use_single_chunk:
            compressed_size = dds_header.reserved1[0]
            decompressed_size = dds_header.reserved1[1]

            compressed_block_sizes = [compressed_size]
            decompressed_block_sizes = [decompressed_size]
        else:
            height = dds_header.height
            width = dds_header.width

            dxgi_format = (
                _dds.get_dxgi_format(dds_header.ddspf)
                if not is_dx10
                else dx10_header.format
            )

            compressed_block_sizes = dds_header.reserved1[:4]

            decompressed_block_sizes = []

            for _ in range(min(4, dds_header.mip_map_count)):
                mip_size, _, _ = _dds.get_surface_info(width, height, dxgi_format)
                decompressed_block_sizes.append(mip_size)

                height >>= 1
                width >>= 1

        current_data_offset = header_size
        output_data = header[:header_size]

        for compressed_size, decompressed_size in zip(
            compressed_block_sizes, decompressed_block_sizes
        ):
            if compressed_size == decompressed_size:
                output_data += data[
                    current_data_offset : current_data_offset + decompressed_size
                ]
                current_data_offset += decompressed_size
                continue

            compressed_data = data[
                current_data_offset : current_data_offset + compressed_size
            ]
            decompressed_data = lz4.block.decompress(
                compressed_data, uncompressed_size=decompressed_size
            )
            output_data += decompressed_data
            current_data_offset += compressed_size

        if current_data_offset != len(data):
            output_data += data[current_data_offset:]

        return output_data

    def get_file(self, path: str) -> bytes | None:
        group_id, encrypt_info, entry = self._get_entry_by_path(path)
        # print(group_id, entry)

        if entry is None:
            return None

        paz_path = self._base_path / group_id / f"{entry.chunk_id}.paz"
        if (f := self._paz_handle_cache.get(paz_path, None)) is None:
            f = paz_path.open("rb")
            self._paz_handle_cache[paz_path] = f

        f.seek(entry.chunk_offset)

        is_encrypted = entry.flags.crypto != PackMetaFileCrypto.NONE
        is_compressed = entry.flags.compression != PackMetaFileCompression.NONE

        read_size = (
            entry.uncompressed_size if not is_compressed else entry.compressed_size
        )
        data = f.read(read_size)

        if is_encrypted:
            assert entry.flags.crypto == PackMetaFileCrypto.CHACHA20
            data = _crypto.chacha20_decrypt_pack_entry(data, encrypt_info, path)

        if is_compressed:
            assert entry.flags.compression == PackMetaFileCompression.LZ4
            data: bytes = lz4.block.decompress(
                data, uncompressed_size=entry.uncompressed_size
            )

        is_dds_file = path.endswith(".dds") or path.endswith(".DDS")
        # is_gnf_file = path.endswith(".gnf")

        if (
            entry.flags.is_partial
            and is_dds_file
            and entry.compressed_size != entry.uncompressed_size
        ):
            header = self._pthc.get_file_header(path)
            data = self._handle_partial_texture(data, header)

        return data


__all__ = [
    "PackageContext",
]
