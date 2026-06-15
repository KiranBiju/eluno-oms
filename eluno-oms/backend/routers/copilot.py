"""AI Copilot API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.copilot import CopilotRequest, CopilotResponse
from backend.services import copilot_service

router = APIRouter()


@router.post("/chat", response_model=CopilotResponse)
def chat(req: CopilotRequest, db: Session = Depends(get_db)):
    result = copilot_service.answer_question(db, req.question)
    return CopilotResponse(**result)
