
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from ..database import get_session
from ..models import Booking, BookingCreate, BookingRead

router = APIRouter()

@router.post("/", response_model=BookingRead)
def create_booking(data: BookingCreate, session: Session = Depends(get_session)):
    booking = Booking(**data.dict())
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking

@router.get("/", response_model=list[BookingRead])
def list_bookings(
    date: datetime | None = Query(None, description="Αν δοθεί, φέρνει μόνο όσα είναι την ημέρα αυτή")
    , session: Session = Depends(get_session)
):
    stmt = select(Booking)
    if date:
        start = datetime(date.year, date.month, date.day, 0, 0, 0)
        end = datetime(date.year, date.month, date.day, 23, 59, 59)
        stmt = stmt.where(Booking.pickup_dt >= start, Booking.pickup_dt <= end)
    return session.exec(stmt.order_by(Booking.pickup_dt)).all()

@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: int, session: Session = Depends(get_session)):
    bk = session.get(Booking, booking_id)
    if not bk:
        raise HTTPException(status_code=404, detail="Not found")
    return bk

@router.put("/{booking_id}", response_model=BookingRead)
def update_booking(booking_id: int, data: BookingCreate, session: Session = Depends(get_session)):
    bk = session.get(Booking, booking_id)
    if not bk:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.dict().items():
        setattr(bk, k, v)
    session.add(bk)
    session.commit()
    session.refresh(bk)
    return bk

@router.delete("/{booking_id}")
def delete_booking(booking_id: int, session: Session = Depends(get_session)):
    bk = session.get(Booking, booking_id)
    if not bk:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(bk)
    session.commit()
    return {"ok": True}

@router.get("/{booking_id}/contract")
def contract_pdf(booking_id: int, session: Session = Depends(get_session)):
    bk = session.get(Booking, booking_id)
    if not bk:
        raise HTTPException(status_code=404, detail="Not found")
    # Make simple 1-page PDF
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "ΙΔΙΩΤΙΚΟ ΣΥΜΦΩΝΗΤΙΚΟ ΜΙΣΘΩΣΗΣ Ε.Ι.Χ. ΟΧΗΜΑΤΟΣ ΜΕ ΟΔΗΓΟ")
    y -= 30
    c.setFont("Helvetica", 10)
    def line(label, value):
        nonlocal y
        c.drawString(40, y, f"{label}: {value or ''}")
        y -= 16
    line("Οδηγός", bk.driver_name)
    line("Αρ. Ταυτότητας Οδηγού", bk.driver_id)
    line("Αρ. Διπλώματος", bk.driver_license)
    line("Όχημα Πινακίδα", bk.vehicle_plate)
    line("Μάρκα", bk.vehicle_make)
    line("Μοντέλο", bk.vehicle_model)
    y -= 8
    line("Μισθωτής (Πελάτης)", bk.customer_name)
    line("ΑΦΜ/ID/Διαβατήριο", bk.customer_id_doc)
    line("Επιβάτης", bk.passenger_name)
    line("Άτομα", bk.pax)
    y -= 8
    line("Ημ/νία Συμφωνητικού", bk.contract_date)
    line("Έναρξη", bk.pickup_dt)
    line("Λήξη", bk.dropoff_dt)
    line("Σημείο Έναρξης", bk.pickup_address)
    line("Σημείο Επιβίβασης", bk.dropoff_address)
    y -= 8
    line("Τιμή (€)", bk.price)
    line("Παρατηρήσεις", bk.notes)
    c.showPage()
    c.save()
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=contract_{booking_id}.pdf"})
