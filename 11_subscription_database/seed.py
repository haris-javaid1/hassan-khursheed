from database import SessionLocal
from models import Plan


def seed_plans():
    db = SessionLocal()

    if db.query(Plan).count() == 0:
        plans = [
            Plan(name="Free", price=0, max_users=3),
            Plan(name="Pro", price=29.99, max_users=10),
        ]
        db.add_all(plans)
        db.commit()

    db.close()
