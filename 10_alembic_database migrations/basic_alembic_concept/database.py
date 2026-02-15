# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL
DATABASE_URL = "postgresql://postgres:%4012345@localhost/basic_alembic_db"

make_engine = create_engine(DATABASE_URL)

make_session = sessionmaker(autocommit=False, autoflush=False, bind=make_engine)

Base = declarative_base()


# Dependency to get DB session (used later in APIs)
def get_db():
    db = make_session()
    try:
        yield db
    finally:
        db.close()
