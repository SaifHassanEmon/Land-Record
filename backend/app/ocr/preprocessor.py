import logging
import math
from pathlib import Path
from typing import List, Optional, Union
import cv2
import numpy as np
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)


def read_image_safely(file_path: Union[str, Path]) -> np.ndarray:
    """
    Safely reads an image from file_path, handling Unicode paths on Windows.
    Returns BGR numpy array.
    """
    file_path = str(file_path)
    try:
        raw_bytes = np.fromfile(file_path, dtype=np.uint8)
        img = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
        if img is None:
            pil_img = Image.open(file_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return img
    except Exception as e:
        logger.error(f"Error reading image {file_path}: {e}")
        pil_img = Image.open(file_path).convert("RGB")
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def extract_text_from_pdf(pdf_path: Union[str, Path]) -> Optional[str]:
    """
    Extracts embedded digital text from PDF if available.
    Returns None if no readable digital text layer is present.
    """
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(pdf_path))
        text_parts = []
        for page in pdf:
            txt = page.get_textpage().get_text_range()
            if txt and txt.strip():
                text_parts.append(txt.strip())
        full_text = "\n\n".join(text_parts)
        if len(full_text.strip()) > 30:
            return full_text.strip()
    except Exception as e:
        logger.debug(f"Direct PDF text extraction skipped: {e}")
    return None


def convert_pdf_to_images(pdf_path: Union[str, Path]) -> List[np.ndarray]:
    """
    Converts all pages of a PDF to a list of BGR numpy images.
    Uses pypdfium2 first (zero external dependencies), falls back to pdf2image.
    """
    pdf_path_str = str(pdf_path)

    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_path_str)
        images = []
        for page in pdf:
            pil_img = page.render(scale=2).to_pil()
            rgb_arr = np.array(pil_img.convert("RGB"))
            bgr_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)
            images.append(bgr_arr)
        if images:
            return images
    except Exception as e:
        logger.debug(f"pypdfium2 conversion fallback: {e}")

    try:
        from pdf2image import convert_from_path

        kwargs = {"dpi": 200}
        if settings.POPPLER_PATH:
            kwargs["poppler_path"] = settings.POPPLER_PATH

        pil_pages = convert_from_path(pdf_path_str, **kwargs)
        images = []
        for p in pil_pages:
            rgb_arr = np.array(p.convert("RGB"))
            bgr_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)
            images.append(bgr_arr)
        return images
    except Exception as e:
        logger.error(f"pdf2image conversion failed for {pdf_path}: {e}")
        raise RuntimeError(f"Failed to convert PDF to images: {e}")


def deskew_image(gray: np.ndarray) -> np.ndarray:
    """
    Detects skew angle using Hough Transform and rotates image to deskew.
    """
    try:
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        lines = cv2.HoughLinesP(
            thresh,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=max(gray.shape[1] // 5, 50),
            maxLineGap=20,
        )

        angles = []
        if lines is not None:
            for line in lines:
                flat = np.array(line).flatten()
                if len(flat) < 4:
                    continue
                x1, y1, x2, y2 = flat[:4]
                if x2 - x1 == 0:
                    continue
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                if -45 < angle < 45:
                    angles.append(angle)

        if not angles:
            try:
                coords = np.column_stack(np.where(thresh > 0))
                if len(coords) > 50:
                    rect = cv2.minAreaRect(coords)
                    angle = float(rect[-1])
                    if angle < -45:
                        angle = -(90 + angle)
                    else:
                        angle = -angle
                    if -45 < angle < 45:
                        angles.append(angle)
            except Exception as deskew_e:
                logger.debug(f"minAreaRect fallback skipped: {deskew_e}")

        if not angles:
            return gray

        median_angle = float(np.median(angles))

        if abs(median_angle) < 0.5:
            return gray

        h, w = gray.shape[:2]
        center = (w // 2, h // 2)
        rot_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        deskewed = cv2.warpAffine(
            gray,
            rot_matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=255,
        )
        return deskewed
    except Exception as e:
        logger.warning(f"Deskew failed, keeping original: {e}")
        return gray


def preprocess_single_image(bgr_or_gray: np.ndarray) -> np.ndarray:
    """
    Applies clean, text-preserving preprocessing:
    1. Grayscale conversion
    2. Intelligent deskew
    3. Resolution upscale (target ~2000px height / 300 DPI for sharp Bengali OCR)
    4. Contrast stretching & normalization
    Preserves exact Bengali strokes, ligatures, and numerals.
    """
    if len(bgr_or_gray.shape) == 3:
        gray = cv2.cvtColor(bgr_or_gray, cv2.COLOR_BGR2GRAY)
    else:
        gray = bgr_or_gray.copy()

    # Deskew to ensure straight text lines for OCR
    deskewed = deskew_image(gray)

    h, w = deskewed.shape[:2]
    # Check if image resolution is low (< 1800px on the short/long edge)
    # Bengali LSTM requires at least 30-40px font height to distinguish conjuncts & matras
    if h < 1800 or w < 1800:
        target_dim = 2000.0
        scale = min(max(target_dim / h, target_dim / w), 3.5)
        new_w = int(w * scale)
        new_h = int(h * scale)
        deskewed = cv2.resize(deskewed, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    # Normalize contrast to remove scan shadows and maximize text legibility
    normalized = cv2.normalize(deskewed, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    return normalized


def preprocess_document(file_path: Union[str, Path]) -> List[np.ndarray]:
    """
    Entrypoint to preprocess any document (image or PDF).
    Returns a list of preprocessed images (one per page).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    if ext == ".pdf":
        raw_pages = convert_pdf_to_images(path)
    else:
        raw_img = read_image_safely(path)
        raw_pages = [raw_img]

    processed_pages = []
    for page in raw_pages:
        processed = preprocess_single_image(page)
        processed_pages.append(processed)

    return processed_pages
