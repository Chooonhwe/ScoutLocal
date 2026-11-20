
from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#10243A")
BLUE = colors.HexColor("#285A87")
LIGHT_BLUE = colors.HexColor("#EDF3F8")
TEXT = colors.HexColor("#263445")
MUTED = colors.HexColor("#667789")
BORDER = colors.HexColor("#DCE4EC")


def safe_text(value):
    """Safely format user-provided text for a PDF paragraph."""
    if value is None or str(value).strip() == "":
        return "Not recorded"

    text = str(value)

    # Standard PDF fonts do not support all Unicode characters.
    text = text.encode("latin-1", errors="replace").decode("latin-1")

    return escape(text).replace("\n", "<br/>")


def rating_text(value):
    if value is None:
        return "Not rated"

    return f"{value}/5"


def create_styles():
    return {
        "brand": ParagraphStyle(
            "Brand",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=NAVY,
            spaceAfter=5,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=MUTED,
        ),
        "heading": ParagraphStyle(
            "SectionHeading",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=9.5,
            leading=15,
            textColor=TEXT,
            spaceAfter=8,
        ),
        "label": ParagraphStyle(
            "Label",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=12,
            textColor=MUTED,
        ),
        "value": ParagraphStyle(
            "Value",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=TEXT,
        ),
        "small": ParagraphStyle(
            "Small",
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=MUTED,
        ),
    }


def add_section(story, styles, title, content):
    """Add a section that flows onto another page if necessary."""
    story.append(
        Paragraph(title, styles["heading"])
    )

    story.append(
        Paragraph(safe_text(content), styles["body"])
    )


def add_information_table(story, styles, items):
    """Display player and match information in two columns."""
    rows = []

    for label, value in items:
        rows.append([
            Paragraph(
                safe_text(label),
                styles["label"],
            ),
            Paragraph(
                safe_text(value),
                styles["value"],
            ),
        ])

    table = Table(
        rows,
        colWidths=[43 * mm, 135 * mm],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -2), 0.4, BORDER),
        ])
    )

    story.append(table)


def draw_page_footer(canvas, document):
    canvas.saveState()

    width, _ = A4

    canvas.setStrokeColor(BORDER)
    canvas.line(16 * mm, 18 * mm, width - 16 * mm, 18 * mm)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)

    canvas.drawString(
        16 * mm,
        12 * mm,
        "ScoutLocal | Scouting & Recruitment Intelligence",
    )

    canvas.drawRightString(
        width - 16 * mm,
        12 * mm,
        f"Page {document.page}",
    )

    canvas.restoreState()


def generate_scouting_pdf(report):
    """
    Build a professional scouting report PDF.

    Args:
        report: Dictionary from the scouting_reports database.

    Returns:
        PDF file contents as bytes.
    """
    buffer = BytesIO()
    styles = create_styles()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=17 * mm,
        bottomMargin=26 * mm,
        title="ScoutLocal Scouting Report",
        author="ScoutLocal",
    )

    story = []

    # BRAND HEADER
    story.append(
        Paragraph("SCOUTLOCAL", styles["brand"])
    )

    story.append(
        Paragraph(
            "FOOTBALL SCOUTING & RECRUITMENT INTELLIGENCE",
            styles["subtitle"],
        )
    )

    story.append(Spacer(1, 8 * mm))

    story.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=BLUE,
        )
    )

    story.append(Spacer(1, 6 * mm))

    # PLAYER HEADER
    story.append(
        Paragraph(
            safe_text(report.get("player_name")),
            styles["brand"],
        )
    )

    story.append(
        Paragraph(
            "INDIVIDUAL SCOUTING ASSESSMENT",
            styles["subtitle"],
        )
    )

    story.append(Spacer(1, 6 * mm))

    # PLAYER INFORMATION
    add_information_table(
        story,
        styles,
        [
            ("Club", report.get("team_name")),
            ("Position", report.get("position")),
            ("Scout", report.get("scout_name")),
            ("Observation Date", report.get("observation_date")),
            ("Match Context", report.get("match_context")),
            ("Report ID", report.get("id", "Not assigned")),
        ],
    )

    story.append(Spacer(1, 5 * mm))

    # RECOMMENDATION
    story.append(
        Paragraph(
            "Recruitment Recommendation",
            styles["heading"],
        )
    )

    recommendation = Paragraph(
        safe_text(report.get("recommendation")),
        ParagraphStyle(
            "RecommendationValue",
            parent=styles["value"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=BLUE,
        ),
    )

    recommendation_table = Table(
        [[recommendation]],
        colWidths=[178 * mm],
    )

    recommendation_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ])
    )

    story.append(recommendation_table)

    # HUMAN SCOUT RATINGS
    story.append(
        Paragraph(
            "Scout Evaluation",
            styles["heading"],
        )
    )

    rating_data = [
        [
            Paragraph("TECHNICAL", styles["label"]),
            Paragraph("TACTICAL", styles["label"]),
            Paragraph("PHYSICAL", styles["label"]),
        ],
        [
            Paragraph(
                safe_text(rating_text(report.get("technical_rating"))),
                styles["value"],
            ),
            Paragraph(
                safe_text(rating_text(report.get("tactical_rating"))),
                styles["value"],
            ),
            Paragraph(
                safe_text(rating_text(report.get("physical_rating"))),
                styles["value"],
            ),
        ],
    ]

    rating_table = Table(
        rating_data,
        colWidths=[59.3 * mm] * 3,
    )

    rating_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
            ("LINEBEFORE", (1, 0), (-1, -1), 0.6, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])
    )

    story.append(rating_table)

    # SCOUTING OBSERVATIONS
    add_section(
        story,
        styles,
        "Key Strengths",
        report.get("strengths"),
    )

    add_section(
        story,
        styles,
        "Development Areas",
        report.get("weaknesses"),
    )

    add_section(
        story,
        styles,
        "Detailed Scouting Observations",
        report.get("observations"),
    )

    story.append(Spacer(1, 5 * mm))

    # METHODOLOGY NOTICE
    story.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=BORDER,
        )
    )

    story.append(Spacer(1, 3 * mm))

    generated_at = datetime.now().strftime(
        "%d %B %Y, %H:%M"
    )

    story.append(
        Paragraph(
            f"Generated on {safe_text(generated_at)}. "
            "Ratings and written assessments represent "
            "the scout's observations, not independently "
            "verified player ability scores.",
            styles["small"],
        )
    )

    document.build(
        story,
        onFirstPage=draw_page_footer,
        onLaterPages=draw_page_footer,
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
