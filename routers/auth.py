# Imports
import os
from dotenv import load_dotenv
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from database import session_local
from sqlalchemy.orm import  Session
from models import User
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

# Router for authorization/authentication
router = APIRouter(
    prefix = "/auth",
    tags = ["Auth"]
)

# env variable loading
load_dotenv()

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# Algorithm for JWT
ALGORITHM = os.getenv("ALGORITHM")

# Bearer for auth lock pads
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Setting up context
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database session
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# Database dependency for endpoints
db_dependency = Annotated[Session, Depends(get_db)]


# Pydantic class for User validation
class UserCreate(BaseModel):
    password: str = Field(min_length=4, max_length=20)
    full_name: str = Field(min_length=1)
    email: EmailStr = Field(min_length=8)
    age: int = Field(ge=18, lt=60)

    model_config = {
        "json_schema_extra": {
            "example": {
                "password": "test",
                "full_name": "Chinatsu Kanno",
                "email": "chinatsu@email.com",
                "age": 22,
            }
        }
    }



# Function to create access token
def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": email, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# Function for authenticating user
def authenticate_user(db: Session, email: str, password: str):
    user_model = db.query(User).filter(User.email == email).first()
    if not user_model:
        return False
    if not bcrypt_context.verify(password, user_model.hashed_password):
        return False
    return user_model

# Function to get current user
def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")

        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate User")

        return {"email": email, "id": user_id}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate User")

# User dependency for username and id
user_dependency = Annotated[dict, Depends(get_current_user)]

# User login using request form
@router.post("/token", status_code=status.HTTP_201_CREATED)
async def login(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_access_token(user.email, user.id, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}



# POST/CREATE user: Adding a new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: db_dependency):
    new_user = User(
        full_name = user.full_name,
        email = user.email,
        age = user.age,
        hashed_password = bcrypt_context.hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



