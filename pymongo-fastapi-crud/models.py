import uuid
from typing import Optional
from pydantic import BaseModel, Field

# Model Book to store in the DB - also note that Field
# annotations can control field validation for each object
class Book(BaseModel):
    id: str = Field(default_factory=uuid.UUID, alias="_id")
    title: str = Field(...)
    author: str = Field(...)
    synopsis: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e", 
                "title": "Malcolm X",
                "author": "Alex Haley",
                "synopsis": "The autobio of Malcolm X"
            }
        }

# Class for updating the BookModel 
# note that the id field is not included since user cannot change
class BookUpdate(BaseModel):
    title: Optional[str]
    author: Optional[str]
    synopsis: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "title": "Malcolm X",
                "author": "Alex Haley",
                "synopsis": "Update the autobio of X"
            }
        }
