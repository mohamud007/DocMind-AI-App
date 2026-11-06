
from fastapi import APIRouter, HTTPException

from app.schemas.rag import QuestionRequest
from app.services.rag_service import answer_document_question

router = APIRouter()


@router.post("/ask")
def ask_documents(request: QuestionRequest):
    try:
        return answer_document_question(request.question)

    except Exception as error:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"RAG error: {str(error)}"
        ) from error
