from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from schemas.decision_context import DecisionContextCreate

from models.user import User
from models.decision_context import DecisionContext


router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/decision_context")
def create_decision_context(
    payload: DecisionContextCreate,
    db: DBSession,
    current_user: User = Depends(get_current_user)
):

    # start decision session
    session = start_decision_session(
        db,
        current_user.id,
        "decision_context_created"
    )

    # create decision context
    db_decision = DecisionContext(
        user_id=current_user.id,
        description=payload.description
    )

    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)

    # log event
    log_event(
        db,
        session.id,
        "decision_context_created",
        payload={
            "description": payload.description
        },
        decision_context_id=db_decision.id
    )

    # response
    return {
        "message": "Decision context created",
        "decision_context_id": db_decision.id,
        "description": db_decision.description
    }
