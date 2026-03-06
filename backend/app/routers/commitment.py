from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from schemas.commitment import CommitmentCreate

from models.commitment import Commitment

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@app.post("/commitment")
def create_commitment(
    payload: CommitmentCreate,
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    session = start_decision_session(db, user_id, "commitment_created")

    db_commitment = Commitment(
        user_id=user_id,
        commitment=payload.commitment,
        source=payload.source
    )

    db.add(db_commitment)
    db.commit()
    db.refresh(db_commitment)

    log_event(
        db,
        session.id,
        "commitment_created",
        commitment_id=db_commitment.id,
        payload={
            "text": payload.commitment,
            "source": payload.source
        }
    )

    return {"message": "Commitment created"}
