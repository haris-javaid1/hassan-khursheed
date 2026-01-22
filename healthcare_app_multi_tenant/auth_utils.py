from passlib.context import CryptContext

# cryptcontext - to use in password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# password hashing
def hash_password(password: str):
    return pwd_context.hash(password)

# password verification
def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)
