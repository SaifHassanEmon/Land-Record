import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Bengali to English digit translation map
BN_TO_EN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
EN_TO_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bn_to_en(text: str) -> str:
    """Converts Bengali numerals to English numerals."""
    return text.translate(BN_TO_EN_DIGITS)


def clean_field_value(value: Optional[str]) -> Optional[str]:
    """Cleans punctuation, colons, extra dashes, and whitespace from field values."""
    if not value:
        return None
    val = re.sub(r"^[\s:：\-—–.=|_।]+", "", value)
    val = re.sub(r"[\s:：\-—–.=|_।]+$", "", val)
    val = re.sub(r"\s+", " ", val)
    return val.strip() if val.strip() else None


def search_first_match(patterns: List[str], text: str, flags: int = re.IGNORECASE) -> Optional[str]:
    """Tries multiple regex patterns in order and returns the first stripped match."""
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            group_val = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
            cleaned = clean_field_value(group_val)
            if cleaned:
                return cleaned
    return None


def extract_khatian_fields(ocr_text: str) -> Dict[str, Any]:
    """
    Extracts structured fields from Bengali Khatian (Record of Rights / Porcha):
    - khatian_number
    - district
    - upazila
    - union_name
    - mouza
    - jl_number
    - owner_name
    - plot_numbers
    - total_area
    """
    fields: Dict[str, Any] = {}

    # 1. Khatian Number
    khatian_patterns = [
        r"(?:খতিয়ান|খতিয়ান)\s*(?:নম্বর|নং|নঃ)?\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"Khatian\s*(?:No|Number)?\s*[:：\-—–.=]?\s*([0-9০-৯\-/]+)",
        r"(?:খং|খঃ)\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
    ]
    fields["khatian_number"] = search_first_match(khatian_patterns, ocr_text)

    # 2. District (জেলা)
    district_patterns = [
        r"(?:জেলা|জিলা)\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s]+?)(?=\s+(?:উপজেলা|থানা|মৌজা|জে|খতিয়ান|$|\n))",
        r"District\s*[:：\-—–.=]?\s*([a-zA-Z\s]+?)(?=\s+(?:Upazila|Thana|Mouza|$|\n))",
    ]
    fields["district"] = search_first_match(district_patterns, ocr_text)

    # 3. Upazila / Thana (উপজেলা / থানা)
    upazila_patterns = [
        r"(?:উপজেলা|থানা)\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s]+?)(?=\s+(?:জেলা|মৌজা|ইউনিয়ন|জে|$|\n))",
        r"(?:Upazila|Thana)\s*[:：\-—–.=]?\s*([a-zA-Z\s]+?)(?=\s+(?:District|Mouza|Union|$|\n))",
    ]
    fields["upazila"] = search_first_match(upazila_patterns, ocr_text)

    # 4. Union (ইউনিয়ন / ইউনিয়ন)
    union_patterns = [
        r"(?:ইউনিয়ন|ইউনিয়ন)\s*(?:নং)?\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s0-9০-৯]+?)(?=\s+(?:উপজেলা|মৌজা|$|\n))",
        r"Union\s*(?:No)?\s*[:：\-—–.=]?\s*([a-zA-Z0-9\s]+?)(?=\s+(?:Upazila|Mouza|$|\n))",
    ]
    fields["union_name"] = search_first_match(union_patterns, ocr_text)

    # 5. Mouza (মৌজা)
    mouza_patterns = [
        r"(?:মৌজা|মৌজার\s*নাম)\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s]+?)(?=\s+(?:জে\s*এল|জেএল|দাগ|খতিয়ান|$|\n))",
        r"Mouza\s*[:：\-—–.=]?\s*([a-zA-Z\s]+?)(?=\s+(?:J\.?L\.?|Plot|$|\n))",
    ]
    fields["mouza"] = search_first_match(mouza_patterns, ocr_text)

    # 6. J.L Number (জে এল নং)
    jl_patterns = [
        r"(?:জে\s*[.]?\s*এল\s*[.]?\s*(?:নং|নম্বর)?|জেএল\s*নং)\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"(?:J\.?L\.?\s*(?:No|Number)?)\s*[:：\-—–.=]?\s*([0-9০-৯\-/]+)",
    ]
    fields["jl_number"] = search_first_match(jl_patterns, ocr_text)

    # 7. Owner / Tenant Name (মালিক / প্রজা / দখলদার)
    owner_patterns = [
        r"মালিকের\s*নাম\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s.,]+?)(?=\s+(?:পিতার|পিতা|মাতার|মাতা|এনআইডি|ঠিকানা|দাগ|অংশ|মোট|$|\n))",
        r"(?:মালিক(?:\w*)|দখলদার|প্রজার\s*নাম|স্বত্বাধিকারী|রায়তের\s*নাম)\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s,]+?)(?=\s+(?:পিতা|স্বামী|দাগ|অংশ|মোট|$|\n))",
        r"(?:Owner(?:\'s)?\s*Name|Tenant(?:\'s)?\s*Name)\s*[:：\-—–.=]?\s*([a-zA-Z\s,]+?)(?=\s+(?:Father|Plot|Area|$|\n))",
    ]
    fields["owner_name"] = search_first_match(owner_patterns, ocr_text)

    # 8. Plot / Dag Numbers (দাগ নং)
    plot_patterns = [
        r"(?:দাগ\s*(?:নং|নম্বর)?|প্লট\s*নং)\s*[:：\-—–.=]?\s*([০-৯0-9\s,/\-]+?)(?=\s+(?:জমির|পরিমাণ|শ্রেণী|মোট|$|\n))",
        r"(?:Plot|Dag)\s*(?:No|Number)?\s*[:：\-—–.=]?\s*([0-9০-৯\s,/\-]+)",
    ]
    fields["plot_numbers"] = search_first_match(plot_patterns, ocr_text)

    # 9. Total Area (জমির পরিমাণ / মোট জমি)
    area_patterns = [
        r"(?:সর্বমোট|মোট\s*জমির\s*পরিমাণ|মোট\s*জমি)\s*[:：\-—–.=]?(?:.*?)([০-৯0-9.]+\s*(?:একর|শতক|শতাংশ|হেক্টর|বিঘা|কাঠা))",
        r"(?:মোট\s*জমির\s*পরিমাণ|জমির\s*পরিমাণ|মোট\s*জমি)\s*[:：\-—–.=]?\s*([০-৯0-9.]+\s*(?:একর|শতক|শতাংশ|বর্গফুট|বর্গমিটার|dismil|shotok|acre|acres|decimals)?)",
        r"([০-৯0-9.]+\s*(?:একর|শতক|শতাংশ))\s*(?:জমি)?",
        r"(?:Total\s*Area|Area\s*of\s*Land)\s*[:：\-—–.=]?\s*([0-9০-৯.]+\s*(?:acre|shotok|decimal|sq\s*ft)?)",
    ]
    fields["total_area"] = search_first_match(area_patterns, ocr_text)

    return fields


