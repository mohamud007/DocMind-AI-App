
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database.connection import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)

    po_number = Column(String(100), unique=True, nullable=False, index=True)

    vendor = Column(String(255), nullable=False)

    amount = Column(Float, nullable=False)

    currency = Column(String(10), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
