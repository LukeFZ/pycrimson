# pycrimson

A python library and CLI tool to work with Crimson Desert game files and savegames.

-----

## Notice
This is, to my knowledge, the first public implementation of the proper[^1] key derivation for both asset files and save files.  
As such, please credit me if you reuse the implementations found in this tool in your own projects.

[^1]: The pre-existing one for asset files, which seems LLM-generated, is hardcoded to only work with packs that use the default encryption key material. This happens to currently work, as no packs currently use different encryption key material. 

-----

## Features

- Extraction of assets from the .paz/.pamt packs
- Proper decompression of partially-compressed .dds assets
- Decryption and re-encryption of game save files
- Deserialization of the reflection-based serializer used for the savegame and a lot of asset formats

## Installation

This library targets Python 3.14.

```console
pip install git+https://github.com/LukeFZ/pycrimson
```

or, as an uv tool:
```console
uv tool install git+https://github.com/LukeFZ/pycrimson
```

## License

`pycrimson` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Acknowledgements

- [Samboy063](https://github.com/SamboyCoding) for listening to me rant about the formats for hours on end and helping with some of the struct definitions. 