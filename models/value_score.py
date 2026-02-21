from sqlalchemy import Column, Integer, Float, String
from db.base import Base
from sqlalchemy import ForeignKey

class ValueScore(Base):
    __tablename__ = "value_score_pairs"

    id = Column(Integer, primary_key=True, index=True)
    value_compass_id = Column(String, ForeignKey("value_compasses.id"))
    values = Column(String)
    scores = Column(Float)
