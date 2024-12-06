from pydantic import BaseModel, Field
from typing import List
from models.TrailDetail import TrailDetail 

# Trail summary model used for LLM Trailz responses
class TrailSummary(BaseModel):
     intro: str = Field(description="Intro to the summary of found trailz.")
     trailz: List[TrailDetail]
     outro: str = Field(description="Outro to the summary of found trailz.") 