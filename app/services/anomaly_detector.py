
from sklearn.ensemble import IsolationForest

from app.models.invoice import Invoice


MIN_RECORDS_FOR_ML = 5


def detect_amount_anomalies(db):
    # Fetch actual uploaded invoices from the database.
    invoices = (
        db.query(Invoice)
        .order_by(Invoice.id.asc())
        .all()
    )

    results = []

    for invoice in invoices:
        results.append({
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "total_amount": float(invoice.total_amount or 0),
            "currency": invoice.currency or "INR",
            "is_anomaly": False,
            "status_label": "NOT_EVALUATED",
            "anomaly_score": None
        })

    total_records = len(results)

    # No invoices in the database.
    if total_records == 0:
        return {
            "algorithm": "Isolation Forest",
            "records_analyzed": 0,
            "anomalies_found": 0,
            "status": "no_data",
            "message": "No uploaded invoices found.",
            "results": []
        }

    # Too few invoices for meaningful ML analysis.
    if total_records < MIN_RECORDS_FOR_ML:
        return {
            "algorithm": "Isolation Forest",
            "records_analyzed": total_records,
            "anomalies_found": 0,
            "status": "insufficient_data",
            "message": (
                f"At least {MIN_RECORDS_FOR_ML} invoices are required "
                "for this basic ML analysis. "
                "Current invoices have not been classified."
            ),
            "results": results
        }

    # Prepare actual database invoice amounts.
    amounts = [[invoice["total_amount"]] for invoice in results]

    model = IsolationForest(
        n_estimators=100,
        contamination=0.10,
        random_state=42
    )

    predictions = model.fit_predict(amounts)
    scores = model.decision_function(amounts)

    anomalies_found = 0

    for index, invoice in enumerate(results):
        is_anomaly = predictions[index] == -1

        invoice["is_anomaly"] = bool(is_anomaly)
        invoice["status_label"] = (
            "ANOMALY" if is_anomaly else "NORMAL"
        )
        invoice["anomaly_score"] = float(scores[index])

        if is_anomaly:
            anomalies_found += 1

    return {
        "algorithm": "Isolation Forest",
        "records_analyzed": total_records,
        "anomalies_found": anomalies_found,
        "status": "completed",
        "message": "Anomaly detection completed successfully.",
        "results": results
    }
