from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base

class DecisionContext(Base):
    __tablename__ = "decision_contexts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
