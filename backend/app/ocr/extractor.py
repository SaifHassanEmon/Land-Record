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
    """Cleans punctuation, colons, extra dashes, semicolons, and whitespace from field values."""
    if not value:
        return None
    val = re.sub(r"^[\s:：;\-—–.=|_।,।'\"]+", "", value)
    val = re.sub(r"[\s:：;\-—–.=|_।,।'\"]+$", "", val)
    val = re.sub(r"\s+", " ", val)
    val = val.strip()
    # Reject header labels that accidentally matched
    invalid_labels = {
        "পিতার নাম", "মালিকের নাম", "স্বামীর নাম", "দাগ নং", "খতিয়ান নং",
        "পিতা", "স্বামী", "মালিক", "ঠিকানা", "মন্তব্য", "দাগনং",
    }
    if val in invalid_labels or len(val) < 2:
        return None
    return val


def normalize_ocr_text(text: str) -> str:
    """Normalizes common OCR character confusions in Bengali government documents."""
    if not text:
        return ""
    t = text
    # Normalize common abbreviations and misrecognitions
    t = re.sub(r"মো[;:\.]", "মোঃ ", t)
    t = re.sub(r"মোছা[;:\.]", "মোছাঃ ", t)
    t = re.sub(r"জে\s*[.]?\s*এ\s*[.]?\s*এল", "জে.এল.", t)
    t = re.sub(r"জে\s*[.]?\s*এল", "জে.এল.", t)
    t = re.sub(r"খতিয়ান", "খতিয়ান", t)
    t = re.sub(r"পর্চ্চা|পরচা", "পর্চা", t)
    return t


def search_first_match(patterns: List[str], text: str, flags: int = re.IGNORECASE) -> Optional[str]:
    """Tries multiple regex patterns in order and returns the first cleaned match."""
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags):
            group_val = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
            cleaned = clean_field_value(group_val)
            if cleaned:
                return cleaned
    return None


def extract_owners_from_table(ocr_text: str) -> List[str]:
    """Extracts owner names from multi-party Bengali land record tables."""
    owners = []
    # Lines with owner prefixes
    owner_name_patterns = [
        r"(?:মোঃ|মোছাঃ|মোহাম্মদ|শ্রী|বেগম|আলী)\s+[\u0980-\u09FF\w\s]+?(?=\s+(?:পিতা|মাতা|স্বামী|মাধবপুর|দোহার|ঢাকা|বর্গা|নিজ|উত্তর|$|\n|\r|\|))",
    ]
    for line in ocr_text.split("\n"):
        line_clean = line.strip()
        # Skip table headers
        if "ক্রমিক" in line_clean or "তফসিল" in line_clean or "বিবরণ" in line_clean:
            continue
        for p in owner_name_patterns:
            for m in re.finditer(p, line_clean):
                val = clean_field_value(m.group(0))
                if val and val not in owners and len(val) > 4:
                    owners.append(val)
    return owners


