
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from psycopg import Error

from app.database import get_db_connection

router = APIRouter(prefix="/units", tags=["Units"])


class UnitResponse(BaseModel):
    id: int
    unit_number: str
    area_m2: Decimal
    status: str
    container_id: int


@router.get("", response_model=list[UnitResponse])
def list_units():
    try:
        with get_db_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, unit_number, area_m2, status, container_id
                FROM public.units
                ORDER BY unit_number
                """
            ).fetchall()

        return [
            {
                "id": row[0],
                "unit_number": row[1],
                "area_m2": row[2],
                "status": row[3],
                "container_id": row[4],
            }
            for row in rows
        ]

    except Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )


@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: int):
    try:
        with get_db_connection() as connection:
            row = connection.execute(
                """
                SELECT id, unit_number, area_m2, status, container_id
                FROM public.units
                WHERE id = %s
                """,
                (unit_id,),
            ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Unit not found",
            )

        return {
            "id": row[0],
            "unit_number": row[1],
            "area_m2": row[2],
            "status": row[3],
            "container_id": row[4],
        }

    except Error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )
