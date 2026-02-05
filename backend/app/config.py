import os
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from backend root (where this file is backend/app/config.py, so .env is ../.env)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    APP_NAME = "Agentic Research Assistant"
    
    # LLM keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # RAG
    CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "research_reports")

    # API Auth
    APP_API_KEY = os.getenv("APP_API_KEY", "")

settings = Settings()
