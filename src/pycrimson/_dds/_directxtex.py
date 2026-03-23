from ._types import DDS_PIXELFORMAT, DXGI_FORMAT

# These are ports from the respective DirectXTex functions with the same (pascal-cased) name.


def _bits_per_pixel(fmt: DXGI_FORMAT) -> int:
    match fmt:
        case (
            DXGI_FORMAT.DXGI_FORMAT_R32G32B32A32_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R32G32B32A32_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_R32G32B32A32_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R32G32B32A32_SINT
        ):
            return 128

        case (
            DXGI_FORMAT.DXGI_FORMAT_R32G32B32_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R32G32B32_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_R32G32B32_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R32G32B32_SINT
        ):
            return 96

        case (
            DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_SNORM
            | DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_SINT
            | DXGI_FORMAT.DXGI_FORMAT_R32G32_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R32G32_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_R32G32_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R32G32_SINT
            | DXGI_FORMAT.DXGI_FORMAT_R32G8X24_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_D32_FLOAT_S8X24_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R32_FLOAT_X8X24_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_X32_TYPELESS_G8X24_UINT
            | DXGI_FORMAT.DXGI_FORMAT_Y416
            | DXGI_FORMAT.DXGI_FORMAT_Y210
            | DXGI_FORMAT.DXGI_FORMAT_Y216
        ):
            return 64

        case (
            DXGI_FORMAT.DXGI_FORMAT_R10G10B10A2_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R10G10B10A2_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R10G10B10A2_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R11G11B10_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_R8G8B8A8_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R8G8B8A8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R8G8B8A8_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_R8G8B8A8_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R8G8B8A8_SNORM
            | DXGI_FORMAT.DXGI_FORMAT_R8G8B8A8_SINT
            | DXGI_FORMAT.DXGI_FORMAT_R16G16_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R16G16_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_R16G16_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R16G16_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R16G16_SNORM
            | DXGI_FORMAT.DXGI_FORMAT_R16G16_SINT
            | DXGI_FORMAT.DXGI_FORMAT_R32_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_D32_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_R32_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_R32_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R32_SINT
            | DXGI_FORMAT.DXGI_FORMAT_R24G8_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_D24_UNORM_S8_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R24_UNORM_X8_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_X24_TYPELESS_G8_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R9G9B9E5_SHAREDEXP
            | DXGI_FORMAT.DXGI_FORMAT_R8G8_B8G8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_G8R8_G8B8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_B8G8R8A8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_B8G8R8X8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R10G10B10_XR_BIAS_A2_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_B8G8R8A8_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_B8G8R8A8_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_B8G8R8X8_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_B8G8R8X8_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_AYUV
            | DXGI_FORMAT.DXGI_FORMAT_Y410
            | DXGI_FORMAT.DXGI_FORMAT_YUY2
        ):
            return 32

        case DXGI_FORMAT.DXGI_FORMAT_P010 | DXGI_FORMAT.DXGI_FORMAT_P016:
            return 24

        case (
            DXGI_FORMAT.DXGI_FORMAT_R8G8_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R8G8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R8G8_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R8G8_SNORM
            | DXGI_FORMAT.DXGI_FORMAT_R8G8_SINT
            | DXGI_FORMAT.DXGI_FORMAT_R16_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R16_FLOAT
            | DXGI_FORMAT.DXGI_FORMAT_D16_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R16_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R16_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R16_SNORM
            | DXGI_FORMAT.DXGI_FORMAT_R16_SINT
            | DXGI_FORMAT.DXGI_FORMAT_B5G6R5_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_B5G5R5A1_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_A8P8
            | DXGI_FORMAT.DXGI_FORMAT_B4G4R4A4_UNORM
        ):
            return 16

        case (
            DXGI_FORMAT.DXGI_FORMAT_NV12
            | DXGI_FORMAT.DXGI_FORMAT_420_OPAQUE
            | DXGI_FORMAT.DXGI_FORMAT_NV11
        ):
            return 12

        case (
            DXGI_FORMAT.DXGI_FORMAT_R8_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_R8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_R8_UINT
            | DXGI_FORMAT.DXGI_FORMAT_R8_SNORM
            | DXGI_FORMAT.DXGI_FORMAT_R8_SINT
            | DXGI_FORMAT.DXGI_FORMAT_A8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC2_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC2_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC2_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_BC3_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC3_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC3_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_BC5_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC5_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC5_SNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC6H_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC6H_UF16
            | DXGI_FORMAT.DXGI_FORMAT_BC6H_SF16
            | DXGI_FORMAT.DXGI_FORMAT_BC7_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC7_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC7_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_AI44
            | DXGI_FORMAT.DXGI_FORMAT_IA44
            | DXGI_FORMAT.DXGI_FORMAT_P8
        ):
            return 8

        case DXGI_FORMAT.DXGI_FORMAT_R1_UNORM:
            return 1

        case (
            DXGI_FORMAT.DXGI_FORMAT_BC1_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC1_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC1_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_BC4_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC4_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC4_SNORM
        ):
            return 4

        case _:
            return 0


