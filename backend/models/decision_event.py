from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from db.base import Base
from sqlalchemy import UUID, ForeignKey

class DecisionEvent(Base):
    __tablename__ = "decision_events"

    id = Column(Integer, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("decision_sessions.id"), index=True)
    event_type = Column(String, index=True)
    decision_context_id = Column(Integer, ForeignKey("decision_contexts.id"), nullable=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"), nullable=True)
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    engine_version = Column(String)
