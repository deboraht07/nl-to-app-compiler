from stages.llm_client import call_llm_json
from schemas.models import UISchema, APISchema, DBSchema, AuthSchema
from validator.cross_layer import validate_cross_layer, ValidationError
from typing import List


MAX_REPAIR_ATTEMPTS = 3


def group_errors_by_layer(errors: List[ValidationError]) -> dict:
    """Splits errors by which layer they belong to, so we only repair what's broken."""
    grouped = {"ui": [], "api": [], "db": [], "auth": []}
    for e in errors:
        grouped[e.layer].append(e)
    return grouped


def repair_layer(layer: str, current_value: dict, errors: List[ValidationError], full_schemas: dict) -> dict:
    """
    Asks the LLM to fix ONE specific layer, given the exact errors found.
    Returns the corrected dict for that layer only.
    """
    error_descriptions = "\n".join(f"- {e.message}" for e in errors)

    system_prompt = f"""You are a JSON repair engine. You will be given a broken JSON object
for the "{layer}" layer of an app schema, along with the specific validation errors found in it.

Fix ONLY the listed errors. Do not change anything else. Do not remove valid fields.
Return ONLY the corrected JSON object for this layer, in the exact same shape as the input.
"""

    user_prompt = f"""Broken {layer} schema:
{current_value}

Validation errors to fix:
{error_descriptions}

Context — full db_schema (for reference, to know valid entities/fields):
{full_schemas['db_schema'].model_dump()}

Context — full auth_schema (for reference, to know valid roles):
{full_schemas['auth_schema'].model_dump()}

Return the corrected {layer} schema as JSON.
"""

    return call_llm_json(system_prompt, user_prompt)


LAYER_MODELS = {
    "ui": UISchema,
    "api": APISchema,
    "db": DBSchema,
    "auth": AuthSchema,
}

LAYER_KEY = {
    "ui": "ui_schema",
    "api": "api_schema",
    "db": "db_schema",
    "auth": "auth_schema",
}


def validate_and_repair(schemas: dict, log: list = None) -> dict:
    """
    Main entry point. Validates cross-layer consistency.
    If broken, repairs ONLY the broken layers, re-validates, and retries
    up to MAX_REPAIR_ATTEMPTS times. Returns the final (hopefully fixed) schemas dict.

    `log` (optional list) gets appended with attempt records — used later for eval metrics.
    """
    if log is None:
        log = []

    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        errors = validate_cross_layer(schemas)

        if not errors:
            log.append({"attempt": attempt, "status": "success", "errors_found": 0})
            return schemas

        log.append({
            "attempt": attempt,
            "status": "errors_found",
            "errors_found": len(errors),
            "error_messages": [str(e) for e in errors],
        })

        broken_layers = group_errors_by_layer(errors)

        for layer, layer_errors in broken_layers.items():
            if not layer_errors:
                continue  # this layer is fine, skip it — this IS the "targeted" part

            key = LAYER_KEY[layer]
            current_value = schemas[key].model_dump()

            try:
                fixed_raw = repair_layer(layer, current_value, layer_errors, schemas)
                fixed_model = LAYER_MODELS[layer](**fixed_raw)
                schemas[key] = fixed_model  # only this layer gets replaced
            except Exception as e:
                log.append({"attempt": attempt, "status": "repair_failed", "layer": layer, "error": str(e)})

    # Ran out of attempts
    final_errors = validate_cross_layer(schemas)
    log.append({"status": "gave_up", "remaining_errors": len(final_errors)})
    return schemas