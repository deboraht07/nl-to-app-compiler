from stages.llm_client import call_llm_json
from schemas.models import AppDesign

SYSTEM_PROMPT = """You are a system design engine for a no-code app builder.
Given structured intent (entities, roles, features), design the application architecture.

You MUST return ONLY valid JSON matching this exact shape:
{
  "app_name": "string",
  "entities": [
    {
      "name": "EntityName",
      "fields": [
        {"name": "field_name", "type": "string|number|boolean|date|relation", "required": true or false}
      ]
    }
  ],
  "roles": [
    {"role": "RoleName", "can_access": ["PageName1", "PageName2"]}
  ],
  "pages": ["list of all page names needed, e.g. Login, Dashboard, Contacts, Billing"]
}

Rules:
- Every entity needs an "id" field of type "string", required true.
- Admin-type roles can access every page. Non-admin roles get a sensible subset.
- If has_payments is true, include a "Billing" page and a "Plan" or "Subscription" entity.
- Every entity name used must also appear as a related page where it makes sense (e.g. Contact entity -> Contacts page).
- Return ONLY the JSON object, nothing else.
"""


def design_system(intent_dict: dict) -> AppDesign:
    user_prompt = f"Structured intent:\n{intent_dict}"
    raw = call_llm_json(SYSTEM_PROMPT, user_prompt)
    return AppDesign(**raw)