# DocGen — Chat-Based Document Generator

> Type a sentence. Get a download-ready PDF or PPT in seconds.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![Gemini](https://img.shields.io/badge/Gemini-2.0--flash-orange)

---

## What It Does

DocGen is a chat-first document generation prototype. A user types a natural language request, and the system:

1. **Parses intent** via Gemini 2.5 Flash — extracting doc type, template, client, and all relevant fields
2. **Selects a template** from a registry of 4 templates across 2 formats
3. **Hydrates the template** with extracted data + sensible defaults
4. **Renders a document** (PDF or PPTX) and returns a download link in the chat

---

## Supported Templates

| Format | Template | Trigger words |
|--------|----------|---------------|
| PDF | Sales Proposal | "proposal", "sales proposal" |
| PDF | Project One-Pager | "one pager", "overview", "one-pager" |
| PPT | Discovery Call Brief | "discovery call", "discovery brief" |
| PDF | Fillable Onboarding Form | "onboarding form", "fillable form" |

---

## Quick Start (10 minutes)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/docgen
cd docgen
pip install -r requirements.txt
```

### 2. Set your Gemini API key

Create a `.env` file (or export directly):

```bash
export GEMINI_API_KEY=your_key_here
```

Get a free key at [aistudio.google.com](https://aistudio.google.com)

### 3. Run

```bash
uvicorn main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000)

---

## Example Prompts

```
Create a sales proposal PDF for Acme Corp for a HubSpot CRM build. Budget $40K. Kickoff Nov 15.
```
```
Generate a discovery call brief PPT for our meeting with Wardell tomorrow.
```
```
Make a fillable onboarding form for new Wardell sales reps. Fields for name, role, start date, manager.
```

**Multi-turn refinement:**
```
Change the budget to $60K and regenerate.
```

---

## Project Structure

```
docgen/
├── main.py                  → FastAPI app, /chat endpoint, download route
├── intent_parser.py         → Gemini 2.5 Flash integration, returns structured JSON
├── template_selector.py     → Template registry + data hydration
├── renderers/
│   ├── pdf_renderer.py      → ReportLab: sales_proposal, one_pager, onboarding_form
│   └── ppt_renderer.py      → python-pptx: discovery_call, onboarding_summary
├── frontend/
│   └── index.html           → Single-file chat UI (vanilla JS)
├── outputs/                 → Generated files served statically
├── samples/                 → Pre-generated example documents
└── requirements.txt
```

---

## Architecture (4 clean layers)

```
User Chat Input
      │
      ▼
┌─────────────────────┐
│  1. Intent Parser   │  Gemini 2.5 Flash → JSON: {doc_type, template, client, fields}
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 2. Template Selector│  Registry lookup → template config + defaults
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  3. Data Hydrator   │  Merge extracted fields over defaults
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    4. Renderer      │  ReportLab (PDF) or python-pptx (PPT) → file on disk
└─────────┬───────────┘
          │
          ▼
   Download URL returned to chat
```

---

## Why Gemini 2.5 Flash?

- **Free tier available** via Google AI Studio — no billing needed for prototyping
- **Structured JSON output** — reliably returns parseable intent objects with clear prompting
- **Fast** — sub-2s response on intent parsing, keeping the chat feel responsive
- **Familiar** — used in production on the Onified PO extraction pipeline, so the team can defend every integration detail

---

## Sample Outputs

See [`/samples`](./samples/) for 4 pre-generated documents:

- `sales_proposal_acme.pdf` — Sales proposal for Acme Corp
- `onboarding_form_wardell.pdf` — Fillable onboarding form (try clicking the fields!)
- `discovery_call_wardell.pptx` — 5-slide discovery call deck
- `one_pager_globaltech.pdf` — Project one-pager

---

## API

### `POST /chat`

```json
{
  "message": "Create a sales proposal for Acme Corp...",
  "history": []
}
```

Response:
```json
{
  "reply": "✅ Your Sales Proposal for Acme Corp is ready!",
  "download_url": "/outputs/sales_proposal_abc123.pdf",
  "filename": "sales_proposal_abc123.pdf",
  "doc_type": "pdf",
  "template": "Sales Proposal",
  "intent": { "template": "sales_proposal", "client_name": "Acme Corp", ... }
}
```

---

## What I'd Build Next

1. **Brand injection** — Upload a logo + hex colour and have it injected into every template
2. **File upload context** — Attach a CRM export CSV and auto-populate proposal fields
3. **Email trigger** — Forward a brief to a mailbox, get the doc back as a reply
4. **More templates** — SOW, invoice, project status report
5. **Streaming** — Stream Gemini's extraction reasoning into the chat while the doc builds
