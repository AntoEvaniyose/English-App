from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.role_guard import require_user

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from app.services.ai.chat_service import ask_ai

from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/user/chat",
    tags=["AI Chat"]
)


@router.post("")
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    logger.info(
        f"[CHAT_REQUEST] user_id={current_user.id}"
    )

    reply = ask_ai(
        db,
        current_user,
        payload.message
    )

    logger.info(
        f"[CHAT_REPLY] user_id={current_user.id}"
    )

    return {
        "reply": reply
    }