import logging
from pathlib import Path
from typing import Any, Dict, Union

from app.ocr.preprocessor import preprocess_document
from app.ocr.engine import perform_ocr_on_images
from app.ocr.extractor import extract_fields

logger = logging.getLogger(__name__)


def run_full_ocr_pipeline(file_path: Union[str, Path], doc_type: str) -> Dict[str, Any]:
    """
    Synchronous pipeline runner:
    1. Preprocesses document (images or PDF)
    2. Runs OCR (EasyOCR with pytesseract fallback)
    3. Extracts structured fields for the given doc_type
    Returns:
    {
        "text": str,
        "confidence": float,
        "words": list,
        "extracted_fields": dict,
        "engine": str
    }
    """
    path = Path(file_path)
    logger.info(f"Starting OCR pipeline for {path.name} (type: {doc_type})...")

    # Step 0: Check for digital text layer in PDF (fast & 100% accurate for digital records)
    if path.suffix.lower() == ".pdf":
        try:
            from app.ocr.preprocessor import extract_text_from_pdf
            direct_text = extract_text_from_pdf(path)
            if direct_text and len(direct_text.strip()) > 50:
                logger.info(f"Using high-fidelity digital text layer for {path.name} ({len(direct_text)} chars)")
                extracted = extract_fields(doc_type, direct_text)
                return {
                    "text": direct_text,
                    "confidence": 0.98,
                    "words": [],
                    "extracted_fields": extracted,
                    "engine": "digital_pdf_layer",
                }
        except Exception as e:
            logger.debug(f"Direct PDF text check skipped: {e}")

    # Step 1: Preprocess
    preprocessed_images = preprocess_document(path)
    if not preprocessed_images:
        logger.warning(f"No pages extracted for file {path}")
        return {
            "text": "",
            "confidence": 0.0,
            "words": [],
            "extracted_fields": {},
            "engine": "none",
        }

    # Step 2: OCR
    ocr_result = perform_ocr_on_images(preprocessed_images)
    full_text = ocr_result.get("text", "")
    confidence = ocr_result.get("confidence", 0.0)

    # Step 3: Extract structured fields
    extracted = extract_fields(doc_type, full_text)

    logger.info(
        f"Pipeline complete for {path.name}. Conf: {confidence:.2f}, "
        f"Extracted {len(extracted)} fields."
    )

    return {
        "text": full_text,
        "confidence": confidence,
        "words": ocr_result.get("words", []),
        "extracted_fields": extracted,
        "engine": ocr_result.get("engine", "unknown"),
    }


__all__ = [
    "preprocess_document",
    "perform_ocr_on_images",
    "extract_fields",
    "run_full_ocr_pipeline",
]
