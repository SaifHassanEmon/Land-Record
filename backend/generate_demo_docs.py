#!/usr/bin/env python3
"""
generate_demo_docs.py
---------------------
Generates realistic demo Bengali land record documents for Bangladesh's Land Ministry system:
1. demo_docs/khatian_demo.pdf — A Khatian (খতিয়ান) document (Record of Rights / জমাবন্দি)
2. demo_docs/porcha_demo.pdf  — A Porcha (পর্চা) document (Land Development Tax Receipt / দাখিলা)
3. demo_docs/deed_demo.pdf    — A Legal Deed (দলিল) document (Registered Sale Deed / সাফ-কবলা)

Usage:
    python backend/generate_demo_docs.py
    # or inside backend/:
    python generate_demo_docs.py
"""

import os
import sys
import urllib.request
from pathlib import Path

# Force UTF-8 output on Windows (avoids UnicodeEncodeError in CP1252 terminals)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle

# Page dimensions (A4 in points: 595.27 x 841.89)
PAGE_WIDTH, PAGE_HEIGHT = A4

# Output directory relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "demo_docs"


# =============================================================================
# 1. BENGALI FONT SETUP
# =============================================================================

def setup_bengali_font(target_dir: Path) -> tuple[str, str]:
    """
    Ensures a valid Bengali TrueType font is registered with ReportLab.
    Downloads Hind Siliguri font if not locally present.
    Returns (regular_font_name, bold_font_name).
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    reg_font_file = target_dir / "HindSiliguri-Regular.ttf"
    bold_font_file = target_dir / "HindSiliguri-Bold.ttf"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # Candidates for Regular font — using Noto Sans Bengali (reliable jsDelivr CDN)
    reg_urls = [
        "https://cdn.jsdelivr.net/gh/googlefonts/noto-fonts@main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf",
        "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf",
        "https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-bengali@5.0.3/files/noto-sans-bengali-bengali-400-normal.woff2",
    ]

    # Download regular font if needed
    if not (reg_font_file.exists() and reg_font_file.stat().st_size > 15000):
        print(f"[*] Bengali regular font not found. Downloading to {reg_font_file}...")
        downloaded = False
        for url in reg_urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=12) as resp, open(reg_font_file, "wb") as out_f:
                    out_f.write(resp.read())
                if reg_font_file.exists() and reg_font_file.stat().st_size > 15000:
                    print(f"    [+] Successfully downloaded: {reg_font_file.name} ({reg_font_file.stat().st_size} bytes)")
                    downloaded = True
                    break
            except Exception as e:
                print(f"    [-] Failed downloading from {url}: {e}")

        # Fallback to Windows system fonts if download failed
        if not downloaded:
            win_fallbacks = [
                Path(r"C:\Windows\Fonts\vrinda.ttf"),
                Path(r"C:\Windows\Fonts\Nirmala.ttf"),
                Path(r"C:\Windows\Fonts\Kalpurush.ttf"),
                Path(r"C:\Windows\Fonts\SolaimanLipi.ttf"),
            ]
            for wf in win_fallbacks:
                if wf.exists() and wf.stat().st_size > 15000:
                    print(f"    [+] Using Windows system Bengali font: {wf}")
                    reg_font_file = wf
                    break

    # Candidates for Bold font
    bold_urls = [
        "https://fonts.gstatic.com/s/hindsiliguri/v18/ijwRs5juQtMx-MWNV3bpku0GlgE7f2E.ttf",
        "https://raw.githubusercontent.com/googlefonts/hindsiliguri/main/fonts/ttf/HindSiliguri-Bold.ttf",
        "https://github.com/googlefonts/hindsiliguri/raw/main/fonts/ttf/HindSiliguri-Bold.ttf",
    ]

    if not (bold_font_file.exists() and bold_font_file.stat().st_size > 15000):
        for url in bold_urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp, open(bold_font_file, "wb") as out_f:
                    out_f.write(resp.read())
                if bold_font_file.exists() and bold_font_file.stat().st_size > 15000:
                    break
            except Exception:
                pass

    if not (bold_font_file.exists() and bold_font_file.stat().st_size > 15000):
        bold_font_file = reg_font_file  # Alias regular as bold fallback

    # Register fonts in ReportLab
    reg_name = "BengaliFont"
    bold_name = "BengaliFont-Bold"

    pdfmetrics.registerFont(TTFont(reg_name, str(reg_font_file)))
    pdfmetrics.registerFont(TTFont(bold_name, str(bold_font_file)))

    # Also register HindSiliguri aliases
    pdfmetrics.registerFont(TTFont("HindSiliguri", str(reg_font_file)))
    pdfmetrics.registerFont(TTFont("HindSiliguri-Bold", str(bold_font_file)))

    return reg_name, bold_name


# =============================================================================
# 2. DRAWING HELPERS (BORDERS, SEALS, WATERMARKS, CARDS)
# =============================================================================

def draw_double_border(c: canvas.Canvas, stroke_color: colors.Color, fill_color: colors.Color = None):
    """Draws an official double frame border around the page with decorative corners."""
    c.saveState()
    # Outer rectangle
    c.setStrokeColor(stroke_color)
    c.setLineWidth(1.6)
    if fill_color:
        c.setFillColor(fill_color)
        c.rect(20, 20, PAGE_WIDTH - 40, PAGE_HEIGHT - 40, fill=1, stroke=1)
    else:
        c.rect(20, 20, PAGE_WIDTH - 40, PAGE_HEIGHT - 40, fill=0, stroke=1)

    # Inner rectangle
    c.setLineWidth(0.6)
    c.rect(24, 24, PAGE_WIDTH - 48, PAGE_HEIGHT - 48, fill=0, stroke=1)

    # Decorative corner squares
    corner_size = 5
    c.setFillColor(stroke_color)
    for x in [24, PAGE_WIDTH - 24 - corner_size]:
        for y in [24, PAGE_HEIGHT - 24 - corner_size]:
            c.rect(x, y, corner_size, corner_size, fill=1, stroke=0)
    c.restoreState()


def draw_watermark(c: canvas.Canvas, text: str, font_name: str):
    """Draws a faint diagonal watermark across the page."""
    c.saveState()
    c.setFont(font_name, 36)
    c.setFillColor(colors.HexColor("#0f172a"), alpha=0.04)
    c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
    c.rotate(35)
    c.drawCentredString(0, 0, text)
    c.restoreState()


def draw_circular_seal(c: canvas.Canvas, cx: float, cy: float, radius: float,
                       outer_color: colors.Color, seal_text: str, font_name: str):
    """Draws a stylized Bangladesh Government circular emblem/seal."""
    c.saveState()
    # Outer circle
    c.setStrokeColor(outer_color)
    c.setLineWidth(1.2)
    c.circle(cx, cy, radius, stroke=1, fill=0)

    # Inner circle
    c.setLineWidth(0.6)
    c.circle(cx, cy, radius - 2.5, stroke=1, fill=0)

    # Central emblem star / star cluster
    c.setFillColor(outer_color)
    c.setFont(font_name, 10)
    c.drawCentredString(cx, cy - 3.5, "★")

    # Star accents around seal
    c.setFont(font_name, 6)
    c.drawCentredString(cx - 10, cy - 2, "★")
    c.drawCentredString(cx + 10, cy - 2, "★")
    c.restoreState()


def draw_qr_verification_box(c: canvas.Canvas, x: float, y: float, size: float,
                             label: str, sub_label: str, font_reg: str, font_bold: str):
    """Draws a simulated digital verification QR box."""
    c.saveState()
    # Outer frame
    c.setStrokeColor(colors.HexColor("#64748b"))
    c.setLineWidth(0.6)
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.roundRect(x, y, size, size, 3, fill=1, stroke=1)

    # Simulated QR pixel grid corners
    c.setFillColor(colors.HexColor("#1e293b"))
    # Top-left finder pattern
    c.rect(x + 5, y + size - 17, 12, 12, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.rect(x + 7, y + size - 15, 8, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.rect(x + 9, y + size - 13, 4, 4, fill=1, stroke=0)

    # Top-right finder pattern
    c.rect(x + size - 17, y + size - 17, 12, 12, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.rect(x + size - 15, y + size - 15, 8, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.rect(x + size - 13, y + size - 13, 4, 4, fill=1, stroke=0)

    # Bottom-left finder pattern
    c.rect(x + 5, y + 5, 12, 12, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.rect(x + 7, y + 7, 8, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.rect(x + 9, y + 9, 4, 4, fill=1, stroke=0)

    # Simulated data dots in middle
    for dx in [22, 28, 34, 40]:
        for dy in [8, 14, 20, 26, 32, 38]:
            if (dx + dy) % 3 == 0 or (dx * dy) % 5 == 0:
                c.rect(x + dx, y + dy, 3.5, 3.5, fill=1, stroke=0)

    # Labels below QR
    c.setFont(font_bold, 7)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawCentredString(x + size / 2, y - 10, label)
    c.setFont(font_reg, 6)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(x + size / 2, y - 18, sub_label)
    c.restoreState()


# =============================================================================
# 3. DOCUMENT 1: KHATIAN (জমাবন্দি - খতিয়ান)
# =============================================================================

def generate_khatian_pdf(output_path: Path, font_reg: str, font_bold: str):
    """
    Generates a realistic Jamabandi Khatian (খতিয়ান) document.
    Government of Bangladesh Land Ministry - BS Survey Record of Rights.
    """
    c = canvas.Canvas(str(output_path), pagesize=A4)
    primary_color = colors.HexColor("#064e3b")    # Deep Bangladesh Forest Green
    dark_slate = colors.HexColor("#0f172a")

    draw_double_border(c, stroke_color=primary_color)
    draw_watermark(c, "বাংলাদেশ সরকার — ডিজিটাল খতিয়ান", font_bold)

    # Top Official Seal
    draw_circular_seal(c, cx=PAGE_WIDTH / 2, cy=800, radius=13,
                       outer_color=primary_color, seal_text="", font_name=font_bold)

    # Top Form Header
    c.setFont(font_reg, 8)
    c.setFillColor(dark_slate)
    c.drawString(32, 804, "বাংলাদেশ ফরম নং ১০৭৭ (সংশোধিত)")
    c.drawRightString(PAGE_WIDTH - 32, 804, "ডিজিটাল ল্যান্ড রেকর্ড ও জরিপ")

    # Government Title
    c.setFont(font_bold, 14)
    c.setFillColor(primary_color)
    c.drawCentredString(PAGE_WIDTH / 2, 775, "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার")

    c.setFont(font_reg, 9.5)
    c.setFillColor(dark_slate)
    c.drawCentredString(PAGE_WIDTH / 2, 760, "ভূমি মন্ত্রণালয় / ভূমি রেকর্ড ও জরিপ অধিদপ্তর")

    # Document Name Banner
    banner_w, banner_h = 240, 22
    banner_x = (PAGE_WIDTH - banner_w) / 2
    banner_y = 730
    c.setFillColor(primary_color)
    c.roundRect(banner_x, banner_y, banner_w, banner_h, 3, fill=1, stroke=1)

    c.setFont(font_bold, 12.5)
    c.setFillColor(colors.white)
    c.drawCentredString(PAGE_WIDTH / 2, banner_y + 6, "জমাবন্দি - খতিয়ান")

    # Subtitle & Survey Type
    c.setFont(font_bold, 9.5)
    c.setFillColor(dark_slate)
    c.drawCentredString(PAGE_WIDTH / 2, 715, "জরিপের ধরন: বি. এস. জরিপ (বাংলাদেশ সার্ভে)")

    # Top Right Highlight: Khatian Number Badge
    badge_x = PAGE_WIDTH - 150
    badge_y = 728
    c.setStrokeColor(primary_color)
    c.setFillColor(colors.HexColor("#f0fdf4"))
    c.roundRect(badge_x, badge_y, 118, 24, 3, fill=1, stroke=1)
    c.setFont(font_bold, 11)
    c.setFillColor(primary_color)
    c.drawCentredString(badge_x + 59, badge_y + 7, "খতিয়ান নং: ৪৫৬")

    # -------------------------------------------------------------------------
    # Location / Administrative Hierarchy Box
    # -------------------------------------------------------------------------
    loc_table_data = [
        ["জেলা: ঢাকা", "উপজেলা / থানা: সাভার", "ইউনিয়ন: আমিনবাজার"],
        ["মৌজা: উত্তর সাভার", "জে. এল. নং: ১৪২", "তৌজি নং: ৫৪৩০ / রে. সা."],
    ]
    loc_table = Table(loc_table_data, colWidths=[178, 178, 179])
    loc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    loc_table.wrapOn(c, 535, 60)
    loc_table.drawOn(c, 30, 660)

    # -------------------------------------------------------------------------
    # Ownership Details Section (মালিকগণের বিবরণ)
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 10)
    c.setFillColor(primary_color)
    c.drawString(32, 642, "১ নং কলাম: অংশীদার ও মালিকগণের বিবরণ")

    owner_data = [
        ["মালিকের নাম:", "মোঃ আবদুল করিম", "পিতার নাম:", "মোঃ রহিম উদ্দিন"],
        ["মাতার নাম:", "মোসাঃ সালেহা বেগম", "এনআইডি:", "১৯৮৫২৬৯৮৭৪৫৬৩২১০"],
        ["ঠিকানা:", "গ্রাম: উত্তর সাভার, ডাকঘর: আমিনবাজার, উপজেলা: সাভার, জেলা: ঢাকা", "", ""],
        ["অংশ:", "১.০০০ (সমগ্র অংশ)", "হিসাব নং:", "জোত নং- ৪৫৬/২০২৪"],
    ]
    owner_table = Table(owner_data, colWidths=[80, 185, 75, 195])
    owner_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_reg),
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (2, 0), (2, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('SPAN', (1, 2), (3, 2)),  # Address spans columns
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    owner_table.wrapOn(c, 535, 100)
    owner_table.drawOn(c, 30, 560)

    # -------------------------------------------------------------------------
    # Land & Plot Details Table (দাগ ও জমির বিবরণ)
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 10)
    c.setFillColor(primary_color)
    c.drawString(32, 542, "২ ও ৩ নং কলাম: দাগ নং এবং জমির শ্রেণী ও পরিমাণের বিবরণ")

    plot_data = [
        ["দাগ নং", "জমির শ্রেণী", "দাগের মোট জমি (একর)", "অত্র খতিয়ানের অংশ", "জমির পরিমাণ (একর)", "দখল ও মন্তব্য"],
        ["১২৩", "কৃষি জমি (নাল)", "০.৩৫", "১.০০০", "০.৩৫", "নিজস্ব ভোগদখলীয় নাল জমি"],
        ["১২৪", "কৃষি জমি (ভিটি)", "০.২৫", "১.০০০", "০.২৫", "বসতবাড়ি সংলগ্ন আবাদি জমি"],
        ["১২৫", "কৃষি জমি (বাগান)", "০.১৫", "১.০০০", "০.১৫", "আম ও কাঁঠাল ফলের বাগান"],
        ["মোট জমি:", "৩টি দাগ সর্বমোট", "০.৭৫ একর", "-", "০.৭৫ একর", "কথায়: পঁচাত্তর শতাংশ জমি মাত্র"],
    ]
    plot_table = Table(plot_data, colWidths=[55, 95, 95, 85, 95, 110])
    plot_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_reg),
        ('FONTNAME', (0, -1), (-1, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#ffffff")),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#ffffff")),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor("#e2e8f0")),
        ('TEXTCOLOR', (0, 4), (-1, 4), primary_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (5, 1), (5, -1), 6),
    ]))
    plot_table.wrapOn(c, 535, 140)
    plot_table.drawOn(c, 30, 422)

    # -------------------------------------------------------------------------
    # Revenue & Mutation Tracking Box
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 10)
    c.setFillColor(primary_color)
    c.drawString(32, 405, "৪ নং কলাম: রাজস্ব ও অন্যান্য বিশেষ বিবরণ")

    rev_data = [
        ["পূর্ববর্তী খতিয়ান রেফারেন্স:", "আর এস খতিয়ান নং ৩২১", "সর্বশেষ দাখিলা নং:", "LD-2024-98761"],
        ["নামজারি ও জমাভাগ কেস:", "মিউটেশন কেস নং- ৮৯২/সাভার/২০২৪", "ভূমি উন্নয়ন কর স্ট্যাটাস:", "হাল সন ২০২৪-২৫ পর্যন্ত পরিশোধিত"],
        ["মন্তব্য ও সরকারি নোট:", "অত্র খতিয়ানের জমিতে কোনো সরকারি বা ওয়াকফ খাস স্বার্থ জড়িত নাই।", "", ""],
    ]
    rev_table = Table(rev_data, colWidths=[120, 150, 115, 150])
    rev_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_reg),
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (2, 0), (2, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('SPAN', (1, 2), (3, 2)),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    rev_table.wrapOn(c, 535, 80)
    rev_table.drawOn(c, 30, 335)

    # -------------------------------------------------------------------------
    # Digital Verification Box & QR Code
    # -------------------------------------------------------------------------
    cert_box_y = 245
    cert_box_h = 75
    c.setStrokeColor(colors.HexColor("#94a3b8"))
    c.setFillColor(colors.HexColor("#f1f5f9"))
    c.roundRect(30, cert_box_y, 440, cert_box_h, 3, fill=1, stroke=1)

    c.setFont(font_bold, 8.5)
    c.setFillColor(primary_color)
    c.drawString(40, cert_box_y + 58, "ডিজিটাল সনদ ও সত্যায়ন বিবরণী:")

    c.setFont(font_reg, 8)
    c.setFillColor(dark_slate)
    c.drawString(40, cert_box_y + 44, "প্রত্যয়ন করা যাইতেছে যে, অত্র খতিয়ানটি ভূমি মন্ত্রণালয়ের ডিজিটাল ডাটাবেজ (DLRMS) হইতে সংগৃহীত ও মুদ্রিত।")
    c.drawString(40, cert_box_y + 31, "ইস্যু তারিখ: ১৫ অক্টোবর ২০২৪  |  ট্র্যাকিং কোড: DLRMS-DH-SAV-2024-BS-0456")
    c.drawString(40, cert_box_y + 18, "অনলাইন যাচাইকরণ লিংক: https://dlrms.land.gov.bd/verify?ref=BS456-DH")
    c.drawString(40, cert_box_y + 6, "বিশেষ সতর্কতা: ডিজিটাল খতিয়ানে কোনো প্রকার ম্যানুয়াল সংশোধন বা ঘষামাজা গ্রহণযোগ্য নহে।")

    # QR Code placeholder
    draw_qr_verification_box(c, x=485, y=cert_box_y + 2, size=70,
                             label="অনলাইন যাচাই", sub_label="স্ক্যান করুন",
                             font_reg=font_reg, font_bold=font_bold)

    # -------------------------------------------------------------------------
    # Official Signatures Section
    # -------------------------------------------------------------------------
    sig_y = 135
    c.setStrokeColor(colors.HexColor("#475569"))
    c.setLineWidth(0.6)

    # Signature 1: Assistant / Surveyor
    c.line(45, sig_y, 165, sig_y)
    c.setFont(font_reg, 8)
    c.setFillColor(dark_slate)
    c.drawCentredString(105, sig_y - 12, "প্রস্তুতকারীর স্বাক্ষর")
    c.setFont(font_bold, 8)
    c.drawCentredString(105, sig_y - 23, "অফিস সহকারী / সার্ভেয়ার")
    c.setFont(font_reg, 7.5)
    c.drawCentredString(105, sig_y - 34, "আমিনবাজার ইউনিয়ন ভূমি অফিস")

    # Signature 2: Kanungo / Verifier
    c.line(235, sig_y, 355, sig_y)
    c.setFont(font_reg, 8)
    c.drawCentredString(295, sig_y - 12, "যাচাইকারীর স্বাক্ষর")
    c.setFont(font_bold, 8)
    c.drawCentredString(295, sig_y - 23, "উপ-সহকারী ভূমি কর্মকর্তা / কানুনগো")
    c.setFont(font_reg, 7.5)
    c.drawCentredString(295, sig_y - 34, "উপজেলা ভূমি অফিস, সাভার")

    # Signature 3: Assistant Commissioner (Land) - Official Seal
    c.line(425, sig_y, 545, sig_y)
    c.setFont(font_reg, 8)
    c.drawCentredString(485, sig_y - 12, "সহকারী কমিশনার (ভূমি)")
    c.setFont(font_bold, 8)
    c.setFillColor(primary_color)
    c.drawCentredString(485, sig_y - 23, "সাভার, ঢাকা")
    c.setFont(font_reg, 7.5)
    c.setFillColor(dark_slate)
    c.drawCentredString(485, sig_y - 34, "[ডিজিটাল সীল মোহর ও অনুমোদন]")

    # Bottom notice banner
    c.setFont(font_reg, 7.5)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawCentredString(PAGE_WIDTH / 2, 45, "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার — ভূমি মন্ত্রণালয় | জনস্বার্থে ডিজিটাল রেকর্ড সংরক্ষণাগার")

    c.showPage()
    c.save()
    print(f"[+] Generated Khatian PDF: {output_path}")


# =============================================================================
# 4. DOCUMENT 2: PORCHA / LD TAX RECEIPT (ভূমি উন্নয়ন কর রসিদ / পর্চা)
# =============================================================================

def generate_porcha_pdf(output_path: Path, font_reg: str, font_bold: str):
    """
    Generates a realistic Porcha (পর্চা) / Land Development Tax Receipt document.
    Government of Bangladesh Land Ministry - Chittagong District, Hathazari Upazila.
    """
    c = canvas.Canvas(str(output_path), pagesize=A4)
    primary_color = colors.HexColor("#881337")    # Deep Burgundy / Official Treasury Crimson
    dark_slate = colors.HexColor("#0f172a")

    draw_double_border(c, stroke_color=primary_color)
    draw_watermark(c, "বাংলাদেশ সরকার — ভূমি উন্নয়ন কর রসিদ", font_bold)

    # Top Emblem
    draw_circular_seal(c, cx=PAGE_WIDTH / 2, cy=800, radius=13,
                       outer_color=primary_color, seal_text="", font_name=font_bold)

    # Top Form Header
    c.setFont(font_reg, 8)
    c.setFillColor(dark_slate)
    c.drawString(32, 804, "বাংলাদেশ ফরম নং ১০৭৭")
    c.drawRightString(PAGE_WIDTH - 32, 804, "অনলাইন ভূমি উন্নয়ন কর ও দাখিলা")

    # Government Title
    c.setFont(font_bold, 14)
    c.setFillColor(primary_color)
    c.drawCentredString(PAGE_WIDTH / 2, 775, "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার")

    c.setFont(font_reg, 9.5)
    c.setFillColor(dark_slate)
    c.drawCentredString(PAGE_WIDTH / 2, 760, "ভূমি মন্ত্রণালয় — ইউনিয়ন ভূমি অফিস, মেখল, হাটহাজারী, চট্টগ্রাম")

    # Document Name Banner
    banner_w, banner_h = 280, 22
    banner_x = (PAGE_WIDTH - banner_w) / 2
    banner_y = 730
    c.setFillColor(primary_color)
    c.roundRect(banner_x, banner_y, banner_w, banner_h, 3, fill=1, stroke=1)

    c.setFont(font_bold, 12.5)
    c.setFillColor(colors.white)
    c.drawCentredString(PAGE_WIDTH / 2, banner_y + 6, "ভূমি উন্নয়ন কর রসিদ / পর্চা")

    c.setFont(font_bold, 9)
    c.setFillColor(dark_slate)
    c.drawCentredString(PAGE_WIDTH / 2, 715, "(ই-নামজারি ও ডিজিটাল ভূমি কর পরিশোধ দাখিলা)")

    # Tracking Badge: Porcha & Dakhila No
    badge_x = PAGE_WIDTH - 165
    badge_y = 728
    c.setStrokeColor(primary_color)
    c.setFillColor(colors.HexColor("#fff1f2"))
    c.roundRect(badge_x, badge_y, 133, 24, 3, fill=1, stroke=1)
    c.setFont(font_bold, 10.5)
    c.setFillColor(primary_color)
    c.drawCentredString(badge_x + 66, badge_y + 7, "পর্চা নং: ৭৮৯")

    # -------------------------------------------------------------------------
    # Land & Holding Location Table
    # -------------------------------------------------------------------------
    loc_data = [
        ["জেলা: চট্টগ্রাম", "উপজেলা / সার্কেল: হাটহাজারী", "ইউনিয়ন / পৌরসভা: মেখল"],
        ["মৌজা: মেখল", "জে. এল. নং: ৭২", "হোল্ডিং নং: ১৪৫"],
        ["আর এস খতিয়ান নং: ৩২১", "বি এস খতিয়ান নং: ৪৫৬", "অর্থবছর: ২০২৪-২০২৫"],
    ]
    loc_table = Table(loc_data, colWidths=[178, 178, 179])
    loc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    loc_table.wrapOn(c, 535, 80)
    loc_table.drawOn(c, 30, 642)

    # -------------------------------------------------------------------------
    # Taxpayer / Owner Information Card
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 10)
    c.setFillColor(primary_color)
    c.drawString(32, 625, "করদাতা ও জমির মালিকের বিবরণ:")

    owner_data = [
        ["মালিকের নাম:", "ফাতেমা বেগম", "স্বামী / পিতার নাম:", "মরহুম শামসুল হক"],
        ["এনআইডি নং:", "১৯৬৮১৫৯৭৫৩১২০০০০১", "মোবাইল নম্বর:", "০১৮XXXXXXXX"],
        ["ঠিকানা:", "গ্রাম: মেখল, ডাকঘর: মেখল বাজার, উপজেলা: হাটহাজারী, জেলা: চট্টগ্রাম", "", ""],
        ["স্বত্বের বিবরণ:", "ওয়ারিশ ও খরিদ সূত্রে ভোগদখলীয় রায়তী স্বত্ব", "ইস্যু তারিখ:", "০১ সেপ্টেম্বর ২০২৪"],
    ]
    owner_table = Table(owner_data, colWidths=[80, 185, 95, 175])
    owner_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_reg),
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (2, 0), (2, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('SPAN', (1, 2), (3, 2)),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    owner_table.wrapOn(c, 535, 100)
    owner_table.drawOn(c, 30, 545)

    # -------------------------------------------------------------------------
    # Plot Assessment & Tax Details Table
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 10)
    c.setFillColor(primary_color)
    c.drawString(32, 527, "দাগওয়ারি জমির শ্রেণী ও কর নির্ধারণের হিসাব:")

    tax_data = [
        ["ক্রমিক", "দাগ নং", "জমির শ্রেণী", "জমির পরিমাণ", "বার্ষিক দাবি (টাকা)", "বকেয়া (টাকা)", "মোট আদায় (টাকা)"],
        ["১", "২৫৬", "কৃষি জমি (নাল)", "২০ শতাংশ (০.২০ একর)", "২০০.০০", "০০.০০", "২০০.০০"],
        ["২", "২৫৭", "আবাসিক (ভিটি)", "১৫ শতাংশ (০.১৫ একর)", "৩৫০.০০", "০০.০০", "৩৫০.০০"],
        ["সর্বমোট", "২টি দাগ", "মোট পরিমাণ:", "৩৫ শতাংশ (০.৩৫ একর)", "৫৫০.০০", "০০.০০", "৫৫০.০০ টাকা"],
    ]
    tax_table = Table(tax_data, colWidths=[40, 60, 95, 110, 80, 70, 80])
    tax_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_reg),
        ('FONTNAME', (0, -1), (-1, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#ffffff")),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#fee2e2")),
        ('TEXTCOLOR', (0, 3), (-1, 3), primary_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    tax_table.wrapOn(c, 535, 120)
    tax_table.drawOn(c, 30, 437)

    # -------------------------------------------------------------------------
    # Payment Breakdown & Settlement Card
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 10)
    c.setFillColor(primary_color)
    c.drawString(32, 418, "আদায়কৃত ভূমি কর ও ডিজিটাল পেমেন্ট বিবরণ:")

    pay_data = [
        ["ভূমি কর (মূল দাবি):", "৫৫০.০০ টাকা", "জরিমানা / সুদ:", "০০.০০ টাকা"],
        ["সর্বমোট আদায়কৃত অর্থ:", "৫৫০.০০ টাকা (কথায়: পাঁচশত পঞ্চাশ টাকা মাত্র)", "", ""],
        ["পেমেন্ট মাধ্যম:", "সোনালী ব্যাংক ই-সেবা গেটওয়ে / ডিজিটাল পে", "ট্রানজেকশন আইডি:", "TXN-8923741029"],
        ["পরিশোধের তারিখ ও সময়:", "০১ সেপ্টেম্বর ২০২৪, বেলা ১১:৩০ ঘটিকা", "চালান নম্বর:", "CH-2024-CTG-89102"],
    ]
    pay_table = Table(pay_data, colWidths=[120, 150, 105, 160])
    pay_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_reg),
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (2, 0), (2, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('SPAN', (1, 1), (3, 1)),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    pay_table.wrapOn(c, 535, 80)
    pay_table.drawOn(c, 30, 348)

    # -------------------------------------------------------------------------
    # Digital Security & Verification Box
    # -------------------------------------------------------------------------
    sec_box_y = 250
    sec_box_h = 80
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setFillColor(colors.HexColor("#fef2f2"))
    c.roundRect(30, sec_box_y, 440, sec_box_h, 3, fill=1, stroke=1)

    c.setFont(font_bold, 8.5)
    c.setFillColor(primary_color)
    c.drawString(40, sec_box_y + 64, "ডিজিটাল দাখিলা ও পর্চা সংক্রান্ত সতর্কবার্তা:")

    c.setFont(font_reg, 8)
    c.setFillColor(dark_slate)
    c.drawString(40, sec_box_y + 49, "১. এটি একটি সরকারি ডিজিটাল সিস্টেমে প্রস্তুতকৃত দাখিলা/পর্চা। কোনো ম্যানুয়াল স্বাক্ষরের প্রয়োজন নাই।")
    c.drawString(40, sec_box_y + 36, "২. রসিদটির সত্যতা যাচাইয়ের জন্য ভিজিট করুন: https://ldtax.gov.bd/citizen/verify_receipt")
    c.drawString(40, sec_box_y + 23, "৩. হোল্ডিং নং ১৪৫ এর বিপরীতে দাখিলকৃত কর সরকারি কোষাগারে সরাসরি জমা হইয়াছে।")
    c.drawString(40, sec_box_y + 10, "৪. যেকোনো জিজ্ঞাসায় উপজেলা ভূমি অফিস হাটহাজারী অথবা ১৬১২২ হেল্পলাইনে যোগাযোগ করুন।")

    # QR Code placeholder
    draw_qr_verification_box(c, x=485, y=sec_box_y + 5, size=70,
                             label="অনলাইন যাচাই", sub_label="ldtax.gov.bd",
                             font_reg=font_reg, font_bold=font_bold)

    # -------------------------------------------------------------------------
    # Official Signature Blocks
    # -------------------------------------------------------------------------
    sig_y = 150
    c.setStrokeColor(colors.HexColor("#475569"))
    c.setLineWidth(0.6)

    # Left: Taxpayer acknowledgment
    c.line(45, sig_y, 185, sig_y)
    c.setFont(font_reg, 8)
    c.setFillColor(dark_slate)
    c.drawCentredString(115, sig_y - 12, "করদাতার স্বাক্ষর / টিপসহি")
    c.setFont(font_bold, 8)
    c.drawCentredString(115, sig_y - 23, "ফাতেমা বেগম")
    c.setFont(font_reg, 7.5)
    c.drawCentredString(115, sig_y - 34, "মেখল, হাটহাজারী, চট্টগ্রাম")

    # Middle: Cashier / System seal
    c.line(220, sig_y, 340, sig_y)
    c.setFont(font_reg, 8)
    c.drawCentredString(280, sig_y - 12, "হিসাব রক্ষক / ক্যাশিয়ার")
    c.setFont(font_bold, 8)
    c.drawCentredString(280, sig_y - 23, "ডিজিটাল রাজস্ব আদায় শাখা")
    c.setFont(font_reg, 7.5)
    c.drawCentredString(280, sig_y - 34, "অনলাইন লেনদেন সফল")

    # Right: Assistant Land Officer
    c.line(390, sig_y, 540, sig_y)
    c.setFont(font_reg, 8)
    c.drawCentredString(465, sig_y - 12, "ইউনিয়ন ভূমি সহকারী কর্মকর্তা (ULAO)")
    c.setFont(font_bold, 8)
    c.setFillColor(primary_color)
    c.drawCentredString(465, sig_y - 23, "মেখল ইউনিয়ন ভূমি অফিস")
    c.setFont(font_reg, 7.5)
    c.setFillColor(dark_slate)
    c.drawCentredString(465, sig_y - 34, "হাটহাজারী, চট্টগ্রাম [ডিজিটাল সীল]")

    # Footer
    c.setFont(font_reg, 7.5)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawCentredString(PAGE_WIDTH / 2, 45, "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার — ভূমি মন্ত্রণালয় | ভূমি উন্নয়ন কর ব্যবস্থাপনা পোর্টাল")

    c.showPage()
    c.save()
    print(f"[+] Generated Porcha PDF: {output_path}")


# =============================================================================
# 5. DOCUMENT 3: LEGAL DEED (বায়না দলিল / সাফ-বিক্রয় দলিল)
# =============================================================================

def generate_deed_pdf(output_path: Path, font_reg: str, font_bold: str):
    """
    Generates a realistic Legal Deed (দলিল) document.
    Bangladesh Non-Judicial Stamp Deed of Sale / সাফ-কবলা বায়না ও বিক্রয় দলিল.
    Sub-Registry Office: Mirpur, Dhaka.
    """
    c = canvas.Canvas(str(output_path), pagesize=A4)
    primary_color = colors.HexColor("#1e3a5f")    # Dark Legal Navy / Slate
    stamp_green = colors.HexColor("#064e3b")      # Non-judicial stamp green
    gold_accent = colors.HexColor("#92400e")
    dark_slate = colors.HexColor("#0f172a")

    draw_double_border(c, stroke_color=primary_color)
    draw_watermark(c, "গণপ্রজাতন্ত্রী বাংলাদেশ — বায়না ও বিক্রয় দলিল", font_bold)

    # -------------------------------------------------------------------------
    # Top Non-Judicial Stamp Header (১০০০ টাকার সরকারি স্ট্যাম্প রেপ্লিকা)
    # -------------------------------------------------------------------------
    stamp_y = 720
    stamp_h = 88
    stamp_w = PAGE_WIDTH - 60
    stamp_x = 30

    # Stamp outer background and ornate frame
    c.setFillColor(colors.HexColor("#f0fdf4"))
    c.setStrokeColor(stamp_green)
    c.setLineWidth(1.2)
    c.roundRect(stamp_x, stamp_y, stamp_w, stamp_h, 4, fill=1, stroke=1)

    # Stamp inner security border
    c.setLineWidth(0.5)
    c.rect(stamp_x + 3, stamp_y + 3, stamp_w - 6, stamp_h - 6, fill=0, stroke=1)

    # Stamp central circular emblem
    draw_circular_seal(c, cx=PAGE_WIDTH / 2, cy=stamp_y + 44, radius=16,
                       outer_color=stamp_green, seal_text="", font_name=font_bold)

    # Stamp Titles
    c.setFont(font_bold, 11)
    c.setFillColor(stamp_green)
    c.drawCentredString(PAGE_WIDTH / 2, stamp_y + 68, "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার — NON-JUDICIAL")

    c.setFont(font_bold, 13)
    c.setFillColor(stamp_green)
    c.drawCentredString(PAGE_WIDTH / 2, stamp_y + 20, "১০০০/- এক হাজার টাকা")

    # Left & Right Stamp details
    c.setFont(font_bold, 8.5)
    c.setFillColor(stamp_green)
    c.drawString(stamp_x + 12, stamp_y + 66, "বাংলাদেশ নন-জুডিশিয়াল স্ট্যাম্প")
    c.setFont(font_reg, 7.5)
    c.drawString(stamp_x + 12, stamp_y + 52, "ক্রমিক নং: খগ-৭৮৬৪৫২১")
    c.drawString(stamp_x + 12, stamp_y + 38, "ট্রেজারি চালান: ঢাকা কালেক্টরেট")
    c.drawString(stamp_x + 12, stamp_y + 24, "ভেন্ডার লাইসেন্স: ৪২/মিরপুর")

    c.setFont(font_bold, 8.5)
    c.drawRightString(stamp_x + stamp_w - 12, stamp_y + 66, "দলিল নং: ১১২৩ / ২০২৪")
    c.setFont(font_reg, 7.5)
    c.drawRightString(stamp_x + stamp_w - 12, stamp_y + 52, "সাব-রেজিস্ট্রি অফিস: মিরপুর, ঢাকা")
    c.drawRightString(stamp_x + stamp_w - 12, stamp_y + 38, "নিবন্ধন তারিখ: ২০ আগস্ট ২০২৪")
    c.drawRightString(stamp_x + stamp_w - 12, stamp_y + 24, "ভলিউম নং: ৪৭, পৃষ্ঠা: ৮৫-৯২")

    # -------------------------------------------------------------------------
    # Deed Main Title Banner
    # -------------------------------------------------------------------------
    banner_w, banner_h = 300, 22
    banner_x = (PAGE_WIDTH - banner_w) / 2
    banner_y = 690
    c.setFillColor(primary_color)
    c.roundRect(banner_x, banner_y, banner_w, banner_h, 3, fill=1, stroke=1)

    c.setFont(font_bold, 12)
    c.setFillColor(colors.white)
    c.drawCentredString(PAGE_WIDTH / 2, banner_y + 6, "বায়না দলিল / সাফ-বিক্রয় দলিল")

    # -------------------------------------------------------------------------
    # Parties Section (পক্ষগণের পরিচিতি: ১ম পক্ষ বিক্রেতা ও ২য় পক্ষ ক্রেতা)
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 9.5)
    c.setFillColor(primary_color)
    c.drawString(32, 675, "দলিলদাতা (বিক্রেতা) ও দলিলগ্রহীতা (ক্রেতা) এর পরিচয়:")

    parties_data = [
        ["১ম পক্ষ (বিক্রেতা / দাতা):", "মোঃ জাহাঙ্গীর আলম", "পিতা: মরহুম রফিকুল ইসলাম", "মাতা: জাহানারা বেগম"],
        ["এনআইডি:", "৮৭৬৫৪৩২১০৯৮৭৬", "ধর্ম: ইসলাম  |  পেশা: ব্যবসা", "জাতীয়তা: বাংলাদেশী"],
        ["বর্তমান ও স্থায়ী ঠিকানা:", "বাড়ি নং ১২, রোড নং ৪, মিরপুর-১০, ঢাকা-১২১৬", "", ""],
        ["২য় পক্ষ (ক্রেতা / গ্রহীতা):", "নাসরিন সুলতানা", "পিতা: সুলতান মাহমুদ", "মাতা: রাজিয়া সুলতানা"],
        ["এনআইডি:", "২৩৪৫৬৭৮৯০১২৩৪", "ধর্ম: ইসলাম  |  পেশা: চাকুরী", "জাতীয়তা: বাংলাদেশী"],
        ["বর্তমান ও স্থায়ী ঠিকানা:", "ফ্ল্যাট ৩বি, বাড়ি নং ৪৫, সেক্টর-৩, উত্তরা মডেল টাউন, ঢাকা-১২৩০", "", ""],
    ]
    parties_table = Table(parties_data, colWidths=[110, 145, 140, 140])
    parties_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_reg),
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (1, 0), (1, 0), font_bold),
        ('FONTNAME', (1, 3), (1, 3), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('SPAN', (1, 2), (3, 2)),
        ('SPAN', (1, 5), (3, 5)),
        ('BACKGROUND', (0, 0), (-1, 2), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0, 3), (-1, 5), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ]))
    parties_table.wrapOn(c, 535, 120)
    parties_table.drawOn(c, 30, 560)

    # -------------------------------------------------------------------------
    # Land Schedule Table (জমির তফসিল ও অবস্থান বিবরণ)
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 9.5)
    c.setFillColor(primary_color)
    c.drawString(32, 545, "বিক্রিত ভূমির চৌহদ্দি ও পূর্ণ তফসিল বিবরণ:")

    sched_data = [
        ["জেলা: ঢাকা", "উপজেলা / থানা: মিরপুর", "সাব-রেজিস্ট্রি অফিস: মিরপুর, ঢাকা"],
        ["মৌজা: পীরেরবাগ", "জে. এল. নং: ৫৪", "খতিয়ান নং: ৮৯ (সাবেক সি.এস/এস.এ)"],
        ["দাগ নং (সি.এস/এস.এ): ৩৩৪", "আর. এস. দাগ নং: ৭৬২", "জমির শ্রেণী: বাস্তু / নাল জমি"],
        ["বিক্রিত জমির পরিমাণ:", "০.২৫ শতাংশ (পয়েন্ট দুই পাঁচ শতাংশ / পঁচিশ অযুতাংশ জমি)", ""],
    ]
    sched_table = Table(sched_data, colWidths=[178, 178, 179])
    sched_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_bold),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('SPAN', (1, 3), (2, 3)),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    sched_table.wrapOn(c, 535, 80)
    sched_table.drawOn(c, 30, 460)

    # Boundaries (চৌহদ্দি) Box
    bound_y = 422
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.roundRect(30, bound_y, 535, 32, 3, fill=1, stroke=1)

    c.setFont(font_bold, 8)
    c.setFillColor(primary_color)
    c.drawString(36, bound_y + 20, "জমির চতুঃসীমানা (চৌহদ্দি):")
    c.setFont(font_reg, 7.8)
    c.setFillColor(dark_slate)
    c.drawString(145, bound_y + 20, "উত্তরে: ১২ ফুট প্রশস্ত চলাচলের রাস্তা  |  দক্ষিণে: বিক্রেতার নিজস্ব অবশিষ্ট জমি")
    c.drawString(36, bound_y + 7, "পূর্বে: হাজী আবদুর রাজ্জাকের সীমানা ও দেওয়াল  |  পশ্চিমে: ওয়াসা ড্রেন সংলগ্ন সরকারি রাস্তা")

    # -------------------------------------------------------------------------
    # Consideration & Terms (পণমূল্য ও চুক্তির শর্তাবলী)
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 9.5)
    c.setFillColor(primary_color)
    c.drawString(32, 405, "পণমূল্য (বিক্রয় মূল্য) ও দলিলের শর্তাবলী:")

    terms_data = [
        ["মোট বিক্রয় মূল্য:", "৩৫,০০,০০০/- টাকা (পঁয়ত্রিশ লক্ষ টাকা মাত্র)"],
        ["পরিশোধের বিবরণ:", "বায়না ও দলিল সম্পাদনকালে সমুদয় অর্থ নগদ ও পে-অর্ডার (নং PO-459201, সোনালী ব্যাংক পিএলসি, মিরপুর শাখা) যোগে বিক্রেতা ১ম পক্ষ ক্রেতা ২য় পক্ষের নিকট হইতে বুঝিয়া পাইয়া রসিদ প্রদান করিলেন।"],
        ["দখল হস্তান্তর ও স্বত্ব:", "অদ্য তারিখে বিক্রিত ভূমির সমস্ত স্বত্ব, স্বার্থ ও দখল ১ম পক্ষ ২য় পক্ষের বরাবর সমর্পণ করিলেন। অদ্য হইতে ক্রেতা নিজ নামে নামজারি ও জমাভাগ করাইয়া চিরকাল ভোগদখল করিতে পারিবেন।"],
        ["দায়মুক্তি ও নিশ্চয়তা:", "উক্ত জমি পূর্বে কোনো ব্যক্তি, ব্যাংক বা সংস্থার নিকট দায়বদ্ধ বা বন্ধক রাখা হয় নাই। জমি সম্পূর্ণ নির্ভেজাল ও নিষ্কণ্টক। ভবিষ্যতে কোনো ওজর-আপত্তি আইনত বাতিল বলিয়া গণ্য হইবে।"],
    ]
    terms_table = Table(terms_data, colWidths=[110, 425])
    terms_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), font_bold),
        ('FONTNAME', (1, 0), (1, -1), font_reg),
        ('FONTSIZE', (0, 0), (-1, -1), 7.8),
        ('TEXTCOLOR', (0, 0), (-1, -1), dark_slate),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ]))
    terms_table.wrapOn(c, 535, 120)
    terms_table.drawOn(c, 30, 280)

    # -------------------------------------------------------------------------
    # Signatures, Witnesses & Registration Seal
    # -------------------------------------------------------------------------
    c.setFont(font_bold, 9.5)
    c.setFillColor(primary_color)
    c.drawString(32, 262, "স্বাক্ষর, সাক্ষীগণ ও সাব-রেজিস্ট্রারের অনুমোদন:")

    # 4 Signature Boxes
    box_w = 125
    box_h = 75
    gap = 11
    boxes_y = 175

    # 1. Seller
    bx1 = 30
    c.setStrokeColor(colors.HexColor("#94a3b8"))
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.roundRect(bx1, boxes_y, box_w, box_h, 3, fill=1, stroke=1)
    c.setFont(font_bold, 8)
    c.setFillColor(primary_color)
    c.drawCentredString(bx1 + box_w / 2, boxes_y + box_h - 12, "১ম পক্ষ (বিক্রেতা)")
    c.setFont(font_reg, 7.5)
    c.setFillColor(dark_slate)
    c.drawCentredString(bx1 + box_w / 2, boxes_y + box_h - 26, "[স্বাক্ষর ও টিপসহি]")
    c.setFont(font_bold, 8)
    c.drawCentredString(bx1 + box_w / 2, boxes_y + 12, "মোঃ জাহাঙ্গীর আলম")

    # 2. Buyer
    bx2 = bx1 + box_w + gap
    c.roundRect(bx2, boxes_y, box_w, box_h, 3, fill=1, stroke=1)
    c.setFont(font_bold, 8)
    c.setFillColor(primary_color)
    c.drawCentredString(bx2 + box_w / 2, boxes_y + box_h - 12, "২য় পক্ষ (ক্রেতা)")
    c.setFont(font_reg, 7.5)
    c.setFillColor(dark_slate)
    c.drawCentredString(bx2 + box_w / 2, boxes_y + box_h - 26, "[স্বাক্ষর]")
    c.setFont(font_bold, 8)
    c.drawCentredString(bx2 + box_w / 2, boxes_y + 12, "নাসরিন সুলতানা")

    # 3. Identifier
    bx3 = bx2 + box_w + gap
    c.roundRect(bx3, boxes_y, box_w, box_h, 3, fill=1, stroke=1)
    c.setFont(font_bold, 8)
    c.setFillColor(primary_color)
    c.drawCentredString(bx3 + box_w / 2, boxes_y + box_h - 12, "সনাক্তকারীর স্বাক্ষর")
    c.setFont(font_reg, 7.5)
    c.setFillColor(dark_slate)
    c.drawCentredString(bx3 + box_w / 2, boxes_y + box_h - 26, "এডভোকেট আতিকুর রহমান")
    c.setFont(font_reg, 7)
    c.drawCentredString(bx3 + box_w / 2, boxes_y + 12, "ঢাকা বার কাউন্সিল সদস্য")

    # 4. Sub-Registrar
    bx4 = bx3 + box_w + gap
    c.roundRect(bx4, boxes_y, box_w, box_h, 3, fill=1, stroke=1)
    c.setFont(font_bold, 8)
    c.setFillColor(primary_color)
    c.drawCentredString(bx4 + box_w / 2, boxes_y + box_h - 12, "সাব-রেজিস্ট্রার (সীল)")
    c.setFont(font_reg, 7)
    c.setFillColor(dark_slate)
    c.drawCentredString(bx4 + box_w / 2, boxes_y + box_h - 26, "মিরপুর সাব-রেজিস্ট্রি অফিস")
    c.setFont(font_bold, 7.5)
    c.setFillColor(stamp_green)
    c.drawCentredString(bx4 + box_w / 2, boxes_y + 12, "[রেজিস্ট্রেশন সম্পন্ন]")

    # Witnesses & Scribe bottom bar
    wit_y = 95
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setFillColor(colors.HexColor("#ffffff"))
    c.roundRect(30, wit_y, 535, 68, 3, fill=1, stroke=1)

    c.setFont(font_bold, 8)
    c.setFillColor(primary_color)
    c.drawString(38, wit_y + 54, "সাক্ষীগণের নাম ও ঠিকানা:")

    c.setFont(font_reg, 7.5)
    c.setFillColor(dark_slate)
    c.drawString(38, wit_y + 38, "১. মোস্তফা কামাল, পিতা: আজহার আলী, সাং: পীরেরবাগ, মিরপুর, ঢাকা।")
    c.drawString(38, wit_y + 24, "২. কামরুল হাসান, পিতা: বশির উল্লাহ, সাং: মিরপুর-১০, ঢাকা-১২১৬।")
    c.drawString(38, wit_y + 10, "দলিল লেখক: বশির আহমেদ, লাইসেন্স নং- ৫৬/মিরপুর সাব-রেজিস্ট্রি অফিস, ঢাকা।")

    # QR Code Verification at right inside witness area
    draw_qr_verification_box(c, x=495, y=wit_y + 6, size=56,
                             label="দলিল যাচাই", sub_label="রেজিস্ট্রি অফিস",
                             font_reg=font_reg, font_bold=font_bold)

    # Footer
    c.setFont(font_reg, 7.5)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawCentredString(PAGE_WIDTH / 2, 45, "গণপ্রজাতন্ত্রী বাংলাদেশ সরকার — নিবন্ধন অধিদপ্তর, আইন ও সংসদ বিষয়ক মন্ত্রণালয়")

    c.showPage()
    c.save()
    print(f"[+] Generated Deed PDF: {output_path}")


# =============================================================================
# 6. MAIN CONTROLLER
# =============================================================================

def main():
    print("=" * 70)
    print("Bangladesh Land Record Demo Document Generator")
    print("=" * 70)

    # 1. Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[*] Target directory: {OUTPUT_DIR}")

    # 2. Setup Bengali Font
    font_reg, font_bold = setup_bengali_font(OUTPUT_DIR)
    print(f"[*] Registered Fonts: Regular='{font_reg}', Bold='{font_bold}'")

    # 3. Define target PDF file paths
    khatian_path = OUTPUT_DIR / "khatian_demo.pdf"
    porcha_path = OUTPUT_DIR / "porcha_demo.pdf"
    deed_path = OUTPUT_DIR / "deed_demo.pdf"

    # 4. Generate Khatian
    print("\n[1/3] Generating Khatian (জমাবন্দি - খতিয়ান)...")
    generate_khatian_pdf(khatian_path, font_reg, font_bold)

    # 5. Generate Porcha
    print("\n[2/3] Generating Porcha (ভূমি উন্নয়ন কর রসিদ / পর্চা)...")
    generate_porcha_pdf(porcha_path, font_reg, font_bold)

    # 6. Generate Deed
    print("\n[3/3] Generating Legal Deed (বায়না দলিল / বিক্রয় দলিল)...")
    generate_deed_pdf(deed_path, font_reg, font_bold)

    print("\n" + "=" * 70)
    print("ALL 3 DEMO LAND RECORD DOCUMENTS GENERATED SUCCESSFULLY!")
    print(f"1. Khatian: {khatian_path}")
    print(f"2. Porcha:  {porcha_path}")
    print(f"3. Deed:    {deed_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
