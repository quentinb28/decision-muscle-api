from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db.base import Base
from db.session import engine, get_db
from typing import Annotated
from sqlalchemy.orm import Session
from app.auth import get_current_user

from app.routers import home
from routers import identity
from routers import prioritization_filter
from routers import decision_context
from routers import capacity_snapshot
from routers import commitment_calibration
from routers import commitment
from routers import execution
from routers import metrics

from models.identity_anchor import IdentityAnchor
from models.value_compass import ValueCompass
from models.value_score import ValueScore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace later with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# routers
app.include_router(home.router)
app.include_router(identity.router)
app.include_router(prioritization_filter.router)
app.include_router(decision_context.router)
app.include_router(capacity_snapshot.router)
app.include_router(commitment_calibration.router)
app.include_router(commitment.router)
app.include_router(execution.router)
app.include_router(metrics.router)

DBSession = Annotated[Session, Depends(get_db)]


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


# python -m uvicorn app.main:app --reload --port 8000
# python -m uvicorn app.main:app --reload
# lsof -i :8000
# kill -9 12569
# http://127.0.0.1:8000/docs
# crontab -e / EDITOR=nano crontab -e
# crontab 48 hours: 0 0 */2 * *
# sqlite3 test.db
# finder: DB Browser for SQLite
