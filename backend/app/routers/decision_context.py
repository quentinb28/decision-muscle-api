from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from schemas.decision_context import DecisionContextCreate

from models.decision_context import DecisionContext

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@app.post("/decision_context")
def create_decision_context(
    payload: DecisionContextCreate,
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    session = start_decision_session(db, user_id, "decision_context_created")

    db_decision = DecisionContext(
        user_id=user_id,
        description=payload.description
    )

    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)

    log_event(
        db,
        session.id,
        "decision_context_created",
        payload={"description": payload.description},
        decision_context_id=db_decision.id
    )

    return {"message": "Decision Context logged"}
