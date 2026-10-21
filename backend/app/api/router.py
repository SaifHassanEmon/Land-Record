from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import demo, documents, search
from app.database import get_db
from app.models.document import Document

api_router = APIRouter()

@api_router.get("/stats", tags=["Stats"], summary="Get system statistics")
def get_system_stats(db: Session = Depends(get_db)):
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

api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(search.router, tags=["Search"])
api_router.include_router(demo.router, tags=["Demo Documents"])
