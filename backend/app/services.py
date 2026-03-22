import jinja2
import io
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai
import json
import re
from typing import List, Dict
from app.models import Recipient, EmailTemplate, BulkEmailRequest, AIGenerateRequest
from app.config import settings

class EmailService:
    @staticmethod
    def render_template(template_str: str, variables: Dict[str, str]) -> str:
        t = jinja2.Template(template_str)
        return t.render(**variables)

    @staticmethod
    def generate_csv_template(placeholders: List[str]) -> bytes:
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\r\n')
        headers = ["email"] + placeholders
        writer.writerow(headers)
        
        if placeholders:
            writer.writerow(["example@hotel.com"] + ["example_value" for _ in placeholders])
        else:
            writer.writerow(["example@hotel.com"])
        
        content = "\ufeff" + output.getvalue()
        return content.encode("utf-8")

    @classmethod
    def send_bulk_emails(cls, request: BulkEmailRequest) -> List[Dict]:
        results = []
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(request.smtp_user, request.smtp_password)
        
        for recipient in request.recipients:
            try:
                vars = {"email": recipient.email, **recipient.variables}
                subject = cls.render_template(request.template.subject, vars)
                body = cls.render_template(request.template.body, vars)
                
                msg = MIMEMultipart()
                msg['From'] = request.smtp_user
                msg['To'] = recipient.email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                
                server.send_message(msg)
                
                results.append({"id": recipient.id, "status": "success"})
            except Exception as e:
                results.append({"id": recipient.id, "status": "failed", "error": str(e)})
        
        server.quit()
        return results

class AIService:
    @staticmethod
    def generate_email(request: AIGenerateRequest) -> Dict[str, str]:
        # --- HARDCODED MOCK RESPONSE FOR UI TESTING ---
        # (Remove this return statement to re-enable actual Gemini AI generation)
        return {
            "subject": "Collaboration Inquiry | Globe Plates x {{hotel_name}}",
            "body": "Dear {{hotel_name}} Team,\n\nThis is a hardcoded mock response to help you test the UI without hitting the Gemini API and expending your quota limits!\n\nAs you can see, the popup modal should display this text nicely.\n\nWarm regards,\nGlobe Plates"
        }
        
        api_key = settings.get_gemini_key()
        if not api_key:
            raise ValueError("Gemini API key is required")
            
        genai.configure(api_key=api_key)
        # Using gemini-2.5-flash since this API Key tier exclusively supports newer preview/advanced models without rate limits
        model = genai.GenerativeModel("gemini-2.5-flash")

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
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()

        try:
            result = json.loads(text)
            if "subject" not in result or "body" not in result:
                raise ValueError("Response missing 'subject' or 'body' keys")
            return {"subject": result["subject"], "body": result["body"]}
        except json.JSONDecodeError:
            raise ValueError(f"AI returned invalid JSON. Raw response: {text[:500]}")
