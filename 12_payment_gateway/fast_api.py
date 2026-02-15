from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import PaymentRequest, PaymentResponse
from payment_logic import PaymentProcessor
from database import Database
from config import STRIPE_PUBLISHABLE_KEY, STRIPE_TEST_TOKENS

app = FastAPI(title="Payment Gateway API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
payment_processor = PaymentProcessor()


@app.on_event("startup")
def startup():
    db.create_tables()


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/api/config")
def get_config():
    return {
        "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY,
        "test_tokens": STRIPE_TEST_TOKENS,
    }


@app.post("/api/payment/process", response_model=PaymentResponse)
def process_payment(payment: PaymentRequest):
    return payment_processor.process_payment(payment)


@app.get("/api/transactions/{user_id}")
def get_user_transactions(user_id: int):
    return {"transactions": db.get_user_transactions(user_id)}


@app.get("/api/transaction/{transaction_id}")
def get_transaction(transaction_id: int):
    transaction = db.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.get("/health")
def health():
    return {"status": "healthy"}
