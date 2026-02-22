from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base
from sqlalchemy import ForeignKey

class DecisionContext(Base):
    __tablename__ = "decision_contexts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    description = Column(String)
    value_compass_id = Column(Integer, ForeignKey("value_compasses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
