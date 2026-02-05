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



class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "research_reports")

settings = Settings()


APP_API_KEY = os.getenv("APP_API_KEY", "")
