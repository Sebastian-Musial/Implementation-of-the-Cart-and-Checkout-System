from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers.products import router as products_router
from app.routers.clients import router as clients_router

def create_app(create_tables_on_startup: bool = False) -> FastAPI:  #False w celu szybszego uruchamiania aplikacji
    application = FastAPI()

    @application.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(products_router)
    application.include_router(clients_router)

    if create_tables_on_startup:
        create_db_and_tables()


    return application

app = create_app()