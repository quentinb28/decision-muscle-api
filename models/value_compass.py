from sqlalchemy import Column, Integer, DateTime
from db.base import Base
from sqlalchemy import ForeignKey

class ValueCompass(Base):
    __tablename__ = "value_compasses"

    id = Column(Integer, primary_key=True, index=True)
    identity_anchor_id = Column(Integer, ForeignKey("identity_anchors.id"))
    created_at = Column(DateTime)
