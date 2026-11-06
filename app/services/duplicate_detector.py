
from sqlalchemy.orm import Session

from app.models.invoice import Invoice


def check_duplicate(invoice: dict, db: Session) -> dict:
    invoice_number = (
        invoice.get("invoice_number") or ""
    ).strip().casefold()

    vendor = (
        invoice.get("vendor") or ""
    ).strip().casefold()

    amount = invoice.get("total_amount")

    if not invoice_number or not vendor or amount is None:
        return {
            "is_duplicate": False,
            "message": (
                "Insufficient invoice information "
                "for duplicate detection."
            )
        }

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return {
            "is_duplicate": False,
            "message": "Invalid invoice amount."
        }

    existing_invoice = db.query(Invoice).filter(
        Invoice.invoice_number.ilike(invoice_number),
        Invoice.vendor.ilike(vendor),
        Invoice.total_amount == amount
    ).first()

    if existing_invoice:
        return {
            "is_duplicate": True,
            "message": "This invoice appears to have been uploaded before.",
            "matched_invoice_number": existing_invoice.invoice_number
        }

    return {
        "is_duplicate": False,
        "message": "No matching invoice was found."
    }

def save_invoice_record(invoice: dict, db: Session) -> None:
    try:
        new_invoice = Invoice(
            invoice_number=invoice.get("invoice_number"),
            vendor=invoice.get("vendor"),
            invoice_date=invoice.get("invoice_date"),
            total_amount=float(invoice.get("total_amount")),
            currency=invoice.get("currency"),
            purchase_order=invoice.get("purchase_order"),
            risk_level=invoice.get("risk_level", "LOW")
        )

        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)

    except Exception:
        db.rollback()
        raise