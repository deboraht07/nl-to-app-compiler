from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
import json

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

intent = extract_intent(prompt)
design = design_system(intent.model_dump())
schemas = generate_schemas(design.model_dump())

print("=== UI SCHEMA ===")
print(schemas["ui_schema"].model_dump_json(indent=2))
print("\n=== API SCHEMA ===")
print(schemas["api_schema"].model_dump_json(indent=2))
print("\n=== DB SCHEMA ===")
print(schemas["db_schema"].model_dump_json(indent=2))
print("\n=== AUTH SCHEMA ===")
print(schemas["auth_schema"].model_dump_json(indent=2))