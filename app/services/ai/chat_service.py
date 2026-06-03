import json

from google import genai
from google.genai import types

from fastmcp import Client

from app.core.config import settings
from app.core.logger import get_logger

from app.services.ai.memory_service import (
    save_memory,
    get_memory
)

logger = get_logger(__name__)

client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)
# for model in client.models.list():
#     print(model.name)


def sanitize_schema(schema):

    if not isinstance(schema, dict):
        return schema

    bad_keys = [
        "additionalProperties",
        "additional_properties",
        "$schema"
    ]

    cleaned = {
        k: sanitize_schema(v)
        for k, v in schema.items()
        if k not in bad_keys
    }

    return cleaned


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
        # MCP CLIENT
        # =====================================

        async with Client(
            "http://127.0.0.1:8000/mcp"
        ) as mcp_client:

            # =====================================
            # DISCOVER MCP TOOLS
            # =====================================

            available_tools = (
                await mcp_client.list_tools()
            )

            gemini_tools = []

            for tool in available_tools:

                schema = (
                    tool.inputSchema
                    if hasattr(tool, "inputSchema")
                    else {}
                )

                if hasattr(
                    schema,
                    "model_dump"
                ):
                    schema = schema.model_dump()

                gemini_tools.append(
                    types.Tool(
                        function_declarations=[
                            types.FunctionDeclaration(
                                name=tool.name,
                                description=tool.description,
                                parameters=sanitize_schema(
                                    schema
                                )
                            )
                        ]
                    )
                )

            logger.info(
                f"[MCP_TOOLS] Loaded {len(gemini_tools)} tools"
            )

            # =====================================
            # CREATE GEMINI CHAT SESSION
            # =====================================

            chat = client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    tools=gemini_tools
                )
            )

            logger.info(
                "[GEMINI_CHAT_CREATED]"
            )

            # =====================================
            # SYSTEM PROMPT
            # =====================================

            prompt = f"""
You are an AI Assistant for an English Learning Platform.

ABOUT PLATFORM:
- Help users learn English.
- Recommend learning packages.
- Answer grammar questions.
- Answer speaking questions.
- Answer vocabulary questions.
- Use MCP tools whenever data is needed.

CURRENT USER:
User ID = {user.id}

PREVIOUS CONVERSATION:
{memory_context}

AVAILABLE TOOLS:
- get_packages
- get_package
- get_users
- get_user

RULES:
1. Use tools whenever package information is needed.
2. Never invent package information.
3. Never invent user information.
4. Use memory context when user refers to:
   - first package
   - second package
   - that package
   - previous package
5. Be concise and helpful.

CURRENT MESSAGE:
{message}
"""

            # =====================================
            # FIRST GEMINI MESSAGE
            # =====================================

            response = chat.send_message(
                prompt
            )

            logger.info(
                "[GEMINI_INITIAL_RESPONSE]"
            )

            # =====================================
            # TOOL LOOP
            # =====================================

            while (
                hasattr(
                    response,
                    "function_calls"
                )
                and response.function_calls
            ):

                for call in response.function_calls:

                    logger.info(
                        f"[MCP_TOOL_CALL] {call.name}"
                    )

                    logger.info(
                        f"[MCP_TOOL_ARGS] {call.args}"
                    )

                    # =============================
                    # EXECUTE MCP TOOL
                    # =============================

                    tool_result = (
                        await mcp_client.call_tool(
                            call.name,
                            arguments=call.args
                        )
                    )

                    raw_output = (
                        tool_result.content[0].text
                    )

                    logger.info(
                        f"[MCP_TOOL_RESULT] {raw_output}"
                    )

                    try:

                        parsed = json.loads(
                            raw_output
                        )

                    except Exception:

                        parsed = {
                            "result": raw_output
                        }

                    # Gemini requires dict

                    if isinstance(
                        parsed,
                        list
                    ):
                        parsed = {
                            "data": parsed
                        }

                    # =============================
                    # SEND TOOL RESPONSE
                    # BACK TO SAME CHAT SESSION
                    # =============================

                    response = chat.send_message(
                        types.Part.from_function_response(
                            name=call.name,
                            response=parsed
                        )
                    )

            # =====================================
            # FINAL RESPONSE
            # =====================================

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
            f"[CHAT_ERROR] {str(e)}"
        )

        return (
            "Sorry, I couldn't process your request."
        )