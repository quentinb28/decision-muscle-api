from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base
from sqlalchemy import ForeignKey

class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"))
    user_id = Column(String)
    outcome = Column(String) # ("fully_completed" | "partially_completed")
    prompt_response = Column(String)
    executed_at = Column(DateTime, default=datetime.utcnow)
