from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime
from app.database import Base


class Document(Base):
    """SQLAlchemy model for scanned land record documents."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    doc_type = Column(String(50), nullable=False, index=True)  # khatian, porcha, deed
    status = Column(String(50), default="processing", index=True)  # processing, done, failed
    ocr_text = Column(Text, nullable=True)  # Full OCR text
    ocr_confidence = Column(Float, nullable=True)
    extracted_fields = Column(JSON, nullable=True)  # Dict of extracted fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_size = Column(Integer, default=0)
    page_count = Column(Integer, default=1)

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename='{self.filename}', doc_type='{self.doc_type}', status='{self.status}')>"
