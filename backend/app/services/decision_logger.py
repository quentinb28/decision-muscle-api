from datetime import datetime
import uuid
from models.decision_session import DecisionSession
from models.decision_event import DecisionEvent


def start_decision_session(db, user_id, trigger_type):

    session = DecisionSession(
        id=uuid.uuid4(),
        user_id=user_id,
        trigger_type=trigger_type,
        started_at=datetime.utcnow()
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def log_event(
    db,
    session_id,
    event_type,
    payload=None,
    commitment_id=None,
    decision_context_id=None
):

    event = DecisionEvent(
        session_id=session_id,
        event_type=event_type,
        payload=payload,
        commitment_id=commitment_id,
        decision_context_id=decision_context_id,
        created_at=datetime.utcnow()
    )

    db.add(event)
    db.commit()