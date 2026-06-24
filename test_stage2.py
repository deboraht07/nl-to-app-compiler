from stages.intent_extraction import extract_intent
from stages.system_design import design_system

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

intent = extract_intent(prompt)
print("=== INTENT ===")
print(intent.model_dump_json(indent=2))

design = design_system(intent.model_dump())
print("\n=== DESIGN ===")
print(design.model_dump_json(indent=2))
