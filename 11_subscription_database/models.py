from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    max_users = Column(Integer)

    subscriptions = relationship("Subscription", back_populates="plan")


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True)
    company_name = Column(String(100), nullable=False)
    subdomain = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="tenant")
    subscription = relationship("Subscription", back_populates="tenant", uselist=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), unique=True)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    status = Column(String(20), default="active")

    tenant = relationship("Tenant", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    name = Column(String(100))
    email = Column(String(100))
    password = Column(String(200))

    tenant = relationship("Tenant", back_populates="users")
