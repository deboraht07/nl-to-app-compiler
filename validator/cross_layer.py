from typing import List


class ValidationError:
    """A single, specific, machine-actionable validation failure."""
    def __init__(self, layer: str, message: str, path: str = ""):
        self.layer = layer       # which layer broke: "ui", "api", "db", "auth"
        self.message = message
        self.path = path         # e.g. "ui_schema.pages[2].components[0]"

    def __repr__(self):
        return f"[{self.layer}] {self.message} (at {self.path})"


def validate_cross_layer(schemas: dict) -> List[ValidationError]:
    """
    Checks consistency ACROSS layers — things Pydantic alone can't catch:
    - every entity referenced in UI/API exists in DB
    - every field referenced in UI exists on that entity in DB
    - every role referenced in UI/API exists in Auth
    Returns a list of errors. Empty list = fully consistent.
    """
    errors: List[ValidationError] = []

    ui = schemas["ui_schema"]
    api = schemas["api_schema"]
    db = schemas["db_schema"]
    auth = schemas["auth_schema"]

    db_tables = {t.name: {f.name for f in t.fields} for t in db.tables}
    valid_roles = set(auth.roles)

    # --- UI checks ---
    for p_idx, page in enumerate(ui.pages):
        if len(page.components) == 0:
            errors.append(ValidationError(
                "ui", f"page '{page.name}' has no components — nothing would render",
                f"ui_schema.pages[{p_idx}]"
            ))
        for c_idx, comp in enumerate(page.components):
            path = f"ui_schema.pages[{p_idx}].components[{c_idx}]"

            if comp.entity is not None:
                if comp.entity not in db_tables:
                    errors.append(ValidationError(
                        "ui", f"references unknown entity '{comp.entity}' not found in db_schema", path
                    ))
                else:
                    valid_fields = db_tables[comp.entity]
                    for field in comp.fields:
                        if field not in valid_fields:
                            errors.append(ValidationError(
                                "ui", f"field '{field}' not found on entity '{comp.entity}' in db_schema", path
                            ))

        for role in page.allowed_roles:
            if role not in valid_roles:
                errors.append(ValidationError(
                    "ui", f"page '{page.name}' allows unknown role '{role}' not in auth_schema",
                    f"ui_schema.pages[{p_idx}]"
                ))

    # --- API checks ---
    for e_idx, endpoint in enumerate(api.endpoints):
        path = f"api_schema.endpoints[{e_idx}]"
        if endpoint.entity not in db_tables:
            errors.append(ValidationError(
                "api", f"endpoint '{endpoint.path}' references unknown entity '{endpoint.entity}'", path
            ))
        for role in endpoint.allowed_roles:
            if role not in valid_roles:
                errors.append(ValidationError(
                    "api", f"endpoint '{endpoint.path}' allows unknown role '{role}'", path
                ))

    # --- Auth checks ---
    page_names = {page.name for page in ui.pages}
    for perm in auth.permissions:
        for page_name in perm.can_access:
            if page_name not in page_names:
                errors.append(ValidationError(
                    "auth", f"role '{perm.role}' grants access to unknown page '{page_name}'",
                    "auth_schema.permissions"
                ))

    return errors