import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "Agentic Research Assistant"
    CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "research_reports")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")  # you can change later

settings = Settings()
