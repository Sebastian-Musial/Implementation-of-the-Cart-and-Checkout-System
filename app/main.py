from fastapi import FastAPI
from app.database import create_db_and_tables


def create_app(create_tables_on_startup: bool = False) -> FastAPI:  #False w celu szybszego uruchamiania aplikacji
    application = FastAPI()

    @application.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    if create_tables_on_startup:
        create_db_and_tables()


    return application

app = create_app()