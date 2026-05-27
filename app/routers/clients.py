from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.schemas import ClientRead, ClientCreate
from app.database import get_session
from app.models import Client



router = APIRouter()

@router.post("/clients", response_model=ClientRead, status_code=status.HTTP_201_CREATED, tags=["clients"])
def create_client(payload: ClientCreate, session: Session = Depends(get_session)) -> Client:
    client = Client.model_validate(payload)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.get("/clients/{client_id}", response_model=ClientRead, status_code=status.HTTP_200_OK, tags=["clients"])
def read_client(client_id: int,session: Session = Depends(get_session)) -> Client:
    client = session.get(Client, client_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return client


@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["clients"])
def delete_client(client_id: int, session: Session = Depends(get_session),) -> None:
    client = session.get(Client, client_id)

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    session.delete(client)
    session.commit()

    return None