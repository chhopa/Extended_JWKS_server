"""
crypto_utils.py
---------------
Contains helper functions for RSA key generation, PEM ↔ JWK conversion,
and Unix time utilities.
"""

import time
from typing import Dict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwcrypto import jwk

def generate_rsa_private_key_pem() -> bytes:
    """Generates a 2048-bit RSA private key and returns it as PEM bytes."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem

def pem_to_jwk_public(pem: bytes, kid: str) -> Dict:
    """Converts a PEM private key to its public JWK representation."""
    key = jwk.JWK.from_pem(pem)
    pub = jwk.JWK()
    pub.import_key(**key.export_public(as_dict=True))
    pub = jwk.JWK(**pub.export(as_dict=True))
    pub.update(kid=kid, kty="RSA")
    return pub.export(as_dict=True)

def now() -> int:
    """Returns current Unix timestamp as an integer."""
    return int(time.time())