
from collections import Counter
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.database.connection import SessionLocal, get_db
from app.routers.search import router as search_router
from app.routers.rag import router as rag_router

from app.services.document_processor import (
    extract_text,
    save_uploaded_document,
)
from app.services.invoice_extractor import extract_invoice_fields
from app.services.invoice_validator import validate_invoice
from app.services.duplicate_detector import (
    check_duplicate,
    save_invoice_record,
)
from app.services.po_matcher import match_purchase_order
from app.services.anomaly_detector import detect_amount_anomalies
from app.services.semantic_search.indexer import (
    index_invoices_from_database
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Building semantic search index...")

    db = SessionLocal()
    try:
        result = index_invoices_from_database(db)
        print("Semantic search index initialized!")
        print(result)
    finally:
        db.close()

    yield
    print("DocuMind AI application shutting down.")


app = FastAPI(
    title="DocuMind AI",
    description="Intelligent Document Processing & Risk Detection",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(search_router)
app.include_router(rag_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("static/index.html")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/invoices")
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.id.desc()).all()

    invoice_list = []

    for invoice in invoices:
        invoice_data = {
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "invoice_date": invoice.invoice_date,
            "total_amount": invoice.total_amount,
            "currency": invoice.currency,
            "purchase_order": invoice.purchase_order
        }

        validation = validate_invoice(invoice_data)
        po_result = match_purchase_order(invoice_data, db)

        risk = validation["risk_level"]

        if po_result["risk"] == "HIGH":
            risk = "HIGH"

        risk_details = []

        if validation.get("issues"):
            for issue in validation["issues"]:
                risk_details.append(issue["message"])

        if po_result["risk"] == "HIGH":
            risk_details.append(po_result["message"])

            if "difference" in po_result:
                risk_details.append(
                    f"Amount difference: {invoice.currency} "
                    f"{po_result['difference']}"
                )

        if not risk_details:
            risk_details.append(
                "No validation or purchase order mismatch detected."
            )

        invoice_list.append({
            **invoice_data,
            "risk_level": risk,
            "risk_details": risk_details,
            "po_amount": po_result.get("po_amount"),
            "po_matched": po_result["matched"]
        })

    return {
        "total_invoices": len(invoice_list),
        "invoices": invoice_list
    }


@app.get("/risk-summary")
def get_risk_summary(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()

    counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    for invoice in invoices:
        risk = (invoice.risk_level or "LOW").upper()

        if risk not in counts:
            risk = "MEDIUM"

        counts[risk] += 1

    return {
        "total_invoices": len(invoices),
        "risk_counts": counts
    }
@app.post("/recalculate-risks")
def recalculate_invoice_risks(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    results = []

    for invoice in invoices:
        invoice_data = {
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "invoice_date": invoice.invoice_date,
            "total_amount": invoice.total_amount,
            "currency": invoice.currency,
            "purchase_order": invoice.purchase_order
        }

        validation = validate_invoice(invoice_data)
        po_result = match_purchase_order(invoice_data, db)

        risk = validation["risk_level"]

        if po_result["risk"] == "HIGH":
            risk = "HIGH"

        invoice.risk_level = risk

        results.append({
            "invoice_number": invoice.invoice_number,
            "invoice_amount": invoice.total_amount,
            "validation_risk": validation["risk_level"],
            "po_check": po_result,
            "calculated_risk": risk
        })

    db.commit()

    return {
        "message": "Risk recalculation completed.",
        "results": results
    }

@app.get("/anomalies")
def get_anomaly_report(db: Session = Depends(get_db)):
    try:
        return detect_amount_anomalies(db)

    except Exception as error:
        print(f"Anomaly detection error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Anomaly detection failed."
        ) from error


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    try:
        content = await file.read()

        saved_document = save_uploaded_document(
            filename=file.filename,
            content=content
        )

        extracted_text = extract_text(saved_document["file_path"])
        invoice_fields = extract_invoice_fields(extracted_text)

        validation_result = validate_invoice(invoice_fields)
        duplicate_result = check_duplicate(invoice_fields, db)
        po_result = match_purchase_order(invoice_fields, db)

        overall_risk = validation_result["risk_level"]

        if (
            duplicate_result["is_duplicate"]
            or po_result["risk"] == "HIGH"
        ):
            overall_risk = "HIGH"

        invoice_fields["risk_level"] = overall_risk

        if validation_result["is_valid"] and not duplicate_result["is_duplicate"]:
            save_invoice_record(invoice_fields, db)

            try:
                index_result = index_invoices_from_database(db)
                print("Semantic search index refreshed!")
                print(index_result)
            except Exception as error:
                print(f"Warning: Search index refresh failed: {error}")

        return {
            "message": "Document uploaded and processed successfully.",
            "document": {
                **saved_document,
                "extracted_text": extracted_text,
                "invoice_fields": invoice_fields,
                "validation": validation_result,
                "duplicate_check": duplicate_result,
                "purchase_order_check": po_result,
                "overall_risk": overall_risk
            }
        }

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        db.rollback()
        print(f"Document processing error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Document processing failed."
        ) from error

    finally:
        await file.close()
