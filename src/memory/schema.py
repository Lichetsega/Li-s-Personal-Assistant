from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MemoryCategory(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    GOAL = "goal"
    HABIT = "habit"
    GENERAL = "general"

class UserProfile(BaseModel):
    name: str = Field(default="Li", description="Name of the user")
    bio: str = Field(default="", description="General background or bio of the user")
    communication_style: str = Field(default="Friendly, efficient, and direct", description="Preferred communication style")
    preferred_voice: str = Field(default="Female", description="Preferred voice gender for TTS")
    interests: List[str] = Field(default_factory=list, description="List of user interests")
    custom_rules: List[str] = Field(default_factory=list, description="Custom behavioral rules for assistant")

class MemoryItem(BaseModel):
    id: Optional[int] = None
    category: MemoryCategory = MemoryCategory.FACT
    content: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class KnowledgeExcerpt(BaseModel):
    file_name: str
    file_path: str
    content: str
    relevance_score: float = 1.0
