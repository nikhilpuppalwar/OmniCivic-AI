"""
OmniCivic AI -- Vision Service
Vision analysis wrapper. MVP uses deterministic lookup; stretch uses real vision model.
"""

from services.ai_service import generate_narrative


async def analyze_image(image_filename: str, context: str = "") -> str:
    """
    Generate descriptive evidence text for an image.
    MVP: The classification is deterministic (lookup table).
    This function only generates the narrative description.
    """
    prompt = f"""You are a civic infrastructure analyst examining a photo of a civic issue.
The image filename is: {image_filename}
Additional context: {context}

Describe what you observe in 2-3 sentences. Focus on:
- Physical evidence visible (water, cracks, debris, etc.)
- Severity indicators (size, depth, extent of damage)
- Safety implications for citizens

Be factual and observational. Do not speculate beyond what the image shows."""

    fallback = f"Visual analysis of {image_filename}: Infrastructure issue documented. Physical evidence consistent with reported complaint category."

    return await generate_narrative(
        system_prompt="You are a civic infrastructure analysis AI. Describe visual evidence objectively.",
        user_prompt=prompt,
        fallback_text=fallback,
    )
