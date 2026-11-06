from fastapi import APIRouter

from app.schemas.search import SearchRequest

from app.services.semantic_search.engine import (
    search_documents
)


router = APIRouter()


@router.post("/search")
def search_invoices(request: SearchRequest):
    """
    Search invoices using the existing FAISS index.
    """

    search_results = search_documents(
        request.query,
        top_k=request.top_k
    )

    results = []

    for item in search_results:
        document = item["document"]

        results.append({
            "invoice_id": document["invoice_number"],
            "description": document["text"],
            "similarity_score": round(
                item["similarity_score"],
                4
            )
        })

    return {
        "query": request.query,
        "total_results": len(results),
        "results": results
    }