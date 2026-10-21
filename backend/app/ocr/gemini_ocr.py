"""
gemini_ocr.py
-------------
Uses Google Gemini Vision API (generative AI) to perform high-quality OCR
on Bengali land record documents. Works with both handwritten and printed text.

Requires:  pip install google-genai
Env vars:  GEMINI_API_KEY  (or GOOGLE_API_KEY)
"""

import base64
import json
import logging
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Lazy-loaded client
_gemini_client = None


def _get_client():
    """Lazy-initialize the Gemini client."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    try:
        from google import genai
    except ImportError:
        logger.warning("google-genai package not installed. Run: pip install google-genai")
        return None

    import os
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    if not api_key:
        logger.warning("No GEMINI_API_KEY or GOOGLE_API_KEY found in environment.")
        return None

    _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


# ---------------------------------------------------------------------------
# Prompt templates for different document types
# ---------------------------------------------------------------------------

_BASE_SYSTEM_PROMPT = """You are an expert OCR system specialized in Bangladeshi land records.
You can read both printed and handwritten Bengali text with very high accuracy.
You understand the structure of Khatian (খতিয়ান), Porcha (পর্চা), and Deed (দলিল) documents
from the Bangladesh Land Ministry.

Your job is to:
1. Read ALL text from the document image accurately in Bengali
2. Extract structured fields based on the document type
3. Return the result as valid JSON

IMPORTANT:
- Preserve Bengali numerals (০১২৩৪৫৬৭৮৯) as they appear in the document
- If a field is not visible or readable, set it to null
- Read every cell in tables carefully
- Include ALL owners/parties if multiple exist
"""

_KHATIAN_PROMPT = """Analyze this Khatian (খতিয়ান) land record document image.

Return a JSON object with exactly these keys:
{
  "full_text": "<complete OCR text from the entire document, preserving layout>",
  "extracted_fields": {
    "khatian_number": "<খতিয়ান নং>",
    "district": "<জেলা>",
    "upazila": "<উপজেলা/থানা>",
    "union_name": "<ইউনিয়ন>",
    "mouza": "<মৌজা>",
    "jl_number": "<জে.এল. নং>",
    "former_khatian": "<সাবেক খতিয়ান নং>",
    "owner_name": "<মালিকের নাম>",
    "father_name": "<পিতার/স্বামীর নাম>",
    "address": "<ঠিকানা>",
    "plot_numbers": "<দাগ নং (comma-separated)>",
    "total_area": "<মোট জমির পরিমাণ>",
    "land_type": "<জমির শ্রেণি>",
    "issue_date": "<তারিখ>"
  },
  "confidence": <0.0 to 1.0 based on text clarity>
}

Return ONLY valid JSON, no markdown, no explanation."""

_PORCHA_PROMPT = """Analyze this Porcha (পর্চা / পরচা) land record document image.

Return a JSON object with exactly these keys:
{
  "full_text": "<complete OCR text from the entire document, preserving layout>",
  "extracted_fields": {
    "porcha_number": "<পর্চা নং>",
    "khatian_number": "<খতিয়ান নং>",
    "district": "<জেলা>",
    "upazila": "<উপজেলা/থানা>",
    "mouza": "<মৌজা>",
    "village": "<গ্রাম>",
    "rs_khatian": "<আর.এস. খতিয়ান নং>",
    "bs_khatian": "<বি.এস. খতিয়ান নং>",
    "owner_name": "<মালিকের নাম (all owners, comma-separated)>",
    "father_name": "<পিতার নাম (all, comma-separated)>",
    "plot_numbers": "<দাগ নং (comma-separated)>",
    "total_area": "<মোট জমির পরিমাণ>",
    "land_type": "<জমির শ্রেণি>",
    "issue_date": "<তারিখ>",
    "register_no": "<রেজিস্টার নং>"
  },
  "confidence": <0.0 to 1.0 based on text clarity>
}

Return ONLY valid JSON, no markdown, no explanation."""

_DEED_PROMPT = """Analyze this Deed (দলিল) document image.

