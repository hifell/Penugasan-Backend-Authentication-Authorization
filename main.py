from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import User
from schemas import UserSchema
from auth_util import (
    hash_password,
    verify_password,
    create_access_token
)

app = FastAPI()
Base.metadata.create_all(bind=engine)

#register
@app.post("/register")
def register(
    user: UserSchema,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username sudah digunakan"
        )

    hashed = hash_password(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed,
        role="user"
    )
    db.add(new_user)
    db.commit()
    return {
        "message": "User created"
    }

#login
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()
    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Salah login"
        )

    token = create_access_token({
        "sub": user.username,
        "role": user.role
    })
    return {
        "access_token": token,
        "token_type": "bearer"
    }