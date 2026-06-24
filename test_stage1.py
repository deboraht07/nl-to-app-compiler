from stages.intent_extraction import extract_intent

prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."

result = extract_intent(prompt)
print(result.model_dump_json(indent=2))