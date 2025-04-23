from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.db.db import SessionLocal
from backend.models.user_model import User
from backend.services.auth_utils import hash_password, verify_password, create_access_token
from typing import List

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    favorite_team: str

class UserLogin(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = User(username=user.username, hashed_password=hash_password(user.password), favorite_team=user.favorite_team)
    db.add(db_user)
    db.commit()
    return {"msg": "User created successfully"}

valid_teams = [
    "Atlanta Hawks", 
    "Boston Celtics",
    "Brooklyn Nets",
    "Charlotte Hornets",
    "Chicago Bulls",
    "Cleveland Cavaliers",
    "Dallas Mavericks",
    "Denver Nuggets",
    "Detroit Pistons",
    "Golden State Warriors",
    "Houston Rockets",
    "Indiana Pacers",
    "LA Clippers",
    "Los Angeles Lakers",
    "Memphis Grizzlies",
    "Miami Heat",
    "Milwaukee Bucks",
    "Minnesota Timberwolves",
    "New Orleans Pelicans",
    "New York Knicks",
    "Oklahoma City Thunder",
    "Orlando Magic",
    "Philadelphia 76ers",
    "Phoenix Suns",
    "Portland Trail Blazers",
    "Sacramento Kings",
    "San Antonio Spurs",
    "Toronto Raptors",
    "Utah Jazz",
    "Washington Wizards"
]

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    favorite_team: str

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if db_user.favorite_team not in valid_teams:
        db_user.favorite_team = "Atlanta Hawks"
        db.commmit()
    
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "favorite_team": db_user.favorite_team.strip()}