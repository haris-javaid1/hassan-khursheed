"""
Configuration for Payment Gateway with Stripe
"""

# STRIPE_SECRET_KEY = "sk_test_51Suv7kGeI2OTInqlrtskUM509Iljdzqxn7DDUxdmIuBraK0hNoD5CoqlZHdkfwo1evkdgSOy5QWEHaddshjPD1WI00P9KVQXzf"
# STRIPE_PUBLISHABLE_KEY = "pk_test_51Suv7kGeI2OTInqlEM5xwTeo0ap4tF2QOMnhgbRaDuscsJNFcz3mRoKnTAXc4tZDkSafpyaOYknbv8rzNg6TdfSp00JCflIpja"

DB_CONFIG = {
    "dbname": "payment_gateway",
    "user": "postgres",
    "password": "@12345",
    "host": "localhost",
    "port": "5432",
}

API_BASE_URL = "http://127.0.0.1:8000"
CURRENCY = "usd"

STRIPE_TEST_TOKENS = {
    "visa_success": "tok_visa",
    "visa_declined": "tok_chargeDeclined",
    "insufficient_funds": "tok_chargeDeclinedInsufficientFunds",
    "mastercard": "tok_mastercard",
    "amex": "tok_amex",
}
