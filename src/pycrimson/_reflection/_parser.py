from dataclasses import dataclass
from pathlib import Path

from bier.EndianedBinaryIO import EndianedReaderIOBase, EndianedFileIO
from bier.serialization import SerializationContext

from ._types import (
    ReflectionHeader,
    ReflectionType,
    ReflectionObjectInfo,
    ReflectionOptional,
    ReflectionProperty,
    ReflectionPropertyType,
    TransferInstructionFlags,
)

from . import _converters


@dataclass(slots=True)
class ReflectionParser:
    _reader: EndianedReaderIOBase
    _base_reader_offset: int

    _header: ReflectionHeader
    _types: list[ReflectionType]
    _object_names: list[str]
    _object_infos: list[ReflectionObjectInfo]
    _opt_entries: list[ReflectionOptional]

    objects: list[dict]

    _enable_debug_logging: bool

    def __init__(
        self,
        reader: EndianedReaderIOBase,
        has_opt_entry: bool = False,
        enable_debug_logging: bool = False,
    ):
        self._enable_debug_logging = enable_debug_logging

        self._reader = reader
        self._base_reader_offset = reader.tell()
        self._header = ReflectionHeader.read_from(reader)

        context = SerializationContext(
            settings={
                "metadata_version": self._header.metadata_version,
                "serialization_version": self._header.serialization_version,
            }
        )

        self._types = [
            ReflectionType.read_from(reader, context)
            for _ in range(self._header.type_count)
        ]

        self._object_names = (
            [reader.read_string(reader.read_u32()) for _ in range(reader.read_u32())]
            if self._header.serialization_version > 0xD
            else []
        )

        self._opt_entries = (
            [
                ReflectionOptional.read_from(reader, context)
                for _ in range(reader.read_u32())
            ]
            if has_opt_entry
            else []
        )

        object_count = reader.read_u32()

        end_offset = reader.read_u32() if self._header.metadata_version >= 2 else None
        if self._enable_debug_logging:
            print("end offset:", end_offset)

        if self._header.metadata_version >= 3:
            self._object_infos = [
                ReflectionObjectInfo.read_from(reader, context)
                for _ in range(object_count)
            ]
        else:
            assert False, "todo: parsing without explicit object infos"

        self.objects = []
        for i, obj in enumerate(self._object_infos):
            absolute_object_offset = obj.offset + self._base_reader_offset
            assert reader.tell() == absolute_object_offset, (
                f"{hex(reader.tell())} vs. {hex(absolute_object_offset)}"
            )

            if self._enable_debug_logging:
                print("parsing obj at idx", i)

            parsed_obj = self._parse_object(*self._read_object_metadata(i, False))
            self.objects.append(parsed_obj)

    def print_all_types(self):
        for type in self._types:
            print(type.name)
            for property in type.properties:
                print(
                    f"\t {property.type_name} {property.name} {property.type.name, property.fixed_size, property.flags.name}"
                )

    def _parse_object(
        self,
        bitmap: bytes,
        type_info: ReflectionType,
        has_metadata: bool,
        object_name: str | None,
    ) -> dict:
        if self._enable_debug_logging:
            print(
                f"parsing object @ {hex(self._reader.tell())} '{f'{object_name or ""}'}' : {type_info.name} ({bitmap})"
            )
            for prop in type_info.properties:
                print("\t", prop)

        if self._header.serialization_version >= 0xA:
            unknown0 = self._reader.read_u8()
            if self._enable_debug_logging:
                print("object unknown0:", unknown0)

        obj: dict = {
            "__pycr_type__": type_info.name,
        }
        if object_name is not None:
            obj["__pycr_name__"] = object_name

        no_tags = False
        if self._header.serialization_version >= 5:
            no_tags = self._reader.read_u8() == 1

        if not no_tags:
            if self._header.serialization_version >= 6:
                tags = {}
                for _ in range(self._reader.read_u16()):
                    property_index = self._reader.read_u16()
                    tags[type_info.properties[property_index].name] = (
                        self._reader.read_string(self._reader.read_u32())
                    )

                if len(tags) > 0:
                    if self._enable_debug_logging:
                        print("object tags: ", tags)

                    obj["__pycr_tags__"] = tags

        for i, property in enumerate(type_info.properties):
            bitmap_bit_missing = ((bitmap[(i // 8)] >> (i & 7)) & 1) == 0

            if (self._header.serialization_version < 7) and bitmap_bit_missing:
                continue

            if (self._header.serialization_version >= 9) and (
                property.flags
                & (
                    TransferInstructionFlags.UNKNOWN_7
                    | TransferInstructionFlags.UNKNOWN_1
                )
            ) != 0:
                continue

            if not property.type.is_array_type() and bitmap_bit_missing:
                continue

            if self._enable_debug_logging:
                print(f"parsing property @ {hex(self._reader.tell())}: {property}")

            obj[property.name] = self._parse_property(property)

        if has_metadata:
            object_size = self._reader.read_u32()
            if self._enable_debug_logging:
                print("reported object size:", object_size)

        return obj

    def _parse_property(self, property: ReflectionProperty):
        if (
            (self._header.serialization_version >= 0xF)
            and property.type.is_array_type()
            and self._reader.read_u8() == 1
        ):
            return []

        match property.type:
            case ReflectionPropertyType.DEFAULT:
                return _converters.get_converted_value(
                    property.type_name, self._reader.read_bytes(property.fixed_size)
                )
            case ReflectionPropertyType.SIZE_PREFIXED:
                return _converters.get_converted_value(
                    property.type_name, self._reader.read_bytes(self._reader.read_u32())
                )
            case ReflectionPropertyType.ENUM:
                return _converters.get_converted_value(
                    property.type_name, self._reader.read_bytes(property.fixed_size)
                )
            case ReflectionPropertyType.OBJECT:
                return self._parse_object(*self._read_object_metadata(None, False))
            case ReflectionPropertyType.OPTIONAL_OBJECT:
                if self._reader.read_u8() == 0:
                    return None

                return self._parse_object(*self._read_object_metadata(None, False))
            case ReflectionPropertyType.SIMPLE_ARRAY:
                return [
                    _converters.get_converted_value(
                        property.type_name, self._reader.read_bytes(property.fixed_size)
                    )
                    for _ in range(self._reader.read_u32())
                ]
            case (
                ReflectionPropertyType.OBJECT_ARRAY
                | ReflectionPropertyType.OBJECT_PTR_ARRAY
            ):
                array_count = self._reader.read_u32()

                has_named_objects = False
                if self._header.serialization_version >= 0xE:
                    has_named_objects = self._reader.read_u8() == 1

                unknown0 = 0
                if self._header.serialization_version >= 0xB:
                    unknown0 = self._reader.read_i64()
                elif self._header.serialization_version >= 0x8:
                    unknown0 = self._reader.read_i32()
                elif self._header.serialization_version >= 0x4:
                    unknown0 = self._reader.read_i16()

                if self._enable_debug_logging:
                    print("array unknown0:", unknown0)

                if self._header.serialization_version >= 0xB:
                    unk_count = self._reader.read_i32()
                    if unk_count > 0:
                        unknown_list_0 = self._reader.read_i64_array(unk_count)
                        if self._enable_debug_logging:
                            print(
                                "unknown list:",
                                unknown_list_0,
                            )

                        if has_named_objects:
                            object_name_indices = self._reader.read_i32_array(unk_count)
                            if self._enable_debug_logging or True:
                                print(
                                    "unknown list object names:",
                                    [
                                        self._object_names[x]
                                        for x in object_name_indices
                                    ],
                                    unknown_list_0,
                                )

                value = []
                for _ in range(array_count):
                    value.append(
                        self._parse_object(
                            *self._read_object_metadata(None, has_named_objects)
                        )
                    )

                return value
            case ReflectionPropertyType.SIZE_PREFIXED_ARRAY:
                [
                    _converters.get_converted_value(
                        property.type_name,
                        self._reader.read_bytes(
                            self._reader.read_u32() * property.fixed_size
                        ),
                    )
                    for _ in range(self._reader.read_u32())
                ]
            case _:
                assert False, property

    def _read_object_metadata(
        self, index: int | None, has_object_name_index: bool
    ) -> tuple[bytes, ReflectionType, bool, str | None]:
        type_index = 0
        if index is None or self._header.metadata_version < 3:
            has_metadata = True
        else:
            obj_meta = self._object_infos[index]
            type_index = obj_meta.type_index
            self._reader.seek(self._base_reader_offset + obj_meta.offset)
            has_metadata = False

        object_property_bitmap = self._reader.read_bytes(self._reader.read_u16())
        object_name = None

        if has_metadata:
            type_index = self._reader.read_u16()
            if self._header.serialization_version >= 3:
                if self._header.serialization_version >= 0xB:
                    unknown1 = self._reader.read_u8() == 1
                    if self._enable_debug_logging:
                        print(
                            "object meta unknown1 (maybe is static object?):", unknown1
                        )

                    unknown0 = self._reader.read_i64()

                    if self._header.serialization_version >= 0xE:
                        if has_object_name_index:
                            object_name_index = self._reader.read_i32()
                            assert object_name_index >= 0, object_name_index

                            object_name = self._object_names[object_name_index]
                            if self._enable_debug_logging:
                                print("object name:", object_name)

                else:
                    if self._header.serialization_version >= 8:
                        unknown0 = self._reader.read_i32()
                    else:
                        unknown0 = self._reader.read_i16()

                if self._enable_debug_logging:
                    print("object meta unknown0:", unknown0)

            value_offset = self._reader.read_u32()
            self._reader.seek(self._base_reader_offset + value_offset)

        return (
            object_property_bitmap,
            self._types[type_index],
            has_metadata,
            object_name,
        )

    @classmethod
    def from_file(cls, path: Path, enable_debug_logging: bool = False):
        with EndianedFileIO(path, "rb") as f:
            return cls(f, enable_debug_logging=enable_debug_logging)
