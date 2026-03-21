import os
import base64
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "Bulk Email Sender API"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # Fallback key
    ENCODED_GEMINI_KEY = "QUl6YVN5QzZ6OUV2ekJGSm5ia0pqRlFsZjlWaWN2QkhGekk3WUp4WQ=="

    @classmethod
    def get_gemini_key(cls) -> str:
        if cls.GEMINI_API_KEY:
            return cls.GEMINI_API_KEY
        return base64.b64decode(cls.ENCODED_GEMINI_KEY).decode('utf-8')

settings = Settings()
