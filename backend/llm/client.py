import os

from anthropic import Anthropic
from anthropic.types import TextBlock

_api_key = os.environ.get("ANTHROPIC_API_KEY")
if not _api_key:
    raise RuntimeError("ANTHROPIC_API_KEY is not set in environment")

_client = Anthropic(api_key=_api_key)


def call_llm(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    try:
        response = _client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        
        text_block = next(b for b in response.content if isinstance(b, TextBlock))
        text = text_block.text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            lines = lines[1:] if lines[0].startswith("```") else lines
            lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
            text = "\n".join(lines).strip()
        return text
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc
