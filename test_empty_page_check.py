from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
from validator.cross_layer import validate_cross_layer
from validator.repair import validate_and_repair

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

intent = extract_intent(prompt)
design = design_system(intent.model_dump())
schemas = generate_schemas(design.model_dump())

errors = validate_cross_layer(schemas)
print(f"Errors found: {len(errors)}")
for e in errors:
    print(" -", e)

if errors:
    print("\nRunning repair...")
    log = []
    schemas = validate_and_repair(schemas, log)
    print("Repair log:", log)
    final_errors = validate_cross_layer(schemas)
    print(f"\nErrors after repair: {len(final_errors)}")