
import re


def extract_invoice_fields(text: str) -> dict:
    patterns = {
        "invoice_number": (
            r"Invoice\s*(?:Number|No\.?|#)?\s*:\s*([A-Z0-9/-]+)"
        ),
        "vendor": r"Vendor\s*:\s*(.+)",
        "invoice_date": r"Invoice\s*Date\s*:\s*(\d{4}-\d{2}-\d{2})",
        "total_amount": r"Total\s*Amount\s*:\s*([\d,]+(?:\.\d{1,2})?)",
        "currency": r"Currency\s*:\s*([A-Z]{3})",
        "purchase_order": r"Purchase\s*Order\s*:\s*([A-Z0-9/-]+)",
    }

    result = {}

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            result[field] = match.group(1).strip()
        else:
            result[field] = None

    amount = result["total_amount"]

    if amount is not None:
        try:
            result["total_amount"] = float(amount.replace(",", ""))
        except ValueError:
            result["total_amount"] = None

    return result
