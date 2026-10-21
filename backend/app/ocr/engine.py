import logging
import os
import threading
from typing import Any, Dict, List, Optional
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

# Global EasyOCR reader cache and lock
_reader_lock = threading.Lock()
_easyocr_reader = None
_easyocr_available = None


def check_easyocr_available() -> bool:
    """Checks once if EasyOCR is installed and importable."""
    global _easyocr_available
    if _easyocr_available is None:
        try:
            import easyocr
            _easyocr_available = True
        except ImportError:
            _easyocr_available = False
            logger.info("EasyOCR not installed. Pytesseract will be primary local OCR.")
    return _easyocr_available


def get_easyocr_reader():
    """Thread-safe accessor for EasyOCR Reader if installed."""
    global _easyocr_reader
    if not check_easyocr_available():
        return None

    if _easyocr_reader is None:
        with _reader_lock:
            if _easyocr_reader is None:
                try:
                    import easyocr
                    langs = list(settings.DEFAULT_OCR_LANGUAGES)
                    logger.info(f"Initializing EasyOCR for: {langs} (CPU)...")
                    _easyocr_reader = easyocr.Reader(langs, gpu=False)
                    logger.info("EasyOCR Reader successfully initialized.")
                except Exception as e:
                    logger.warning(f"EasyOCR initialization failed: {e}")
                    _easyocr_reader = None
    return _easyocr_reader


def run_easyocr_on_image(image_arr: np.ndarray) -> Optional[Dict[str, Any]]:
    """Runs EasyOCR on an image if available."""
    reader = get_easyocr_reader()
    if reader is None:
        return None

    try:
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
        logger.warning(f"EasyOCR extraction error: {e}")
        return None


def run_pytesseract_on_image(image_arr: np.ndarray) -> Dict[str, Any]:
    """
    Robust OCR using pytesseract with Bengali ('ben') and English ('eng').
    Uses settings.TESSERACT_CMD and settings.TESSDATA_PREFIX.
    """
    import pytesseract

    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    if settings.TESSDATA_PREFIX:
        os.environ["TESSDATA_PREFIX"] = settings.TESSDATA_PREFIX

    # Languages to try in order
    lang_options = ["ben+eng", "ben", "eng"]
    data = None
    used_lang = "eng"

    # 1. First get detailed bounding boxes and confidence scores
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
            logger.debug(f"pytesseract image_to_data failed for lang '{lang}': {e}")
            continue

    # 2. Get high-quality full text with image_to_string using the detected language
    full_text = ""
    try:
        text_psm6 = pytesseract.image_to_string(image_arr, lang=used_lang, config="--psm 6").strip()
        text_default = pytesseract.image_to_string(image_arr, lang=used_lang).strip()
        full_text = text_psm6 if len(text_psm6) >= len(text_default) else text_default
    except Exception as e:
        logger.warning(f"pytesseract image_to_string error: {e}")

    # 3. Zonal extraction for structured tabular land records
    h, w = image_arr.shape[:2]
    if h >= 600 and w >= 600:
        extra_zones = []
        try:
            # Header zone (top 22% of document)
            header_crop = image_arr[0:int(h * 0.22), :]
            h_text = pytesseract.image_to_string(header_crop, lang=used_lang, config="--psm 6").strip()
            if h_text and len(h_text) > 10:
                extra_zones.append(h_text)
        except Exception:
            pass

        try:
            # Left owner column zone (x: 5% - 35%, y: 12% - 50%)
            owner_crop = image_arr[int(h * 0.12):int(h * 0.50), int(w * 0.05):int(w * 0.35)]
            o_text = pytesseract.image_to_string(owner_crop, lang=used_lang, config="--psm 6").strip()
            if o_text and len(o_text) > 10:
                extra_zones.append(o_text)
        except Exception:
            pass

        try:
            # Plot numbers column zone (x: 35% - 46%, y: 14% - 85%)
            plot_crop = image_arr[int(h * 0.14):int(h * 0.85), int(w * 0.35):int(w * 0.46)]
            p_text = pytesseract.image_to_string(plot_crop, lang=used_lang, config="--psm 6").strip()
            if p_text and len(p_text) > 5:
                extra_zones.append(p_text)
        except Exception:
            pass

        if extra_zones:
            full_text = "\n\n".join(extra_zones + [full_text])

    if data is None:
        logger.error("All pytesseract language options failed.")
        return {
            "text": full_text,
            "confidence": 0.0,
            "words": [],
            "engine": "pytesseract_failed",
        }

    words = []
    lines_map = {}
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

    # If image_to_string produced text, prefer it; otherwise use reconstructed line text
    if not full_text and lines_map:
        full_text = "\n".join(" ".join(line_words) for line_words in lines_map.values())

    avg_confidence = float(np.mean(confidences)) if confidences else (0.75 if full_text else 0.0)

    return {
        "text": full_text,
        "confidence": round(avg_confidence, 4),
        "words": words,
        "engine": f"tesseract ({used_lang})",
    }


def perform_ocr_on_images(images: List[np.ndarray]) -> Dict[str, Any]:
    """
    Performs OCR across a list of preprocessed page images.
    Uses Tesseract (with Bengali) as primary local engine, or EasyOCR if installed.
    """
    if not images:
        return {"text": "", "confidence": 0.0, "words": [], "engine": "none"}

    all_page_texts = []
    all_words = []
    page_confidences = []
    engines_used = set()

    for idx, img in enumerate(images):
        logger.info(f"Processing OCR for page {idx + 1}/{len(images)}...")

        # If EasyOCR is available, try it
        res = None
        if check_easyocr_available():
            res = run_easyocr_on_image(img)

        # Fallback / primary: pytesseract
        if res is None:
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
