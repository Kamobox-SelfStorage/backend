
from fastapi import APIRouter, HTTPException
from psycopg import Error

from app.database import get_db_connection

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/health/db")
def database_health_check():
    try:
        with get_db_connection() as connection:
            connection.execute("SELECT 1")

        return {"status": "ok", "database": "connected"}

    except RuntimeError:
        raise

    except Error as exc:
        print(f"Database connection error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )