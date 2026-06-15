from pydantic import BaseModel, Field


class CopilotRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class CopilotResponse(BaseModel):
    answer: str
    context_snapshot: dict
