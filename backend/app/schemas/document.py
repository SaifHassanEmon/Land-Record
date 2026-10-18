from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentType(str, Enum):
    KHATIAN = "khatian"
    PORCHA = "porcha"
    DEED = "deed"


class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class DocumentBase(BaseModel):
    original_filename: str
    doc_type: DocumentType


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    doc_type: str
    status: str
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    extracted_fields: Optional[Dict[str, Any]] = None
    created_at: datetime
    file_size: int
    page_count: int

    model_config = ConfigDict(from_attributes=True)


class DocumentUpdateRequest(BaseModel):
    extracted_fields: Optional[Dict[str, Any]] = None
    ocr_text: Optional[str] = None
    doc_type: Optional[str] = None


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int


class DemoDocItem(BaseModel):
    filename: str
    doc_type: str
    file_size: int
    file_path: str


class DemoDocListResponse(BaseModel):
    items: List[DemoDocItem]
    total: int


class BulkUploadErrorItem(BaseModel):
    filename: str
    error: str


class BulkUploadResponse(BaseModel):
    processed: int
    failed: int
    documents: List[DocumentResponse]
    errors: List[BulkUploadErrorItem]


class SearchResponse(BaseModel):
    query: str
    doc_type: Optional[str] = None
    items: List[DocumentResponse]
    total: int
