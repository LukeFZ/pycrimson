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
    _header: ReflectionHeader
    _types: list[ReflectionType]
    _entry2: list[str]
    _object_infos: list[ReflectionObjectInfo]
    _opt_entries: list[ReflectionOptional]

    objects: list[dict]

    _enable_debug_logging: bool

    def __init__(self, reader: EndianedReaderIOBase, has_opt_entry: bool = False):
        self._enable_debug_logging = False

        self._reader = reader
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

        self._entry2 = (
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

        if object_count > 0 and self._header.metadata_version >= 3:
            self._object_infos = [
                ReflectionObjectInfo.read_from(reader, context)
                for _ in range(object_count)
            ]

        self.objects = []
        for i, obj in enumerate(self._object_infos):
            assert reader.tell() == obj.offset, (
                f"{hex(reader.tell())} vs. {hex(obj.offset)}"
            )

            if self._enable_debug_logging:
                print("parsing obj at idx", i)

            bitmap, obj_type, has_metadata = self._read_object_metadata(i, False, False)
            parsed_obj = self._parse_object(bitmap, obj_type, has_metadata)
            self.objects.append(parsed_obj)

    def print_all_types(self):
        for type in self._types:
            print(type.name)
            for property in type.properties:
                print(
                    f"\t {property.type_name} {property.name} {property.type.name, property.fixed_size, property.flags.name}"
                )

    def _parse_object(
        self, bitmap: bytes, type_info: ReflectionType, has_metadata: bool
    ) -> dict:
        if self._enable_debug_logging:
            print(
                f"parsing object @ {hex(self._reader.tell())} : {type_info.name} ({bitmap})"
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
                object_property_bitmap, object_type, object_has_metadata = (
                    self._read_object_metadata(None, False, False)
                )
                return self._parse_object(
                    object_property_bitmap, object_type, object_has_metadata
                )
            case ReflectionPropertyType.OPTIONAL_OBJECT:
                if self._reader.read_u8() == 0:
                    return None

                object_property_bitmap, object_type, object_has_metadata = (
                    self._read_object_metadata(None, False, False)
                )
                return self._parse_object(
                    object_property_bitmap, object_type, object_has_metadata
                )
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

                has_entry2_index = False
                if self._header.serialization_version >= 0xE:
                    has_entry2_index = self._reader.read_u8() == 1

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

                        if has_entry2_index:
                            unknown_list_1 = self._reader.read_i32_array(unk_count)
                            if self._enable_debug_logging:
                                print("unknown list 2:", unknown_list_1)

                value = []
                for _ in range(array_count):
                    object_property_bitmap, object_type, object_has_metadata = (
                        self._read_object_metadata(None, has_entry2_index, False)
                    )
                    value.append(
                        self._parse_object(
                            object_property_bitmap, object_type, object_has_metadata
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
        self, index: int | None, has_entry2_index: bool, unknown_2: bool
    ) -> tuple[bytes, ReflectionType, bool]:
        type_index = 0
        if index is None or self._header.metadata_version < 3:
            has_metadata = True
        else:
            obj_meta = self._object_infos[index]
            type_index = obj_meta.type_index
            self._reader.seek(obj_meta.offset)
            has_metadata = False

        object_property_bitmap = self._reader.read_bytes(self._reader.read_u16())
        if has_metadata:
            type_index = self._reader.read_u16()
            if self._header.serialization_version >= 3:
                if self._header.serialization_version >= 0xB:
                    _ = self._reader.read_u8()  # unknown0
                    _ = self._reader.read_u64()  # unknown1
                    if has_entry2_index and self._header.serialization_version >= 0xE:
                        entry2_index = self._reader.read_u32()  # entry2_index
                        if self._enable_debug_logging:
                            print("object entry2 val:", self._entry2[entry2_index])
                            assert False

                        assert not unknown_2
                else:
                    if self._header.serialization_version < 8:
                        _ = self._reader.read_u16()
                    else:
                        _ = self._reader.read_u32()

            value_offset = self._reader.read_u32()
            self._reader.seek(value_offset)

        return object_property_bitmap, self._types[type_index], has_metadata

    @classmethod
    def from_file(cls, path: Path):
        with EndianedFileIO(path, "rb") as f:
            return cls(f)
