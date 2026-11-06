
from app.database.connection import Base, engine, SessionLocal

from app.models.invoice import Invoice
from app.models.purchase_order import PurchaseOrder


PURCHASE_ORDERS = [
    {
        "po_number": "PO-5001",
        "vendor": "ABC Office Supplies",
        "amount": 12000.0,
        "currency": "INR"
    },
    {
        "po_number": "PO-5002",
        "vendor": "XYZ Technologies",
        "amount": 25000.0,
        "currency": "INR"
    },
    {
        "po_number": "PO-5003",
        "vendor": "Global Traders",
        "amount": 18000.0,
        "currency": "INR"
    }
]


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def seed_purchase_orders():
    db = SessionLocal()

    try:
        for po_data in PURCHASE_ORDERS:
            existing_po = db.query(PurchaseOrder).filter(
                PurchaseOrder.po_number == po_data["po_number"]
            ).first()

            if existing_po:
                print(
                    f"{po_data['po_number']} already exists. Skipping."
                )
                continue

            new_po = PurchaseOrder(**po_data)

            db.add(new_po)

            print(
                f"{po_data['po_number']} inserted successfully."
            )

        db.commit()
        print("Purchase order initialization completed!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed_purchase_orders()
