#!/usr/bin/env python3
"""
Encrypts passwords
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """ This func returns a salted, hashed password, via a byte string """
    encoded = password.encode()
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt())

    return hashed


def is_valid(hashed_password: bytes, password: str) -> bool:
    """ This func validates that the provided password matches the hashed password """
    valid = False
    encoded = password.encode()
    if bcrypt.checkpw(encoded, hashed_password):
        valid = True
    return valid
