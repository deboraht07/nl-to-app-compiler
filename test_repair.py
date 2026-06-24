from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
from validator.cross_layer import validate_cross_layer
from validator.repair import validate_and_repair

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

intent = extract_intent(prompt)
design = design_system(intent.model_dump())
schemas = generate_schemas(design.model_dump())

# Inject the same 3 faults as before
schemas["ui_schema"].pages[2].components[0].fields.append("hallucinated_field")
schemas["api_schema"].endpoints[0].entity = "GhostEntity"
schemas["ui_schema"].pages[0].allowed_roles.append("SuperGod")

print("BEFORE REPAIR:")
errors_before = validate_cross_layer(schemas)
print(f"  {len(errors_before)} errors found")

log = []
repaired = validate_and_repair(schemas, log)

print("\nAFTER REPAIR:")
errors_after = validate_cross_layer(repaired)
print(f"  {len(errors_after)} errors remaining")

print("\nREPAIR LOG:")
for entry in log:
    print(" -", entry)
