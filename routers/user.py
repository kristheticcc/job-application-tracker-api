# Imports
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from starlette import status
from models import User
from database import session_local
from routers.auth import user_dependency


# User router for fastapi application
router = APIRouter(prefix="/user", tags=["user"])

# Database sessions
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# For adding database dependency to the endpoints
db_dependency = Annotated[Session, Depends(get_db)]


# For PUT
class UserUpdate(BaseModel):
    email: EmailStr = Field(min_length=8)
    full_name: str = Field(min_length=1)
    age: int = Field(ge=18, lt=60)

    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "Chinatsu Kanno",
                "email": "chinatsu@email.com",
                "age": 22,
            }
        }
    }


# Getting a user by user id
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!")

    return user_model



# Deleting a user by user id
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user: user_dependency):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!")

    db.delete(user_model)
    db.commit()


# update details of existing user
@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(db: db_dependency, user: user_dependency, new_user: UserUpdate):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!")

    user_model.full_name = new_user.full_name
    user_model.email = new_user.email
    user_model.age = new_user.age

    db.commit()

