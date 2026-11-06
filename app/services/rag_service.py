
import os
import time

from dotenv import load_dotenv
from google import genai

from app.services.semantic_search.engine import search_documents

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"


def answer_document_question(question: str) -> dict:

    if not question or not question.strip():
        return {
            "question": question,
            "answer": "Please enter a valid question.",
            "evidence": []
        }

    search_results = search_documents(
        question.strip(),
        top_k=5
    )

    if not search_results:
        return {
            "question": question,
            "answer": "No relevant invoice records were found.",
            "evidence": []
        }

    evidence = []

    for item in search_results:
        document = item["document"]

        evidence.append({
            "invoice_id": document["invoice_number"],
            "description": document["text"],
            "similarity_score": round(
                item["similarity_score"], 4
            )
        })

    evidence_text = "\n".join(
        item["description"] for item in evidence
    )

    prompt = f"""
You are DocuMind AI, an invoice analysis assistant.

Answer using ONLY the invoice evidence below.

Do not invent information.
If information is unavailable, say so.
Explain amount differences clearly.
Mention invoice numbers.

INVOICE EVIDENCE:
{evidence_text}

QUESTION:
{question}
"""

    # Retry temporary server overload errors
    for attempt in range(3):
        try:
            response = client.models.generate_content(
    model=MODEL_NAME,
    contents=prompt,
    config={
        "http_options": {
            "timeout": 15000
        }
    }
)
            return {
                "question": question,
                "answer": response.text or "No answer generated.",
                "evidence": evidence
            }

        except Exception as error:
            error_message = str(error)

            if "503" in error_message or "UNAVAILABLE" in error_message:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue

                return {
                    "question": question,
                    "answer": (
                        "AI service is temporarily busy. "
                        "Your invoice evidence was retrieved successfully. "
                        "Please try again shortly."
                    ),
                    "evidence": evidence
                }

            raise
