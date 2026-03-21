from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
import jinja2
import io
import csv
import smtplib
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import google.generativeai as genai
import base64

app = FastAPI(title="Bulk Email Sender API")

# Enable CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

class Recipient(BaseModel):
    id: str
    email: EmailStr
    variables: Dict[str, str] = {}

class EmailTemplate(BaseModel):
    subject: str
    body: str

class BulkEmailRequest(BaseModel):
    smtp_user: str
    smtp_password: str
    template: EmailTemplate
    recipients: List[Recipient]

class TemplateRequest(BaseModel):
    placeholders: List[str]

class AIGenerateRequest(BaseModel):
    prompt: str
    mode: str = "generate"  # generate | rewrite | improve
    existing_subject: Optional[str] = None
    existing_body: Optional[str] = None
    placeholders: List[str] = []

def render_template(template_str: str, variables: Dict[str, str]) -> str:
    # Handle both {{var}} (Angular/Custom) and jinja2 style if needed
    # For simplicity, we just use jinja2 but the UI uses {{var}} 
    # Let's ensure compatibility
    t = jinja2.Template(template_str)
    return t.render(**variables)

# Pre-encoded Gemini API Key
# Original: AIzaSyC6z9EvzBFJnbKjFQlf9VicvBHFzI7YJ8Y
ENCODED_GEMINI_KEY = "QUl6YVN5QzZ6OUV2ekJGSm5ia0pqRlFsZjlWaWN2QkhGekk3WUp4WQ=="

def get_gemini_key():
    return base64.b64decode(ENCODED_GEMINI_KEY).decode('utf-8')

@app.post("/generate-template")
async def generate_template(request: TemplateRequest):
    output = io.StringIO()
    # Use lineterminator='\r\n' for better Excel compatibility
    writer = csv.writer(output, lineterminator='\r\n')
    headers = ["email"] + request.placeholders
    writer.writerow(headers)
    
    # Add an example row
    if request.placeholders:
        writer.writerow(["example@hotel.com"] + ["example_value" for _ in request.placeholders])
    else:
        writer.writerow(["example@hotel.com"])
    
    # Add UTF-8 BOM for Excel compatibility
    content = "\ufeff" + output.getvalue()
    
    from fastapi import Response
    return Response(
        content=content.encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="recipients_template.csv"'}
    )

@app.post("/preview")
async def preview_email(template: EmailTemplate, recipient: Recipient):
    try:
        vars = {"email": recipient.email, **recipient.variables}
        subject = render_template(template.subject, vars)
        body = render_template(template.body, vars)
        return {"subject": subject, "body": body}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template rendering error: {str(e)}")

@app.post("/send-bulk")
async def send_bulk_emails(request: BulkEmailRequest):
    results = []
    try:
        # Connect to SMTP server once for the entire batch
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(request.smtp_user, request.smtp_password)
        
        for recipient in request.recipients:
            try:
                vars = {"email": recipient.email, **recipient.variables}
                subject = render_template(request.template.subject, vars)
                body = render_template(request.template.body, vars)
                
                msg = MIMEMultipart()
                msg['From'] = request.smtp_user
                msg['To'] = recipient.email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                
                server.send_message(msg)
                
                results.append({
                    "id": recipient.id,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "id": recipient.id,
                    "status": "failed",
                    "error": str(e)
                })
        
        server.quit()
        return {"results": results}
    except Exception as e:
        print(f"SMTP Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect/login to SMTP: {str(e)}")

@app.post("/generate-email")
async def generate_email(request: AIGenerateRequest):
    try:
        # Use the backend encoded key
        api_key = get_gemini_key()
        if not api_key:
            raise HTTPException(status_code=400, detail="Gemini API key is required")
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        placeholder_list = ", ".join([f"{{{{{p}}}}}" for p in request.placeholders]) if request.placeholders else "none detected yet"

        system_instruction = (
            "You are an expert email copywriter for influencer outreach. "
            "You write professional, warm, and compelling collaboration emails that influencers send to hotels, cafes, and resorts.\n\n"
            "RULES:\n"
            "1. Return ONLY a JSON object with exactly two keys: \"subject\" and \"body\".\n"
            "2. Do NOT include any markdown, code fences, or extra text outside the JSON.\n"
            "3. Use these template placeholders in the output where appropriate: " + placeholder_list + ". "
            "Keep them in the {{placeholder}} format so the system can replace them per recipient.\n"
            "4. The body should be plain text (no HTML). Use line breaks for paragraphs.\n"
            "5. Keep the tone professional yet personable — like a confident creator pitching a collaboration.\n"
            "6. The email should feel bespoke, not mass-produced."
        )

        if request.mode == "rewrite" and request.existing_body:
            user_prompt = (
                f"Rewrite and improve this outreach email based on the user's instructions.\n\n"
                f"USER INSTRUCTIONS: {request.prompt}\n\n"
                f"EXISTING SUBJECT: {request.existing_subject or '(none)'}\n"
                f"EXISTING BODY:\n{request.existing_body}\n\n"
                f"Return the rewritten version as a JSON object with \"subject\" and \"body\" keys."
            )
        elif request.mode == "improve" and request.existing_body:
            user_prompt = (
                f"Improve the tone, grammar, and impact of this outreach email. "
                f"Make it more compelling and professional while keeping the same structure and placeholders.\n\n"
                f"Additional notes from user: {request.prompt}\n\n"
                f"EXISTING SUBJECT: {request.existing_subject or '(none)'}\n"
                f"EXISTING BODY:\n{request.existing_body}\n\n"
                f"Return the improved version as a JSON object with \"subject\" and \"body\" keys."
            )
        else:
            user_prompt = (
                f"Generate a professional influencer outreach email based on these instructions:\n\n"
                f"{request.prompt}\n\n"
                f"Available placeholders to use: {placeholder_list}\n\n"
                f"Return the email as a JSON object with \"subject\" and \"body\" keys."
            )

        response = model.generate_content(
            [system_instruction, user_prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=2048,
            )
        )

        text = response.text.strip()
        # Strip markdown code fences if present
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()

        result = json.loads(text)

        if "subject" not in result or "body" not in result:
            raise ValueError("Response missing 'subject' or 'body' keys")

        return {"subject": result["subject"], "body": result["body"]}

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON. Raw response: {text[:500]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
