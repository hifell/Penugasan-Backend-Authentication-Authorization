from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List

from connection import engine, Base, get_db
from user import User
from event import Event
from registration import Registration
from event_dto import EventCreate, EventUpdate, EventResponse
from registration_dto import RegistrationCreate, RegistrationUpdate, RegistrationResponse
from auth_util import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from schemas import UserSchema

app = FastAPI(title="CRUD API dengan Autentikasi", version="1.0.0")

Base.metadata.create_all(bind=engine)


# ── ROLE-BASED ACCESS CONTROL ──

async def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency untuk memastikan user memiliki role admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ── AUTH ENDPOINTS (tidak diproteksi) ──

@app.post("/register", tags=["Auth"])
def register(user: UserSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    hashed = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed, role="user")
    db.add(new_user)
    db.commit()
    return {"message": "User created"}


@app.post("/login", tags=["Auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Username atau password salah")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# ── EVENT ENDPOINTS (semua diproteksi token) ──

@app.get("/api/events", response_model=List[EventResponse], tags=["Events"])
def get_events(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET semua events - semua user (user dan admin) dapat mengakses"""
    return db.query(Event).all()


@app.get("/api/events/{event_id}", response_model=EventResponse, tags=["Events"])
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET event by ID - semua user (user dan admin) dapat mengakses"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/api/events", response_model=EventResponse, tags=["Events"])
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """POST (Create) event - hanya admin yang dapat mengakses"""
    new_event = Event(**event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@app.put("/api/events/{event_id}", response_model=EventResponse, tags=["Events"])
def update_event(
    event_id: int,
    event: EventUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """PUT (Update) event - hanya admin yang dapat mengakses"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.patch("/api/events/{event_id}", response_model=EventResponse, tags=["Events"])
def patch_event(
    event_id: int,
    event: EventUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """PATCH (Partial Update) event - hanya admin yang dapat mengakses"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.delete("/api/events/{event_id}", tags=["Events"])
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """DELETE event - hanya admin yang dapat mengakses"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return {"message": "Event deleted successfully"}


# ── REGISTRATION ENDPOINTS (semua diproteksi token) ──

@app.get("/api/registrations", response_model=List[RegistrationResponse], tags=["Registrations"])
def get_registrations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET semua registrations - semua user dapat mengakses"""
    return db.query(Registration).all()


@app.get("/api/registrations/{registration_id}", response_model=RegistrationResponse, tags=["Registrations"])
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """GET registration by ID - semua user dapat mengakses"""
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg


@app.post("/api/registrations", response_model=RegistrationResponse, tags=["Registrations"])
def create_registration(
    registration: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """POST (Create) registration - semua user (user dan admin) dapat mendaftar"""
    new_reg = Registration(**registration.dict())
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return new_reg


@app.put("/api/registrations/{registration_id}", response_model=RegistrationResponse, tags=["Registrations"])
def update_registration(
    registration_id: int,
    registration: RegistrationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """PUT (Update) registration - hanya admin yang dapat mengakses"""
    db_reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not db_reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    for key, value in registration.dict(exclude_unset=True).items():
        setattr(db_reg, key, value)
    db.commit()
    db.refresh(db_reg)
    return db_reg


@app.patch("/api/registrations/{registration_id}", response_model=RegistrationResponse, tags=["Registrations"])
def patch_registration(
    registration_id: int,
    registration: RegistrationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """PATCH (Partial Update) registration - hanya admin yang dapat mengakses"""
    db_reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not db_reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    for key, value in registration.dict(exclude_unset=True).items():
        setattr(db_reg, key, value)
    db.commit()
    db.refresh(db_reg)
    return db_reg


@app.delete("/api/registrations/{registration_id}", tags=["Registrations"])
def delete_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """DELETE registration - hanya admin yang dapat mengakses"""
    db_reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not db_reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    db.delete(db_reg)
    db.commit()
    return {"message": "Registration deleted successfully"}
