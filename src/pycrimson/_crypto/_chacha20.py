from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import ChaCha20
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.hashes import SHA256

from . import _checksum

import secrets


def _create_cipher(key: bytes, nonce: bytes) -> Cipher:
    return Cipher(ChaCha20(key, nonce), mode=None)


def _chacha20_decrypt(data: bytes, key: bytes, nonce: bytes) -> bytes:
    return _create_cipher(key, nonce).decryptor().update(data)


def _chacha20_encrypt(data: bytes, key: bytes, nonce: bytes) -> bytes:
    return _create_cipher(key, nonce).encryptor().update(data)


_PACK_ENTRY_BASE_KEY = bytes.fromhex(
    "0E0F0C0D040506070203000108090A0B000102030405060708090A0B0C0D0E0F"
)


def chacha20_decrypt_pack_entry(
    data: bytes, group_encrypt_info: bytes, entry_path: str
) -> bytes:
    key = bytearray(_PACK_ENTRY_BASE_KEY)

    counter = _checksum.calculate_checksum(entry_path.rsplit("/", 1)[1].encode("utf-8"))
    nonce = counter.to_bytes(4, "little") * 4

    k = group_encrypt_info[0] ^ group_encrypt_info[1] ^ group_encrypt_info[2]
    for i in range(len(key)):
        key[i] ^= nonce[i % len(nonce)] ^ k

    return _chacha20_decrypt(data, key, nonce)


# The key material is originally 32 bytes, but the last one gets overwritten by a null byte
# (they probably used a string type)
_SAVE_BASE_KEY = bytes.fromhex(
    "C41B8E730DF259A637CC04E9B12F9668DA107A853E61F9224DB80AD75C13EF90"
)[:31]


def _generate_save_key(version: int) -> bytes:
    match version:
        case 1:
            prefix = b'^Qgbrm/.#@`zsr]\\@rvfal#"'
        case 2:
            prefix = b"^Pearl--#Abyss__@!!"
        case _:
            assert False, f"Unsupported save version {version}"

    key_material_2 = prefix + b"PRIVATE_HMAC_SECRET_CHECK"
    return bytes(x ^ y for x, y in zip(_SAVE_BASE_KEY, key_material_2)) + b"\x00"


def chacha20_decrypt_save_file(
    data: bytes, version: int, nonce: bytes, hmac_signature: bytes
) -> bytes:
    key = _generate_save_key(version)

    decrypted = _chacha20_decrypt(key, nonce, data)

    hmac = HMAC(key, SHA256())
    hmac.update(data)
    hmac.verify(hmac_signature)

    return decrypted


def chacha20_encrypt_save_file(
    data: bytes, version: int, nonce_override: bytes | None = None
) -> tuple[bytes, bytes, bytes]:
    key = _generate_save_key(version)

    nonce = nonce_override or secrets.token_bytes(16)

    hmac = HMAC(key, SHA256())
    hmac.update(data)
    hmac_signature = hmac.finalize()

    encrypted = _chacha20_encrypt(data, key, nonce)
    return (hmac_signature, nonce, encrypted)
