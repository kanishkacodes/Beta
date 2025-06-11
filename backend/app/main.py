from fastapi import FastAPI
from app.routes import base
from app.config import settings
from app.routes import image

app = FastAPI()

app.include_router(base.router)
app.include_router(image.router)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "env": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }
