
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from .database import engine
from .routers import bookings

app = FastAPI(title="Transfers Contract API", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

@app.get("/")
def health():
    return {"status": "ok"}
