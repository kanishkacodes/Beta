from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str
    ENVIRONMENT: str
    DEBUG: bool

    class Config:
        env_file = ".env"

settings = Settings()
