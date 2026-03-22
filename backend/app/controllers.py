from fastapi import APIRouter, HTTPException, Response
from app.models import (
    Recipient, EmailTemplate, BulkEmailRequest, TemplateRequest, AIGenerateRequest
)
from app.services import EmailService, AIService

router = APIRouter()

@router.post("/generate-template")
async def generate_template(request: TemplateRequest):
    content = EmailService.generate_csv_template(request.placeholders)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="recipients_template.csv"'}
    )

@router.post("/preview")
async def preview_email(template: EmailTemplate, recipient: Recipient):
    try:
        vars = {"email": recipient.email, **recipient.variables}
        subject = EmailService.render_template(template.subject, vars)
        body = EmailService.render_template(template.body, vars)
        return {"subject": subject, "body": body}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template rendering error: {str(e)}")

@router.post("/send-bulk")
async def send_bulk_emails(request: BulkEmailRequest):
    try:
        results = EmailService.send_bulk_emails(request)
        return {"results": results}
    except Exception as e:
        print(f"SMTP Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect/login to SMTP: {str(e)}")

import traceback

@router.post("/generate-email")
async def generate_email(request: AIGenerateRequest):
    try:
        return AIService.generate_email(request)
    except ValueError as e:
        print(f"ValueError in generate_email: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Exception in generate_email: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
