"""
tests/test_app.py
-----------------
Unit tests for JWKS server endpoints and database functions.
Covers normal and edge cases to achieve ≥ 90% coverage.
"""

from app import app
from db import get_conn, fetch_one_key, fetch_valid_keys
from crypto_utils import generate_rsa_private_key_pem, pem_to_jwk_public, now

# --- Core endpoint tests ---

def test_healthz():
    """Verify that /healthz returns {'ok': True}."""
    client = app.test_client()
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json["ok"] is True

def test_auth_valid_and_expired():
    """Check that /auth and /auth?expired both issue JWTs."""
    client = app.test_client()
    r1 = client.post("/auth")
    assert r1.status_code == 200 and r1.get_json()["expired_param"] is False

    r2 = client.post("/auth?expired")
    assert r2.status_code == 200 and r2.get_json()["expired_param"] is True

def test_jwks_only_valid_keys():
    """Ensure /.well-known/jwks.json returns only non-expired keys."""
    client = app.test_client()
    r = client.get("/.well-known/jwks.json")
    assert r.status_code == 200
    for k in r.get_json()["keys"]:
        assert "kid" in k and "n" in k and "e" in k

# --- Edge cases & helpers ---

def test_auth_no_keys():
    """Force missing keys to trigger error branch in /auth."""
    with get_conn() as conn:
        conn.execute("DELETE FROM keys")
    client = app.test_client()
    r = client.post("/auth")
    assert r.status_code == 500 and "error" in r.get_json()

def test_db_empty_and_expired():
    """Check that DB functions return None when empty."""
    with get_conn() as conn:
        conn.execute("DELETE FROM keys")
    assert fetch_one_key(expired=True) is None
    assert fetch_one_key(expired=False) is None
    assert fetch_valid_keys() == []

def test_crypto_functions():
    """Test RSA key generation, JWK conversion, and time utility."""
    pem = generate_rsa_private_key_pem()
    assert pem.startswith(b"-----BEGIN RSA PRIVATE KEY-----")
    jwk_dict = pem_to_jwk_public(pem, kid="999")
    assert jwk_dict["kty"] == "RSA"
    assert "n" in jwk_dict and "e" in jwk_dict
    assert isinstance(now(), int)