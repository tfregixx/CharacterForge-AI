import os
from groq import Groq

client = Groq(
api_key=os.getenv("GROQ_API_KEY")
)

def generate_character(
genre,
personality,
powers
):
prompt = f"""
Create a detailed fictional character.

Genre: {genre}
Personality: {personality}
Powers: {powers}

Generate:

Name
Age
Appearance
Backstory
Strengths
Weaknesses
Abilities
Catchphrase

Format clearly using markdown.
"""

```
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.9
)

return response.choices[0].message.content
```
