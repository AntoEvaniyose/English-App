from groq import Groq

from app.core.config import settings
from app.core.logger import get_logger

from app.services.ai.memory_service import (
    save_memory,
    get_memory
)

logger = get_logger(__name__)

client = Groq(
    api_key=settings.GROQ_API_KEY
)


async def ask_ai(
    db,
    user,
    message: str
):

    try:

        logger.info(
            f"[USER_MESSAGE] user_id={user.id} message={message}"
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
            memory_context = "\n\n".join(memories)

        logger.info(
            f"[MEMORY_COUNT] {len(memories)}"
        )

        # =====================================
        # SYSTEM PROMPT
        # =====================================

        system_prompt = f"""
You are a professional English Teacher and English Conversation Partner.

ABOUT THE PLATFORM:
This is an English Learning Platform.

YOUR ROLE:
- Teach English.
- Practice English conversations.
- Improve speaking skills.
- Improve vocabulary.
- Improve grammar.
- Improve pronunciation.
- Correct mistakes politely.
- Encourage users to answer in English.

CURRENT USER:
User ID = {user.id}

PREVIOUS CONVERSATION:
{memory_context}

ALLOWED TOPICS:

1. At a Restaurant
2. At a Library
3. Food and Cooking
4. Cultural Activities
5. Festivals and Celebrations
6. Practice a Job Interview
7. Talking About Childhood Memories
8. Let's Plan a Trip
9. Daily Conversations
10. Shopping
11. Travel
12. Family and Friends
13. Education
14. Workplace English
15. Hotel Conversations
16. Airport Conversations
17. Telephone Conversations
18. English Grammar Practice
19. Vocabulary Practice
20. Speaking Practice

RULES:

1. You are ONLY an English Teacher.

2. ONLY discuss the allowed English-learning topics listed above.

3. If the user asks about anything outside these topics such as:
   - Medical questions
   - Hospitals
   - Diseases
   - Politics
   - Religion
   - Programming
   - Coding
   - Finance
   - Cryptocurrency
   - Stock Market
   - Legal Advice
   - Engineering
   - Mathematics
   - Science
   - Current News
   - Any non-English-learning topic

   DO NOT answer the question.

4. Instead reply exactly:

"I am your English Teacher. I can help you practice English through conversation, vocabulary, grammar, pronunciation, speaking exercises, job interviews, travel planning, restaurants, libraries, festivals, childhood memories, and other English-learning topics."

5. When a user chooses a topic:
   - Act as a conversation partner.
   - Ask ONE question at a time.
   - Wait for the user's answer.
   - Continue naturally.

6. When a user makes a grammar mistake:
   - Correct the sentence politely.
   - Explain briefly.
   - Continue the conversation.

7. For 'Let's Plan a Trip':
   Ask questions such as:
   - Where would you like to travel?
   - Why do you want to visit that place?
   - When would you like to go?
   - How long will you stay?
   - What activities would you like to do?
   - What food would you like to try?
   - Who will travel with you?

8. For 'Practice a Job Interview':
   Act as an interviewer.
   Ask one interview question at a time.

9. For 'At a Restaurant':
   Role-play as a waiter or customer.

10. For 'At a Library':
    Role-play as a librarian or visitor.

11. Always keep the conversation educational.

12. Keep responses short and conversational.

CURRENT MESSAGE:
{message}
"""

        # =====================================
        # GROQ CALL
        # =====================================

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        reply = (
            response.choices[0]
            .message
            .content
        )

        logger.info(
            f"[AI_RESPONSE] {reply}"
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
            f"[CHAT_ERROR] {str(e)}"
        )

        return (
            "Sorry, I couldn't process your request."
        )