def get_surface_info(
    width: int,
    height: int,
    fmt: DXGI_FORMAT,
) -> tuple[int, int, int]:
    assert fmt != DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

    num_bytes: int = 0
    row_bytes: int = 0
    num_rows: int = 0

    bc = False
    packed = False
    planar = False
    bpe = 0

    match fmt:
        case (
            DXGI_FORMAT.DXGI_FORMAT_BC1_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC1_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC1_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_BC4_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC4_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC4_SNORM
        ):
            bc = True
            bpe = 8

        case (
            DXGI_FORMAT.DXGI_FORMAT_BC2_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC2_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC2_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_BC3_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC3_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC3_UNORM_SRGB
            | DXGI_FORMAT.DXGI_FORMAT_BC5_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC5_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC5_SNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC6H_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC6H_UF16
            | DXGI_FORMAT.DXGI_FORMAT_BC6H_SF16
            | DXGI_FORMAT.DXGI_FORMAT_BC7_TYPELESS
            | DXGI_FORMAT.DXGI_FORMAT_BC7_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_BC7_UNORM_SRGB
        ):
            bc = True
            bpe = 16

        case (
            DXGI_FORMAT.DXGI_FORMAT_R8G8_B8G8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_G8R8_G8B8_UNORM
            | DXGI_FORMAT.DXGI_FORMAT_YUY2
        ):
            packed = True
            bpe = 4

        case DXGI_FORMAT.DXGI_FORMAT_Y210 | DXGI_FORMAT.DXGI_FORMAT_Y216:
            packed = True
            bpe = 8

        case DXGI_FORMAT.DXGI_FORMAT_NV12 | DXGI_FORMAT.DXGI_FORMAT_420_OPAQUE:
            assert (height % 2) == 0

            planar = True
            bpe = 2

        case DXGI_FORMAT.DXGI_FORMAT_P208:
            planar = True
            bpe = 2

        case DXGI_FORMAT.DXGI_FORMAT_P010 | DXGI_FORMAT.DXGI_FORMAT_P016:
            assert (height % 2) == 0

            planar = True
            bpe = 4

        case _:
            pass

    if bc:
        num_blocks_wide = 0
        if width > 0:
            num_blocks_wide = max(1, (int(width) + 3) // 4)

        num_blocks_high = 0
        if height > 0:
            num_blocks_high = max(1, (int(height) + 3) // 4)

        row_bytes = num_blocks_wide * bpe
        num_rows = num_blocks_high
        num_bytes = row_bytes * num_blocks_high

    elif packed:
        row_bytes = ((int(width) + 1) >> 1) * bpe
        num_rows = int(height)
        num_bytes = row_bytes * int(height)

    elif fmt == DXGI_FORMAT.DXGI_FORMAT_NV11:
        row_bytes = ((int(width) + 3) >> 2) * 4
        # Direct3D makes this simplifying assumption, although it is larger than the 4:1:1 data
        num_rows = int(height) * 2
        num_bytes = row_bytes * num_rows

    elif planar:
        row_bytes = ((int(width) + 1) >> 1) * bpe
        num_bytes = (row_bytes * int(height)) + ((row_bytes * int(height) + 1) >> 1)
        num_rows = int(height) + ((int(height) + 1) >> 1)

    else:
        bpp = _bits_per_pixel(fmt)
        assert bpp != 0

        # round up to nearest byte
        row_bytes = (int(width) * bpp + 7) // 8
        num_rows = int(height)
        num_bytes = row_bytes * int(height)

    return int(num_bytes), int(row_bytes), int(num_rows)


def get_dxgi_format(ddpf: DDS_PIXELFORMAT) -> DXGI_FORMAT:
    DDS_FOURCC = 0x00000004  # DDPF_FOURCC
    DDS_RGB = 0x00000040  # DDPF_RGB
    # DDS_RGBA = 0x00000041  # DDPF_RGB | DDPF_ALPHAPIXELS
    DDS_LUMINANCE = 0x00020000  # DDPF_LUMINANCE
    # DDS_LUMINANCEA = 0x00020001  # DDPF_LUMINANCE | DDPF_ALPHAPIXELS
    # DDS_ALPHAPIXELS = 0x00000001  # DDPF_ALPHAPIXELS
    DDS_ALPHA = 0x00000002  # DDPF_ALPHA
    # DDS_PAL8 = 0x00000020  # DDPF_PALETTEINDEXED8
    # DDS_PAL8A = 0x00000021  # DDPF_PALETTEINDEXED8 | DDPF_ALPHAPIXELS
    # DDS_BUMPLUMINANCE = 0x00040000  # DDPF_BUMPLUMINANCE
    DDS_BUMPDUDV = 0x00080000  # DDPF_BUMPDUDV
    # DDS_BUMPDUDVA = 0x00080001  # DDPF_BUMPDUDV | DDPF_ALPHAPIXELS

    def _make_fourcc(a: str, b: str, c: str, d: str) -> bytes:
        return bytes((ord(a) & 0xFF, ord(b) & 0xFF, ord(c) & 0xFF, ord(d) & 0xFF))

    def _is_bitmask(ddpf: DDS_PIXELFORMAT, r: int, g: int, b: int, a: int) -> bool:
        return (
            int(ddpf.r_bit_mask) == r
            and int(ddpf.g_bit_mask) == g
            and int(ddpf.b_bit_mask) == b
            and int(ddpf.a_bit_mask) == a
        )

    if ddpf.flags & DDS_RGB:
        # Note that sRGB formats are written using the "DX10" extended header
        bitcount = int(ddpf.rgb_bit_count)

        if bitcount == 32:
            if _is_bitmask(ddpf, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000):
                return DXGI_FORMAT.DXGI_FORMAT_R8G8B8A8_UNORM

            if _is_bitmask(ddpf, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000):
                return DXGI_FORMAT.DXGI_FORMAT_B8G8R8A8_UNORM

            if _is_bitmask(ddpf, 0x00FF0000, 0x0000FF00, 0x000000FF, 0x00000000):
                return DXGI_FORMAT.DXGI_FORMAT_B8G8R8X8_UNORM

            # 10:10:10:2 (D3DX commonly wrote "backwards" masks)
            if _is_bitmask(ddpf, 0x3FF00000, 0x000FFC00, 0x000003FF, 0xC0000000):
                return DXGI_FORMAT.DXGI_FORMAT_R10G10B10A2_UNORM

            if _is_bitmask(ddpf, 0x0000FFFF, 0xFFFF0000, 0x00000000, 0x00000000):
                return DXGI_FORMAT.DXGI_FORMAT_R16G16_UNORM

            if _is_bitmask(ddpf, 0xFFFFFFFF, 0x00000000, 0x00000000, 0x00000000):
                # Only 32-bit color channel format in D3D9 was R32F; D3DX may also store as FourCC=114
                return DXGI_FORMAT.DXGI_FORMAT_R32_FLOAT

            return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

        if bitcount == 24:
            # No 24bpp DXGI formats
            return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

        if bitcount == 16:
            if _is_bitmask(ddpf, 0x7C00, 0x03E0, 0x001F, 0x8000):
                return DXGI_FORMAT.DXGI_FORMAT_B5G5R5A1_UNORM

            if _is_bitmask(ddpf, 0xF800, 0x07E0, 0x001F, 0x0000):
                return DXGI_FORMAT.DXGI_FORMAT_B5G6R5_UNORM

            if _is_bitmask(ddpf, 0x0F00, 0x00F0, 0x000F, 0xF000):
                return DXGI_FORMAT.DXGI_FORMAT_B4G4R4A4_UNORM

            # NVTT 1.x wrote this as RGB instead of LUMINANCE
            if _is_bitmask(ddpf, 0x00FF, 0x0000, 0x0000, 0xFF00):
                return DXGI_FORMAT.DXGI_FORMAT_R8G8_UNORM

            if _is_bitmask(ddpf, 0xFFFF, 0x0000, 0x0000, 0x0000):
                return DXGI_FORMAT.DXGI_FORMAT_R16_UNORM

            return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

        if bitcount == 8:
            # NVTT 1.x wrote this as RGB instead of LUMINANCE
            if _is_bitmask(ddpf, 0xFF, 0x0000, 0x0000, 0x0000):
                return DXGI_FORMAT.DXGI_FORMAT_R8_UNORM

            return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

        return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

    if ddpf.flags & DDS_LUMINANCE:
        bitcount = int(ddpf.rgb_bit_count)

        if bitcount == 16:
            if _is_bitmask(ddpf, 0xFFFF, 0x0000, 0x0000, 0x0000):
                return (
                    DXGI_FORMAT.DXGI_FORMAT_R16_UNORM
                )  # often written as DX10 extension
            if _is_bitmask(ddpf, 0x00FF, 0x0000, 0x0000, 0xFF00):
                return (
                    DXGI_FORMAT.DXGI_FORMAT_R8G8_UNORM
                )  # often written as DX10 extension
            return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

        if bitcount == 8:
            if _is_bitmask(ddpf, 0xFF, 0x0000, 0x0000, 0x0000):
                return (
                    DXGI_FORMAT.DXGI_FORMAT_R8_UNORM
                )  # often written as DX10 extension

            # Some DDS writers assume the bitcount should be 8 instead of 16
            if _is_bitmask(ddpf, 0x00FF, 0x0000, 0x0000, 0xFF00):
                return DXGI_FORMAT.DXGI_FORMAT_R8G8_UNORM

            return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

        return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

    if ddpf.flags & DDS_ALPHA:
        if int(ddpf.rgb_bit_count) == 8:
            return DXGI_FORMAT.DXGI_FORMAT_A8_UNORM
        return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

    if ddpf.flags & DDS_BUMPDUDV:
        bitcount = int(ddpf.rgb_bit_count)

        if bitcount == 32:
            if _is_bitmask(ddpf, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000):
                return (
                    DXGI_FORMAT.DXGI_FORMAT_R8G8B8A8_SNORM
                )  # often written as DX10 extension

            if _is_bitmask(ddpf, 0x0000FFFF, 0xFFFF0000, 0x00000000, 0x00000000):
                return (
                    DXGI_FORMAT.DXGI_FORMAT_R16G16_SNORM
                )  # often written as DX10 extension

            return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

        if bitcount == 16:
            if _is_bitmask(ddpf, 0x00FF, 0xFF00, 0x0000, 0x0000):
                return (
                    DXGI_FORMAT.DXGI_FORMAT_R8G8_SNORM
                )  # often written as DX10 extension

            return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

        return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

    if ddpf.flags & DDS_FOURCC:
        fourcc = ddpf.four_cc

        if fourcc == _make_fourcc("D", "X", "T", "1"):
            return DXGI_FORMAT.DXGI_FORMAT_BC1_UNORM
        if fourcc == _make_fourcc("D", "X", "T", "3"):
            return DXGI_FORMAT.DXGI_FORMAT_BC2_UNORM
        if fourcc == _make_fourcc("D", "X", "T", "5"):
            return DXGI_FORMAT.DXGI_FORMAT_BC3_UNORM

        # Pre-multiplied alpha variants map to same BC formats
        if fourcc == _make_fourcc("D", "X", "T", "2"):
            return DXGI_FORMAT.DXGI_FORMAT_BC2_UNORM
        if fourcc == _make_fourcc("D", "X", "T", "4"):
            return DXGI_FORMAT.DXGI_FORMAT_BC3_UNORM

        if fourcc == _make_fourcc("A", "T", "I", "1") or fourcc == _make_fourcc(
            "B", "C", "4", "U"
        ):
            return DXGI_FORMAT.DXGI_FORMAT_BC4_UNORM
        if fourcc == _make_fourcc("B", "C", "4", "S"):
            return DXGI_FORMAT.DXGI_FORMAT_BC4_SNORM

        if fourcc == _make_fourcc("A", "T", "I", "2") or fourcc == _make_fourcc(
            "B", "C", "5", "U"
        ):
            return DXGI_FORMAT.DXGI_FORMAT_BC5_UNORM
        if fourcc == _make_fourcc("B", "C", "5", "S"):
            return DXGI_FORMAT.DXGI_FORMAT_BC5_SNORM

        # BC6H and BC7 are written using the "DX10" extended header

        if fourcc == _make_fourcc("R", "G", "B", "G"):
            return DXGI_FORMAT.DXGI_FORMAT_R8G8_B8G8_UNORM
        if fourcc == _make_fourcc("G", "R", "G", "B"):
            return DXGI_FORMAT.DXGI_FORMAT_G8R8_G8B8_UNORM

        if fourcc == _make_fourcc("Y", "U", "Y", "2"):
            return DXGI_FORMAT.DXGI_FORMAT_YUY2

        fourcc_u32 = int.from_bytes(fourcc, "little")

        if fourcc_u32 == 36:  # D3DFMT_A16B16G16R16
            return DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_UNORM
        if fourcc_u32 == 110:  # D3DFMT_Q16W16V16U16
            return DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_SNORM
        if fourcc_u32 == 111:  # D3DFMT_R16F
            return DXGI_FORMAT.DXGI_FORMAT_R16_FLOAT
        if fourcc_u32 == 112:  # D3DFMT_G16R16F
            return DXGI_FORMAT.DXGI_FORMAT_R16G16_FLOAT
        if fourcc_u32 == 113:  # D3DFMT_A16B16G16R16F
            return DXGI_FORMAT.DXGI_FORMAT_R16G16B16A16_FLOAT
        if fourcc_u32 == 114:  # D3DFMT_R32F
            return DXGI_FORMAT.DXGI_FORMAT_R32_FLOAT
        if fourcc_u32 == 115:  # D3DFMT_G32R32F
            return DXGI_FORMAT.DXGI_FORMAT_R32G32_FLOAT
        if fourcc_u32 == 116:  # D3DFMT_A32B32G32R32F
            return DXGI_FORMAT.DXGI_FORMAT_R32G32B32A32_FLOAT

        return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN

    return DXGI_FORMAT.DXGI_FORMAT_UNKNOWN
