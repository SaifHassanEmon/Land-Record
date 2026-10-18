import asyncio
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
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
    DocumentResponse,
)
from app.utils.file_handler import (
    ALLOWED_EXTENSIONS,
    copy_local_file_to_uploads,
    infer_doc_type_from_filename,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/demo-docs",
    response_model=DemoDocListResponse,
    summary="List available demo documents",
    description="Returns list of sample land documents available in the demo_docs folder.",
)
def get_demo_documents():
    demo_dir = Path(settings.DEMO_DOCS_DIR)
    if not demo_dir.exists():
        demo_dir.mkdir(parents=True, exist_ok=True)
        return {"items": [], "total": 0}

    items: List[DemoDocItem] = []
    for f in sorted(demo_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS:
            doc_type = infer_doc_type_from_filename(f.name)
            items.append(
                DemoDocItem(
                    filename=f.name,
                    doc_type=doc_type,
                    file_size=f.stat().st_size,
                    file_path=str(f),
                )
            )

    return {"items": items, "total": len(items)}


@router.post(
    "/demo-docs/upload-all",
    response_model=BulkUploadResponse,
    summary="Bulk upload and process all demo documents",
    description="Loads all documents from demo_docs, copies to uploads, runs OCR, and saves to database.",
)
async def upload_all_demo_documents(db: Session = Depends(get_db)):
    demo_dir = Path(settings.DEMO_DOCS_DIR)
    if not demo_dir.exists() or not any(demo_dir.iterdir()):
        return BulkUploadResponse(
            processed=0,
            failed=0,
            documents=[],
            errors=[BulkUploadErrorItem(filename="none", error="No files found in demo_docs directory")],
        )

    files = [
        f for f in sorted(demo_dir.iterdir())
        if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS
    ]

    processed_docs: List[DocumentResponse] = []
    errors: List[BulkUploadErrorItem] = []
    loop = asyncio.get_running_loop()

    for file_path in files:
        doc_type = infer_doc_type_from_filename(file_path.name)
        try:
            target_path, unique_name, file_size, page_count = copy_local_file_to_uploads(file_path)

            doc_record = Document(
                filename=unique_name,
                original_filename=file_path.name,
                file_path=str(target_path.resolve()),
                doc_type=doc_type,
                status="processing",
                file_size=file_size,
                page_count=page_count,
            )
            db.add(doc_record)
            db.commit()
            db.refresh(doc_record)

            try:
                ocr_result = await loop.run_in_executor(
                    None, run_full_ocr_pipeline, target_path, doc_type
                )
                doc_record.ocr_text = ocr_result.get("text", "")
                doc_record.ocr_confidence = ocr_result.get("confidence", 0.0)
                doc_record.extracted_fields = ocr_result.get("extracted_fields", {})
                doc_record.status = "done"
            except Exception as ocr_err:
                logger.error(f"OCR error on demo doc {file_path.name}: {ocr_err}")
                doc_record.status = "failed"
                doc_record.extracted_fields = {"error": str(ocr_err)}

            db.commit()
            db.refresh(doc_record)
            processed_docs.append(DocumentResponse.model_validate(doc_record))
        except Exception as e:
            logger.error(f"Failed processing demo document {file_path.name}: {e}")
            errors.append(BulkUploadErrorItem(filename=file_path.name, error=str(e)))

    return BulkUploadResponse(
        processed=len(processed_docs),
        failed=len(errors),
        documents=processed_docs,
        errors=errors,
    )


@router.post(
    "/demo-docs/{filename}/process",
    response_model=DocumentResponse,
    summary="Process a specific demo document",
    description="Imports a specific document from demo_docs, runs OCR, and stores it in the database.",
)
async def process_single_demo_document(filename: str, db: Session = Depends(get_db)):
    demo_file = Path(settings.DEMO_DOCS_DIR) / filename
    if not demo_file.exists() or not demo_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo document '{filename}' not found in demo_docs folder",
        )

    doc_type = infer_doc_type_from_filename(demo_file.name)
    target_path, unique_name, file_size, page_count = copy_local_file_to_uploads(demo_file)

    doc_record = Document(
        filename=unique_name,
        original_filename=demo_file.name,
        file_path=str(target_path.resolve()),
        doc_type=doc_type,
        status="processing",
        file_size=file_size,
        page_count=page_count,
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    loop = asyncio.get_running_loop()
    try:
        ocr_result = await loop.run_in_executor(
            None, run_full_ocr_pipeline, target_path, doc_type
        )
        doc_record.ocr_text = ocr_result.get("text", "")
        doc_record.ocr_confidence = ocr_result.get("confidence", 0.0)
        doc_record.extracted_fields = ocr_result.get("extracted_fields", {})
        doc_record.status = "done"
    except Exception as ocr_err:
        logger.error(f"OCR error on demo doc {filename}: {ocr_err}")
        doc_record.status = "failed"
        doc_record.extracted_fields = {"error": str(ocr_err)}

    db.commit()
    db.refresh(doc_record)
    return doc_record
