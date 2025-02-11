from datetime import datetime

from beanie import Document
from pydantic import Field


class Student(Document):
    first_name: str
    last_name: str
    date_of_birth: datetime = Field(default_factory=datetime.now)
    knowledge_level: str = Field(default="debutant")
    score: int = Field(default=0)
    test_taken: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
