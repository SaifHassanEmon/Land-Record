import logging
import threading
from typing import Any, Dict, List, Optional
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

# Global EasyOCR reader cache and lock
_reader_lock = threading.Lock()
_easyocr_reader = None


def get_easyocr_reader():
    """Thread-safe singleton accessor for EasyOCR Reader."""
    global _easyocr_reader
    if _easyocr_reader is None:
        with _reader_lock:
            if _easyocr_reader is None:
                try:
                    import easyocr
                    langs = list(settings.DEFAULT_OCR_LANGUAGES)
                    logger.info(f"Initializing EasyOCR Reader for languages: {langs} (CPU mode)...")
                    _easyocr_reader = easyocr.Reader(langs, gpu=False)
                    logger.info("EasyOCR Reader successfully initialized.")
                except Exception as e:
                    logger.error(f"Failed to initialize EasyOCR reader: {e}")
                    _easyocr_reader = None
    return _easyocr_reader


def run_easyocr_on_image(image_arr: np.ndarray) -> Optional[Dict[str, Any]]:
    """
    Runs EasyOCR on a preprocessed image (numpy array).
    Returns dict with text, confidence, and words list, or None if failed.
    """
    reader = get_easyocr_reader()
    if reader is None:
        return None

    try:
        # EasyOCR readtext returns list of (bbox, text, prob)
        # bbox is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        results = reader.readtext(image_arr, detail=1, paragraph=False)
        
        extracted_lines = []
        words = []
        confidences = []

        for bbox, text, prob in results:
            clean_text = str(text).strip()
            if not clean_text:
                continue
            
            box_coords = [[int(pt[0]), int(pt[1])] for pt in bbox]
            confidence_val = round(float(prob), 4)

            words.append({
                "text": clean_text,
                "confidence": confidence_val,
                "box": box_coords,
            })
            extracted_lines.append(clean_text)
            confidences.append(confidence_val)

        full_text = "\n".join(extracted_lines)
        avg_confidence = float(np.mean(confidences)) if confidences else 0.0

        return {
            "text": full_text,
            "confidence": round(avg_confidence, 4),
            "words": words,
            "engine": "easyocr",
        }
    except Exception as e:
        logger.warning(f"EasyOCR extraction error: {e}. Falling back to pytesseract.")
        return None


def run_pytesseract_on_image(image_arr: np.ndarray) -> Dict[str, Any]:
    """
    Fallback OCR using pytesseract.
    Supports Bengali ('ben') and English ('eng').
    """
    import pytesseract

    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    # Try ben+eng first, then fallback to eng if ben is not installed
    lang_options = ["ben+eng", "ben", "eng"]
    data = None
    used_lang = "eng"

    for lang in lang_options:
        try:
            data = pytesseract.image_to_data(
                image_arr,
                lang=lang,
                output_type=pytesseract.Output.DICT,
            )
            used_lang = lang
            break
        except Exception as e:
            logger.warning(f"pytesseract failed with lang '{lang}': {e}")
            continue

    if data is None:
        logger.error("All pytesseract language options failed.")
        return {
            "text": "",
            "confidence": 0.0,
            "words": [],
            "engine": "pytesseract_failed",
        }

    words = []
    lines_map = {}  # group by line number
    confidences = []

    num_boxes = len(data.get("text", []))
    for i in range(num_boxes):
        word_text = data["text"][i].strip()
        conf = float(data["conf"][i])

        if word_text and conf >= 0:
            norm_conf = round(conf / 100.0, 4)
            confidences.append(norm_conf)

            x = data["left"][i]
            y = data["top"][i]
            w = data["width"][i]
            h = data["height"][i]
            box = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]

            words.append({
                "text": word_text,
                "confidence": norm_conf,
                "box": box,
            })

            line_idx = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            if line_idx not in lines_map:
                lines_map[line_idx] = []
            lines_map[line_idx].append(word_text)

    # Reconstruct text by lines
    full_text = "\n".join(" ".join(line_words) for line_words in lines_map.values())
    avg_confidence = float(np.mean(confidences)) if confidences else 0.0

    return {
        "text": full_text,
        "confidence": round(avg_confidence, 4),
        "words": words,
        "engine": f"pytesseract ({used_lang})",
    }


def perform_ocr_on_images(images: List[np.ndarray]) -> Dict[str, Any]:
    """
    Performs OCR across a list of preprocessed page images.
    Uses EasyOCR as primary and pytesseract as fallback.
    Returns: {text: str, confidence: float, words: list, engine: str}
    """
    if not images:
        return {"text": "", "confidence": 0.0, "words": [], "engine": "none"}

    all_page_texts = []
    all_words = []
    page_confidences = []
    engines_used = set()

    for idx, img in enumerate(images):
        logger.info(f"Processing OCR for page {idx + 1}/{len(images)}...")
        
        # Primary: EasyOCR
        res = run_easyocr_on_image(img)

        # Fallback: pytesseract
        if res is None:
            logger.info("EasyOCR unavailable or failed. Using pytesseract fallback.")
            res = run_pytesseract_on_image(img)

        page_text = res.get("text", "").strip()
        if page_text:
            all_page_texts.append(page_text)
        
        all_words.extend(res.get("words", []))
        if res.get("confidence", 0) > 0:
            page_confidences.append(res["confidence"])
        
        engines_used.add(res.get("engine", "unknown"))

    consolidated_text = "\n\n--- Page Break ---\n\n".join(all_page_texts) if len(all_page_texts) > 1 else (all_page_texts[0] if all_page_texts else "")
    overall_confidence = float(np.mean(page_confidences)) if page_confidences else 0.0

    return {
        "text": consolidated_text,
        "confidence": round(overall_confidence, 4),
        "words": all_words,
        "engine": ", ".join(sorted(engines_used)),
    }
