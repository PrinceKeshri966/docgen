"""Generate the architecture one-pager PDF for the submission."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

W, H = A4
DARK   = colors.HexColor("#0D1117")
ACCENT = colors.HexColor("#2563EB")
WHITE  = colors.white
MUTED  = colors.HexColor("#64748B")
LIGHT  = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#E2E8F0")

def wrap_text(c, text, x, y, max_width, font, size, color, line_height=5.5):
    c.setFont(font, size)
    c.setFillColor(color)
    lines = simpleSplit(text, font, size, max_width)
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height * mm
    return y

out = "samples/architecture_writeup.pdf"
cv = canvas.Canvas(out, pagesize=A4)

# ── Header ──
cv.setFillColor(DARK)
cv.rect(0, H - 52*mm, W, 52*mm, fill=1, stroke=0)
cv.setFillColor(ACCENT)
cv.rect(0, H - 54*mm, W, 2*mm, fill=1, stroke=0)

cv.setFillColor(WHITE)
cv.setFont("Helvetica-Bold", 20)
cv.drawString(18*mm, H - 20*mm, "DocGen — Architecture Writeup")
cv.setFont("Helvetica", 11)
cv.setFillColor(colors.HexColor("#CBD5E1"))
cv.drawString(18*mm, H - 32*mm, "Agentic Take-Home Assignment  ·  Full-Stack / AI Engineer Role")
cv.setFont("Helvetica", 9)
cv.setFillColor(colors.HexColor("#94A3B8"))
cv.drawString(18*mm, H - 43*mm, "Stack: FastAPI · Gemini 2.0 Flash · ReportLab · python-pptx · Vanilla JS")

y = H - 65*mm

def section(title, body_lines):
    global y
    cv.setFont("Helvetica-Bold", 11)
    cv.setFillColor(ACCENT)
    cv.drawString(18*mm, y, title)
    y -= 4*mm
    cv.setStrokeColor(BORDER)
    cv.line(18*mm, y, W - 18*mm, y)
    y -= 6*mm
    for line in body_lines:
        bold = line.startswith("**")
        if bold:
            line = line.replace("**","")
            cv.setFont("Helvetica-Bold", 9)
        else:
            cv.setFont("Helvetica", 9)
        cv.setFillColor(DARK)
        lines = simpleSplit(line, "Helvetica" + ("-Bold" if bold else ""), 9, W - 36*mm)
        for l in lines:
            cv.drawString(18*mm, y, l)
            y -= 5*mm
    y -= 3*mm

section("Components & Data Flow", [
    "The system is split into 4 clean, independently testable layers:",
    "**1. Intent Parser (intent_parser.py)**",
    "   Calls Gemini 2.0 Flash with a strict system prompt instructing it to return ONLY a JSON",
    "   object with keys: doc_type, template, client_name, fields, refinement.",
    "   Strips markdown fences from the response before parsing.",
    "**2. Template Selector (template_selector.py)**",
    "   A static registry maps template keys to configs with required_fields and defaults.",
    "   Extracted intent fields are merged over defaults — no field is ever empty.",
    "**3. Data Hydrator (inside template_selector.select_template)**",
    "   Overlays Gemini-extracted fields on top of defaults. Handles type normalisation",
    "   (e.g., rep_fields list from Gemini → title-cased strings).",
    "**4. Renderer (renderers/pdf_renderer.py + ppt_renderer.py)**",
    "   ReportLab canvas API for PDFs; python-pptx for slides. Each template is a",
    "   pure function: (data: dict, output_path: str) → str. Fully stateless.",
])

section("Prompt Strategy", [
    "The Gemini prompt uses a fixed system message with an explicit JSON schema and",
    "a deterministic template selection rule table (keyword → template name).",
    "This removes ambiguity from the model's decision and makes output predictable.",
    "Conversation history is passed as Gemini 'contents' turns so multi-turn refinement",
    "('change the budget to $60K') resolves correctly against the prior turn's context.",
    "If Gemini returns malformed JSON, the parser strips code fences and retries.",
])

section("Why Gemini 2.0 Flash?", [
    "Free tier via Google AI Studio — no billing setup required for a prototype.",
    "Reliably returns structured JSON given clear schema prompts (tested vs GPT-4o-mini).",
    "Sub-2s latency keeps the chat interaction feeling responsive.",
    "Already in production use on the Onified PO extraction pipeline — defensible.",
])

section("Trade-offs Considered", [
    "**ReportLab vs WeasyPrint:** ReportLab gives pixel-precise control over layout.",
    "   WeasyPrint would allow HTML/CSS templates which are easier to style but harder",
    "   to control pagination and form field placement.",
    "**Single HTML frontend vs React:** Vanilla JS keeps the repo zero-dependency on the",
    "   frontend. A React app would enable better streaming UX but adds build tooling.",
    "**Template registry as code vs DB:** Hardcoded registry is immediately readable and",
    "   reviewable. A DB-backed registry would enable runtime template CRUD.",
])

section("What I'd Build Next (2 More Weeks)", [
    "1. Brand injection — logo + hex colour per client, applied across all templates.",
    "2. File upload context — attach a CRM CSV export, auto-populate proposal fields.",
    "3. Email trigger — forward a brief to a mailbox, receive the doc as a reply.",
    "4. Streaming — stream Gemini's extraction trace into the chat while doc renders.",
    "5. More templates — SOW, invoice, project status report, NDA.",
])

# Footer
cv.setFillColor(DARK)
cv.rect(0, 0, W, 12*mm, fill=1, stroke=0)
cv.setFillColor(colors.HexColor("#94A3B8"))
cv.setFont("Helvetica", 8)
cv.drawCentredString(W/2, 4*mm, "DocGen — Architecture Writeup  ·  Confidential")

cv.save()
print("Architecture PDF saved:", out)
