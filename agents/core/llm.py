import os

from dotenv import load_dotenv
from langchain.chat_models import BaseChatModel

from agents.core.deepseek import ChatDeepSeek


def get_llm(
    model_name: str = "deepseek-flash", temperature: float = 0
) -> BaseChatModel:
    """Build a DeepSeek model from the local environment."""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set DEEPSEEK_API_KEY in .env or the environment before running TriVAL."
        )
    if not model_name:
        raise ValueError("A DeepSeek model name is required.")

    config = {
        "model": model_name,
        "api_key": api_key,
        "base_url": "https://api.deepseek.com",
        "temperature": temperature,
        "max_tokens": 8192,
        "timeout": 1800,
        "extra_body": {"thinking": {"type": "disabled"}},
    }
    return ChatDeepSeek(**config)
