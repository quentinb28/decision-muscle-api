from datetime import datetime
from fastapi import FastAPI, Depends
from db.base import Base
from db.session import engine
from typing import Annotated
from sqlalchemy.orm import Session
from db.session import get_db
from app.auth import get_current_user

from models.user import User
from models.decision_session import DecisionSession
from models.decision_event import DecisionEvent
from models.identity_anchor import IdentityAnchor
from models.value_compass import ValueCompass
from models.value_score import ValueScore
from models.decision_context import DecisionContext
from models.commitment import Commitment
from models.execution import Execution

from schemas.identity_anchor import IdentityAnchorCreate
# from schemas.value_compass import ValueCompassCreate
# from schemas.value_score import ValueScoreCreate
from schemas.decision_context import DecisionContextCreate
from schemas.capacity_snapshot import CapacitySnapshotCreate
from schemas.commitment_calibration import CommitmentCalibrationCreate
from schemas.commitment import CommitmentCreate
from schemas.execution import ExecutionCreate

from app.ai.extract_top_values import extract_top_values
from app.ai.rank_commitments_from_values import rank_commitments_from_values
from app.ai.rank_commitments_from_wisdom import rank_commitments_from_wisdom
from app.ai.generate_commitment_appraisal import generate_commitment_appraisal
from app.ai.generate_scaled_commitment import generate_scaled_commitments
from app.ai.compute_capacity_score import compute_capacity_score

import uuid

app = FastAPI()
Base.metadata.create_all(bind=engine)

DBSession = Annotated[Session, Depends(get_db)]


# ------------------------------------------------
# SESSION + EVENT HELPERS
# ------------------------------------------------

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


# ------------------------------------------------
# HOME
# ------------------------------------------------

@app.get("/home")
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

    available_actions = [
        "create_identity_anchor",
        "create_decision_context"
    ]

    if remaining_slots > 0:
        available_actions.extend([
            "self_endorsed_commitment",
            "ai_suggested_commitments"
        ])
    else:
        available_actions.append("report_execution")

    if not latest_identity_anchor:
        primary = "create_identity_anchor"
        state = "no_identity"

    elif not latest_decision_context:
        primary = "create_decision_context"
        state = "no_decision"

    elif len(active_commitments) == 0:
        primary = "create_commitment"
        state = "no_commitment"

    elif remaining_slots == 0:
        primary = "report_execution"
        state = "limit_reached"

    else:
        primary = "report_execution_or_add"
        state = "active_commitments"

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
        "state": state,
        "primary_action": primary,
        "available_actions": available_actions,
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


# ------------------------------------------------
# IDENTITY ANCHOR
# ------------------------------------------------

@app.post("/identity_anchor")
def create_identity_anchor(
    payload: IdentityAnchorCreate,
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    session = start_decision_session(db, user_id, "identity_anchor_created")

    try:

        db_identity_anchor = IdentityAnchor(
            user_id=user_id,
            description=payload.description
        )

        db.add(db_identity_anchor)
        db.commit()
        db.refresh(db_identity_anchor)

        db_value_compass = ValueCompass(
            identity_anchor_id=db_identity_anchor.id,
            user_id=user_id
        )

        db.add(db_value_compass)
        db.commit()
        db.refresh(db_value_compass)

        top_values = extract_top_values([db_identity_anchor.description])

        value_pairs = []

        for value, score in top_values:

            db_value_score = ValueScore(
                value_compass_id=db_value_compass.id,
                values=value,
                scores=score
            )

            db.add(db_value_score)
            db.commit()

            value_pairs.append({
                "value": value,
                "score": score
            })

        log_event(
            db,
            session.id,
            "identity_anchor_created",
            payload={
                "description": payload.description,
                "values": value_pairs
            }
        )

        return {"message": "Identity Anchor + Value Compass registered"}

    finally:
        db.close()


# ------------------------------------------------
# ACTIVE IDENTITY ANCHOR
# ------------------------------------------------

@app.get("/identity-anchor/active")
def get_active_identity_anchor(
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    identity_anchor = db.query(IdentityAnchor).filter(
        IdentityAnchor.user_id == user_id
    ).order_by(
        IdentityAnchor.created_at.desc()
    ).first()

    if not identity_anchor:
        return {"exists": False}

    return {
        "exists": True,
        "id": identity_anchor.id,
        "description": identity_anchor.description,
        "created_at": identity_anchor.created_at
    }


# ------------------------------------------------
# ACTIVE VALUE COMPASS
# ------------------------------------------------

@app.get("/value-compass/active")
def get_latest_value_compass(
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    result = (
        db.query(
            ValueScore.values.label("value"),
            ValueScore.scores.label("score")
        )
        .join(ValueCompass, ValueScore.value_compass_id == ValueCompass.id)
        .filter(ValueCompass.user_id == user_id)
        .order_by(ValueCompass.created_at.desc())
        .all()
    )

    return [row._asdict() for row in result]


# ------------------------------------------------
# DECISION CONTEXT
# ------------------------------------------------

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


# ------------------------------
# PRIORITIZATION FILTER
# ------------------------------

@app.post("/prioritization_filter")
def create_prioritization_filter(db: DBSession, user_id: str = Depends(get_current_user)):

    session = start_decision_session(db, user_id, "prioritization_filter")

    latest_decision_context = (
        db.query(DecisionContext)
        .filter(DecisionContext.user_id == user_id)
        .order_by(DecisionContext.created_at.desc())
        .first()
    )

    if not latest_decision_context:
        return {"error": "Decision context not found"}

    latest_value_compass = (
        db.query(ValueCompass)
        .filter(ValueCompass.user_id == user_id)
        .order_by(ValueCompass.created_at.desc())
        .first()
    )

    if latest_value_compass:

        top_values = (
            db.query(ValueScore)
            .filter(ValueScore.value_compass_id == latest_value_compass.id)
            .order_by(ValueScore.scores.desc())
            .all()
        )

        values_str = "\n".join(
            [f"{v.values}: {round(v.scores, 2)}" for v in top_values]
        )

        priorities = rank_commitments_from_values(
            latest_decision_context.description,
            values_str
        )

        mode = "values"

    else:

        priorities = rank_commitments_from_wisdom(
            latest_decision_context.description
        )

        mode = "wisdom"

    log_event(
        db,
        session.id,
        "prioritization_filter_applied",
        payload={
            "mode": mode,
            "priorities": priorities
        },
        decision_context_id=latest_decision_context.id
    )

    response = {
        f"priority{i+1}": value
        for i, value in enumerate(priorities)
    }

    response["mode"] = mode

    return response


# ------------------------------------------------
# CAPACITY SNAPSHOT
# ------------------------------------------------

@app.post("/capacity_snapshot")
def create_capacity_snapshot(
    payload: CapacitySnapshotCreate,
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    session = start_decision_session(db, user_id, "capacity_check")

    capacity_score = compute_capacity_score(payload)

    log_event(
        db,
        session.id,
        "capacity_calculated",
        payload={"baseline_capacity": capacity_score}
    )

    return {
        "baseline_capacity": capacity_score
    }


# ------------------------------------------------
# COMMITMENT CALIBRATION
# ------------------------------------------------

@app.post("/commitment_calibration")
def create_commitment_calibration(
    payload: CommitmentCalibrationCreate,
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    session = start_decision_session(db, user_id, "commitment_evaluation")

    baseline_capacity = payload.baseline_capacity
    candidate_commitment = payload.candidate_commitment

    commitment_appraisal = generate_commitment_appraisal(candidate_commitment)

    adjusted_capacity = int(
        round(
            max(1, baseline_capacity * (1 - commitment_appraisal / 10))
        )
    )

    if adjusted_capacity >= 40:
        recommendation = "keep"
        alternatives = []

    elif adjusted_capacity >= 20:
        recommendation = "kneel"
        alternatives = generate_scaled_commitments(candidate_commitment)

    else:
        recommendation = "kill"
        alternatives = []

    log_event(
        db,
        session.id,
        "commitment_evaluated",
        payload={
            "candidate_commitment": candidate_commitment,
            "baseline_capacity": baseline_capacity,
            "commitment_appraisal": commitment_appraisal,
            "adjusted_capacity": adjusted_capacity,
            "recommendation": recommendation,
            "alternatives": alternatives
        }
    )

    return {
        "baseline_capacity": baseline_capacity,
        "commitment_appraisal": commitment_appraisal,
        "adjusted_capacity": adjusted_capacity,
        "recommendation": recommendation,
        "alternatives": alternatives
    }


# ------------------------------------------------
# CREATE COMMITMENT
# ------------------------------------------------

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


# ------------------------------------------------
# EXECUTION
# ------------------------------------------------

@app.post("/execution")
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


# ------------------------------------------------
# COMPUTE METRICS
# ------------------------------------------------

@app.get("/metrics/follow-through-rate")
def get_follow_through_rate(
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):

    # 1. Get all commitments for user
    commitments = db.query(Commitment).filter(
        Commitment.user_id == user_id).filter(
        Commitment.status != "active").all(
    )

    if len(commitments) == 0:
        db.close()
        return {"Follow Through Rate (FTR)": 0}
    
    # 2. Count all completed commitments
    completed_count = sum([1 for commitment in commitments if commitment.status == "fully_completed"])

    # 3. Compute score
    score = completed_count / len(commitments)

    db.close()

    return {"Follow Through Rate (FTR)": score}

# @app.get("/metrics/self-leadership-rate")
# def get_self_leadership_rate(
#     db: DBSession, 
#     user_id: str = Depends(get_current_user)
# ):

#     # 1. Get all commitments for user
#     commitments = db.query(Commitment).filter(
#         Commitment.user_id == user_id).all(
#     )

#     if len(commitments) == 0:
#         db.close()
#         return {"Self Leadership Rate (SLR)": 0}
    
#     # 2. Count all self endorsed commitments
#     self_endorsed_count = sum([1 for commitment in commitments if commitment.source == "self_endorsed"])

#     # 3. Compute score
#     score = self_endorsed_count / len(commitments)

#     db.close()

#     return {"Self Leadership Rate (SLR)": score}

# python -m uvicorn app.main:app --reload --port 8001
# python -m uvicorn app.main:app --reload
# lsof -i :8001
# kill -9 12569
# http://127.0.0.1:8001/docs
# crontab -e / EDITOR=nano crontab -e
# crontab 48 hours: 0 0 */2 * *
# sqlite3 test.db
# finder: DB Browser for SQLite
