from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from db.base import Base
from sqlalchemy import ForeignKey

class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    decision_context_id = Column(Integer, ForeignKey("decision_contexts.id"), nullable=True)
    filter_options = Column(JSON, nullable=True, default=None)
    filter_mode = Column(String, nullable=True)
    baseline_capacity = Column(Integer, nullable=True)
    candidate_commitment = Column(String, nullable=True)
    commitment_appraisal = Column(Integer, nullable=True)
    adjusted_capacity = Column(Float, nullable=True)
    recommendation = Column(String, nullable=True)  # Keep / Kneel / Kill
    recommendation_alternatives = Column(JSON, nullable=True, default=None)
    commitment_id = Column(Integer, ForeignKey("commitments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True, default=None)
