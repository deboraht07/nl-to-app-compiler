from stages.llm_client import call_llm_json
from schemas.models import UISchema, APISchema, DBSchema, AuthSchema


SYSTEM_PROMPT = """You are a schema generation engine for a no-code app builder.
Given an application design (entities with fields, roles, pages), generate four
schemas: UI, API, Database, and Auth.

You MUST return ONLY valid JSON matching this exact shape:
{
  "ui_schema": {
    "pages": [
      {
        "name": "PageName",
        "route": "/lowercase-route",
        "components": [
          {"type": "table|form|card|chart", "entity": "EntityName or null", "fields": ["field1", "field2"]}
        ],
        "allowed_roles": ["Role1", "Role2"]
      }
    ]
  },
  "api_schema": {
    "endpoints": [
      {"path": "/api/entities", "method": "GET|POST|PUT|DELETE", "entity": "EntityName", "allowed_roles": ["Role1"]}
    ]
  },
  "db_schema": {
    "tables": [
      {"name": "TableName", "fields": [{"name": "field_name", "type": "string|number|boolean|date|relation", "required": true}]}
    ]
  },
  "auth_schema": {
    "roles": ["Role1", "Role2"],
    "permissions": [{"role": "Role1", "can_access": ["PageName1"]}]
  }
}

CRITICAL CONSISTENCY RULES (this will be checked):
- Every "entity" referenced in ui_schema components MUST exist in db_schema tables.
- Every "fields" list in ui_schema components MUST only use field names that exist on that entity in db_schema.
- Every entity in api_schema endpoints MUST exist in db_schema tables. Never use null for "entity" in api_schema.
- db_schema tables MUST exactly match the entities and fields given in the input design (use the same field names and types).
- Every role in allowed_roles (ui_schema, api_schema) MUST exist in auth_schema roles.
- Generate at least one GET, POST, PUT, DELETE endpoint per entity (except read-only entities like Analytics).
- PUT and DELETE endpoints MUST include an identifier in the path, e.g. "/api/students/:id", never just "/api/students".
- Never generate a page/form with entity: null AND an empty fields list. If a page genuinely needs no entity (e.g. a delete confirmation), give it at least one field (e.g. the id field) or omit the page.
- Every page must have at least one component. Never leave "components" as an empty list.

Return ONLY the JSON object, nothing else.
"""


def generate_schemas(app_design_dict: dict) -> dict:
    user_prompt = f"Application design:\n{app_design_dict}"
    raw = call_llm_json(SYSTEM_PROMPT, user_prompt)

    required_keys = ["ui_schema", "api_schema", "db_schema", "auth_schema"]
    missing = [k for k in required_keys if k not in raw or raw[k] is None]

    if missing:
        # Targeted repair: ask the LLM specifically for the missing piece(s),
        # instead of crashing or regenerating everything from scratch.
        repair_prompt = f"""Your previous response was missing these required top-level keys: {missing}.
Application design:
{app_design_dict}

Return ONLY a JSON object containing the missing key(s): {missing}, in the exact shape
described in your instructions, consistent with any data already present here:
{raw}
"""
        fixed = call_llm_json(SYSTEM_PROMPT, repair_prompt)
        for key in missing:
            if key in fixed:
                raw[key] = fixed[key]

    # Re-check after attempted repair — if still missing, fail clearly (not a crash)
    still_missing = [k for k in required_keys if k not in raw or raw[k] is None]
    if still_missing:
        raise ValueError(f"Schema generation failed: missing keys after repair attempt: {still_missing}")

    # Validate each piece independently — if one fails, we know exactly which layer broke.
    # Wrapped in try/except so a bad field (e.g. entity: null) becomes a clean, typed
    # error instead of an unhandled crash.
    try:
        ui = UISchema(**raw["ui_schema"])
        api = APISchema(**raw["api_schema"])
        db = DBSchema(**raw["db_schema"])
        auth = AuthSchema(**raw["auth_schema"])
    except Exception as e:
        raise ValueError(f"Schema generation produced invalid structure: {e}")

    return {
        "ui_schema": ui,
        "api_schema": api,
        "db_schema": db,
        "auth_schema": auth,
        "raw": raw,
    }