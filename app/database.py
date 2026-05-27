from sqlalchemy import create_engine
from app.config import get_settings
from sqlmodel import Session

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=False,
)

def get_session():
    with Session(engine) as session:
        yield session
