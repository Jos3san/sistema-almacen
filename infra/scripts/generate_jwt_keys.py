"""Generate the RSA key pair that signs (auth) and validates (every service) access tokens.

Run once per environment, from the repo root:
    uv run --no-project --with cryptography python infra/scripts/generate_jwt_keys.py

Writes infra/secrets/jwt_private.pem and jwt_public.pem. Both are ignored by
Git (.gitignore: secrets/ and *.pem). The private key never leaves auth;
the public key is mounted read-only in the other services (ADR-0007, docs/06 D1.6).
Existing keys are never overwritten: rotating them is a manual, documented step.
"""

import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

SECRETS_DIR = Path(__file__).resolve().parents[1] / "secrets"
PRIVATE_KEY = SECRETS_DIR / "jwt_private.pem"
PUBLIC_KEY = SECRETS_DIR / "jwt_public.pem"


def main() -> None:
    """Create the key pair, unless it already exists."""
    if PRIVATE_KEY.exists() or PUBLIC_KEY.exists():
        sys.exit(f"Keys already exist in {SECRETS_DIR}: not overwriting them.")

    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    PRIVATE_KEY.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    PUBLIC_KEY.write_bytes(
        key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    print(f"Created {PRIVATE_KEY.name} and {PUBLIC_KEY.name} in {SECRETS_DIR}")


if __name__ == "__main__":
    main()
