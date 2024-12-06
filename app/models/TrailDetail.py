from pydantic import BaseModel, Field
from typing import List

# Trail detail base model used for Pydantic response 
class TrailDetail(BaseModel):
    name: str = Field(description="The name of the trail.")
    location: str = Field(description="The location of the trail.")
    difficulty: str = Field(description="The difficulty of the trail.")
    features: str = Field(description="The trail features and details.") #min_length=250, max_length=500)
