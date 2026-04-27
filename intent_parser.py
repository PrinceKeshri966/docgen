"""
intent_parser.py
-----------------
Uses Gemini 2.5 Flash to extract structured intent from a user's natural language message.
Returns: doc_type, template_name, client_name, and all dynamic fields needed for the doc.
"""

import os, json, requests
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

SYSTEM_PROMPT = """
You are a document intent parser. A user sends a natural language request to generate a business document.
Your job is to extract structured data from their message.

You must respond ONLY with a valid JSON object — no markdown, no explanation, no backticks.

JSON schema:
{
  "doc_type": "pdf" | "ppt",
  "template": "sales_proposal" | "one_pager" | "discovery_call" | "onboarding_form",
  "client_name": "<string or null>",
  "fields": {
    // any key-value pairs you can extract, e.g.:
    // "budget": "$40K",
    // "kickoff_date": "Nov 15",
    // "project_name": "HubSpot CRM Build",
    // "meeting_date": "tomorrow",
    // "rep_fields": ["name", "role", "start date", "manager"]
  },
  "refinement": "<original instruction if this is a refinement request, else null>"
}

Template selection rules:
- "sales proposal" or "proposal" → template: "sales_proposal", doc_type: "pdf"
- "one pager" or "one-pager" or "overview" → template: "one_pager", doc_type: "pdf"
- "discovery call" or "discovery brief" → template: "discovery_call", doc_type: "ppt"
- "onboarding form" or "fillable form" or "form" → template: "onboarding_form", doc_type: "pdf"

If the user says "change X to Y and regenerate" — set refinement to their instruction.
"""

def parse_intent(user_message: str, history: list = None) -> dict:
    """
    Calls Gemini to extract structured intent from user message.
    history: list of {"role": "user"/"model", "parts": [{"text": "..."}]}
    """
    contents = []
    if history:
        contents.extend(history)
    contents.append({
        "role": "user",
        "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser request: {user_message}"}]
    })

    payload = {"contents": contents}
    resp = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip markdown fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)
