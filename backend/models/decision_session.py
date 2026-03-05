from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base
from sqlalchemy import UUID, ForeignKey

class DecisionSession(Base):
    __tablename__ = "decision_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    trigger_type = Column(String)  # manual / cron / capacity_check / review
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
