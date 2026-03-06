from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from models.identity_anchor import IdentityAnchor
from models.decision_context import DecisionContext
from models.commitment import Commitment

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/home")
def get_home_state(
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    session = start_decision_session(db, user_id, "home_load")

    latest_identity_anchor = db.query(IdentityAnchor).filter(
        IdentityAnchor.user_id == user_id
    ).order_by(
        IdentityAnchor.created_at.desc()
    ).first()

    latest_decision_context = db.query(DecisionContext).filter(
        DecisionContext.user_id == user_id
    ).order_by(
        DecisionContext.created_at.desc()
    ).first()

    active_commitments = db.query(Commitment).filter(
        Commitment.user_id == user_id,
        Commitment.status == "active"
    ).all()

    remaining_slots = 3 - len(active_commitments)

    log_event(
        db,
        session.id,
        "context_snapshot",
        payload={
            "state": state,
            "remaining_slots": remaining_slots,
            "active_commitments": len(active_commitments),
            "primary_action": primary
        },
        decision_context_id=latest_decision_context.id if latest_decision_context else None
    )

    return {
        "remaining_slots": remaining_slots,
        "decision_context": latest_decision_context.description if latest_decision_context else None,
        "active_commitments": [
            {
                "id": c.id,
                "text": c.commitment,
                "due_at": c.due_at
            }
            for c in active_commitments
        ]
    }
