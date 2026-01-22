from models import Tenant, User
from auth_utils import hash_password, verify_password

# admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def admin_login(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def create_tenant(db, name, subdomain, username, password):
    existing = db.query(Tenant).filter(Tenant.username == username).first()
    if existing:
        return None
    
    tenant = Tenant(
        name=name,
        subdomain=subdomain,
        username=username,
        password_hash=hash_password(password)
    )
    db.add(tenant)
    db.commit()
    return tenant

def get_all_tenants(db):
    return db.query(Tenant).all()


# tenant credentials verification
def tenant_login(db, username, password):
    tenant = db.query(Tenant).filter(Tenant.username == username).first()
    if tenant and verify_password(password, tenant.password_hash):
        return tenant
    return None


def create_user(db, name, username, password, role, tenant_id):
    user = User(
        name=name,
        username=username,
        password_hash=hash_password(password),
        role=role,
        tenant_id=tenant_id
    )
    db.add(user)
    db.commit()
    return user

def get_users(db, tenant_id):
    # Ensure users are always returned in the same order
    return db.query(User).filter(User.tenant_id == tenant_id).order_by(User.id.asc()).all()

def get_user_by_username(db, username, tenant_id):
    return db.query(User).filter(
        User.username == username,
        User.tenant_id == tenant_id
    ).first()

def update_user_role(db, user_id, tenant_id, new_role):
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()
    if not user:
        return None
    user.role = new_role
    db.commit()
    return user
