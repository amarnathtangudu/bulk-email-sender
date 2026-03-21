from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional

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
