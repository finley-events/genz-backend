import base64
import hashlib
import secrets
from typing import Dict


def generate_state(length: int = 32) -> str:
    """
    Generate a cryptographically secure OAuth state parameter.
    Used to protect against CSRF attacks.
    """
    return secrets.token_urlsafe(length)


def generate_code_verifier(length: int = 64) -> str:
    """
    Generate a PKCE code verifier.

    RFC 7636 requires a verifier between 43 and 128 characters.
    """
    verifier = secrets.token_urlsafe(length)

    # Ensure maximum allowed length
    return verifier[:128]


def generate_code_challenge(code_verifier: str) -> str:
    """
    Generate a SHA256 PKCE code challenge.
    """

    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()

    challenge = base64.urlsafe_b64encode(digest)

    return challenge.decode("utf-8").rstrip("=")


def generate_pkce_pair() -> Dict[str, str]:
    """
    Generate a complete PKCE bundle.
    """

    verifier = generate_code_verifier()

    challenge = generate_code_challenge(verifier)

    state = generate_state()

    return {
        "state": state,
        "code_verifier": verifier,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
