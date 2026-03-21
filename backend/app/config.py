import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "Bulk Email Sender API"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    @classmethod
    def get_gemini_key(cls) -> str | None:
        return cls.GEMINI_API_KEY

settings = Settings()
