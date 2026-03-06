from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base
from sqlalchemy import ForeignKey

class Commitment(Base):
    __tablename__ = "commitments"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decision_contexts.id"))
    user_id = Column(String)
    commitment = Column(String)
    start_at = Column(DateTime, default=datetime.utcnow) # = created_at
    due_at = Column(DateTime, default=datetime.utcnow() + timedelta(minutes=5)) # start_at + 48 hours
    source = Column(String) # ("self_endorsed" | "ai_generated")
    status = Column(String, default="active") # ("active" | "fully_completed" | "partially_completed" | "expired")
    