from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
from validator.cross_layer import validate_cross_layer

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

intent = extract_intent(prompt)
design = design_system(intent.model_dump())
schemas = generate_schemas(design.model_dump())

errors = validate_cross_layer(schemas)

if not errors:
    print("✅ No cross-layer errors found.")
else:
    print(f"❌ Found {len(errors)} errors:")
    for e in errors:
        print(" -", e)