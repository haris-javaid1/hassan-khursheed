"""
Streamlit Frontend for Payment Gateway
Uses Stripe test tokens (SAFE - no raw card input)
Refund feature REMOVED (payment-only learning version)
"""

import streamlit as st
import requests
from database import Database
from config import API_BASE_URL

# Page config
st.set_page_config(
    page_title="Payment Gateway - Stripe",
    layout="wide"
)

# Initialize database
db = Database()


def init_session():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None


def login_user(username: str, email: str):
    try:
        user_id = db.create_user(username, email)
        st.session_state.user_id = user_id
        st.session_state.username = username
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def process_payment(payment_data: dict):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/payment/process",
            json=payment_data,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        error = response.json().get("detail", "Unknown error")
        return {"status": "FAILED", "message": error}

    except requests.exceptions.ConnectionError:
        return {
            "status": "FAILED",
            "message": "Backend not running. Start: uvicorn fast_api:app --reload"
        }
    except Exception as e:
        return {"status": "FAILED", "message": str(e)}


def get_transactions(user_id: int):
    try:
        response = requests.get(f"{API_BASE_URL}/api/transactions/{user_id}")
        if response.status_code == 200:
            return response.json().get("transactions", [])
        return []
    except Exception:
        return []


def show_login():
    st.title("Payment Gateway with Stripe")

    st.subheader("Login here!")
    username = st.text_input("Username")
    email = st.text_input("Email")

    if st.button("Login", type="primary", use_container_width=True):
        if username and email:
            if login_user(username, email):
                st.success("Login successful!")
                st.rerun()
        else:
            st.warning("Please enter username and email")


def show_payment_page():
    st.title(f"Welcome, {st.session_state.username}")

    # ---------------- SIDEBAR PROFILE ----------------
    with st.sidebar:
        st.subheader("Profile")
        st.write(f"**Username:** {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

    tab1, tab2 = st.tabs(["Make Payment", "Transaction History"])

    # ---------------- PAYMENT TAB ----------------
    with tab1:
        st.subheader("Make a Payment")

        amount = st.number_input(
            "Amount (USD)",
            min_value=0.50,
            value=50.00,
            step=1.00
        )

        description = st.text_area("Description (optional)")

        token_options = {
            "Visa Success": "tok_visa",
            "Mastercard Success": "tok_mastercard",
            "Amex Success": "tok_amex",
            "Card Declined": "tok_chargeDeclined",
            "Insufficient Funds": "tok_chargeDeclinedInsufficientFunds"
        }

        scenario = st.selectbox("Payment Scenario", list(token_options.keys()))
        selected_token = token_options[scenario]

        st.markdown("**Stripe Test Token**")
        st.code(selected_token)

        if st.button("Pay Now", type="primary", use_container_width=True):
            payment_data = {
                "user_id": st.session_state.user_id,
                "amount": amount,
                "stripe_token": selected_token,
                "description": description or None
            }

            with st.spinner("Processing payment..."):
                result = process_payment(payment_data)

            if result.get("status") == "SUCCESS":
                st.success("Payment Successful 🎉")
                st.write(f"**Transaction ID:** {result.get('transaction_id')}")
                st.write(f"**Amount:** ${amount:.2f}")
                st.write(f"**Stripe Charge ID:** {result.get('stripe_charge_id')}")
                st.balloons()
            else:
                st.error(f"Payment Failed: {result.get('message')}")

    # ---------------- HISTORY TAB ----------------
    with tab2:
        st.subheader("Transaction History")

        transactions = get_transactions(st.session_state.user_id)

        if not transactions:
            st.info("No transactions yet.")
            return

        for txn in transactions:
            icon = "✅" if txn["status"] == "SUCCESS" else "❌"

            with st.expander(
                f"{icon} Transaction #{txn['transaction_id']} - ${txn['amount']:.2f}"
            ):
                st.write(f"**Status:** {txn['status']}")
                st.write(f"**Amount:** ${txn['amount']:.2f}")
                st.write(f"**Date:** {txn['created_at']}")

                if txn.get("stripe_charge_id"):
                    st.write(f"**Stripe Charge ID:** {txn['stripe_charge_id']}")

                if txn.get("description"):
                    st.write(f"**Description:** {txn['description']}")

                if txn.get("error_message"):
                    st.error(txn["error_message"])


def main():
    init_session()

    try:
        requests.get(f"{API_BASE_URL}/health", timeout=2)
    except Exception:
        st.error("Backend not running. Start with: uvicorn fast_api:app --reload")
        return

    if st.session_state.user_id is None:
        show_login()
    else:
        show_payment_page()


main()
