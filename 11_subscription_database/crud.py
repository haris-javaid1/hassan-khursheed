from sqlalchemy.orm import Session
from models import Tenant, Subscription, User, Plan


# plan
def get_plans(db: Session):
    return db.query(Plan).all()


# tenant
def create_tenant(db: Session, company_name: str, subdomain: str, plan_id: int):
    tenant = Tenant(
        company_name=company_name,
        subdomain=subdomain
    )
    db.add(tenant)
    db.flush()

    subscription = Subscription(tenant_id=tenant.id, plan_id=plan_id)
    db.add(subscription)

    db.commit()
    return tenant

# user
def create_user(
    db: Session,
    tenant_id: int,
    name: str,
    email: str,
    password: str
):
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == tenant_id
    ).first()

    if subscription and subscription.plan.max_users:
        count = db.query(User).filter(
            User.tenant_id == tenant_id
        ).count()

        if count >= subscription.plan.max_users:
            raise ValueError("User limit reached")

    user = User(
        tenant_id=tenant_id,
        name=name,
        email=email,
        password=password
    )
    db.add(user)
    db.commit()
    return user