def extract_porcha_fields(ocr_text: str) -> Dict[str, Any]:
    """
    Extracts structured fields from Porcha documents:
    - porcha_number
    - rs_khatian
    - bs_khatian
    - issue_date
    - mouza
    - district
    - owner_name
    """
    fields: Dict[str, Any] = {}

    # 1. Porcha Number
    porcha_patterns = [
        r"(?:পর্চা|পরচা)\s*(?:নং|নম্বর)?\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"Porcha\s*(?:No|Number)?\s*[:：\-—–.=]?\s*([0-9০-৯\-/]+)",
    ]
    fields["porcha_number"] = search_first_match(porcha_patterns, ocr_text)

    # 2. RS Khatian
    rs_patterns = [
        r"(?:আর\s*[.]?\s*এস\s*[.]?\s*(?:খতিয়ান|খতিয়ান)?|RS\s*Khatian)\s*(?:নং|নম্বর)?\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
    ]
    fields["rs_khatian"] = search_first_match(rs_patterns, ocr_text)

    # 3. BS Khatian (or CS / SA)
    bs_patterns = [
        r"(?:বি\s*[.]?\s*এস\s*[.]?\s*(?:খতিয়ান|খতিয়ান)?|BS\s*Khatian)\s*(?:নং|নম্বর)?\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"(?:সি\s*[.]?\s*এস\s*[.]?\s*(?:খতিয়ান|খতিয়ান)?|CS\s*Khatian)\s*(?:নং|নম্বর)?\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"(?:এস\s*[.]?\s*এ\s*[.]?\s*(?:খতিয়ান|খতিয়ান)?|SA\s*Khatian)\s*(?:নং|নম্বর)?\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
    ]
    fields["bs_khatian"] = search_first_match(bs_patterns, ocr_text)

    # 4. Issue Date
    date_patterns = [
        r"(?:প্রদানের\s*তারিখ|ইস্যুর\s*তারিখ|তারিখ)\s*[:：\-—–.=]?\s*([০-৯0-9]{1,2}[./\-][০-৯0-9]{1,2}[./\-][০-৯0-9]{2,4})",
        r"(?:Issue\s*Date|Date)\s*[:：\-—–.=]?\s*([0-9০-৯]{1,2}[./\-][0-9০-৯]{1,2}[0-9০-৯]{2,4})",
    ]
    fields["issue_date"] = search_first_match(date_patterns, ocr_text)

    # Additional contextual fields
    khatian_extra = extract_khatian_fields(ocr_text)
    for k in ["district", "upazila", "mouza", "owner_name", "total_area"]:
        if khatian_extra.get(k):
            fields[k] = khatian_extra[k]

    return fields


