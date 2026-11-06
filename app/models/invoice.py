from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), nullable=False, index=True)
    vendor = Column(String(255), nullable=False)
    invoice_date = Column(String(50), nullable=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    purchase_order = Column(String(100), nullable=True)

    risk_level = Column(String(20), nullable=False, default="LOW")

    created_at = Column(DateTime(timezone=True), server_default=func.now())