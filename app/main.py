from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers.products import router as products_router
from app.routers.clients import router as clients_router
from app.routers.carts import router as carts_router

def create_app(create_tables_on_startup: bool = True) -> FastAPI:  #False w celu szybszego uruchamiania aplikacji, jeżeli aplikacja jest uruchamiana pierwszy raz to należy zostawić True w celu utworzenmia bazy danych z tabelami
    application = FastAPI()

    @application.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    application.include_router(products_router)
    application.include_router(clients_router)
    application.include_router(carts_router)

    if create_tables_on_startup:
        create_db_and_tables()


    return application

app = create_app()