"""
app.py
------
Main Flask application for the JWKS Server.
Implements endpoints for health check, JWT issuance, and JWKS retrieval.
Automatically manages RSA keys (valid and expired) stored in SQLite.
"""

from flask import Flask, jsonify, request
import time, jwt
from cryptography.hazmat.primitives import serialization
from db import insert_key, fetch_one_key, fetch_valid_keys, get_conn
from crypto_utils import generate_rsa_private_key_pem, pem_to_jwk_public, now

# Initialize Flask app
app = Flask(__name__)

def _ensure_seed_keys():
    """
    Ensures that at least one valid and one expired RSA key exist in the database.
    Called once before the first incoming request.
    """
    with get_conn() as _:
        pass
    expired = fetch_one_key(expired=True)
    valid = fetch_one_key(expired=False)

    # Insert one expired key if missing
    if not expired:
        pem = generate_rsa_private_key_pem()
        insert_key(pem, now() - 5)  # expired 5 seconds ago

    # Insert one valid key if missing
    if not valid:
        pem = generate_rsa_private_key_pem()
        insert_key(pem, now() + 3600)  # valid for 1 hour

def _load_private_key(pem: bytes):
    """Converts PEM bytes into a usable private key object."""
    return serialization.load_pem_private_key(pem, password=None)

@app.before_request
def init_app():
    """Runs once before the first request to seed keys in DB."""
    if not getattr(app, "_initialized", False):
        _ensure_seed_keys()
        app._initialized = True

@app.route("/auth", methods=["POST"])
def auth():
    """
    Issues a JWT signed with either a valid or expired RSA private key.
    Use '?expired' query parameter to request an expired-key signature.
    """
    use_expired = "expired" in request.args
    row = fetch_one_key(expired=use_expired)
    if not row:
        return jsonify({"error": "No suitable key in DB"}), 500

    kid, pem, key_exp = row
    private_key = _load_private_key(pem)

    # Create the JWT payload
    payload = {
        "sub": "userABC",
        "username": "userABC",
        "iat": int(time.time()),
        "exp": int(time.time()) + 900,  # token valid for 15 minutes
    }

    # Encode the token with RS256
    token = jwt.encode(
        payload, private_key, algorithm="RS256", headers={"kid": str(kid)}
    )
    return jsonify({"jwt": token, "kid_used": kid, "key_exp": key_exp, "expired_param": use_expired})

@app.route("/.well-known/jwks.json", methods=["GET"])
def jwks():
    """
    Returns the public JWKs (JSON Web Keys) for all valid keys in the DB.
    Expired keys are excluded from this endpoint.
    """
    valid = fetch_valid_keys()
    keys = [pem_to_jwk_public(pem, kid=str(kid)) for kid, pem, _ in valid]
    return jsonify({"keys": keys})

@app.route("/healthz")
def health():
    """Simple health check endpoint."""
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)