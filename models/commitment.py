from sqlalchemy import Column, Integer, Boolean
from db.base import Base

class Commitment(Base):
    __tablename__ = "commitments"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer)
    next_step = Column(Integer)
    completed = Column(Boolean, default=False)
