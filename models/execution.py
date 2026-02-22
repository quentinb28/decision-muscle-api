from sqlalchemy import Column, Integer, String, Date
from db.base import Base
from sqlalchemy import ForeignKey

class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"))
    outcome = Column(String) # ("done" | "partial" | "skipped")
    comment= Column(String)
    executed_at = Column(Date)
