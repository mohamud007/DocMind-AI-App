
def validate_invoice(invoice: dict) -> dict:
    issues = []

    required_fields = {
        "invoice_number": "Invoice number",
        "vendor": "Vendor name",
        "invoice_date": "Invoice date",
        "total_amount": "Total amount",
        "purchase_order": "Purchase order number"
    }

    # Check for missing invoice information
    for field, label in required_fields.items():
        value = invoice.get(field)

        if value is None or str(value).strip() == "":
            issues.append({
                "type": "missing_field",
                "field": field,
                "message": f"{label} is missing."
            })

    # Check whether invoice amount is valid
    amount = invoice.get("total_amount")

    if amount is not None:
        try:
            amount = float(amount)

            if amount <= 0:
                issues.append({
                    "type": "invalid_amount",
                    "field": "total_amount",
                    "message": "Invoice amount must be greater than zero."
                })

        except (ValueError, TypeError):
            issues.append({
                "type": "invalid_amount",
                "field": "total_amount",
                "message": "Invoice amount is not a valid number."
            })

    # Determine risk level
    if any(issue["type"] == "invalid_amount" for issue in issues):
        risk_level = "HIGH"
    elif len(issues) >= 3:
        risk_level = "HIGH"
    elif len(issues) > 0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "is_valid": len(issues) == 0,
        "risk_level": risk_level,
        "issue_count": len(issues),
        "issues": issues
    }
