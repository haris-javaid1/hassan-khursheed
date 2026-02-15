from pydantic import BaseModel


class TenantCreate(BaseModel):
    company_name: str
    subdomain: str
    plan_id: int


class UserCreate(BaseModel):
    tenant_id: int
    name: str
    email: str
    password: str


class PlanResponse(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        orm_mode = True
