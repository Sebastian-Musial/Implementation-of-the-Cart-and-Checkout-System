from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(validation_alias="DATABASE_URL")
    app_title: str = "System koszyka i checkoutu"
    app_description: str = ("Projekt FastAPI zarządzający koszykiem i checkoutem")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()