from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from schemas.execution import ExecutionCreate

from models.user import User
from models.execution import Execution
from models.commitment import Commitment


router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/execution")
def create_execution(
    payload: ExecutionCreate,
    db: DBSession,
    current_user: User = Depends(get_current_user)
):

    session = start_decision_session(
        db,
        current_user.id,
        "commitment_execution"
    )

    # find commitment
    commitment = db.query(Commitment).filter(
        Commitment.id == payload.commitment_id,
        Commitment.user_id == current_user.id
    ).first()

    if not commitment:
        raise HTTPException(
            status_code=404,
            detail="Commitment not found"
        )

    # create execution record
    db_execution = Execution(
        commitment_id=payload.commitment_id,
        user_id=current_user.id,
        outcome=payload.outcome,
        prompt_response=payload.prompt_response
    )

    db.add(db_execution)

    # update commitment status
    commitment.status = payload.outcome

    db.commit()
    db.refresh(db_execution)

    # log decision event
    log_event(
        db,
        session.id,
        "commitment_action_taken",
        commitment_id=payload.commitment_id,
        payload={
            "outcome": payload.outcome,
            "prompt_response": payload.prompt_response
        }
    )

    return {
        "message": "Execution recorded",
        "commitment_id": payload.commitment_id,
        "outcome": payload.outcome
    }
