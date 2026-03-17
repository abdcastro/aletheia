import hashlib
import os

def generate_sha256_hash(file_bytes: bytes) -> str:
    """
    Generates a SHA-256 hash for the incoming media file.
    This acts as the digital fingerprint for the chain of custody.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()

def verify_media_integrity(file_bytes: bytes, original_hash: str) -> bool:
    """
    Compares the hash of a provided file against the known secure hash.
    """
    current_hash = generate_sha256_hash(file_bytes)
    return current_hash == original_hash
