from datetime import datetime
from sqlalchemy import Column, Integer, String, Date
from db.base import Base

class IdentityAnchor(Base):
    __tablename__ = "identity_anchors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    description = Column(String)
    created_at = Column(Date, default=datetime.utcnow)
