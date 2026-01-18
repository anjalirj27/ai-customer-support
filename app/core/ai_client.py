from openai import AsyncOpenAI
from app.core.config import settings


def get_ai_client() -> AsyncOpenAI:
    """
    Get AI client based on configured provider.
    Works with both OpenAI and Groq using OpenAI SDK.
    
    Returns:
        AsyncOpenAI: Configured async client
    """
    return AsyncOpenAI(
        api_key=settings.ai_api_key,
        base_url=settings.ai_base_url  # None for OpenAI, Groq URL for Groq
    )


# Global client instance (reuse across app)
ai_client = get_ai_client()
