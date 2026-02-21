from sqlalchemy import Column, Integer, Float, String, Boolean, Date
from db.base import Base
from sqlalchemy import ForeignKey

class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"))
    completed = Column(Boolean)
    alignment_rating = Column(Float)
    executed_at = Column(Date)
