import asyncio
import logging
import mimetypes
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import String, cast, desc, or_
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.document import Document
from app.ocr import run_full_ocr_pipeline
from app.schemas.document import (
    BulkUploadErrorItem,
    BulkUploadResponse,
    DemoDocItem,
    DemoDocListResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentType,
    DocumentUpdateRequest,
    SearchResponse,
)
from app.utils.file_handler import (
    ALLOWED_EXTENSIONS,
    copy_local_file_to_uploads,
    delete_file,
    infer_doc_type_from_filename,
    save_upload_file,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process a land document",
    description="Uploads a document (PDF or image), executes OCR asynchronously in thread pool, extracts fields, and stores in database.",
)
async def upload_document(
    file: UploadFile = File(..., description="Document file (.pdf, .png, .jpg, .jpeg, etc.)"),
    doc_type: str = Form(..., description="Document type: khatian, porcha, deed"),
    db: Session = Depends(get_db),
):
    valid_types = {t.value for t in DocumentType}
    norm_doc_type = doc_type.strip().lower()
    if norm_doc_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid doc_type '{doc_type}'. Allowed types: {', '.join(sorted(valid_types))}",
        )

    # 1. Save uploaded file to disk
    target_path, unique_filename, file_size, page_count = await save_upload_file(file)

    # 2. Create initial DB record with 'processing' status
    doc_record = Document(
        filename=unique_filename,
        original_filename=file.filename or unique_filename,
        file_path=str(target_path.resolve()),
        doc_type=norm_doc_type,
        status="processing",
        ocr_text=None,
        ocr_confidence=None,
        extracted_fields=None,
        file_size=file_size,
        page_count=page_count,
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # 3. Execute OCR pipeline in thread pool executor to prevent event loop blocking
    loop = asyncio.get_running_loop()
    try:
        ocr_result = await loop.run_in_executor(
            None, run_full_ocr_pipeline, target_path, norm_doc_type
        )
        doc_record.ocr_text = ocr_result.get("text", "")
        doc_record.ocr_confidence = ocr_result.get("confidence", 0.0)
        doc_record.extracted_fields = ocr_result.get("extracted_fields", {})
        doc_record.status = "done"
    except Exception as e:
        logger.error(f"OCR pipeline failed for document {doc_record.id}: {e}", exc_info=True)
        doc_record.status = "failed"
        doc_record.extracted_fields = {"error": str(e)}

    db.commit()
    db.refresh(doc_record)
    return doc_record


@router.get(
    "/stats",
    summary="Get document statistics",
    description="Returns total document counts grouped by doc_type.",
)
def get_document_stats(db: Session = Depends(get_db)):
    total = db.query(Document).count()
    khatian = db.query(Document).filter(Document.doc_type == "khatian").count()
    porcha = db.query(Document).filter(Document.doc_type == "porcha").count()
    deed = db.query(Document).filter(Document.doc_type == "deed").count()
    return {
        "total": total,
        "khatian": khatian,
        "porcha": porcha,
        "deed": deed,
    }


@router.get(
    "",
    response_model=DocumentListResponse,
    include_in_schema=False,
)
@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List all documents",
    description="Returns a paginated list of documents with optional filtering by doc_type and search keyword.",
)
def list_documents(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    doc_type: Optional[str] = Query(None, description="Filter by khatian, porcha, or deed"),
    search: Optional[str] = Query(None, description="Search in text or filename"),
    db: Session = Depends(get_db),
):
    query = db.query(Document)

    if doc_type:
        query = query.filter(Document.doc_type == doc_type.strip().lower())

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Document.ocr_text.ilike(search_pattern),
                Document.original_filename.ilike(search_pattern),
                cast(Document.extracted_fields, String).ilike(search_pattern),
            )
        )

    total = query.count()
    items = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()

    return {"items": items, "total": total}


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
    description="Retrieve a single document by ID with OCR text and extracted fields.",
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )
    return doc


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Update document fields and text",
    description="Allows verifying, editing, and saving extracted information for a document.",
)
def update_document(
    document_id: int,
    payload: DocumentUpdateRequest,
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )
    if payload.extracted_fields is not None:
        doc.extracted_fields = payload.extracted_fields
    if payload.ocr_text is not None:
        doc.ocr_text = payload.ocr_text
    if payload.doc_type is not None:
        doc.doc_type = payload.doc_type.strip().lower()

    db.commit()
    db.refresh(doc)
    return doc


@router.get(
    "/{document_id}/file",
    summary="Download or view original document file",
    description="Serves the raw file binary (image or PDF).",
)
def get_document_file(
    document_id: int,
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )

    file_path = Path(doc.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{doc.filename}' not found on storage disk",
        )

    media_type, _ = mimetypes.guess_type(str(file_path))
    if not media_type:
        media_type = "application/octet-stream"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=doc.original_filename,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a document",
    description="Deletes document metadata from database and removes file from disk.",
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found",
        )

    # Delete physical file
    delete_file(doc.file_path)

    db.delete(doc)
    db.commit()

    return {"message": f"Document {document_id} deleted successfully", "id": document_id}
