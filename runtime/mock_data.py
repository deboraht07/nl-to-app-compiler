import random

SAMPLE_NAMES = ["Alice Johnson", "Brian Lee", "Carla Mendez", "David Kim", "Elena Petrova"]


def generate_mock_data(db_schema) -> dict:
    """Creates a few fake rows per table, so the rendered UI looks alive, not empty."""
    mock = {}
    for table in db_schema.tables:
        rows = []
        for i in range(3):
            row = {}
            for field in table.fields:
                if field.name == "id":
                    row[field.name] = f"{table.name.lower()}_{i+1}"
                elif field.type == "string" and "name" in field.name.lower():
                    row[field.name] = random.choice(SAMPLE_NAMES)
                elif field.type == "string" and "email" in field.name.lower():
                    row[field.name] = f"user{i+1}@example.com"
                elif field.type == "number":
                    row[field.name] = round(random.uniform(10, 500), 2)
                elif field.type == "boolean":
                    row[field.name] = random.choice([True, False])
                elif field.type == "date":
                    row[field.name] = "2026-0" + str(random.randint(1, 6)) + "-1" + str(random.randint(0, 9))
                else:
                    row[field.name] = f"sample_{field.name}"
            rows.append(row)
        mock[table.name] = rows
    return mock