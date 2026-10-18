import logging
import math
from pathlib import Path
from typing import List, Union
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
        # np.fromfile handles Unicode paths on Windows where cv2.imread fails
        raw_bytes = np.fromfile(file_path, dtype=np.uint8)
        img = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
        if img is None:
            # Fallback to PIL
            pil_img = Image.open(file_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return img
    except Exception as e:
        logger.error(f"Error reading image {file_path}: {e}")
        # Final fallback using PIL directly
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

    # 1. Try pypdfium2 (built-in, no poppler installation needed)
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

    # 2. Try pdf2image with poppler support
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
        raise RuntimeError(
            f"Failed to convert PDF to images. Error: {e}"
        )


def deskew_image(gray: np.ndarray) -> np.ndarray:
    """
    Detects skew angle using Hough Transform and rotates image to deskew.
    """
    try:
        # Invert colors so text is white
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Use Hough transform to detect lines
        lines = cv2.HoughLinesP(
            thresh,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=gray.shape[1] // 4,
            maxLineGap=20,
        )

        angles = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 - x1 == 0:
                    continue
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                # Only consider minor skew angles between -45 and 45 degrees
                if -45 < angle < 45:
                    angles.append(angle)

        if not angles:
            # Fallback to minAreaRect on non-zero points
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) > 50:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                if -45 < angle < 45:
                    angles.append(angle)

        if not angles:
            return gray

        median_angle = float(np.median(angles))

        # Do not rotate for tiny fluctuations under 0.5 degrees
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


def resize_to_standard_dpi(img: np.ndarray, target_min_dim: int = 1800) -> np.ndarray:
    """
    Resizes image if its dimensions are below standard 300 DPI document size.
    Standard A4 at 300 DPI is approx 2480 x 3508.
    """
    h, w = img.shape[:2]
    min_dim = min(h, w)
    if min_dim < target_min_dim:
        scale = target_min_dim / float(min_dim)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        return resized
    return img


def preprocess_single_image(bgr_or_gray: np.ndarray) -> np.ndarray:
    """
    Applies complete OpenCV preprocessing pipeline:
    1. Grayscale conversion
    2. Deskew using Hough transform
    3. Denoising using fastNlMeansDenoising
    4. Binarization using Otsu's thresholding
    5. Resize to ~300 DPI if smaller
    Returns clean binarized image (uint8 grayscale).
    """
    # 1. Convert to grayscale
    if len(bgr_or_gray.shape) == 3:
        gray = cv2.cvtColor(bgr_or_gray, cv2.COLOR_BGR2GRAY)
    else:
        gray = bgr_or_gray.copy()

    # 2. Deskew
    deskewed = deskew_image(gray)

    # 3. Denoise
    # fastNlMeansDenoising for single grayscale image
    try:
        denoised = cv2.fastNlMeansDenoising(deskewed, h=10, templateWindowSize=7, searchWindowSize=21)
    except Exception as e:
        logger.warning(f"Denoising failed, applying Gaussian blur: {e}")
        denoised = cv2.GaussianBlur(deskewed, (3, 3), 0)

    # 4. Binarize using Otsu threshold
    _, binarized = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 5. Resize to 300 DPI if smaller
    processed = resize_to_standard_dpi(binarized)

    return processed


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
