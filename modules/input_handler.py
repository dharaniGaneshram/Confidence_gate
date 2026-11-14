from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any


class SentenceCandidate(BaseModel):
    id: str
    text: str
    position: int
    score: float 
    selected: bool
    is_neighbor: bool = False


class HighlighterInput(BaseModel):

    question: str
    doc_id: str

    sentences: List[SentenceCandidate]

    selected_ids: List[str]

    tokens_original: int = Field(ge=0)
    tokens_selected: int = Field(ge=0)
    budget: int = Field(ge=0)

    budget_hit: bool

    config: Dict[str, Any]

    @model_validator(mode="after")
    def validate_input(self):

        sentence_ids = [s.id for s in self.sentences]

        if len(sentence_ids) != len(set(sentence_ids)):
            raise ValueError("Duplicate sentence IDs found.")

        actual_selected_ids = [
            s.id for s in self.sentences if s.selected
        ]

        if set(actual_selected_ids) != set(self.selected_ids):
            raise ValueError(
                "selected_ids do not match selected sentence flags."
            )

        if self.tokens_selected > self.tokens_original:
            raise ValueError(
                "Selected tokens cannot exceed original tokens."
            )

        if self.tokens_selected > self.budget:
            raise ValueError(
                "Selected tokens exceed the selection budget."
            )

        if not self.sentences:
            raise ValueError("No sentences provided.")

        return self

    @property
    def selected_evidence(self):
        return [s for s in self.sentences if s.selected]

    @property
    def rejected_candidates(self):
        return [s for s in self.sentences if not s.selected]


def validate_highlighter_input(data):

    validated_data = HighlighterInput.model_validate(data)


    return validated_data