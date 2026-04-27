"""
template_selector.py
---------------------
Maps parsed intent → the correct renderer function and template config.
Clean separation: this module knows NOTHING about rendering details.
"""

TEMPLATE_REGISTRY = {
    "sales_proposal": {
        "doc_type": "pdf",
        "renderer": "pdf",
        "label": "Sales Proposal",
        "description": "Full sales proposal with scope, budget, timeline and next steps.",
        "required_fields": ["client_name", "project_name", "budget", "kickoff_date"],
        "defaults": {
            "project_name": "Custom Solution",
            "budget": "TBD",
            "kickoff_date": "TBD",
            "client_name": "Valued Client",
            "prepared_by": "Agentic Solutions Team",
            "scope_items": [
                "Discovery & Requirements Gathering",
                "System Architecture & Design",
                "Development & Integration",
                "Testing & Quality Assurance",
                "Deployment & Handover",
            ],
        },
    },
    "one_pager": {
        "doc_type": "pdf",
        "renderer": "pdf",
        "label": "Project One-Pager",
        "description": "Concise single-page project overview for stakeholders.",
        "required_fields": ["client_name", "project_name"],
        "defaults": {
            "project_name": "Digital Transformation Initiative",
            "client_name": "Valued Client",
            "tagline": "Clarity. Speed. Results.",
            "objective": "Streamline operations and drive measurable growth.",
            "deliverables": [
                "Fully integrated platform",
                "Team onboarding & training",
                "30-day post-launch support",
            ],
            "timeline": "8 weeks",
            "budget": "Contact us",
        },
    },
    "discovery_call": {
        "doc_type": "ppt",
        "renderer": "ppt",
        "label": "Discovery Call Brief",
        "description": "PPT deck for a discovery / intro sales call.",
        "required_fields": ["client_name", "meeting_date"],
        "defaults": {
            "client_name": "Prospective Client",
            "meeting_date": "Upcoming",
            "prepared_by": "Agentic Solutions",
            "agenda": [
                "Introductions & Company Overview",
                "Understanding Your Current Challenges",
                "Our Approach & Methodology",
                "Relevant Case Studies",
                "Proposed Next Steps",
            ],
            "pain_points": [
                "Manual processes slowing growth",
                "Disconnected systems causing data silos",
                "Difficulty scaling operations",
            ],
            "our_strengths": [
                "10+ years enterprise delivery",
                "Certified across major CRM/ERP platforms",
                "Dedicated post-launch support",
            ],
        },
    },
    "onboarding_form": {
        "doc_type": "pdf",
        "renderer": "pdf_form",
        "label": "Fillable Onboarding Form",
        "description": "Fillable PDF form for new employee/sales rep onboarding.",
        "required_fields": ["client_name"],
        "defaults": {
            "client_name": "Your Company",
            "form_title": "New Sales Rep Onboarding Form",
            "rep_fields": ["Full Name", "Role / Title", "Start Date", "Direct Manager"],
        },
    },
}


def select_template(intent: dict) -> dict:
    """
    Takes parsed intent dict, returns template config merged with extracted fields.
    """
    template_key = intent.get("template", "sales_proposal")
    if template_key not in TEMPLATE_REGISTRY:
        template_key = "sales_proposal"

    config = TEMPLATE_REGISTRY[template_key].copy()
    # Deep copy defaults so we don't mutate registry
    data = config["defaults"].copy()

    # Overlay extracted fields from intent
    if intent.get("client_name"):
        data["client_name"] = intent["client_name"]

    extracted = intent.get("fields", {})
    for key, val in extracted.items():
        if val:
            data[key] = val

    # Handle rep_fields list for onboarding form
    if template_key == "onboarding_form" and "rep_fields" in extracted:
        raw = extracted["rep_fields"]
        if isinstance(raw, list):
            data["rep_fields"] = [f.title() for f in raw]

    config["data"] = data
    config["template_key"] = template_key
    return config
