from pydantic import BaseModel
from typing import List, Optional


# ============================================================
# STAGE 1 OUTPUT: Intent Extraction
# ============================================================
class IntentIR(BaseModel):
    """Structured form of what the user wants, extracted from natural language."""
    app_name: str
    entities: List[str]          # e.g. ["Contact", "Deal", "User"]
    roles: List[str]             # e.g. ["Admin", "User"]
    features: List[str]          # e.g. ["login", "dashboard", "payments"]
    has_payments: bool
    assumptions: List[str]       # things we guessed because the prompt was vague


# ============================================================
# STAGE 2 OUTPUT: System Design
# ============================================================
class EntityField(BaseModel):
    name: str
    type: str                    # "string" | "number" | "boolean" | "date" | "relation"
    required: bool


class EntityDesign(BaseModel):
    name: str
    fields: List[EntityField]


class RolePermission(BaseModel):
    role: str
    can_access: List[str]        # list of page/feature names this role can see


class AppDesign(BaseModel):
    app_name: str
    entities: List[EntityDesign]
    roles: List[RolePermission]
    pages: List[str]             # e.g. ["Login", "Dashboard", "Contacts", "Billing"]


# ============================================================
# STAGE 3 OUTPUTS: UI / API / DB / Auth Schemas
# ============================================================
class UIComponent(BaseModel):
    type: str                    # "table" | "form" | "card" | "chart"
    entity: Optional[str] = None
    fields: List[str] = []


class UIPage(BaseModel):
    name: str
    route: str
    components: List[UIComponent]
    allowed_roles: List[str]


class UISchema(BaseModel):
    pages: List[UIPage]


class APIEndpoint(BaseModel):
    path: str
    method: str                  # "GET" | "POST" | "PUT" | "DELETE"
    entity: str
    allowed_roles: List[str]


class APISchema(BaseModel):
    endpoints: List[APIEndpoint]


class DBTable(BaseModel):
    name: str
    fields: List[EntityField]


class DBSchema(BaseModel):
    tables: List[DBTable]


class AuthSchema(BaseModel):
    roles: List[str]
    permissions: List[RolePermission]


# ============================================================
# FINAL COMBINED OUTPUT
# ============================================================
class FullAppSchema(BaseModel):
    app_design: AppDesign
    ui_schema: UISchema
    api_schema: APISchema
    db_schema: DBSchema
    auth_schema: AuthSchema