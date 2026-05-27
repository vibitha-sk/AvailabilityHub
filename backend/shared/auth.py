"""JWT token validation for Azure Entra ID tokens."""
import os
import logging
import requests
from functools import lru_cache
import jwt
from jwt import PyJWKClient

logger = logging.getLogger(__name__)

TENANT_ID = os.environ["AZURE_TENANT_ID"]
CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"


@lru_cache(maxsize=1)
def _get_jwks_client():
    return PyJWKClient(JWKS_URI)


def validate_token(authorization_header: str) -> dict:
    """
    Validate a Bearer token from the Authorization header.
    Returns the decoded claims dict on success, raises ValueError on failure.
    """
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise ValueError("Missing or malformed Authorization header")

    token = authorization_header[len("Bearer "):]
    jwks_client = _get_jwks_client()

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=f"api://{CLIENT_ID}",
            options={"verify_exp": True},
        )
        return claims
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as exc:
        raise ValueError(f"Invalid token: {exc}")


def get_user_id(claims: dict) -> str:
    """Extract a stable user identifier from token claims."""
    return claims.get("oid") or claims.get("sub")


def get_user_email(claims: dict) -> str:
    """Extract user email from token claims."""
    return (
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("upn")
        or ""
    )
