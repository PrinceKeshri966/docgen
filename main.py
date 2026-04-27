"""
main.py
-------
FastAPI backend — single /chat endpoint that:
1. Calls Gemini to parse intent
2. Selects template
3. Renders the document
4. Returns download URL + chat reply
"""

import os, uuid, json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from intent_parser import parse_intent
from template_selector import select_template
from renderers.pdf_renderer import render_pdf
from renderers.ppt_renderer import render_ppt

app = FastAPI(title="DocGen — Chat-Based Document Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/static",  StaticFiles(directory="frontend"), name="frontend")


# ── Models ───────────────────────────────────────────────────────────────────
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []


# ── Helpers ──────────────────────────────────────────────────────────────────
def _friendly_reply(template_cfg: dict, intent: dict) -> str:
    label   = template_cfg.get("label", "Document")
    client  = template_cfg["data"].get("client_name", "your client")
    doc_type = template_cfg.get("doc_type", "file")
    ext = "PDF" if doc_type in ("pdf",) else "PPT"

    if intent.get("refinement"):
        return (
            f"✅ Done! I've applied your changes and regenerated the **{label}** "
            f"for **{client}** as a {ext}. Click below to download."
        )
    return (
        f"✅ Your **{label}** for **{client}** is ready! "
        f"I've generated a {ext} with all the details you mentioned. "
        f"Click the download button to grab it."
    )


# ── Main endpoint ────────────────────────────────────────────────────────────
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # 1. Parse intent via Gemini
        gemini_history = [
            {"role": m.role if m.role in ("user","model") else "user",
             "parts": [{"text": m.content}]}
            for m in req.history
        ]
        intent = parse_intent(req.message, gemini_history)

        # 2. Select template + merge data
        template_cfg = select_template(intent)
        template_key = template_cfg["template_key"]
        renderer     = template_cfg["renderer"]
        data         = template_cfg["data"]

        # 3. Render document
        file_id   = uuid.uuid4().hex[:10]
        ext       = "pdf" if renderer in ("pdf", "pdf_form") else "pptx"
        filename  = f"{template_key}_{file_id}.{ext}"
        out_path  = str(OUTPUT_DIR / filename)

        if renderer in ("pdf", "pdf_form"):
            render_pdf(template_key, data, out_path)
        else:
            render_ppt(template_key, data, out_path)

        # 4. Build response
        reply = _friendly_reply(template_cfg, intent)

        return JSONResponse({
            "reply":        reply,
            "download_url": f"/outputs/{filename}",
            "filename":     filename,
            "doc_type":     ext,
            "template":     template_cfg["label"],
            "intent":       intent,       # useful for debugging / defense
        })

    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Gemini returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/download/{filename}")
async def download(filename: str):
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(str(path), filename=filename)


@app.get("/")
async def root():
    return FileResponse("frontend/index.html")
