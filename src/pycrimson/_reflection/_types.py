from bier.serialization import (
    BinarySerializable,
    u16,
    u32,
    u64,
    i64,
    custom,
    prefixed_length,
    SerializationContext,
)
from bier.EndianedBinaryIO import EndianedReaderIOBase
from dataclasses import dataclass
from enum import Flag, Enum


class TransferInstructionFlags(u32, Flag):
    NONE = 0
    UNKNOWN_0 = 1 << 0
    UNKNOWN_1 = 1 << 1
    UNKNOWN_2 = 1 << 2
    OBJECT = 1 << 3
    UNKNOWN_4 = 1 << 4
    VALIDATED_MB = 1 << 5
    UNKNOWN_6 = 1 << 6
    UNKNOWN_7 = 1 << 7
    # UNKNOWN_8 = 1 << 8
    UNKNOWN_9 = 1 << 9
    # UNKNOWN_10 = 1 << 10
    UNKNOWN_11 = 1 << 11
    VECTOR = 1 << 12
    UNKNOWN_14 = 1 << 14
    UNKNOWN_16 = 1 << 16
    UNKNOWN_17 = 1 << 17
    UNKNOWN_18 = 1 << 18
    UNKNOWN_19 = 1 << 19
    UNKNOWN_20 = 1 << 20
    UNKNOWN_22 = 1 << 22
    UNKNOWN_23 = 1 << 23
    UNKNOWN_24 = 1 << 24


@dataclass(frozen=True)
class ReflectionObjectInfo(BinarySerializable):
    type_index: u16
    unknown1: u16
    unknown2: i64
    offset: u32
    size: u32

    @classmethod
    def read_from(
        cls, reader: EndianedReaderIOBase, context: SerializationContext | None = None
    ):
        settings = context.settings if context else {}
        version = settings.get("serialization_version", 0)

        type_index = reader.read_u16()
        unknown1 = reader.read_u16() if version >= 8 else 0
        if version >= 11:
            unknown2 = reader.read_i64()
        elif version >= 8:
            unknown2 = reader.read_i32()
        else:
            unknown2 = reader.read_i16()

        offset = reader.read_u32()
        size = reader.read_u32()
        return cls(type_index, unknown1, unknown2, offset, size)


class ReflectionPropertyType(u16, Enum):
    DEFAULT = 0
    SIZE_PREFIXED = 1
    ENUM = 2
    SIMPLE_ARRAY = 3
    OBJECT = 4
    OPTIONAL_OBJECT = 5
    OBJECT_ARRAY = 6
    OBJECT_PTR_ARRAY = 7
    UNKNOWN_8 = 8
    SIZE_PREFIXED_ARRAY = 10

    def is_array_type(self):
        return self in [
            ReflectionPropertyType.SIMPLE_ARRAY,
            ReflectionPropertyType.OBJECT_ARRAY,
            ReflectionPropertyType.OBJECT_PTR_ARRAY,
            ReflectionPropertyType.SIZE_PREFIXED_ARRAY,
        ]


@dataclass(frozen=True)
class ReflectionProperty(BinarySerializable):
    name: custom[str, prefixed_length[u32]]
    type_name: custom[str, prefixed_length[u32]]
    type: ReflectionPropertyType
    fixed_size: u16
    flags: TransferInstructionFlags  # version >= 9

    @classmethod
    def read_from(
        cls, reader: EndianedReaderIOBase, context: SerializationContext | None = None
    ):
        settings = context.settings if context else {}
        version = settings.get("serialization_version", 0)

        name = reader.read_string(reader.read_u32())
        type_name = reader.read_string(reader.read_u32())
        type = ReflectionPropertyType(reader.read_u16())
        fixed_size = reader.read_u16()
        flags = TransferInstructionFlags(reader.read_u32() if version >= 9 else 0)
        return cls(name, type_name, type, fixed_size, flags)


@dataclass(frozen=True)
class ReflectionType(BinarySerializable):
    name: custom[str, prefixed_length[u32]]
    properties: custom[list[ReflectionProperty], prefixed_length[u16]]


@dataclass(frozen=True)
class ReflectionHeader(BinarySerializable):
    type_count: u32
    metadata_version: u32
    reflection_hash: u64
    serialization_version: u32

    @classmethod
    def read_from(cls, reader: EndianedReaderIOBase, context=None):
        type_count = reader.read_u16()
        if type_count == 0xFFFF:
            metadata_version = reader.read_u32()
            reflection_hash = reader.read_u64() if metadata_version >= 4 else 0
            serialization_version = reader.read_u32()
            type_count = reader.read_u16()

            return cls(
                type_count, metadata_version, reflection_hash, serialization_version
            )

        return cls(type_count, 0, 0, 0)


@dataclass(frozen=True)
class ReflectionOptional(BinarySerializable):
    unknown0: u32
    data: custom[bytes, prefixed_length[u32]]
