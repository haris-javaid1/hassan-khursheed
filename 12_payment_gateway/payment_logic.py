from datetime import datetime
from fastapi import HTTPException
from models import PaymentRequest, PaymentResponse
from database import Database
from stripe_service import StripeService
from config import CURRENCY


class PaymentProcessor:
    def __init__(self):
        self.db = Database()
        self.stripe = StripeService()

    def process_payment(self, payment: PaymentRequest) -> PaymentResponse:
        if payment.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be greater than zero"
            )

        user = self.db.get_user(payment.user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if not user["stripe_customer_id"]:
            customer_id = self.stripe.create_customer(
                email=user["email"],
                name=user["username"]
            )
            self.db.update_user_stripe_id(payment.user_id, customer_id)
        else:
            customer_id = user["stripe_customer_id"]

        result = self.stripe.charge_with_token(
            amount=payment.amount,
            customer_id=customer_id,
            token=payment.stripe_token,
            description=payment.description,
        )

        transaction_id = self.db.save_transaction(
            user_id=payment.user_id,
            amount=payment.amount,
            currency=CURRENCY,
            stripe_charge_id=result["charge_id"],
            card_last4=result["card_last4"],
            card_brand=result["card_brand"],
            status="SUCCESS" if result["success"] else "FAILED",
            description=payment.description,
            error_message=result["error_message"],
        )

        return PaymentResponse(
            transaction_id=transaction_id,
            status="SUCCESS" if result["success"] else "FAILED",
            message="Payment successful" if result["success"] else result["error_message"],
            stripe_charge_id=result["charge_id"],
            amount=payment.amount,
            timestamp=datetime.utcnow().isoformat(),
        )
