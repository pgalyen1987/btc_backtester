from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Settings(BaseModel):
    darkMode: bool
    autoRefresh: bool
    notifications: bool

# Default settings
default_settings = Settings(
    darkMode=False,
    autoRefresh=True,
    notifications=True
)

# In-memory storage for settings (in a real app, this would be in a database)
current_settings = default_settings.dict()

@router.get("/api/settings")
async def get_settings():
    return current_settings

@router.post("/api/settings")
async def update_settings(settings: Settings):
    global current_settings
    current_settings = settings.dict()
    return current_settings 