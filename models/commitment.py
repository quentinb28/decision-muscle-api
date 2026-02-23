from datetime import datetime
from sqlalchemy import Column, Integer, String, Date
from db.base import Base

class Commitment(Base):
    __tablename__ = "commitments"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer)
    user_id = Column(String)
    next_step = Column(String)
    start_at = Column(Date, default=datetime.utcnow) # = created_at
    due_at = Column(Date) # start_at + 48 hours
    source = Column(String) # ("self_endorsed" | "ai_generated")
    status = Column(String) # ("active" | "completed" | "missed")
    