import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, cast, desc, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, SearchResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Search documents",
    description="Full-text search across OCR extracted text, metadata, and structured fields.",
)
def search_documents(
    q: str = Query(..., min_length=1, description="Search term in Bengali or English"),
    doc_type: Optional[str] = Query(None, description="Optional document type filter"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    search_term = q.strip()
    search_pattern = f"%{search_term}%"

    query = db.query(Document).filter(
        or_(
            Document.ocr_text.ilike(search_pattern),
            Document.original_filename.ilike(search_pattern),
            cast(Document.extracted_fields, String).ilike(search_pattern),
        )
    )

    if doc_type:
        query = query.filter(Document.doc_type == doc_type.strip().lower())

    total = query.count()
    items = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()

    return {
        "query": search_term,
        "doc_type": doc_type,
        "items": [DocumentResponse.model_validate(doc) for doc in items],
        "total": total,
    }
