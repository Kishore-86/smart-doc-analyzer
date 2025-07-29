from pydantic import BaseModel, Field
from typing import List, Dict
import uuid

class Entity(BaseModel):
    Text: str
    Type: str

class Document(BaseModel):
    file_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique document ID")
    filename: str
    summary: str
    sentiment: str
    entities: List[Entity]

    @classmethod
    def from_analysis(cls, filename: str, summary: str, sentiment: str, entities: List[Dict]):
        """Helper to quickly create a Document model from analysis results."""
        return cls(
            filename=filename,
            summary=summary,
            sentiment=sentiment,
            entities=[Entity(**e) for e in entities]
        )
