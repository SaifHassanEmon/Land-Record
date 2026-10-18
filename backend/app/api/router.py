from fastapi import APIRouter
from app.api import demo, documents, search

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(search.router, tags=["Search"])
api_router.include_router(demo.router, tags=["Demo Documents"])
