import unittest
from pathlib import Path
from unittest.mock import patch

from pycrimson._context import PackageContext


class TestPackageContext(unittest.TestCase):
    def test_texture_headers_are_loaded_lazily(self):
        with patch.object(PackageContext, "_parse_pack_meta") as parse_pack_meta:
            with patch(
                "pycrimson._context.PackTextureHeaderCollection.from_file"
            ) as from_file:
                PackageContext(Path("/game"))

        parse_pack_meta.assert_called_once_with()
        from_file.assert_not_called()

    def test_texture_headers_are_cached_after_first_load(self):
        ctx = PackageContext.__new__(PackageContext)
        ctx._base_path = Path("/game")
        ctx._pthc = None

        fake_collection = object()
        expected_path = Path("/game/meta/0.pathc")

        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "pycrimson._context.PackTextureHeaderCollection.from_file",
                return_value=fake_collection,
            ) as from_file:
                self.assertIs(ctx._get_texture_header_collection(), fake_collection)
                self.assertIs(ctx._get_texture_header_collection(), fake_collection)

        from_file.assert_called_once_with(expected_path)


if __name__ == "__main__":
    unittest.main()
