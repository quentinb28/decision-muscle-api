from pydantic import BaseModel, Field

class CommitmentCalibrationCreate(BaseModel):
    baseline_capacity: int = Field(ge=1, le=100)
    candidate_commitment: str
