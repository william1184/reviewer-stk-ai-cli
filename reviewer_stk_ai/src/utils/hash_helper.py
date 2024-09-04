import hashlib


def generate_file_hash(content):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content.encode("utf-8"))
    return sha256_hash.hexdigest()


__all__ = [
    "generate_file_hash",
]
