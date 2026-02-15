from fastapi import FastAPI
from database import Base, engine
from routes import router
from seed import seed_plans

app = FastAPI(title="Multi-Tenant Subscription API")

# Create tables and seed plans
Base.metadata.create_all(bind=engine)
seed_plans()


@app.get("/")
def root():
    return {"message": "API running successfully"}

# Include all routes from router
app.include_router(router, prefix="")  # empty prefix is fine

