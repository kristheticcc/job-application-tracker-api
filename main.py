# Imports
from database import engine, Base
from routers import user, application, auth
from fastapi import FastAPI, Request

app = FastAPI()

# Creates tables in database if not created
Base.metadata.create_all(engine)

@app.get("/")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(application.router)



