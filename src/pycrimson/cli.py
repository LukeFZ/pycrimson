import sys
import tqdm
import json

from typing import Callable
from pathlib import Path

from bier.EndianedBinaryIO import EndianedBytesIO

from ._context import PackageContext
from ._files import (
    PackMetaFileCrypto,
    PackMetaFileCompression,
    PackMetaFileEntry,
    SaveFile,
)
from ._reflection import ReflectionParser


def list_all_files(ctx: PackageContext):
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
                    f"{group_id} {dir_name}/{file_name} ({crypt_status}, {compress_status})"
                )


def extract_all_files(
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


def dump_all_prefabs(
    ctx: PackageContext,
    output_path: Path,
):
    output_path.mkdir(parents=True, exist_ok=True)

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

    for path, _ in all_entries:
        file_output_path = output_path / (path + ".json")
        # if file_output_path.exists():
        #    continue

        data = ctx.get_file(path)
        assert data is not None

        # print(path, len(data))

        try:
            reflection = ReflectionParser(EndianedBytesIO(data))
        except Exception as e:
            print("got exception while reading file", path)
            raise e

        # file_output_path.write_text(json.dumps(reflection.objects, indent=1))

    # print(_converters._MISSING_TYPE_SET)


import pickle


def main():
    base_directory = Path(".")
    cache_path = base_directory / "cache.pickle"
    if cache_path.exists():
        with cache_path.open("rb") as f:
            ctx: PackageContext = pickle.load(f)
    else:
        ctx = PackageContext(base_directory)
        with cache_path.open("wb") as f:
            pickle.dump(ctx, f)
    # a = ReflectionParser.from_file(
    #    base_directory / "output_temp" / "object" / "invalid.prefab"
    # )
    # print(a.objects)
    # return

    dump_all_prefabs(ctx, base_directory / "prefabs")

    # """
    while True:
        ext = input("ext?")
        if ext == "exit":
            break

        extract_all_files(
            ctx,
            base_directory / "output_temp",
            lambda path, _: path.endswith(f".{ext}"),
        )
    return
    # """

    # aaa = ReflectionFile.from_file(Path("extracted/000_water_00001.prefab"))
    # aaa.print_all_types()
    # Path("000_water_00001.prefab.json").write_text(json.dumps(aaa.objects, indent=1))
    save = SaveFile.from_encrypted_file(Path("save.save"))
    reflection_save = ReflectionParser(EndianedBytesIO(save))
    reflection_save.print_all_types()
    Path("save.json").write_text(json.dumps(reflection_save.objects, indent=1))
    return

    ctx = PackageContext(Path("."))

    # list_all_files(ctx)
    # extract_all_files(
    #    ctx, Path("output"), lambda _, y: y.flags.crypto != PackMetaFileCrypto.NONE
    # )
    # return


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
    main()
