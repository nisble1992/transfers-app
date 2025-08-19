
from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class BookingBase(SQLModel):
    # Client
    customer_name: str
    customer_id_doc: Optional[str] = None
    passenger_name: Optional[str] = None
    pax: int = 1
    # Driver
    driver_name: Optional[str] = None
    driver_id: Optional[str] = None
    driver_license: Optional[str] = None
    # Vehicle
    vehicle_plate: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    # Times
    contract_date: Optional[datetime] = None
    pickup_dt: datetime
    dropoff_dt: Optional[datetime] = None
    # Route
    pickup_address: Optional[str] = None
    dropoff_address: Optional[str] = None
    # Other
    price: Optional[float] = None
    notes: Optional[str] = None

class Booking(BookingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class BookingCreate(BookingBase): ...
class BookingRead(BookingBase):
    id: int