Return a JSON object with exactly these keys:
{
  "full_text": "<complete OCR text from the entire document, preserving layout>",
  "extracted_fields": {
    "deed_number": "<দলিল নং>",
    "deed_type": "<দলিলের প্রকৃতি (সাফ কবলা/হেবা/দানপত্র etc.)>",
    "seller_name": "<বিক্রেতা/দাতার নাম>",
    "buyer_name": "<ক্রেতা/গ্রহীতার নাম>",
    "district": "<জেলা>",
    "upazila": "<উপজেলা/থানা>",
    "mouza": "<মৌজা>",
    "plot_numbers": "<দাগ নং>",
    "total_area": "<জমির পরিমাণ>",
    "consideration_amount": "<মূল্য/টাকা>",
    "registration_date": "<রেজিস্ট্রেশন তারিখ>",
    "sub_registry_office": "<সাব-রেজিস্ট্রি অফিস>"
  },
  "confidence": <0.0 to 1.0 based on text clarity>
}

Return ONLY valid JSON, no markdown, no explanation."""


def _get_prompt_for_doc_type(doc_type: str) -> str:
    """Returns the appropriate prompt for the document type."""
    prompts = {
        "khatian": _KHATIAN_PROMPT,
        "porcha": _PORCHA_PROMPT,
        "deed": _DEED_PROMPT,
    }
    return prompts.get(doc_type.strip().lower(), _KHATIAN_PROMPT)


def _read_image_as_base64(file_path: Path) -> tuple[str, str]:
    """Reads an image file and returns (base64_data, mime_type)."""
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        suffix = file_path.suffix.lower()
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".pdf": "application/pdf"}
        mime_type = mime_map.get(suffix, "image/png")

    data = file_path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return b64, mime_type


def _parse_gemini_response(text: str) -> Dict[str, Any]:
    """Parses the Gemini response text into a dict, handling markdown code blocks."""
    cleaned = text.strip()
    # Strip markdown json fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Gemini response as JSON: {e}")
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        # Return raw text as fallback
        return {"full_text": text, "extracted_fields": {}, "confidence": 0.5}


def run_gemini_ocr(
    file_path: Union[str, Path],
    doc_type: str = "khatian",
) -> Optional[Dict[str, Any]]:
    """
    Runs Gemini Vision OCR on a document image.

    Returns dict with:
    {
        "text": str,           # Full OCR text
        "confidence": float,   # 0.0-1.0
        "words": list,         # Empty for Gemini (no bounding boxes)
        "extracted_fields": dict,
        "engine": "gemini_vision"
    }

    Returns None if Gemini is unavailable or fails.
    """
    client = _get_client()
    if client is None:
        return None

    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return None

    try:
        prompt = _get_prompt_for_doc_type(doc_type)
        b64_data, mime_type = _read_image_as_base64(file_path)

        from google.genai import types

        # Build the request
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type,
                                data=base64.b64decode(b64_data),
                            )
                        ),
                        types.Part(text=_BASE_SYSTEM_PROMPT + "\n\n" + prompt),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=4096,
            ),
        )

        if not response or not response.text:
            logger.warning("Gemini returned empty response")
            return None

        parsed = _parse_gemini_response(response.text)

        full_text = parsed.get("full_text", "")
        extracted = parsed.get("extracted_fields", {})
        confidence = parsed.get("confidence", 0.85)

        # Clean out null fields
        extracted = {k: v for k, v in extracted.items() if v is not None and v != "" and v != "null"}

        logger.info(
            f"Gemini OCR completed for {file_path.name}: "
            f"{len(extracted)} fields extracted, confidence={confidence}"
        )

        return {
            "text": full_text,
            "confidence": float(confidence),
            "words": [],
            "extracted_fields": extracted,
            "engine": "gemini_vision",
        }

    except Exception as e:
        logger.error(f"Gemini OCR failed: {e}", exc_info=True)
        return None


def is_gemini_available() -> bool:
    """Check if Gemini API is configured and available."""
    return _get_client() is not None
