from groq import Groq
import os

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_character(prompt):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content":
                f"""
                Generate a detailed fictional character.

                {prompt}

                Include:

                Name
                Age
                Backstory
                Powers
                Weaknesses
                Personality
                Catchphrase
                """
            }
        ]
    )

    return response.choices[0].message.content
