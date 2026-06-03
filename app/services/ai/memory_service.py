import chromadb

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="chat_memory"
)


def save_memory(
    user_id: int,
    user_message: str,
    ai_response: str
):

    memory_text = f"""
User:
{user_message}

Assistant:
{ai_response}
"""

    collection.add(
        ids=[
            f"{user_id}_{collection.count()+1}"
        ],
        documents=[
            memory_text
        ],
        metadatas=[
            {
                "user_id": str(user_id)
            }
        ]
    )


def get_memory(
    user_id: int,
    query: str,
    limit: int = 5
):

    try:

        results = collection.query(
            query_texts=[query],
            n_results=limit
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        return documents

    except Exception:

        return []