"""
Setup PostgreSQL Database
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def setup_database():
    """Create database and tables"""

    print("=" * 60)
    print("Payment Gateway - Database Setup")
    print("=" * 60)
    print()

    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='@12345',
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname='payment_gateway'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("CREATE DATABASE payment_gateway")
            print("✅ Database 'payment_gateway' created")
        else:
            print("✅ Database already exists")

        cursor.close()
        conn.close()

        print("\nCreating tables...")
        conn = psycopg2.connect(
            dbname='payment_gateway',
            user='postgres',
            password='@12345',
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                stripe_customer_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Users table created")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                amount DECIMAL(10, 2) NOT NULL,
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
        print("✅ Transactions table created")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("🎉 Database setup completed!")
        print("=" * 60)

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


setup_database()
