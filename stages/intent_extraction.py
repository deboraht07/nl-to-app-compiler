from stages.llm_client import call_llm_json
from schemas.models import IntentIR

SYSTEM_PROMPT = """You are an intent extraction engine for a no-code app builder.
Given a user's natural language app description, extract structured intent.

You MUST return ONLY valid JSON matching this exact shape:
{
  "app_name": "string",
  "entities": ["list", "of", "entity names, e.g. Contact, Deal"],
  "roles": ["list", "of", "user roles mentioned or implied, e.g. Admin, User"],
  "features": ["list", "of", "features, e.g. login, dashboard, payments"],
  "has_payments": true or false,
  "assumptions": ["list any assumptions you made because the prompt was vague or incomplete"]
}

Rules:
- If no roles are mentioned, assume a single "User" role and note it in assumptions.
- If payments/premium/billing is mentioned, has_payments must be true.
- Always include at least one entity.
- Return ONLY the JSON object, nothing else.
"""


def extract_intent(user_prompt: str) -> IntentIR:
    raw = call_llm_json(SYSTEM_PROMPT, user_prompt)
    return IntentIR(**raw)  # Pydantic validates here — throws if shape is wrong