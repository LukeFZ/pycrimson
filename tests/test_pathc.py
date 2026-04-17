import unittest
from types import SimpleNamespace

from pycrimson._crypto import calculate_checksum
from pycrimson._files._pathc import (
    PackTextureHeaderCollection,
    _PackTextureHeaderCollectionCollisionEntry,
    _PackTextureHeaderCollectionEntry,
)


class TestPackTextureHeaderCollection(unittest.TestCase):
    def _make_collection(self, normalized_path: str) -> PackTextureHeaderCollection:
        checksum = calculate_checksum(normalized_path)

        collection = PackTextureHeaderCollection.__new__(PackTextureHeaderCollection)
        collection._header = SimpleNamespace(header_size=0x80)
        collection._headers = [b"A" * 0x80, b"B" * 0x80]
        collection._entries = {
            checksum: _PackTextureHeaderCollectionEntry(
                texture_header_index=0xFFFF,
                collision_start_index=0,
                collision_end_index=0,
                compressed_block_infos=b"\x00" * 16,
            )
        }
        collection._hash_collision_entries = {
            normalized_path: _PackTextureHeaderCollectionCollisionEntry(
                filename_offset=0,
                texture_header_index=1,
                unknown0=0,
                compressed_block_infos=b"\x00" * 16,
            )
        }
        return collection

    def test_collision_lookup_normalizes_leading_slash(self):
        path = "ui/texture/image/worldmap/cd_worldmap_road_sdf_32768x32768_6_8.dds"
        normalized_path = f"/{path}"
        collection = self._make_collection(normalized_path)

        header = collection.get_file_header(path)

        self.assertEqual(header, b"B" * 0x80)

    def test_collision_lookup_accepts_already_normalized_path(self):
        normalized_path = "/ui/texture/image/worldmap/cd_worldmap_road_sdf_32768x32768_6_8.dds"
        collection = self._make_collection(normalized_path)

        header = collection.get_file_header(normalized_path)

        self.assertEqual(header, b"B" * 0x80)


if __name__ == "__main__":
    unittest.main()
