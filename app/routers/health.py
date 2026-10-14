
from fastapi import APIRouter, HTTPException
from psycopg import Error
from urllib.parse import urlparse

from app.database import get_db_connection
from app.config import settings

router = APIRouter()


def get_database_info():
    parsed_url = urlparse(settings.database_url)
    database_name = parsed_url.path.lstrip("/")

    environments = {
        "self_storage_test": "DEV",
        "self_storage": "PROD",
    }

    return environments.get(database_name, "UNKNOWN"), database_name


@router.get("/health")
def health_check():
    environment, database_name = get_database_info()

    return {
        "status": "ok",
        "environment": environment,
        "database": database_name,
    }


@router.get("/health/db")
def database_health_check():
    try:
        with get_db_connection() as connection:
            connection.execute("SELECT 1")

        environment, database_name = get_database_info()

        return {
            "status": "ok",
            "environment": environment,
            "database": database_name,
            "database_status": "connected",
        }

    except RuntimeError:
        raise

    except Error as exc:
        print(f"Database connection error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )
