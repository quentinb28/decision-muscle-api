from fastapi import FastAPI, Depends
from db.base import Base
from db.session import engine
from typing import Annotated
from sqlalchemy.orm import Session
from db.session import get_db
from app.auth import get_current_user

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

app = FastAPI()
Base.metadata.create_all(bind=engine)

DBSession = Annotated[Session, Depends(get_db)]


@app.get("/home")
def get_home_state(
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):

    # Identity Anchor
    latest_identity_anchor = db.query(IdentityAnchor).filter(
        IdentityAnchor.user_id == user_id).order_by(
        IdentityAnchor.created_at.desc()).first(
    )

    # Decision Context
    latest_decision_context = db.query(DecisionContext).filter(
        DecisionContext.user_id == user_id).order_by(
        DecisionContext.created_at.desc()).first(
    )

    # Active Commitments
    active_commitments = db.query(Commitment).filter(
        Commitment.user_id == user_id,
        Commitment.status == "active").all(
    )

    remaining_slots = 3 - len(active_commitments)

    # Global Available Actions (always)
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

    # Primary Suggested Action
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

@app.post("/decision_context")
def create_decision_context(
    payload: DecisionContextCreate, 
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):

    db_decision = DecisionContext(
        user_id=user_id,
        description=payload.description
    )

    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)

    db.close()

    return {"message": "Decision Context logged"}

@app.post("/prioritization_filter")
def create_prioritization_filter(
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    # Get last decision context
    latest_decision_context = (
        db.query(DecisionContext)
        .filter(DecisionContext.user_id == user_id)
        .order_by(DecisionContext.created_at.desc())
        .first()
    )

    if not latest_decision_context:
        return {"error": "Decision context not found"}

    # Check if latest_value_compass exists
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
            .limit(3)
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

    # Build response cleanly
    response = {
        f"priority{i+1}": value
        for i, value in enumerate(priorities)
    }

    response["mode"] = mode

    return response

@app.post("/identity_anchor")
def create_identity_anchor(
    payload: IdentityAnchorCreate, 
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):

    try:
        # --- create identity anchor ---
        db_identity_anchor = IdentityAnchor(
            user_id=user_id,
            description=payload.description,
            )

        db.add(db_identity_anchor)
        db.commit()
        db.refresh(db_identity_anchor)

        # --- create value compass ---
        db_value_compass = ValueCompass(
            identity_anchor_id=db_identity_anchor.id,
            user_id=user_id,
            )
        
        db.add(db_value_compass)
        db.commit()
        db.refresh(db_value_compass)

        # --- extract top values from identity anchor ---
        top_values = extract_top_values([db_identity_anchor.description])

        # --- create value score pairs ---
        for (value, score) in top_values:
            db_value_score = ValueScore(
                value_compass_id=db_value_compass.id,
                values=value,
                scores=score
                )

            db.add(db_value_score)
            db.commit()
            db.refresh(db_value_score)

        return {"message": "Identity Anchor + Value Compass registered"}

    finally:
        db.close()

@app.get("/identity-anchor/active")
def get_active_identity_anchor(
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):

    identity_anchor = db.query(
        IdentityAnchor).filter(
        IdentityAnchor.user_id == user_id).order_by(
        IdentityAnchor.created_at.desc()).first(
    )

    if not identity_anchor:
        return {"exists": False}

    return {
        "exists": True,
        "id": identity_anchor.id,
        "description": identity_anchor.description,
        "created_at": identity_anchor.created_at
    }

@app.get("/value-compass/active")
def get_latest_value_compass(
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):

    result = (
        db.query(
            ValueScore.values.label("value"),
            ValueScore.scores.label("score")).join(
            ValueCompass,
            ValueScore.value_compass_id == ValueCompass.id).filter(
            ValueCompass.user_id == user_id).order_by(
            ValueCompass.created_at.desc()).limit(5).all()
        )
    
    return [row._asdict() for row in result]

@app.post("/capacity_snapshot")
def create_capacity_snapshot(
    payload: CapacitySnapshotCreate, 
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):

    capacity_score = compute_capacity_score(payload)

    # 80–100 → High regulatory bandwidth
    # 50–79 → Moderate
    # 20–49 → Low
    # 1–19 → High collapse risk

    return {
        "baseline_capacity": capacity_score
    }

@app.post("/commitment_calibration")
def create_commitment_calibration(
    payload: CommitmentCalibrationCreate, 
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):

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

    return {
        "baseline_capacity": baseline_capacity,
        "commitment_appraisal": commitment_appraisal,
        "adjusted_capacity": adjusted_capacity,
        "recommendation": recommendation,
        "alternatives": alternatives
    }

@app.post("/commitment")
def create_commitment(
    payload: CommitmentCreate, 
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):
    
    db_commitment = Commitment(
        user_id=user_id,
        commitment=payload.commitment,
        source=payload.source
    )

    db.add(db_commitment)
    db.commit()
    db.refresh(db_commitment)

    db.close()

    return {"message": "Commitment created"}

# background job every hour
# UPDATE commitment
# SET status = 'missed'
# WHERE due_at < now
# AND status = 'active'
# def mark_missed_commitments():

#     db = SessionLocal()

#     try:
#         overdue = db.query(Commitment)\
#             .filter(
#                 Commitment.due_at < datetime.utcnow(),
#                 Commitment.status == "active"
#             )\
#             .all()

#         for c in overdue:
#             c.status = "missed"

#         db.commit()

#     finally:
#         db.close()

@app.post("/execution")
def create_execution(
    payload: ExecutionCreate, 
    db: DBSession, 
    user_id: str = Depends(get_current_user)
):
    
    try:
        db_execution = Execution(
            commitment_id=payload.commitment_id,
            outcome=payload.outcome,
            comment=payload.comment,
        )

        db.add(db_execution)

        # fetch related commitment
        commitment = db.query(Commitment).filter(
            Commitment.id == payload.commitment_id).first(
        )

        if not commitment:
            return {"error": "Commitment not found"}

        if payload.outcome == "completed":
            commitment.status = "completed"

        elif payload.outcome == "missed":
            commitment.status = "missed"

        db.commit()

        db.refresh(db_execution)
        db.refresh(commitment)

        return {"message": "Execution recorded"}

    finally:
        db.close()

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
    completed_count = sum([1 for commitment in commitments if commitment.status == "completed"])

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
# sqlite3 test.db
# http://127.0.0.1:8001/docs
