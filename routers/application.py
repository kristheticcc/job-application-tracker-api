# Imports
from fastapi import APIRouter, HTTPException, Depends, Path
from typing import Annotated
from pydantic import BaseModel
from starlette import status
from sqlalchemy.orm import Session
from database import session_local
from models import Application, User
from routers.auth import user_dependency


# Router for Application endpoints
router = APIRouter(prefix='/job_application', tags=["Job Application"])

# Database sessions
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# For adding database dependency to the endpoints
db_dependency = Annotated[Session, Depends(get_db)]

# Pydantic class for Application validation
class ApplicationRequest(BaseModel):
    company: str
    role: str
    location: str
    status: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "company": "IBM",
                "role": "SDE",
                "location": "Sunnyvale",
                "status": "Active"
            }
        }
    }

# Pydantic class for POST
class ApplicationCreate(ApplicationRequest):
    pass

# Pydantic class for PUT
class ApplicationUpdate(ApplicationRequest):
    pass


# Get job application(s) by user id
@router.get("/", status_code=status.HTTP_200_OK)
async def get_applications(db: db_dependency, user: user_dependency):
    user_model = db.query(User).filter(user.get("id") == User.id).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!")

    job_applications = db.query(Application).filter(Application.user_id == user.get("id")).all()

    if not job_applications:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applications not found for user!!!")

    return job_applications


# Add an application for user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_application(db: db_dependency, new_application: ApplicationCreate, user: user_dependency):
    user_model = db.query(User).filter(User.id == user.get("id")).first()

    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!")

    application_model = Application(
        company = new_application.company,
        role = new_application.role,
        location = new_application.location,
        status = new_application.status,
        user_id = user.get("id")
    )

    db.add(application_model)
    db.commit()
    db.refresh(application_model)
    return application_model



# Update status on an application
@router.put("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_application_status(db: db_dependency,  upd_application: ApplicationUpdate, user: user_dependency, application_id: int=Path(gt=0)):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!")

    job_application = db.query(Application).filter(user.get("id") == Application.user_id).filter(application_id == Application.id).first()

    if not job_application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    job_application.status = upd_application.status
    job_application.company = upd_application.company
    job_application.role = upd_application.role
    job_application.location = upd_application.location

    db.commit()



# Delete a user's job application
@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_application(db: db_dependency, user: user_dependency, application_id: int=Path(gt=0)):
    user_model = db.query(User).filter(User.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!!!")

    application_model = db.query(Application).filter(Application.user_id == user.get("id")).filter(Application.id == application_id).first()

    if application_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Application not found!!!")

    db.delete(application_model)
    db.commit()