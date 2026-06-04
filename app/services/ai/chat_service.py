import json

from groq import Groq
from fastmcp import Client

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

# for model in client.models.list():
#     print(model.name)

def build_tool_schema(tool):

    schema = (
        tool.inputSchema
        if hasattr(tool, "inputSchema")
        else {}
    )

    if hasattr(schema, "model_dump"):
        schema = schema.model_dump()

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": schema or {
                "type": "object",
                "properties": {}
            }
        }
    }


async def ask_ai(
    db,
    user,
    message: str
):

    try:

        logger.info(
            f"[USER_MESSAGE] user_id={user.id} message={message}"
        )

        # =========================
        # MEMORY
        # =========================

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

        # =========================
        # MCP CLIENT
        # =========================

        async with Client(
            "http://127.0.0.1:8000/mcp"
        ) as mcp_client:

            # =========================
            # LOAD MCP TOOLS
            # =========================

            available_tools = (
                await mcp_client.list_tools()
            )

            tools = [
                build_tool_schema(tool)
                for tool in available_tools
            ]

            logger.info(
                f"[MCP_TOOLS] Loaded {len(tools)} tools"
            )

            # =========================
            # SYSTEM PROMPT
            # =========================

            system_prompt = f"""
You are an English Teacher and English Conversation Partner.

ABOUT THE PLATFORM:
This is an English Learning Platform.

Your job is to:
- Teach English.
- Help users improve speaking skills.
- Help users improve vocabulary.
- Help users improve grammar.
- Help users improve pronunciation.
- Conduct English conversations.
- Recommend English learning packages using MCP tools when appropriate.

CURRENT USER:
User ID = {user.id}

PREVIOUS CONVERSATION:
{memory_context}

ENGLISH LEARNING TOPICS:

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

AVAILABLE TOOLS:
- get_packages
- get_package

RULES:

1. You are ONLY an English teacher.

2. Answer ONLY English-learning related questions.

3. If a user asks about:
   - Hospitals
   - Medical advice
   - Diseases
   - Politics
   - Religion
   - Programming
   - Coding
   - Finance
   - Stock market
   - Legal advice
   - Engineering
   - General knowledge unrelated to English learning

   DO NOT answer the question.

4. Instead reply:

   "I am your English Teacher. I can help you practice English through conversations, vocabulary, grammar, speaking exercises, and English-learning topics such as restaurants, travel, festivals, job interviews, childhood memories, and planning trips."

5. If the user asks:
   - "Show me packages"
   - "Recommend a package"
   - "What courses are available"

   Use MCP tools.

6. If the user asks:
   - "Let's practice English"
   - "Talk with me"
   - "Start a conversation"

   Begin an English conversation.

7. Always encourage the user to reply in English.

8. Correct grammar mistakes gently.

9. Never invent package information.

10. Only use information returned by MCP tools.

11. When users refer to:
    - first package
    - second package
    - that package
    - previous package

    use PREVIOUS CONVERSATION to understand the reference.

12. Keep responses friendly, encouraging, and educational.

CURRENT MESSAGE:
{message}
"""

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ]

            # =========================
            # FIRST GROQ CALL
            # =========================

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            # =========================
            # TOOL LOOP
            # =========================

            while (
                response.choices[0].message.tool_calls
            ):

                tool_calls = (
                    response.choices[0]
                    .message
                    .tool_calls
                )

                messages.append(
                    response.choices[0]
                    .message
                )

                for tool_call in tool_calls:

                    tool_name = (
                        tool_call.function.name
                    )

                    tool_args = json.loads(
                        tool_call.function.arguments
                    )

                    logger.info(
                        f"[MCP_TOOL_CALL] {tool_name}"
                    )

                    logger.info(
                        f"[MCP_TOOL_ARGS] {tool_args}"
                    )

                    # =====================
                    # EXECUTE MCP TOOL
                    # =====================

                    result = (
                        await mcp_client.call_tool(
                            tool_name,
                            arguments=tool_args
                        )
                    )

                    raw_output = (
                        result.content[0].text
                    )

                    logger.info(
                        f"[MCP_TOOL_RESULT] {raw_output}"
                    )

                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": raw_output
                        }
                    )

                # =====================
                # SEND TOOL RESULT
                # BACK TO GROQ
                # =====================

                response = (
                    client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        tools=tools,
                        tool_choice="auto"
                    )
                )

            # =========================
            # FINAL RESPONSE
            # =========================

            reply = (
                response.choices[0]
                .message
                .content
            )

            logger.info(
                f"[GROQ_RESPONSE] {reply}"
            )

            # =========================
            # SAVE MEMORY
            # =========================

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