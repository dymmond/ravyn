from datetime import datetime, timedelta, timezone

import pytest
from freezegun import freeze_time
from jwt.exceptions import InvalidAudienceError, MissingRequiredClaimError
from lilya._internal._connection import Connection

from ravyn.contrib.auth.common.middleware import CommonJWTAuthBackend
from ravyn.core.config.jwt import JWTConfig
from ravyn.exceptions import AuthenticationError
from ravyn.security.jwt.token import Token


@freeze_time("2022-03-03")
def test_token_expiry():
    date = datetime.now()

    token = Token(exp=date)

    assert token.exp == date


def test_decode_validates_requested_audience():
    key = "shared-signing-key-at-least-32-bytes"
    expiration = datetime.now(timezone.utc) + timedelta(minutes=5)
    token = Token(exp=expiration, sub="1", aud="service-B").encode(key, "HS256")
    token_without_audience = Token(exp=expiration, sub="1").encode(key, "HS256")

    with pytest.raises(InvalidAudienceError):
        Token.decode(token, key, ["HS256"], audience="service-A")
    with pytest.raises(InvalidAudienceError):
        Token.decode(token, key, ["HS256"], audience="service-A", options={"verify_aud": False})
    with pytest.raises(MissingRequiredClaimError):
        Token.decode(token_without_audience, key, ["HS256"], audience="service-A")

    assert Token.decode(token, key, ["HS256"], audience="service-B").sub == "1"
    assert Token.decode(token, key, ["HS256"]).aud == "service-B"
    assert Token.decode(token_without_audience, key, ["HS256"]).sub == "1"


@pytest.mark.anyio
async def test_backend_enforces_configured_audience_before_user_lookup():
    class Backend(CommonJWTAuthBackend):
        looked_up: list[str] = []

        async def retrieve_user(self, subject: str) -> str:
            self.looked_up.append(subject)
            return subject

    key = "shared-signing-key-at-least-32-bytes"
    token = Token(
        exp=datetime.now(timezone.utc) + timedelta(minutes=5), sub="1", aud="service-B"
    ).encode(key, "HS256")
    request = Connection(
        {"type": "http", "headers": [(b"authorization", f"Bearer {token}".encode())]}
    )
    backend = Backend(JWTConfig(signing_key=key, audience="service-A"), user_model=None)

    with pytest.raises(AuthenticationError):
        await backend.authenticate(request)
    assert backend.looked_up == []

    backend = Backend(
        JWTConfig(signing_key=key, audience="service-B", issuer="trusted-issuer"), user_model=None
    )
    with pytest.raises(AuthenticationError):
        await backend.authenticate(request)
    assert backend.looked_up == []

    backend = Backend(JWTConfig(signing_key=key, audience="service-B"), user_model=None)
    _, user = await backend.authenticate(request)
    assert user == "1"

    backend = Backend(JWTConfig(signing_key=key), user_model=None)
    _, user = await backend.authenticate(request)
    assert user == "1"
