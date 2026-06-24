from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
from validator.cross_layer import validate_cross_layer

# A vaguer, messier prompt — more likely to produce inconsistency
prompt = "Make an app for managing events with tickets, organizers, attendees, refunds, and some kind of notifications, maybe with different access levels"

intent = extract_intent(prompt)
print("=== INTENT ===")
print(intent.model_dump_json(indent=2))

design = design_system(intent.model_dump())
print("\n=== DESIGN ===")
print(design.model_dump_json(indent=2))

schemas = generate_schemas(design.model_dump())
errors = validate_cross_layer(schemas)

if not errors:
    print("\n✅ No cross-layer errors found.")
else:
    print(f"\n❌ Found {len(errors)} errors:")
    for e in errors:
        print(" -", e)