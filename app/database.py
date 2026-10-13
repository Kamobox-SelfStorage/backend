
from contextlib import contextmanager
from urllib.parse import urlparse

import psycopg

from app.config import settings


def validate_database_url() -> str:
    parsed = urlparse(settings.database_url)
    database_name = parsed.path.lstrip("/")

    if database_name != "self_storage_test":
        raise RuntimeError(
            "Backend development connection is restricted "
            "to the self_storage_test database."
        )

    if parsed.scheme not in ("postgresql", "postgres"):
        raise RuntimeError("Unsupported database URL scheme.")

    return settings.database_url


@contextmanager
def get_db_connection():
    database_url = validate_database_url()

    with psycopg.connect(database_url) as connection:
        yield connection
