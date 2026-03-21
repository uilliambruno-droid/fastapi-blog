from datetime import timedelta

from src.utils.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_create_and_decode_access_token():
    token = create_access_token({"sub": "alice"})
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "alice"
    assert "exp" in payload


def test_decode_expired_token_returns_none():
    token = create_access_token({"sub": "bob"}, expires_delta=timedelta(seconds=-1))
    assert decode_access_token(token) is None
