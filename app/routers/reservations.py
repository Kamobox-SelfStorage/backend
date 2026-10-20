
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from psycopg import Error
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from app.database import get_db_connection

router = APIRouter(prefix="/reservations", tags=["Reservations"])


class ReservationCreate(BaseModel):
    customer_id: int
    unit_id: int


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    unit_id: int
    status: str
    monthly_price: Decimal
    reservation_expires_at: datetime


@router.post("", response_model=ReservationResponse, status_code=201)
def create_reservation(reservation: ReservationCreate):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Lock the unit to serialize competing reservation requests.
                unit = cursor.execute(
                    """
                    SELECT id, status, monthly_price
                    FROM public.units
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (reservation.unit_id,),
                ).fetchone()

                if unit is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Unit not found",
                    )

                # Release expired holds for this unit before checking availability.
                cursor.execute(
                    """
                    SELECT set_config(
                        'app.rental_status_reason',
                        'RESERVATION_EXPIRED',
                        true
                    )
                    """
                )

                cursor.execute(
                    """
                    UPDATE public.rentals
                    SET status = 'CANCELLED'
                    WHERE unit_id = %s
                      AND status = 'RESERVED'
                      AND reservation_expires_at <= now()
                    """,
                    (reservation.unit_id,),
                )

                if unit[1] != "AVAILABLE":
                    raise HTTPException(
                        status_code=409,
                        detail="Unit is not available for reservation",
                    )

                customer = cursor.execute(
                    """
                    SELECT id
                    FROM public.customers
                    WHERE id = %s
                    """,
                    (reservation.customer_id,),
                ).fetchone()

                if customer is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Customer not found",
                    )

                rental = cursor.execute(
                    """
                    INSERT INTO public.rentals (
                        customer_id,
                        unit_id,
                        status,
                        monthly_price,
                        reservation_expires_at
                    )
                    VALUES (
                        %s,
                        %s,
                        'RESERVED',
                        %s,
                        now() + interval '30 minutes'
                    )
                    RETURNING
                        id,
                        customer_id,
                        unit_id,
                        status,
                        monthly_price,
                        reservation_expires_at
                    """,
                    (
                        reservation.customer_id,
                        reservation.unit_id,
                        unit[2],
                    ),
                ).fetchone()

                return {
                    "id": rental[0],
                    "customer_id": rental[1],
                    "unit_id": rental[2],
                    "status": rental[3],
                    "monthly_price": rental[4],
                    "reservation_expires_at": rental[5],
                }

    except HTTPException:
        raise
    except UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Unit already has an active reservation or rental",
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=404,
            detail="Customer or unit not found",
        )
    except Error:
        raise HTTPException(
            status_code=503,
            detail="Database operation failed",
        )
