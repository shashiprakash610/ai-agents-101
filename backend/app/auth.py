from fastapi import Header, HTTPException
from app.config import settings

def get_user_id(x_api_key: str = Header(default="")) -> str:
    # Minimal auth: one API key = one user.
    # Later you can map keys to users from a DB.
    if not getattr(settings, "APP_API_KEY", ""):
        raise HTTPException(status_code=500, detail="APP_API_KEY not configured")

    if x_api_key != settings.APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return "user_001"
