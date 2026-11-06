import faiss
import numpy as np
import re

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

EMBEDDING_DIMENSION = model.get_embedding_dimension()

MIN_SIMILARITY_SCORE = 0.22

documents = []

index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)


def normalize_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(text).lower()))


def add_documents(new_documents: list[dict]) -> dict:

    if not new_documents:
        return {
            "message": "No documents provided.",
            "documents_added": 0,
            "total_documents": len(documents)
        }

    valid_documents = []

    for document in new_documents:

        if not isinstance(document, dict):
            continue

        text = document.get("text")

        if not isinstance(text, str) or not text.strip():
            continue

        if not document.get("id"):
            continue

        valid_documents.append({
            **document,
            "id": str(document["id"]),
            "text": text.strip()
        })

    if not valid_documents:
        return {
            "message": "No valid documents found.",
            "documents_added": 0,
            "total_documents": len(documents)
        }

    texts = [document["text"] for document in valid_documents]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(embeddings, dtype="float32")

    index.add(embeddings)
    documents.extend(valid_documents)

    return {
        "message": "Documents indexed successfully.",
        "documents_added": len(valid_documents),
        "total_documents": len(documents)
    }


def clear_index() -> dict:

    global index

    index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
    documents.clear()

    return {
        "message": "Search index cleared successfully.",
        "total_documents": 0
    }


def find_exact_identifier(query: str):

    normalized_query = normalize_text(query)

    # Find invoice numbers and purchase order numbers.
    identifiers = re.findall(
        r"\b(?:inv|po)[\s-]*\d+\b",
        query.lower()
    )

    for identifier in identifiers:

        normalized_identifier = normalize_text(identifier)

        for document in documents:

            invoice_number = normalize_text(
                document.get("invoice_number", "")
            )

            purchase_order = normalize_text(
                document.get("purchase_order", "")
            )

            if (
                normalized_identifier == invoice_number
                or normalized_identifier == purchase_order
            ):
                return normalized_identifier

    return None


def search_documents(query: str, top_k: int = 3) -> list[dict]:

    if not isinstance(query, str) or not query.strip():
        return []

    if not isinstance(top_k, int) or top_k <= 0:
        return []

    if index.ntotal == 0:
        return []

    normalized_query = normalize_text(query)

    # First check for exact invoice or PO number.
    identifier = find_exact_identifier(query)

    if identifier:

        candidate_documents = [
            document for document in documents
            if (
                normalize_text(document.get("invoice_number", "")) == identifier
                or normalize_text(document.get("purchase_order", "")) == identifier
            )
        ]

    else:

        # Check whether a vendor is mentioned.
        matching_vendors = {
            normalize_text(document.get("vendor", ""))
            for document in documents
            if document.get("vendor")
        }

        vendor_filter = next(
            (
                vendor for vendor in sorted(
                    matching_vendors,
                    key=len,
                    reverse=True
                )
                if vendor and vendor in normalized_query
            ),
            None
        )

        if vendor_filter:

            candidate_documents = [
                document for document in documents
                if normalize_text(document.get("vendor", "")) == vendor_filter
            ]

        else:
            candidate_documents = documents

    if not candidate_documents:
        return []

    query_embedding = model.encode(
        [query.strip()],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    candidate_embeddings = model.encode(
        [document["text"] for document in candidate_documents],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    candidate_embeddings = np.asarray(
        candidate_embeddings,
        dtype="float32"
    )

    scores = np.dot(
        candidate_embeddings,
        query_embedding[0]
    )

    ranked_indices = np.argsort(scores)[::-1]

    results = []

    for document_index in ranked_indices:

        similarity = float(scores[document_index])

        if similarity < MIN_SIMILARITY_SCORE:
            continue

        results.append({
            "document": candidate_documents[document_index],
            "similarity_score": similarity
        })

        if len(results) >= top_k:
            break

    return results