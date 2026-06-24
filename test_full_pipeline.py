from stages.intent_extraction import extract_intent
from stages.system_design import design_system
from stages.schema_generation import generate_schemas
from validator.cross_layer import validate_cross_layer
from validator.repair import validate_and_repair
from runtime.mock_data import generate_mock_data
from runtime.renderer import render_app

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

intent = extract_intent(prompt)
design = design_system(intent.model_dump())
schemas = generate_schemas(design.model_dump())

log = []
schemas = validate_and_repair(schemas, log)

mock_data = generate_mock_data(schemas["db_schema"])
html = render_app(schemas, mock_data)

with open("output_preview.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Done. Repair log:", log)
print("✅ Open output_preview.html in your browser to see the result.")