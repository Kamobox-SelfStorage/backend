
from fastapi import FastAPI

from app.routers import health, units, reservations

app = FastAPI(title="KamoBox API")

app.include_router(health.router)
app.include_router(units.router)
app.include_router(reservations.router)
