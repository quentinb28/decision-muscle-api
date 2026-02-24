from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from db.base import Base
from sqlalchemy import ForeignKey

class ValueCompass(Base):
    __tablename__ = "value_compasses"

    id = Column(Integer, primary_key=True, index=True)
    identity_anchor_id = Column(Integer, ForeignKey("identity_anchors.id"))
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
