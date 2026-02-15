import stripe
from typing import Dict
from config import STRIPE_SECRET_KEY, CURRENCY

stripe.api_key = STRIPE_SECRET_KEY


class StripeService:
    def create_customer(self, email: str, name: str) -> str:
        customer = stripe.Customer.create(email=email, name=name)
        return customer.id

    def charge_with_token(self, amount: float, customer_id: str,
                          token: str, description: str) -> Dict:
        try:
            # Attach token to customer first
            stripe.Customer.create_source(
                customer_id,
                source=token
            )

            # Charge customer (NO source here)
            charge = stripe.Charge.create(
                amount=int(amount * 100),
                currency=CURRENCY,
                customer=customer_id,
                description=description,
            )

            # Some fields might be None, so use getattr safely
            return {
                "success": charge.paid,
                "charge_id": charge.id,
                "card_last4": getattr(charge.source, "last4", "XXXX"),
                "card_brand": getattr(charge.source, "brand", "card"),
                "error_message": None,
            }

        except stripe.error.CardError as e:
            return {
                "success": False,
                "charge_id": None,
                "card_last4": "XXXX",
                "card_brand": "card",
                "error_message": e.user_message,
            }
