from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    user_id: Optional[int]
    username: str
    email: EmailStr
    stripe_customer_id: Optional[str]
    created_at: Optional[datetime]


class PaymentRequest(BaseModel):
    user_id: int
    amount: float
    stripe_token: str
    description: Optional[str]


class PaymentResponse(BaseModel):
    transaction_id: int
    status: str
    message: str
    stripe_charge_id: Optional[str]
    amount: float
    timestamp: str
