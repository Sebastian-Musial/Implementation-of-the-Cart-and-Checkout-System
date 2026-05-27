from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers.products import router

def create_app(create_tables_on_startup: bool = True) -> FastAPI:  #False w celu szybszego uruchamiania aplikacji
    application = FastAPI()

    @application.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(router)

    if create_tables_on_startup:
        create_db_and_tables()


    return application

app = create_app()