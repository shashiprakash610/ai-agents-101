import json
from typing import Dict, Any

from openai import OpenAI
from app.config import settings

# ---------- Router prompt ----------
ROUTER_SYSTEM = """You are a router agent for an investment research assistant.

Return STRICT JSON ONLY.

Possible routes:
- retrieve_summarize
- retrieve_extract
- compare
- internal_kb

Format:
{"route":"...","reason":"short explanation"}
"""

# ---------- Groq client factory ----------
def _groq_client() -> OpenAI:
    return OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

# ---------- Router agent ----------
def router_decide(user_message: str) -> Dict[str, Any]:
    if not settings.GROQ_API_KEY:
        return {
            "route": "retrieve_summarize",
            "reason": "GROQ_API_KEY missing in backend/.env",
        }

    client = _groq_client()
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": ROUTER_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
    )

    text = (resp.choices[0].message.content or "").strip()

    try:
        start = text.find("{")
        end = text.rfind("}")
        return json.loads(text[start:end + 1])
    except Exception:
        return {
            "route": "retrieve_summarize",
            "reason": f"Could not parse JSON: {text[:120]}",
        }

# ---------- Final responder ----------
def respond_with_context(
    user_message: str,
    route: str,
    tool_output: dict,
) -> str:
    if not settings.GROQ_API_KEY:
        return "GROQ_API_KEY missing in backend/.env"

    system = """You are an investment research assistant.
Use the tool output to answer the user.
Be concise and structured.

If tool_output.meta.source == "stub", mention it's demo data.
If tool_output.meta.source == "chroma", do NOT call it demo.
"""


    user = f"""
User question:
{user_message}

Route chosen:
{route}

Tool output (JSON):
{json.dumps(tool_output, indent=2)}

Produce the final answer.
"""

    client = _groq_client()
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )

    return (resp.choices[0].message.content or "").strip()
