from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class Student(Document):
    full_name: str
    date_of_birth: Optional[str] = None
    knowledge_level: str = Field(default="debutant")
    score: int = Field(default=0)
    test_taken: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
