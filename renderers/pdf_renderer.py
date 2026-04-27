"""
pdf_renderer.py
---------------
Renders PDF templates using ReportLab.
Templates: sales_proposal, one_pager, onboarding_form (fillable)
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfform


# ── Brand colours ──────────────────────────────────────────────────────────
DARK    = colors.HexColor("#0D1117")
ACCENT  = colors.HexColor("#2563EB")   # Blue
LIGHT   = colors.HexColor("#F8FAFC")
MUTED   = colors.HexColor("#64748B")
WHITE   = colors.white
BORDER  = colors.HexColor("#E2E8F0")

W, H = A4   # 595 x 842 pts


# ── Shared style helpers ────────────────────────────────────────────────────
def _base_styles():
    from reportlab.lib.styles import StyleSheet1
    styles = StyleSheet1()
    styles.add(ParagraphStyle("DocTitle",   fontName="Helvetica-Bold",  fontSize=26, textColor=WHITE,  spaceAfter=4,  leading=30))
    styles.add(ParagraphStyle("DocSub",     fontName="Helvetica",       fontSize=12, textColor=colors.HexColor("#CBD5E1"), spaceAfter=2))
    styles.add(ParagraphStyle("SectionHdr", fontName="Helvetica-Bold",  fontSize=13, textColor=ACCENT, spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle("Body",       fontName="Helvetica",       fontSize=10, textColor=DARK,   spaceAfter=4,  leading=15))
    styles.add(ParagraphStyle("Bullet",     fontName="Helvetica",       fontSize=10, textColor=DARK,   spaceAfter=3,  leftIndent=14, leading=14, bulletIndent=4))
    styles.add(ParagraphStyle("Label",      fontName="Helvetica-Bold",  fontSize=9,  textColor=MUTED,  spaceAfter=1))
    styles.add(ParagraphStyle("Value",      fontName="Helvetica",       fontSize=11, textColor=DARK,   spaceAfter=8))
    styles.add(ParagraphStyle("Footer",     fontName="Helvetica",       fontSize=8,  textColor=MUTED,  alignment=TA_CENTER))
    return styles


def _draw_header_band(c: canvas.Canvas, title: str, subtitle: str, prepared_by: str = ""):
    """Dark header band at top of first page."""
    c.saveState()
    c.setFillColor(DARK)
    c.rect(0, H - 110*mm, W, 110*mm, fill=1, stroke=0)
    # Accent stripe
    c.setFillColor(ACCENT)
    c.rect(0, H - 113*mm, W, 3*mm, fill=1, stroke=0)
    # Title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(20*mm, H - 45*mm, title)
    # Subtitle
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.setFont("Helvetica", 13)
    c.drawString(20*mm, H - 58*mm, subtitle)
    if prepared_by:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#94A3B8"))
        c.drawString(20*mm, H - 70*mm, f"Prepared by: {prepared_by}")
    c.restoreState()


def _draw_footer(c: canvas.Canvas, page_num: int, total: int, doc_label: str):
    c.saveState()
    c.setFillColor(BORDER)
    c.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(20*mm, 4*mm, doc_label)
    c.drawRightString(W - 20*mm, 4*mm, f"Page {page_num} of {total}")
    c.restoreState()


# ══════════════════════════════════════════════════════════════════════════════
#  TEMPLATE 1 — SALES PROPOSAL
# ══════════════════════════════════════════════════════════════════════════════
def render_sales_proposal(data: dict, output_path: str):
    styles = _base_styles()
    client   = data.get("client_name", "Valued Client")
    project  = data.get("project_name", "Custom Solution")
    budget   = data.get("budget", "TBD")
    kickoff  = data.get("kickoff_date", "TBD")
    prep_by  = data.get("prepared_by", "Agentic Solutions")
    scope    = data.get("scope_items", [])

    class DocWithHeader(SimpleDocTemplate):
        def __init__(self, *args, **kwargs):
            self._header_drawn = False
            super().__init__(*args, **kwargs)

        def handle_pageBegin(self):
            super().handle_pageBegin()
            pn = self.page
            _draw_footer(self.canv, pn, "?", f"Sales Proposal — {client}")
            if not self._header_drawn:
                _draw_header_band(self.canv, f"Sales Proposal", f"{client}  ·  {project}", prep_by)
                self._header_drawn = True

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=120*mm, bottomMargin=20*mm,
    )

    story = []

    # ── Executive Summary ──
    story.append(Paragraph("Executive Summary", styles["SectionHdr"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))
    summary = (
        f"This proposal outlines our recommended approach for <b>{project}</b> "
        f"to be delivered for <b>{client}</b>. Our team will partner closely with "
        f"your stakeholders to ensure a high-quality, on-time, and on-budget delivery."
    )
    story.append(Paragraph(summary, styles["Body"]))
    story.append(Spacer(1, 6))

    # ── Key Details table ──
    story.append(Paragraph("Engagement Details", styles["SectionHdr"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))
    table_data = [
        ["Client",        client],
        ["Project",       project],
        ["Budget",        budget],
        ["Kickoff Date",  kickoff],
        ["Prepared By",   prep_by],
    ]
    t = Table(table_data, colWidths=[55*mm, 110*mm])
    t.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("TEXTCOLOR",   (0,0), (0,-1), MUTED),
        ("TEXTCOLOR",   (1,0), (1,-1), DARK),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LIGHT, WHITE]),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("BOX",         (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",   (0,0), (-1,-1), 0.5, BORDER),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # ── Scope of Work ──
    story.append(Paragraph("Scope of Work", styles["SectionHdr"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))
    for i, item in enumerate(scope, 1):
        story.append(Paragraph(f"<bullet>•</bullet> <b>Phase {i}:</b> {item}", styles["Bullet"]))
    story.append(Spacer(1, 8))

    # ── Investment & Timeline ──
    story.append(Paragraph("Investment & Timeline", styles["SectionHdr"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))
    inv_data = [
        ["Total Investment", budget],
        ["Project Kickoff",  kickoff],
        ["Payment Terms",    "50% upfront, 50% on delivery"],
        ["Validity",         "This proposal is valid for 30 days"],
    ]
    t2 = Table(inv_data, colWidths=[55*mm, 110*mm])
    t2.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("TEXTCOLOR",   (0,0), (0,-1), MUTED),
        ("TEXTCOLOR",   (1,0), (1,-1), DARK),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LIGHT, WHITE]),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("BOX",         (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",   (0,0), (-1,-1), 0.5, BORDER),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    # ── Next Steps ──
    story.append(Paragraph("Next Steps", styles["SectionHdr"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))
    for step in [
        "Review and sign proposal",
        "Submit 50% deposit to initiate project",
        f"Kickoff meeting on {kickoff}",
        "Weekly progress updates throughout delivery",
    ]:
        story.append(Paragraph(f"<bullet>→</bullet>  {step}", styles["Bullet"]))

    doc.build(story)
    return output_path


# ══════════════════════════════════════════════════════════════════════════════
#  TEMPLATE 2 — ONE-PAGER
# ══════════════════════════════════════════════════════════════════════════════
def render_one_pager(data: dict, output_path: str):
    client      = data.get("client_name", "Valued Client")
    project     = data.get("project_name", "Digital Transformation Initiative")
    tagline     = data.get("tagline", "Clarity. Speed. Results.")
    objective   = data.get("objective", "Drive measurable growth.")
    deliverables = data.get("deliverables", [])
    timeline    = data.get("timeline", "8 weeks")
    budget      = data.get("budget", "Contact us")

    c = canvas.Canvas(output_path, pagesize=A4)

    # Header band
    c.setFillColor(DARK)
    c.rect(0, H - 70*mm, W, 70*mm, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, H - 72*mm, W, 2*mm, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20*mm, H - 28*mm, project)
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawString(20*mm, H - 40*mm, f"Client: {client}")
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(ACCENT)
    c.drawString(20*mm, H - 52*mm, tagline)

    y = H - 90*mm

    def section(title, items_or_text, y):
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(ACCENT)
        c.drawString(20*mm, y, title)
        y -= 5*mm
        c.setStrokeColor(BORDER)
        c.line(20*mm, y, W - 20*mm, y)
        y -= 6*mm
        c.setFont("Helvetica", 10)
        c.setFillColor(DARK)
        if isinstance(items_or_text, list):
            for item in items_or_text:
                c.drawString(24*mm, y, f"•  {item}")
                y -= 6*mm
        else:
            from reportlab.lib.utils import simpleSplit
            lines = simpleSplit(items_or_text, "Helvetica", 10, W - 40*mm)
            for line in lines:
                c.drawString(20*mm, y, line)
                y -= 6*mm
        return y - 4*mm

    y = section("Objective", objective, y)
    y = section("Key Deliverables", deliverables, y)
    y = section("Timeline & Investment", [f"Timeline: {timeline}", f"Investment: {budget}"], y)

    # Footer
    c.setFillColor(DARK)
    c.rect(0, 0, W, 15*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, 5*mm, "Confidential — Prepared for exclusive use by the above-named client.")

    c.save()
    return output_path


# ══════════════════════════════════════════════════════════════════════════════
#  TEMPLATE 3 — FILLABLE ONBOARDING FORM
# ══════════════════════════════════════════════════════════════════════════════
def render_onboarding_form(data: dict, output_path: str):
    client     = data.get("client_name", "Your Company")
    form_title = data.get("form_title", "New Sales Rep Onboarding Form")
    rep_fields = data.get("rep_fields", ["Full Name", "Role / Title", "Start Date", "Direct Manager"])

    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(form_title)

    # Header
    c.setFillColor(DARK)
    c.rect(0, H - 55*mm, W, 55*mm, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, H - 57*mm, W, 2*mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(20*mm, H - 25*mm, form_title)
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawString(20*mm, H - 38*mm, client)

    y = H - 75*mm
    field_h = 8*mm
    gap     = 16*mm

    c.setFont("Helvetica", 9)
    c.setFillColor(MUTED)
    c.drawString(20*mm, y, "Please complete all fields below. This form can be saved and submitted electronically.")
    y -= 12*mm

    for label in rep_fields:
        # Label
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(MUTED)
        c.drawString(20*mm, y + 2*mm, label.upper())
        y -= 6*mm

        # Text field box (visual)
        c.setStrokeColor(BORDER)
        c.setFillColor(LIGHT)
        c.roundRect(20*mm, y - field_h, W - 40*mm, field_h, 2, fill=1, stroke=1)

        # Actual fillable field
        form = c.acroForm
        safe_key = label.lower().replace(" ", "_").replace("/", "_")
        form.textfield(
            name=safe_key,
            tooltip=label,
            x=21*mm, y=y - field_h + 1*mm,
            width=W - 42*mm, height=field_h - 2*mm,
            fontSize=10,
            borderColor=BORDER,
            fillColor=LIGHT,
            textColor=DARK,
            borderWidth=0,
        )
        y -= field_h + gap

    # Additional notes field
    y -= 5*mm
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(MUTED)
    c.drawString(20*mm, y + 2*mm, "ADDITIONAL NOTES")
    y -= 6*mm
    notes_h = 30*mm
    c.setFillColor(LIGHT)
    c.setStrokeColor(BORDER)
    c.roundRect(20*mm, y - notes_h, W - 40*mm, notes_h, 2, fill=1, stroke=1)
    form = c.acroForm
    form.textfield(
        name="additional_notes",
        tooltip="Additional Notes",
        x=21*mm, y=y - notes_h + 1*mm,
        width=W - 42*mm, height=notes_h - 2*mm,
        fontSize=10,
        borderColor=BORDER,
        fillColor=LIGHT,
        textColor=DARK,
        borderWidth=0,
        fieldFlags="multiline",
    )

    # Footer
    c.setFillColor(DARK)
    c.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(W/2, 4*mm, f"{client}  ·  Confidential Onboarding Document")

    c.save()
    return output_path


# ── Dispatcher ──────────────────────────────────────────────────────────────
def render_pdf(template_key: str, data: dict, output_path: str) -> str:
    if template_key == "sales_proposal":
        return render_sales_proposal(data, output_path)
    elif template_key == "one_pager":
        return render_one_pager(data, output_path)
    elif template_key == "onboarding_form":
        return render_onboarding_form(data, output_path)
    else:
        return render_sales_proposal(data, output_path)
