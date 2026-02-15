"""
Database operations for PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
from config import DB_CONFIG


class Database:
    def get_connection(self):
        return psycopg2.connect(**DB_CONFIG)

    def create_tables(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        stripe_customer_id VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(user_id),
                        amount DECIMAL(10,2) NOT NULL,
                        currency VARCHAR(10) NOT NULL,
                        stripe_charge_id VARCHAR(100),
                        card_last4 VARCHAR(4),
                        card_brand VARCHAR(20),
                        status VARCHAR(20) NOT NULL,
                        description TEXT,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

    def create_user(self, username: str, email: str, stripe_customer_id: str = None) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        """
                        INSERT INTO users (username, email, stripe_customer_id)
                        VALUES (%s, %s, %s)
                        RETURNING user_id
                        """,
                        (username, email, stripe_customer_id),
                    )
                    return cursor.fetchone()[0]
                except psycopg2.IntegrityError:
                    conn.rollback()
                    cursor.execute(
                        "SELECT user_id FROM users WHERE email = %s", (email,)
                    )
                    return cursor.fetchone()[0]

    def get_user(self, user_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                return cursor.fetchone()

    def update_user_stripe_id(self, user_id: int, stripe_customer_id: str):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET stripe_customer_id = %s WHERE user_id = %s",
                    (stripe_customer_id, user_id),
                )

    def save_transaction(self, **kwargs) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO transactions (
                        user_id, amount, currency, stripe_charge_id,
                        card_last4, card_brand, status, description, error_message
                    )
                    VALUES (%(user_id)s, %(amount)s, %(currency)s,
                            %(stripe_charge_id)s, %(card_last4)s,
                            %(card_brand)s, %(status)s,
                            %(description)s, %(error_message)s)
                    RETURNING transaction_id
                    """,
                    kwargs,
                )
                return cursor.fetchone()[0]

    def get_transaction(self, transaction_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT t.*, u.username, u.email
                    FROM transactions t
                    JOIN users u ON t.user_id = u.user_id
                    WHERE t.transaction_id = %s
                    """,
                    (transaction_id,),
                )
                return cursor.fetchone()

    def get_user_transactions(self, user_id: int) -> List[Dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM transactions WHERE user_id = %s ORDER BY created_at DESC",
                    (user_id,),
                )
                return cursor.fetchall()
