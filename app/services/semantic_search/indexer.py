from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.services.semantic_search.engine import add_documents, clear_index


def index_invoices_from_database(db: Session) -> dict:

    invoices = db.query(Invoice).order_by(Invoice.id).all()

    clear_index()

    if not invoices:
        return {
            "message": "No invoices found.",
            "documents_added": 0,
            "total_documents": 0
        }

    documents = []

    for invoice in invoices:

        text = (
            f"Invoice number {invoice.invoice_number}. "
            f"Vendor {invoice.vendor}. "
            f"Invoice date {invoice.invoice_date}. "
            f"Total amount {invoice.total_amount} "
            f"{invoice.currency}. "
            f"Purchase order {invoice.purchase_order}."
        )

        documents.append({
            "id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "purchase_order": invoice.purchase_order,
            "text": text
        })

    result = add_documents(documents)

    return {
        "message": "Invoice search index rebuilt successfully.",
        "documents_added": result["documents_added"],
        "total_documents": result["total_documents"]
    }