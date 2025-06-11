from fastapi import FastAPI
from app.routes import base
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(base.router)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
