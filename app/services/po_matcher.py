
from sqlalchemy.orm import Session

from app.models.purchase_order import PurchaseOrder


def match_purchase_order(invoice: dict, db: Session) -> dict:
    po_number = invoice.get("purchase_order")

    if not po_number:
        return {
            "matched": False,
            "risk": "HIGH",
            "message": "Purchase order number is missing."
        }

    # Retrieve the purchase order from MySQL.
    purchase_order = db.query(PurchaseOrder).filter(
        PurchaseOrder.po_number.ilike(po_number.strip())
    ).first()

    if not purchase_order:
        return {
            "matched": False,
            "risk": "HIGH",
            "message": "Purchase order was not found."
        }

    # Check whether the vendor names match.
    invoice_vendor = (
        invoice.get("vendor") or ""
    ).strip().casefold()

    po_vendor = (
        purchase_order.vendor or ""
    ).strip().casefold()

    if invoice_vendor != po_vendor:
        return {
            "matched": False,
            "risk": "HIGH",
            "message": "Vendor name does not match the purchase order."
        }

    # Check whether the currencies match.
    invoice_currency = (
        invoice.get("currency") or ""
    ).strip().upper()

    po_currency = (
        purchase_order.currency or ""
    ).strip().upper()

    if invoice_currency != po_currency:
        return {
            "matched": False,
            "risk": "HIGH",
            "message": "Invoice currency does not match the purchase order."
        }

    # Validate the invoice amount.
    invoice_amount = invoice.get("total_amount")

    if invoice_amount is None:
        return {
            "matched": False,
            "risk": "HIGH",
            "message": "Invoice amount is missing."
        }

    try:
        invoice_amount = float(invoice_amount)
    except (ValueError, TypeError):
        return {
            "matched": False,
            "risk": "HIGH",
            "message": "Invoice amount is invalid."
        }

    po_amount = float(purchase_order.amount)

    # Compare invoice amount with purchase order amount.
    difference = round(invoice_amount - po_amount, 2)

    if difference != 0:
        return {
            "matched": False,
            "risk": "HIGH",
            "message": "Invoice amount does not match the purchase order.",
            "invoice_amount": invoice_amount,
            "po_amount": po_amount,
            "difference": difference
        }

    return {
        "matched": True,
        "risk": "LOW",
        "message": "Invoice successfully matched with purchase order.",
        "po_number": purchase_order.po_number,
        "matched_amount": invoice_amount
    }
