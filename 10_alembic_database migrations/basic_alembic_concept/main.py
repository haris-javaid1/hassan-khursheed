from fastapi import FastAPI
from database import make_engine
from models import Base

app = FastAPI(title="Basic Alembic Learning Project")

# Create all tables in the database that don't already exist
Base.metadata.create_all(bind=make_engine)


@app.get("/")
def root():
    return {"message": "running"}