def extract_khatian_fields(ocr_text: str) -> Dict[str, Any]:
    """
    Extracts structured fields from Bengali Khatian (Record of Rights):
    - khatian_number
    - district
    - upazila
    - union_name
    - mouza
    - jl_number
    - former_khatian
    - owner_name
    - father_name
    - address
    - plot_numbers
    - total_area
    - issue_date
    """
    fields: Dict[str, Any] = {}
    norm_text = normalize_ocr_text(ocr_text)

    # 1. Khatian Number
    khatian_patterns = [
        r"(?:খতিয়ান)\s*(?:নম্বর|নং|নঃ)?\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"(?:খং|খঃ)\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"Khatian\s*(?:No|Number)?\s*[:：;\-—–.=]?\s*([0-9০-৯\-/]+)",
    ]
    fields["khatian_number"] = search_first_match(khatian_patterns, norm_text)

    # 2. District (জেলা)
    district_patterns = [
        r"(?:জেলা|জিলা)\s*[:：;\-—–.=]?\s*([^\n\r,;:]{2,30}?)(?=(?:\s+(?:উপজেলা|থানা|মৌজা|জে|খতিয়ান)|$|\r|\n))",
        r"District\s*[:：;\-—–.=]?\s*([a-zA-Z\s]+?)(?=(?:\s+(?:Upazila|Thana|Mouza)|$|\r|\n))",
    ]
    fields["district"] = search_first_match(district_patterns, norm_text)

    # 3. Upazila / Thana (উপজেলা / থানা)
    upazila_patterns = [
        r"(?:উপজেলা|থানা)\s*[:：;\-—–.=]?\s*([^\n\r,;:]{2,30}?)(?=(?:\s+(?:জেলা|মৌজা|ইউনিয়ন|জে|খতিয়ান|দাগ)|$|\r|\n))",
        r"(?:Upazila|Thana)\s*[:：;\-—–.=]?\s*([a-zA-Z\s]+?)(?=(?:\s+(?:District|Mouza|Union)|$|\r|\n))",
    ]
    fields["upazila"] = search_first_match(upazila_patterns, norm_text)

    # 4. Union (ইউনিয়ন)
    union_patterns = [
        r"(?:ইউনিয়ন)\s*(?:নং)?\s*[:：;\-—–.=]?\s*([^\n\r,;:]{2,30}?)(?=(?:\s+(?:উপজেলা|মৌজা)|$|\r|\n))",
        r"Union\s*(?:No)?\s*[:：;\-—–.=]?\s*([a-zA-Z0-9\s]+?)(?=(?:\s+(?:Upazila|Mouza)|$|\r|\n))",
    ]
    fields["union_name"] = search_first_match(union_patterns, norm_text)

    # 5. Mouza (মৌজা)
    mouza_patterns = [
        r"(?:মৌজা|মৌজার\s*নাম)\s*[:：;\-—–.=]?\s*([^\n\r,;:]{2,35}?)(?=(?:\s+(?:জে|দাগ|খতিয়ান|গ্রাম|জমির)|$|\r|\n))",
        r"Mouza\s*[:：;\-—–.=]?\s*([a-zA-Z\s]+?)(?=(?:\s+(?:J\.?L\.?|Plot)|$|\r|\n))",
    ]
    fields["mouza"] = search_first_match(mouza_patterns, norm_text)

    # 6. J.L Number (জে এল নং)
    jl_patterns = [
        r"(?:জে\.?এল\.?\s*(?:নং|নম্বর)?)\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"(?:J\.?L\.?\s*(?:No|Number)?)\s*[:：;\-—–.=]?\s*([0-9০-৯\-/]+)",
    ]
    fields["jl_number"] = search_first_match(jl_patterns, norm_text)

    # 7. Former Khatian (সাবেক খতিয়ান)
    former_patterns = [
        r"(?:সাবেক\s*খতিয়ান\s*(?:নং|নম্বর)?)\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
    ]
    former_match = search_first_match(former_patterns, norm_text)
    if former_match:
        fields["former_khatian"] = former_match

    # 8. Owner Name (মালিক)
    owner_patterns = [
        r"মালিকের\s*নাম\s*[:：;\-—–.=]?\s*([^\n\r]{2,50}?)(?=(?:\s+(?:পিতার|পিতা|মাতার|মাতা|এনআইডি|ঠিকানা|দাগ|অংশ|মোট)|$|\r|\n))",
        r"(?:মালিক|দখলদার|প্রজার\s*নাম|স্বত্বাধিকারী|রায়তের\s*নাম)\s*[:：;\-—–.=]?\s*([^\n\r]{2,50}?)(?=(?:\s+(?:পিতা|স্বামী|দাগ|অংশ|মোট)|$|\r|\n))",
    ]
    fields["owner_name"] = search_first_match(owner_patterns, norm_text)

    # Fallback to multi-owner detection from table
    if not fields.get("owner_name"):
        table_owners = extract_owners_from_table(norm_text)
        if table_owners:
            fields["owner_name"] = ", ".join(table_owners)

    # 9. Father's / Husband's Name (পিতা / স্বামী)
    father_patterns = [
        r"(?:পিতার\s*নাম|পিতা|স্বামীর\s*নাম|স্বামী|from\s+নাম)\s*[:：;\-—–.=]?\s*(?:মৃত\s+|মুত\s+)?([^\n\r]{2,50}?)(?=(?:\s+(?:মাতা|মাতার|ঠিকানা|দাগ|অংশ|এনআইডি)|$|\r|\n))",
    ]
    father_match = search_first_match(father_patterns, norm_text)
    if father_match:
        fields["father_name"] = father_match

    # 10. Address (ঠিকানা)
    addr_patterns = [
        r"(?:ঠিকানা|ঠিকা)\s*[:：;\-—–.=]?\s*([^\n\r]{3,70}?)(?=(?:\s+(?:দাগ|জমির|মোট)|$|\r|\n))",
    ]
    addr_match = search_first_match(addr_patterns, norm_text)
    if addr_match:
        fields["address"] = addr_match

    # 11. Plot / Dag Numbers (দাগ নং)
    plot_patterns = [
        r"(?:দাগ\s*(?:নং|নম্বর)?|দাগনং|প্লট\s*নং)\s*[:：;\-—–.=]?\s*([০-৯0-9\s,/\-]+?)(?=(?:\s+(?:জমির|পরিমাণ|শ্রেণী|শ্রেণি|মোট|মালিকের)|$|\r|\n))",
        r"(?:Plot|Dag)\s*(?:No|Number)?\s*[:：;\-—–.=]?\s*([0-9০-৯\s,/\-]+)",
    ]
    fields["plot_numbers"] = search_first_match(plot_patterns, norm_text)

    # 12. Total Area (জমির পরিমাণ / মোট জমি)
    area_patterns = [
        r"(?:সর্বমোট|মোট\s*জমির\s*পরিমাণ|মোট\s*জমি)\s*[:：;\-—–.=]?(?:.*?)([০-৯0-9.]+\s*(?:একর|শতক|শতাংশ|হেক্টর|বিঘা|কাঠা|ছটাক)+[^\n\r]*)",
        r"(?:মোট\s*জমির\s*পরিমাণ|জমির\s*পরিমাণ|মোট\s*জমি)\s*[:：;\-—–.=]?\s*([০-৯0-9.]+\s*(?:একর|শতক|শতাংশ|বর্গফুট|বর্গমিটার|dismil|shotok|acre|acres|decimals)?)",
        r"([০-৯0-9.]+\s*(?:একর|শতক|শতাংশ))\s*(?:জমি)?",
        r"(?:Total\s*Area|Area\s*of\s*Land)\s*[:：;\-—–.=]?\s*([0-9০-৯.]+\s*(?:acre|shotok|decimal|sq\s*ft)?)",
    ]
    fields["total_area"] = search_first_match(area_patterns, norm_text)

    # 13. Issue Date (তারিখ)
    date_patterns = [
        r"(?:প্রস্তুত\s*তারিখ|ইস্যুর\s*তারিখ|তারিখ)\s*[:：;\-—–.=]?\s*([০-৯0-9]{1,2}[./\-][০-৯0-9]{1,2}[./\-][০-৯0-9]{2,4})",
    ]
    date_match = search_first_match(date_patterns, norm_text)
    if date_match:
        fields["issue_date"] = date_match

    return fields


