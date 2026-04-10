# pycrimson

A python library and CLI tool to work with Crimson Desert game files and savegames.

-----

## Notice

This is, to my knowledge, the first public implementation of the proper[^1] key derivation for both asset files and save files.  
As such, please credit me if you reuse the implementations found in this tool in your own projects.

[^1]: The pre-existing one for asset files, which seems LLM-generated, is hardcoded to only work with packs that use the default encryption key material. This happens to currently work, as no packs currently use different encryption key material.

-----

## Features

`pycrimson` currently supports:

- pack file enumeration and extraction from `.paz` / `.pamt`
- programmatic pack entry iteration via `PackageContext.iter_entries()`
- machine-readable inventory output from `list-pack-files --output-format jsonl`
- proper decompression of partially-compressed `.dds` assets
- save file decryption and re-encryption
- parsing of reflection-based serialized files
- prefab extraction to JSON
- reading additional game file types such as `.pabgh`, `.pabgb`, `.paloc`, and `binarystring`

## Installation

This library targets Python 3.14.

```console
pip install git+https://github.com/LukeFZ/pycrimson
```

or, as an uv tool:

```console
uv tool install git+https://github.com/LukeFZ/pycrimson
```

## CLI

The `pycrimson` CLI works against the game install root, i.e. the directory that contains `meta/` and the numbered shard folders.

Main commands:

| Command                 | Purpose                                                                                  |
|-------------------------|------------------------------------------------------------------------------------------|
| `list-pack-files`       | List pack contents in a human-readable form, or as JSONL                                 |
| `extract-pack-files`    | Extract files from the pack set, optionally filtered by extension, folder, or encryption |
| `extract-prefabs`       | Parse `.prefab` files and write them as JSON                                             |
| `parse-serialized-file` | Parse a serialized file and write JSON output                                            |
| `decrypt-save`          | Decrypt a save file                                                                      |
| `encrypt-save`          | Re-encrypt a decrypted save file                                                         |

Examples:

```console
pycrimson list-pack-files "/path/to/Crimson Desert"
pycrimson list-pack-files "/path/to/Crimson Desert" --output-format jsonl
pycrimson extract-pack-files "/path/to/Crimson Desert" ./out --only-extension dds
pycrimson extract-prefabs "/path/to/Crimson Desert" ./prefabs
pycrimson parse-serialized-file some_file.bin
pycrimson decrypt-save save.save
pycrimson encrypt-save save.save_dec
```

## Library

The library API is centered around `PackageContext` for pack access and `SaveFile` / `ReflectionParser` for save and serialized data.

Main entry points:

- `PackageContext(...)` for pack access
- `PackageContext.get_file(path)` to read one virtual path from the pack set
- `PackageContext.iter_entries()` to enumerate pack entries programmatically
- `SaveFile.from_encrypted_file(...)` / `SaveFile.write_encrypted_file(...)` for save handling
- `ReflectionParser.from_file(...)` for serialized files

Example:

```python
from pathlib import Path

from pycrimson import PackageContext

ctx = PackageContext(Path("/path/to/Crimson Desert"))

for entry in ctx.iter_entries():
    print(entry.path, entry.shard, entry.crypto.name, entry.compression.name)

data = ctx.get_file("actionchart/xml/description/commonactioninfo.xml")
```

## License

`pycrimson` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Special Thanks

- [Samboy063](https://github.com/SamboyCoding) for listening to me rant about the formats for hours on end and helping with some of the struct definitions.
