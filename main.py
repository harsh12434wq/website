"""
DSS Group Website - FastAPI Backend
Deploy on AWS Lambda with Mangum, or run locally with uvicorn.

Local run:
    pip install -r requirements.txt
    uvicorn main:app --reload

AWS Lambda:
    The `handler` function is the Lambda entry point.
    Set handler to: main.handler
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

# ─── Logging ───
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── App ───
app = FastAPI(
    title="DSS Group Website",
    description="Defensive Security Services - Corporate Website API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files ───

STATIC_DIR = Path(__file__).parent


# ─── Models ───
class ContactFormData(BaseModel):
    name: str
    phone: str
    email: Optional[str] = ""
    service: str
    message: Optional[str] = ""


# ─── Routes ───

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main SPA."""
    html_file = STATIC_DIR / "index.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))


@app.post("/api/contact")
async def handle_contact(form: ContactFormData):
    """
    Handle contact form submissions.
    
    In production, integrate with:
    - AWS SES for email notifications
    - A database (DynamoDB, RDS) to store inquiries
    - A CRM system
    """
    logger.info(
        "New contact form submission: name=%s, service=%s, phone=%s",
        form.name,
        form.service,
        form.phone,
    )

    # TODO: Integrate with AWS SES to send email notifications
    # Example:
    # import boto3
    # ses = boto3.client('ses', region_name='ap-south-1')
    # ses.send_email(
    #     Source='noreply@dssgroup.in',
    #     Destination={'ToAddresses': ['info@dssgroup.in']},
    #     Message={
    #         'Subject': {'Data': f'New Inquiry from {form.name}'},
    #         'Body': {'Text': {'Data': f'Name: {form.name}\nPhone: {form.phone}\nService: {form.service}\nMessage: {form.message}'}}
    #     }
    # )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Thank you for reaching out. We will contact you within 24 hours.",
        },
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for AWS load balancers / Route53."""
    return {"status": "healthy", "service": "DSS Group Website"}


@app.get("/api/services")
async def get_services():
    """Return services list (useful for SEO or dynamic rendering)."""
    return {
        "services": [
            {
                "id": "security",
                "name": "Security Personnel Services",
                "icon": "🛡️",
                "short": "Well-trained, background-verified security personnel for industrial, commercial, and residential premises.",
            },
            {
                "id": "manpower",
                "name": "Manpower & Labour Supply",
                "icon": "👷",
                "short": "Reliable and flexible manpower solutions for industrial, manufacturing, and commercial operations.",
            },
            {
                "id": "housekeeping",
                "name": "Housekeeping Services",
                "icon": "🧹",
                "short": "Professional housekeeping staff trained in systematic cleaning procedures and hygiene standards.",
            },
            {
                "id": "fabrication",
                "name": "Fabrication Services",
                "icon": "⚙️",
                "short": "High-quality B2B fabrication — structural, metal, and precision work to exact specifications.",
            },
        ]
    }
from fastapi.responses import FileResponse # Make sure this is imported at the top

# ─── Serve Static Assets ───
@app.get("/secc.png")
async def serve_image():
    """Serve the hero image."""
    image_path = STATIC_DIR / "secc.png"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

# ─── Catch-all for SPA routing ───
@app.get("/{full_path:path}", response_class=HTMLResponse)
# ... rest of your code ...

# ─── Catch-all for SPA routing ───
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_fallback(full_path: str):
    """Return index.html for any unmatched path (SPA routing)."""
    html_file = STATIC_DIR / "index.html"
    if not html_file.exists():
        raise HTTPException(status_code=404, detail="Not found")
    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))


# ─── AWS Lambda Handler (via Mangum) ───
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
    logger.info("Mangum handler initialized for AWS Lambda")
except ImportError:
    logger.warning("Mangum not installed — Lambda deployment unavailable. Run: pip install mangum")
    handler = None