def extract_porcha_fields(ocr_text: str) -> Dict[str, Any]:
    """Extracts structured fields from Porcha documents."""
    fields: Dict[str, Any] = {}
    norm_text = normalize_ocr_text(ocr_text)

    # 1. Porcha Number
    porcha_patterns = [
        r"(?:পর্চা|পরচা)\s*(?:নং|নম্বর)?\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"Porcha\s*(?:No|Number)?\s*[:：;\-—–.=]?\s*([0-9০-৯\-/]+)",
    ]
    fields["porcha_number"] = search_first_match(porcha_patterns, norm_text)

    # 2. RS Khatian
    rs_patterns = [
        r"(?:আর\s*[.]?\s*এস\s*[.]?\s*(?:খতিয়ান)?|RS\s*Khatian)\s*(?:নং|নম্বর)?\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
    ]
    fields["rs_khatian"] = search_first_match(rs_patterns, norm_text)

    # 3. BS Khatian (or CS / SA)
    bs_patterns = [
        r"(?:বি\s*[.]?\s*এস\s*[.]?\s*(?:খতিয়ান)?|BS\s*Khatian)\s*(?:নং|নম্বর)?\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"(?:সি\s*[.]?\s*এস\s*[.]?\s*(?:খতিয়ান)?|CS\s*Khatian)\s*(?:নং|নম্বর)?\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"(?:এস\s*[.]?\s*এ\s*[.]?\s*(?:খতিয়ান)?|SA\s*Khatian)\s*(?:নং|নম্বর)?\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
    ]
    fields["bs_khatian"] = search_first_match(bs_patterns, norm_text)

    # 4. Village (গ্রাম)
    village_patterns = [
        r"গ্রাম\s*[:：;\-—–.=]?\s*([^\n\r,;:]{2,30}?)(?=(?:\s+(?:মৌজা|উপজেলা|দাগ|মোট)|$|\r|\n))",
    ]
    fields["village"] = search_first_match(village_patterns, norm_text)

    # 5. Issue Date
    date_patterns = [
        r"(?:প্রদানের\s*তারিখ|ইস্যুর\s*তারিখ|তারিখ)\s*[:：;\-—–.=]?\s*([০-৯0-9]{1,2}[./\-][০-৯0-9]{1,2}[./\-][০-৯0-9]{2,4})",
        r"(?:Issue\s*Date|Date)\s*[:：;\-—–.=]?\s*([0-9০-৯]{1,2}[./\-][0-9০-৯]{1,2}[0-9০-৯]{2,4})",
    ]
    fields["issue_date"] = search_first_match(date_patterns, norm_text)

    # Additional contextual fields from khatian
    khatian_extra = extract_khatian_fields(norm_text)
    for k in ["district", "upazila", "mouza", "owner_name", "father_name", "plot_numbers", "total_area", "khatian_number"]:
        if khatian_extra.get(k):
            fields[k] = khatian_extra[k]

    return fields


