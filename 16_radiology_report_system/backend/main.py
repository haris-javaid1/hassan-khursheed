from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from models import Base
from database import engine

# Create FastAPI app
app = FastAPI(title="Radiology Report System")

# Auto create tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

# Enable CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Home route
@app.get("/")
def home():
    return {"message": "Radiology Report System API is running!"}