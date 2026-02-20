from pydantic import BaseModel

class FollowThroughCreate(BaseModel):
    commitment_id: int
    completed: bool
    alignment_rating: int