def extract_deed_fields(ocr_text: str) -> Dict[str, Any]:
    """Extracts structured fields from Deed (দলিল) documents."""
    fields: Dict[str, Any] = {}
    norm_text = normalize_ocr_text(ocr_text)

    # 1. Deed Number
    deed_num_patterns = [
        r"(?:দলিল\s*(?:নং|নম্বর|নঃ)?|দস্তাবেজ\s*নং)\s*[:：;\-—–.=]?\s*([০-৯0-9\-/]+)",
        r"Deed\s*(?:No|Number)?\s*[:：;\-—–.=]?\s*([0-9০-৯\-/]+)",
    ]
    fields["deed_number"] = search_first_match(deed_num_patterns, norm_text)

    # 2. Deed Type (দলিলের প্রকৃতি / শ্রেণি)
    deed_type_patterns = [
        r"(?:দলিলের\s*প্রকৃতি|দলিলের\s*শ্রেণি|দলিলের\s*ধরন)\s*[:：;\-—–.=]?\s*([\u0980-\u09FF\w\s\-]+?)(?=(?:\s+(?:দাতা|গ্রহীতা|মূল্য)|$|\r|\n))",
        r"(সাফ\s*কবলা|হেবা\s*বিল\s*এওয়াজ|হেবা\s*বিল\s*এওয়াজ|দানপত্র|বণ্টননামা|হেবানামা|অছিয়তনামা|বায়নাবত্র|এওয়াজ\s*বদল)",
        r"(?:Deed\s*Type|Nature\s*of\s*Deed)\s*[:：;\-—–.=]?\s*([a-zA-Z\s\-]+)",
    ]
    fields["deed_type"] = search_first_match(deed_type_patterns, norm_text)

    # 3. Seller Name (দাতা / হস্তান্তরকারী / বিক্রেতা)
    seller_patterns = [
        r"(?:১ম\s*পক্ষ|প্রথম\s*পক্ষ)[^:\n]*?(?:বিক্রেতা|দাতা)[^:\n]*?[:：;\-—–.=]\s*([\u0980-\u09FF\w\s.,]+?)(?=(?:\s+(?:পিতা|স্বামী|মাতা|এনআইডি|ধর্ম|২য়|দ্বিতীয়|ঠিকানা)|$|\r|\n))",
        r"(?:দাতা|বিক্রেতা|হস্তান্তরকারী)\s*(?:র\s*নাম)?\s*[:：;\-—–.=]?\s*([\u0980-\u09FF\w\s,]+?)(?=(?:\s+(?:গ্রহীতা|পিতা|স্বামী|ক্রেতা|ঠিকানা)|$|\r|\n))",
        r"(?:Seller(?:\'s)?\s*Name|Transferor)\s*[:：;\-—–.=]?\s*([a-zA-Z\s,]+?)(?=(?:\s+(?:Buyer|Father|Address)|$|\r|\n))",
    ]
    fields["seller_name"] = search_first_match(seller_patterns, norm_text)

    # 4. Buyer Name (গ্রহীতা / ক্রেতা)
    buyer_patterns = [
        r"(?:২য়\s*পক্ষ|দ্বিতীয়\s*পক্ষ)[^:\n]*?(?:ক্রেতা|গ্রহীতা)[^:\n]*?[:：;\-—–.=]\s*([\u0980-\u09FF\w\s.,]+?)(?=(?:\s+(?:পিতা|স্বামী|মাতা|এনআইডি|ধর্ম|ঠিকানা|বিক্রিত|জমির)|$|\r|\n))",
        r"(?:গ্রহীতা|ক্রেতা)\s*(?:র\s*নাম)?\s*[:：;\-—–.=]?\s*([\u0980-\u09FF\w\s,]+?)(?=(?:\s+(?:পিতা|স্বামী|ঠিকানা|পণমূল্য|জমির)|$|\r|\n))",
        r"(?:Buyer(?:\'s)?\s*Name|Transferee)\s*[:：;\-—–.=]?\s*([a-zA-Z\s,]+?)(?=(?:\s+(?:Father|Address|Price)|$|\r|\n))",
    ]
    fields["buyer_name"] = search_first_match(buyer_patterns, norm_text)

    # 5. Registration Date
    reg_date_patterns = [
        r"(?:রেজিস্ট্রেশন\s*তারিখ|সম্পাদনের\s*তারিখ|রেজিঃ\s*তারিখ|তারিখ)\s*[:：;\-—–.=]?\s*([০-৯0-9]{1,2}[./\-][০-৯0-9]{1,2}[./\-][০-৯0-9]{2,4})",
        r"(?:Registration\s*Date|Date\s*of\s*Execution|Date)\s*[:：;\-—–.=]?\s*([0-9০-৯]{1,2}[./\-][0-9০-৯]{1,2}[0-9০-৯]{2,4})",
    ]
    fields["registration_date"] = search_first_match(reg_date_patterns, norm_text)

    # 6. Consideration Amount (পণমূল্য / বিক্রয় মূল্য)
    amount_patterns = [
        r"(?:পণমূল্য|পণ\s*মূল্য|বিক্রয়\s*মূল্য|বিক্রয়মূল্য|মূল্য)\s*[:：;\-—–.=]?\s*([০-৯0-9,./]+\s*(?:টাকা|/-)?)",
        r"([০-৯0-9,./]+\s*(?:টাকা মাত্র|টাকা))",
        r"(?:Consideration\s*Amount|Total\s*Value|Price)\s*[:：;\-—–.=]?\s*(?:Tk\.?|BDT)?\s*([0-9০-৯,./]+)",
    ]
    fields["consideration_amount"] = search_first_match(amount_patterns, norm_text)

    # Additional contextual fields
    khatian_extra = extract_khatian_fields(norm_text)
    for k in ["district", "upazila", "mouza"]:
        if khatian_extra.get(k):
            fields[k] = khatian_extra[k]

    return fields


def extract_fields(doc_type: str, ocr_text: str) -> Dict[str, Any]:
    """
    Main extraction interface.
    Extracts structured fields according to doc_type ('khatian', 'porcha', 'deed').
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
        extracted = extract_khatian_fields(ocr_text)

    return {k: v for k, v in extracted.items() if v is not None and str(v).strip()}
