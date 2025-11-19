from fastapi import APIRouter, Depends, HTTPException
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User

router = APIRouter(prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(400, "User already exists")

    hashed = bcrypt.hash(password)
    user = User(username=username, password_hash=hashed)
    db.add(user)
    db.commit()
    return {"message": "Registered"}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    return {"message": "OK", "username": username, "admin": user.is_admin}
