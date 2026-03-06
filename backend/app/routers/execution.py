from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from schemas.execution import ExecutionCreate

from models.execution import Execution
from models.commitment import Commitment

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/execution")
def create_execution(
    payload: ExecutionCreate,
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    session = start_decision_session(db, user_id, "commitment_execution")

    try:

        db_execution = Execution(
            commitment_id=payload.commitment_id,
            user_id=user_id,
            outcome=payload.outcome,
            prompt_response=payload.prompt_response
        )

        db.add(db_execution)

        commitment = db.query(Commitment).filter(
            Commitment.id == payload.commitment_id
        ).first()

        if not commitment:
            raise ValueError("Commitment not found")

        commitment.status = payload.outcome

        db.commit()

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

        return {"message": "Execution recorded"}

    finally:
        db.close()