def extract_deed_fields(ocr_text: str) -> Dict[str, Any]:
    """
    Extracts structured fields from Deed (দলিল) documents:
    - deed_number
    - deed_type
    - seller_name (দাতা / হস্তান্তারক)
    - buyer_name (গ্রহীতা)
    - registration_date
    - consideration_amount (পণমূল্য)
    """
    fields: Dict[str, Any] = {}

    # 1. Deed Number
    deed_num_patterns = [
        r"(?:দলিল\s*(?:নং|নম্বর|নঃ)?|দস্তাবেজ\s*নং)\s*[:：\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"Deed\s*(?:No|Number)?\s*[:：\-—–.=]?\s*([0-9০-৯\-/]+)",
    ]
    fields["deed_number"] = search_first_match(deed_num_patterns, ocr_text)

    # 2. Deed Type (দলিলের প্রকৃতি / শ্রেণি)
    deed_type_patterns = [
        r"(?:দলিলের\s*প্রকৃতি|দলিলের\s*শ্রেণি|দলিলের\s*ধরন)\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s\-]+?)(?=\s+(?:দাতা|গ্রহীতা|মূল্য|$|\n))",
        r"(সাফ\s*কবলা|হেবা\s*বিল\s*এওয়াজ|হেবা\s*বিল\s*এওয়াজ|দানপত্র|বণ্টননামা|হেবানামা|অছিয়তনামা|বায়নাবত্র|এওয়াজ\s*বদল)",
        r"(?:Deed\s*Type|Nature\s*of\s*Deed)\s*[:：\-—–.=]?\s*([a-zA-Z\s\-]+)",
    ]
    fields["deed_type"] = search_first_match(deed_type_patterns, ocr_text)

    # 3. Seller Name (দাতা / হস্তান্তরকারী / বিক্রেতা)
    seller_patterns = [
        r"(?:১ম\s*পক্ষ|প্রথম\s*পক্ষ)[^:\n]*?(?:বিক্রেতা|দাতা)[^:\n]*?[:：\-—–.=]\s*([\u0980-\u09FF\w\s.,]+?)(?=\s+(?:পিতা|স্বামী|মাতা|এনআইডি|ধর্ম|২য়|দ্বিতীয়|ঠিকানা|$|\n))",
        r"(?:দাতা|বিক্রেতা|হস্তান্তরকারী)\s*(?:র\s*নাম)?\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s,]+?)(?=\s+(?:গ্রহীতা|পিতা|স্বামী|ক্রেতা|ঠিকানা|$|\n))",
        r"(?:Seller(?:\'s)?\s*Name|Transferor)\s*[:：\-—–.=]?\s*([a-zA-Z\s,]+?)(?=\s+(?:Buyer|Father|Address|$|\n))",
    ]
    fields["seller_name"] = search_first_match(seller_patterns, ocr_text)

    # 4. Buyer Name (গ্রহীতা / ক্রেতা)
    buyer_patterns = [
        r"(?:২য়\s*পক্ষ|দ্বিতীয়\s*পক্ষ)[^:\n]*?(?:ক্রেতা|গ্রহীতা)[^:\n]*?[:：\-—–.=]\s*([\u0980-\u09FF\w\s.,]+?)(?=\s+(?:পিতা|স্বামী|মাতা|এনআইডি|ধর্ম|ঠিকানা|বিক্রিত|জমির|$|\n))",
        r"(?:গ্রহীতা|ক্রেতা)\s*(?:র\s*নাম)?\s*[:：\-—–.=]?\s*([\u0980-\u09FF\w\s,]+?)(?=\s+(?:পিতা|স্বামী|ঠিকানা|পণমূল্য|জমির|$|\n))",
        r"(?:Buyer(?:\'s)?\s*Name|Transferee)\s*[:：\-—–.=]?\s*([a-zA-Z\s,]+?)(?=\s+(?:Father|Address|Price|$|\n))",
    ]
    fields["buyer_name"] = search_first_match(buyer_patterns, ocr_text)

    # 5. Registration Date
    reg_date_patterns = [
        r"(?:রেজিস্ট্রেশন\s*তারিখ|সম্পাদনের\s*তারিখ|রেজিঃ\s*তারিখ|তারিখ)\s*[:：\-—–.=]?\s*([০-৯0-9]{1,2}[./\-][০-৯0-9]{1,2}[./\-][০-৯0-9]{2,4})",
        r"(?:Registration\s*Date|Date\s*of\s*Execution|Date)\s*[:：\-—–.=]?\s*([0-9০-৯]{1,2}[./\-][0-9০-৯]{1,2}[0-9০-৯]{2,4})",
    ]
    fields["registration_date"] = search_first_match(reg_date_patterns, ocr_text)

    # 6. Consideration Amount (পণমূল্য / বিক্রয় মূল্য)
    amount_patterns = [
        r"(?:পণমূল্য|পণ\s*মূল্য|বিক্রয়\s*মূল্য|বিক্রয়মূল্য|মূল্য)\s*[:：\-—–.=]?\s*([০-৯0-9,./]+\s*(?:টাকা|/-)?)",
        r"([০-৯0-9,./]+\s*(?:টাকা মাত্র|টাকা))",
        r"(?:Consideration\s*Amount|Total\s*Value|Price)\s*[:：\-—–.=]?\s*(?:Tk\.?|BDT)?\s*([0-9০-৯,./]+)",
    ]
    fields["consideration_amount"] = search_first_match(amount_patterns, ocr_text)

    # Additional contextual fields
    khatian_extra = extract_khatian_fields(ocr_text)
    for k in ["district", "upazila", "mouza"]:
        if khatian_extra.get(k):
            fields[k] = khatian_extra[k]

    return fields


def extract_fields(doc_type: str, ocr_text: str) -> Dict[str, Any]:
    """
    Main extraction interface.
    Extracts structured fields according to doc_type ('khatian', 'porcha', 'deed').
    Returns dictionary with extracted fields.
    """
    if not ocr_text:
        return {}

    normalized_type = (doc_type or "").strip().lower()

    if normalized_type == "khatian":
        extracted = extract_khatian_fields(ocr_text)
    elif normalized_type == "porcha":
        extracted = extract_porcha_fields(ocr_text)
    elif normalized_type == "deed":
        extracted = extract_deed_fields(ocr_text)
    else:
        # Default try khatian extractor as base
        extracted = extract_khatian_fields(ocr_text)

    # Filter out empty None values
    return {k: v for k, v in extracted.items() if v is not None}
