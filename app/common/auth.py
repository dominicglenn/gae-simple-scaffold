import hashlib


def hash_plaintext_password(value):
    return hashlib.sha224(value).hexdigest()
