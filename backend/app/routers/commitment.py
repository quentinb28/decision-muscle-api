from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event
from app.services.google_calendar import create_calendar_event

from schemas.commitment import CommitmentCreate

from models.user import User
from models.commitment import Commitment

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/commitment")
def create_commitment(
    payload: CommitmentCreate,
    db: DBSession,
    current_user: User = Depends(get_current_user)
):

    session = start_decision_session(
        db, 
        current_user.id, 
        "commitment_created"
    )

    db_commitment = Commitment(
        user_id=current_user.id,
        commitment=payload.commitment,
        source=payload.source    
    )

    db.add(db_commitment)
    db.commit()
    db.refresh(db_commitment)

    # create calendar event (safe)
    try:

        event_id = create_calendar_event(
            user=current_user,
            commitment_text=payload.commitment,
            start_time=payload.start_time,
            end_time=payload.end_time
        )

        db_commitment.calendar_event_id = event_id
        db.commit()

    except Exception as e:

        print("Calendar event creation failed:", e)

    # log decision event
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

    return {
        "message": "Commitment created",
        "commitment_id": db_commitment.id
    }
