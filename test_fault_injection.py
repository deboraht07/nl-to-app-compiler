from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
from validator.cross_layer import validate_cross_layer
import copy

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

intent = extract_intent(prompt)
design = design_system(intent.model_dump())
schemas = generate_schemas(design.model_dump())

# --- INJECT FAULTS ON PURPOSE ---
# Fault 1: UI references a field that doesn't exist in DB
schemas["ui_schema"].pages[2].components[0].fields.append("hallucinated_field")

# Fault 2: API endpoint references an entity that doesn't exist
schemas["api_schema"].endpoints[0].entity = "GhostEntity"

# Fault 3: A page allows a role that doesn't exist in auth_schema
schemas["ui_schema"].pages[0].allowed_roles.append("SuperGod")

errors = validate_cross_layer(schemas)

print(f"❌ Found {len(errors)} errors (expected 3):")
for e in errors:
    print(" -", e)