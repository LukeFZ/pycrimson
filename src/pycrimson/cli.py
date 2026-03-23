import sys
import tqdm
import json

from typing import Callable
from pathlib import Path
from cyclopts import validators, App, Parameter
from typing import Annotated
from rich.console import Console
from rich import traceback

from bier.EndianedBinaryIO import EndianedBytesIO

from ._context import PackageContext
from ._files import (
    PackMetaFileCrypto,
    PackMetaFileCompression,
    PackMetaFileEntry,
    SaveFile,
)
from ._reflection import ReflectionParser

_error_console = Console(stderr=True)
app = App(error_console=_error_console)
traceback.install(console=_error_console)


def _extract_all_files(
    ctx: PackageContext,
    output_path: Path,
    filter: Callable[[str, PackMetaFileEntry], bool] | None = None,
):
    output_path.mkdir(parents=True, exist_ok=True)

    all_entries: list[tuple[str, PackMetaFileEntry]] = []
    for x in ctx._packs.values():
        for dir_path, y in x.directories.items():
            any_matched = False

            for file_name, file_entry in y.items():
                full_path = f"{dir_path}/{file_name}"
                if filter is not None and not filter(full_path, file_entry):
                    continue

                any_matched = True
                all_entries.append((full_path, file_entry))

            if any_matched:
                (output_path / dir_path).mkdir(parents=True, exist_ok=True)

    for path, _ in tqdm.tqdm(all_entries):
        file_output_path = output_path / path
        if file_output_path.exists():
            continue

        data = ctx.get_file(path)
        assert data is not None
        file_output_path.write_bytes(data)


def _list_all_files(ctx: PackageContext):
    for group_id, pack in ctx._packs.items():
        for dir_name, dir in pack.directories.items():
            for file_name, file in dir.items():
                crypt_status = (
                    "encrypted"
                    if file.flags.crypto != PackMetaFileCrypto.NONE
                    else "unencrypted"
                )
                compress_status = (
                    "compressed"
                    if file.flags.compression != PackMetaFileCompression.NONE
                    else "uncompressed"
                )
                if file.flags.is_partial:
                    compress_status = "partially compressed"

                print(
                    f"{group_id} | {dir_name}/{file_name} ({crypt_status}, {compress_status})"
                )


def _extract_prefabs(
    ctx: PackageContext, output_path: Path, write_to_disk: bool, overwrite: bool
):
    all_entries: list[tuple[str, PackMetaFileEntry]] = []
    for x in ctx._packs.values():
        for dir_path, y in x.directories.items():
            any_matched = False

            for file_name, file_entry in y.items():
                full_path = f"{dir_path}/{file_name}"
                if not file_name.endswith(".prefab"):
                    continue

                any_matched = True
                all_entries.append((full_path, file_entry))

            if any_matched:
                (output_path / dir_path).mkdir(parents=True, exist_ok=True)

    for path, _ in tqdm.tqdm(all_entries):
        file_output_path = output_path / (path + ".json")
        if overwrite and file_output_path.exists():
            continue

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
):
    output_path.mkdir(parents=True, exist_ok=True)

    if only_extension is not None and not only_extension.startswith("."):
        only_extension = f".{only_extension}"

    context = PackageContext(pack_path)

    def _filter(path: str, entry: PackMetaFileEntry):
        if only_extension is not None and not path.endswith(only_extension):
            return False

        if only_encrypted and entry.flags.crypto == PackMetaFileCrypto.NONE:
            return False

        return True

    _extract_all_files(context, output_path, _filter)


@app.command
def list_pack_files(
    pack_path: Annotated[
        Path, Parameter(validator=validators.Path(exists=True, file_okay=False))
    ],
):
    context = PackageContext(pack_path)
    _list_all_files(context)


@app.command
def decrypt_save(
    save_path: Annotated[
        Path, Parameter(validator=validators.Path(exists=True, dir_okay=False))
    ],
    output_path: Annotated[
        Path | None, Parameter(validator=validators.Path(dir_okay=False))
    ],
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
    ],
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
    ],
    enable_debug_logging: bool = False,
):
    if output_path is None:
        output_path = serialized_path.with_suffix(".json")

    parsed = ReflectionParser.from_file(serialized_path, enable_debug_logging)
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
