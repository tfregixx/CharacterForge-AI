from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_with_character(character_content, user_message, conversation_history=None, memory_context=None):
    """
    Chat with a character staying in role.
    
    Args:
        character_content: The character description/details
        user_message: The user's input message
        conversation_history: List of previous messages for context
        memory_context: Optional memory context string to include in prompt
    
    Returns:
        The character's response
    """
    
    prompt_memory = f"\nPrevious Memories:\n{memory_context}\n" if memory_context else ""
    system_prompt = f"""You are the following character:

{character_content}{prompt_memory}
**IMPORTANT RULES:**
1. Stay in character at all times
2. Never break role
3. Respond as this character would
4. Maintain their personality, speech patterns, and values
5. Reference their backstory when relevant
6. Be authentic to their character description
"""
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.8
    )
    
    return response.choices[0].message.content
