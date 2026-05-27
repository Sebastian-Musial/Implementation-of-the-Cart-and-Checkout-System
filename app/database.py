from app.config import get_settings
from sqlmodel import Session, SQLModel, create_engine

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=False,
)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables() -> None:
    from app import models

    SQLModel.metadata.create_all(engine)