from groq import Groq
import os

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def chat_with_character(
    character_profile,
    memory_context,
    user_message
):

    prompt = f"""
    Stay in character.

    Character:
    {character_profile}

    Memory:
    {memory_context}

    User:
    {user_message}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
