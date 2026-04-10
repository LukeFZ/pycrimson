import sys
import tqdm
import json
import pickle

from typing import Callable
from pathlib import Path
from cyclopts import validators, App, Parameter
from typing import Annotated
from rich.console import Console
from rich import traceback

from bier.EndianedBinaryIO import EndianedBytesIO

from ._context import PackEntry, PackageContext
from ._files import (
    PackMetaFileCrypto,
    PackMetaFileCompression,
    SaveFile,
)
from ._reflection import ReflectionParser

_error_console = Console(stderr=True)
app = App(error_console=_error_console)
traceback.install(console=_error_console)


def _extract_all_files(
    ctx: PackageContext,
    output_path: Path,
    filter: Callable[[PackEntry], bool] | None = None,
):
    output_path.mkdir(parents=True, exist_ok=True)

    all_entries = list(ctx.iter_entries())
    if filter is not None:
        all_entries = [entry for entry in all_entries if filter(entry)]

    for entry in tqdm.tqdm(all_entries):
        path = entry.path
        file_output_path = output_path / path
        if file_output_path.exists():
            continue

        file_output_path.parent.mkdir(parents=True, exist_ok=True)
        data = ctx.get_file(path)
        assert data is not None
        file_output_path.write_bytes(data)


def _pack_entry_to_json_obj(entry: PackEntry) -> dict[str, str | int | bool]:
    return {
        "path": entry.path,
        "shard": entry.shard,
        "crypto": entry.crypto.name,
        "compression": entry.compression.name,
        "is_partial": entry.is_partial,
        "uncompressed_size": entry.uncompressed_size,
        "compressed_size": entry.compressed_size,
        "chunk_id": entry.chunk_id,
    }


def _list_all_files(ctx: PackageContext, output_format: str = "text"):
    if output_format == "jsonl":
        for entry in ctx.iter_entries():
            print(json.dumps(_pack_entry_to_json_obj(entry)))
        return

    if output_format != "text":
        raise ValueError(f"unsupported output format: {output_format}")

    for entry in ctx.iter_entries():
        crypt_status = (
            "encrypted" if entry.crypto != PackMetaFileCrypto.NONE else "unencrypted"
        )
        compress_status = (
            "compressed"
            if entry.compression != PackMetaFileCompression.NONE
            else "uncompressed"
        )
        if entry.is_partial:
            compress_status = "partially compressed"

        print(f"{entry.shard} | {entry.path} ({crypt_status}, {compress_status})")


def _extract_prefabs(
    ctx: PackageContext, output_path: Path, write_to_disk: bool, overwrite: bool
):
    all_entries = [entry for entry in ctx.iter_entries() if entry.path.endswith(".prefab")]

    for entry in tqdm.tqdm(all_entries):
        path = entry.path
        file_output_path = output_path / (path + ".json")
        if overwrite and file_output_path.exists():
            continue

        file_output_path.parent.mkdir(parents=True, exist_ok=True)
        data = ctx.get_file(path)
        assert data is not None

        try:
            reflection = ReflectionParser(EndianedBytesIO(data))
        except Exception as e:
            print("got exception while reading file", path)
            raise e

        if write_to_disk:
            with file_output_path.open("w") as f:
                json.dump(reflection.objects, f, indent=1)


@app.command
def extract_pack_files(
    pack_path: Annotated[
        Path, Parameter(validator=validators.Path(exists=True, file_okay=False))
    ],
    output_path: Annotated[Path, Parameter(validator=validators.Path(file_okay=False))],
    only_extension: str | None = None,
    only_encrypted: bool = False,
    only_folder: str | None = None,
    cache_path: Annotated[
        Path | None, Parameter(validator=validators.Path(dir_okay=False))
    ] = None,
):
    output_path.mkdir(parents=True, exist_ok=True)

    if only_extension is not None and not only_extension.startswith("."):
        only_extension = f".{only_extension}"

    if cache_path is not None and cache_path.exists():
        with cache_path.open("rb") as f:
            context: PackageContext = pickle.load(f)
    else:
        context = PackageContext(pack_path)

        if cache_path is not None:
            with cache_path.open("wb") as f:
                pickle.dump(context, f)

    def _filter(entry: PackEntry):
        path = entry.path
        if only_extension is not None and not path.endswith(only_extension):
            return False

        if only_encrypted and entry.crypto == PackMetaFileCrypto.NONE:
            return False

        if only_folder is not None and not path.startswith(only_folder):
            return False

        return True

    _extract_all_files(context, output_path, _filter)


@app.command
def list_pack_files(
    pack_path: Annotated[
        Path, Parameter(validator=validators.Path(exists=True, file_okay=False))
    ],
    output_format: str = "text",
):
    context = PackageContext(pack_path)
    _list_all_files(context, output_format=output_format)


@app.command
def decrypt_save(
    save_path: Annotated[
        Path, Parameter(validator=validators.Path(exists=True, dir_okay=False))
    ],
    output_path: Annotated[
        Path | None, Parameter(validator=validators.Path(dir_okay=False))
    ] = None,
):
    if output_path is None:
        output_path = save_path.with_suffix(".save_dec")

    output_path.write_bytes(SaveFile.from_encrypted_file(save_path))


@app.command
def encrypt_save(
    save_path: Annotated[
        Path, Parameter(validator=validators.Path(exists=True, dir_okay=False))
    ],
    output_path: Annotated[
        Path | None, Parameter(validator=validators.Path(dir_okay=False))
    ] = None,
):
    if output_path is None:
        output_path = save_path.with_suffix(".save")

    SaveFile.write_encrypted_file(save_path.read_bytes(), output_path)


@app.command
def parse_serialized_file(
    serialized_path: Annotated[
        Path, Parameter(validator=validators.Path(exists=True, dir_okay=False))
    ],
    output_path: Annotated[
        Path | None, Parameter(validator=validators.Path(dir_okay=False))
    ] = None,
    enable_debug_logging: bool = False,
):
    if output_path is None:
        output_path = serialized_path.with_suffix(".json")

    parsed = ReflectionParser.from_file(
        serialized_path, enable_debug_logging=enable_debug_logging
    )
    with output_path.open("w") as f:
        json.dump(parsed.objects, f, indent=1)


@app.command
def extract_prefabs(
    pack_path: Annotated[
        Path, Parameter(validator=validators.Path(exists=True, file_okay=False))
    ],
    output_path: Annotated[Path, Parameter(validator=validators.Path(file_okay=False))],
    write_to_disk: bool = True,
    overwrite: bool = True,
):
    output_path.mkdir(parents=True, exist_ok=True)

    context = PackageContext(pack_path)
    _extract_prefabs(context, output_path, write_to_disk, overwrite)


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
    app()


if __name__ == "__main__":
    main()
