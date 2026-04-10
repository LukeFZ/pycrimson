import json

from types import SimpleNamespace

from pycrimson import PackEntry, PackageContext
from pycrimson._files import (
    PackMetaFile,
    PackMetaFileCompression,
    PackMetaFileCrypto,
)
from pycrimson._files._pamt import PackMetaFileFlags
from pycrimson.cli import _list_all_files


def _make_context():
    ctx = PackageContext.__new__(PackageContext)
    ctx._packs = {
        "0000": SimpleNamespace(
            directories={
                "dir": {
                    "file.bin": PackMetaFile(
                        name_offset=0,
                        chunk_offset=0,
                        compressed_size=10,
                        uncompressed_size=20,
                        chunk_id=7,
                        flags=PackMetaFileFlags(
                            PackMetaFileCompression.LZ4,
                            PackMetaFileCrypto.CHACHA20,
                            False,
                        ),
                        unknown0=0,
                    )
                }
            }
        ),
        "0001": SimpleNamespace(
            directories={
                "ui": {
                    "image.dds": PackMetaFile(
                        name_offset=1,
                        chunk_offset=8,
                        compressed_size=30,
                        uncompressed_size=45,
                        chunk_id=3,
                        flags=PackMetaFileFlags(
                            PackMetaFileCompression.NONE,
                            PackMetaFileCrypto.NONE,
                            True,
                        ),
                        unknown0=0,
                    )
                }
            }
        ),
    }
    return ctx


def test_public_exports_include_inventory_api():
    assert PackEntry is not None
    assert PackageContext is not None


def test_iter_entries_returns_pack_entries_in_pack_order():
    ctx = _make_context()

    entries = list(ctx.iter_entries())

    assert entries == [
        PackEntry(
            path="dir/file.bin",
            shard="0000",
            crypto=PackMetaFileCrypto.CHACHA20,
            compression=PackMetaFileCompression.LZ4,
            is_partial=False,
            uncompressed_size=20,
            compressed_size=10,
            chunk_id=7,
        ),
        PackEntry(
            path="ui/image.dds",
            shard="0001",
            crypto=PackMetaFileCrypto.NONE,
            compression=PackMetaFileCompression.NONE,
            is_partial=True,
            uncompressed_size=45,
            compressed_size=30,
            chunk_id=3,
        ),
    ]


def test_list_all_files_text_output_preserves_human_readable_status(capsys):
    ctx = _make_context()

    _list_all_files(ctx)

    assert capsys.readouterr().out.splitlines() == [
        "0000 | dir/file.bin (encrypted, compressed)",
        "0001 | ui/image.dds (unencrypted, partially compressed)",
    ]


def test_list_all_files_jsonl_output_is_machine_readable(capsys):
    ctx = _make_context()

    _list_all_files(ctx, output_format="jsonl")

    lines = capsys.readouterr().out.splitlines()
    assert [json.loads(line) for line in lines] == [
        {
            "path": "dir/file.bin",
            "shard": "0000",
            "crypto": "CHACHA20",
            "compression": "LZ4",
            "is_partial": False,
            "uncompressed_size": 20,
            "compressed_size": 10,
            "chunk_id": 7,
        },
        {
            "path": "ui/image.dds",
            "shard": "0001",
            "crypto": "NONE",
            "compression": "NONE",
            "is_partial": True,
            "uncompressed_size": 45,
            "compressed_size": 30,
            "chunk_id": 3,
        },
    ]
