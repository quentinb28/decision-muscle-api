from datetime import datetime, timedelta

from fastapi import FastAPI, Depends
from db.base import Base
from db.session import engine, SessionLocal
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
from schemas.commitment import CommitmentCreate
from schemas.execution import ExecutionCreate

from app.ai.extract_top_values import extract_top_values
from app.ai.generate_suggestions import generate_suggestions

app = FastAPI()
Base.metadata.create_all(bind=engine)

DBSession = Annotated[Session, Depends(get_db)]

@app.get("/")
def root():
    return {"status": "Decision Integrity Engine Running"}

@app.get("/home")
def get_home_state(db: DBSession, user_id: str = Depends(get_current_user)):

    # 1️⃣ Identity Anchor
    latest_identity_anchor = db.query(IdentityAnchor).filter(
        IdentityAnchor.user_id == user_id).order_by(
        IdentityAnchor.created_at.desc()).first()

    # 2️⃣ Decision Context
    latest_decision_context = db.query(DecisionContext).filter(
        DecisionContext.user_id == user_id).order_by(
        DecisionContext.created_at.desc()).first()

    # 3️⃣ Active Commitments
    active_commitments = db.query(Commitment).join(
        DecisionContext, 
        Commitment.decision_id == DecisionContext.id).filter(
        DecisionContext.user_id == user_id,
        Commitment.status == "active").all()

    remaining_slots = 3 - len(active_commitments)

    # 4️⃣ Global Available Actions (always)
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

    # 5️⃣ Primary Suggested Action
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
                "text": c.next_step,
                "due_at": c.due_at
            }
            for c in active_commitments
        ]
    }
    
@app.get("/identity-anchor/active")
def get_active_identity_anchor(db: DBSession, user_id: str = Depends(get_current_user)):

    identity_anchor = db.query(
        IdentityAnchor).filter(
        IdentityAnchor.user_id == user_id).order_by(
        IdentityAnchor.created_at.desc()).first()

    if not identity_anchor:
        return {"exists": False}

    return {
        "exists": True,
        "id": identity_anchor.id,
        "description": identity_anchor.description,
        "created_at": identity_anchor.created_at
    }

@app.post("/identity_anchors")
def create_identity_anchor(identity_anchor: IdentityAnchorCreate, db: DBSession, user_id: str = Depends(get_current_user)):

    db = SessionLocal()

    try:
        # --- create identity anchor ---
        db_identity_anchor = IdentityAnchor(
            user_id=user_id,
            description=identity_anchor.description,
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

# @app.get("/value-compasses/{user_id}")
# def get_latest_value_compass(user_id: int, db: DBSession):
    
#     return (
#         db.query(ValueCompass)
#         .filter(ValueCompass.user_id == user_id)
#         .order_by(ValueCompass.created_at.desc())
#         .first()
#     )

@app.post("/decision_contexts")
def create_decision_context(decision_context: DecisionContextCreate, db: DBSession, user_id: str = Depends(get_current_user)):

    db = SessionLocal()

    latest_value_compass = db.query(ValueCompass).filter(
            ValueCompass.user_id == user_id).order_by(
            ValueCompass.created_at.desc()).first()

    db_decision = DecisionContext(
        user_id=user_id,
        description=decision_context.description,
        value_compass_id=latest_value_compass.id
    )

    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)

    db.close()

    return {"message": "Decision logged"}

@app.post("/commitments/suggestions")
def get_suggestions(user_id: str, db: DBSession):
    return generate_suggestions(user_id, db)

# Backend fetches:
# DecisionContext.text
# linked ValueCompass
# top 3 values

@app.post("/commitments")
def create_commitment(commitment: CommitmentCreate):
    db = SessionLocal()

    db_commitment = Commitment(
        decision_id=commitment.decision_id,
        user_id=commitment.user_id,
        next_step=commitment.next_step,
        start_at=datetime.utcnow,
        due_at=datetime.utcnow() + timedelta(hours=48),
        source=commitment.source,
        status="active"
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

@app.post("/executions")
def create_execution(execution: ExecutionCreate):
    db = SessionLocal()

    try:
        db_execution = Execution(
            commitment_id=execution.commitment_id,
            outcome=execution.outcome,
            comment=execution.comment,
            executed_at=datetime.utcnow
        )

        db_execution.add(execution)

        # fetch related commitment
        commitment = db.query(Commitment).filter(
            Commitment.id == execution.commitment_id).first(
        )

        if not commitment:
            return {"error": "Commitment not found"}

        if execution.outcome == "done":
            commitment.status = "completed"

        elif execution.outcome in ["partial", "skipped"]:
            commitment.status = "missed"

        db.commit()

        return {"message": "Execution recorded"}

    finally:
        db.close()

@app.get("/metrics/follow-through-rate/{user_id}")
def get_follow_through_rate(user_id: str):

    db = SessionLocal()

    # 1. Get all commitments for user
    commitments = db.query(Commitment).filter(
        Commitment.user_id == user_id
    ).filter(
        Commitment.status != "active"
    ).all()

    if len(commitments) == 0:
        db.close()
        return {"Follow Through Rate (FTR)": 0}
    
    # 2. Count all completed commitments
    completed_count = sum([1 for commitment in commitments if commitment.status == "completed"])

    # 3. Compute score
    score = completed_count / len(commitments)

    db.close()

    return {"Follow Through Rate (FTR)": score}

@app.get("/metrics/self-leadership-rate/{user_id}")
def get_self_leadership_rate(user_id: str):

    db = SessionLocal()

    # 1. Get all commitments for user
    commitments = db.query(Commitment).filter(
        Commitment.user_id == user_id
    ).all()

    if len(commitments) == 0:
        db.close()
        return {"Self Leadership Rate (SLR)": 0}
    
    # 2. Count all self endorsed commitments
    self_endorsed_count = sum([1 for commitment in commitments if commitment.source == "self_endorsed"])

    # 3. Compute score
    score = self_endorsed_count / len(commitments)

    db.close()

    return {"Self Leadership Rate (SLR)": score}

# python -m uvicorn app.main:app --reload --port 8001
# python -m uvicorn app.main:app --reload
# lsof -i :8001
# kill -9 12569
# sqlite3 test.db
# http://127.0.0.1:8001/docs
