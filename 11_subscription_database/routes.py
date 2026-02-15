from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import TenantCreate, UserCreate
from crud import create_tenant as crud_create_tenant, create_user, get_plans

router = APIRouter()


# list all plans
@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    return get_plans(db)



# create tenant endpoint
@router.post("/tenants")
def create_tenant_api(
    data: TenantCreate,
    db: Session = Depends(get_db)
):
    return crud_create_tenant(
        db,
        data.company_name,
        data.subdomain,
        data.plan_id
    )


# create user endpoint
@router.post("/users")
def create_user_api(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_user(
            db,
            data.tenant_id,
            data.name,
            data.email,
            data.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

