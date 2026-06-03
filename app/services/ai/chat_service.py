from google import genai

from app.core.config import settings
from app.core.logger import get_logger

from app.services.ai.tools import (
    get_packages,
    get_user_profile
)

from app.services.ai.memory_service import (
    save_memory,
    get_memory
)

logger = get_logger(__name__)

client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)
for model in client.models.list():
    print(model.name)


def ask_ai(
    db,
    user,
    message: str
):

    try:

        logger.info(
            f"[USER_MESSAGE] user_id={user.id} message={message}"
        )

        # =====================================
        # USER PROFILE
        # =====================================
        profile = get_user_profile(
            db=db,
            user_id=user.id
        )

        logger.info(
            f"[USER_PROFILE] {profile}"
        )

        # =====================================
        # PACKAGES
        # =====================================
        packages = get_packages(db)

        logger.info(
            f"[PACKAGES_COUNT] {len(packages)}"
        )

        # =====================================
        # MEMORY
        # =====================================
        memories = get_memory(
            user_id=user.id,
            query=message
        )

        memory_context = ""

        if memories:
            memory_context = "\n".join(memories)

        logger.info(
            f"[MEMORY_COUNT] {len(memories) if memories else 0}"
        )

        # =====================================
        # PROMPT
        # =====================================
        prompt = f"""
You are an AI Assistant for an English Learning Platform.

ABOUT PLATFORM:
- Help users learn English.
- Recommend learning packages.
- Answer grammar, speaking, vocabulary and writing questions.
- Use conversation history when available.

CURRENT USER:
{profile}

AVAILABLE PACKAGES:
{packages}

PREVIOUS CONVERSATION:
{memory_context}

IMPORTANT:
- If user asks "first package", "second package", "that package", etc,
  use PREVIOUS CONVERSATION to determine which package they mean.
- Never invent packages.
- Only use packages listed in AVAILABLE PACKAGES.
- Be friendly and concise.

CURRENT MESSAGE:
{message}
"""

        logger.info(
            "[GEMINI_CALL] Sending request"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        reply = response.text

        logger.info(
            f"[GEMINI_RESPONSE] {reply}"
        )

        # =====================================
        # SAVE MEMORY
        # =====================================
        save_memory(
            user_id=user.id,
            user_message=message,
            ai_response=reply
        )

        logger.info(
            "[MEMORY_SAVED]"
        )

        return reply

    except Exception as e:

        logger.exception(
            f"[GEMINI_ERROR] {str(e)}"
        )

        return (
            "Sorry, I couldn't process your request at the moment."
        )