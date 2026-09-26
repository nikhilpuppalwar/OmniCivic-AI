import os
from typing import Optional
from dotenv import load_dotenv
from services.llm_manager import generate_completion

load_dotenv()


async def generate_narrative(
    system_prompt: str,
    user_prompt: str,
    fallback_text: str = "",
    max_tokens: int = 500,
    temperature: float = 0.3,
) -> str:
    """
    Generate narrative text using configured LLM provider.
    If no API key or call fails, returns fallback_text.
    """
    try:
        output = await generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return output if output else fallback_text
    except Exception as e:
        print(f"[AI_SERVICE] LLM call failed: {e}. Using fallback.")
        return fallback_text

