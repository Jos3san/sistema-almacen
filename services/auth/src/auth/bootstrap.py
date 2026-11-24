"""Create the first owner user, so a freshly installed system can be used (HU-05).

Run once per environment (in Compose: see docs/codigo/auth.md):
    python -m auth.bootstrap

The data comes from environment variables, never from the code:
BOOTSTRAP_ADMIN_EMAIL, BOOTSTRAP_ADMIN_NAME and BOOTSTRAP_ADMIN_PASSWORD.
If an active owner already exists, it does nothing.
"""

import logging
import os
import sys

from sqlalchemy.orm import Session

from auth.db import get_engine
from auth.logging_config import configure_logging
from auth.users import passwords
from auth.users import repository as users_repo
from auth.users.models import User

logger = logging.getLogger(__name__)


def create_first_owner(session: Session, email: str, name: str, password: str) -> bool:
    """Create the owner user unless one exists. Return True if it was created."""
    if len(password) < passwords.MIN_LENGTH:
        raise ValueError(f"The password needs at least {passwords.MIN_LENGTH} characters")
    with session.begin():
        if users_repo.owner_exists(session):
            return False
        user = User(
            email=email.strip().lower(),
            name=name.strip(),
            password_hash=passwords.hash_password(password),
        )
        users_repo.add(session, user, ["owner"])
    return True


def main() -> None:
    """Read the variables, create the owner and report the result (no secrets in the log)."""
    configure_logging()
    names = ("BOOTSTRAP_ADMIN_EMAIL", "BOOTSTRAP_ADMIN_NAME", "BOOTSTRAP_ADMIN_PASSWORD")
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}")
    email, name, password = (os.environ[name] for name in names)
    with Session(get_engine()) as session:
        created = create_first_owner(session, email, name, password)
    logger.info("First owner created" if created else "An owner already exists: nothing to do")


if __name__ == "__main__":
    main()
