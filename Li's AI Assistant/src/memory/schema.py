import time
from enum import Enum
from typing import List, Dict, Any, Optional

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

class MemoryCategory(str, Enum):
    FACT = "FACT"
    PREFERENCE = "PREFERENCE"
    GOAL = "GOAL"
    RELATIONSHIP = "RELATIONSHIP"
    WORKFLOW = "WORKFLOW"

if HAS_PYDANTIC:
    class UserIdentity(BaseModel):
        name: str = "Li"
        preferred_name: str = "Li"
        bio: str = "Software Developer and AI enthusiast building personal AI voice tools."
        location: str = "London, UK"
        timezone: str = "UTC"

    class UserPreferences(BaseModel):
        communication_style: str = "Concise, friendly, direct, and intelligent."
        units: str = "Metric (Celsius, km)"
        favorite_topics: List[str] = ["AI & Machine Learning", "Python Development", "Technology", "Voice Assistants"]
        hobbies: List[str] = ["Coding", "Tech Reading", "Music"]
        voice_tone: str = "Warm, natural, clear vocal responses."

    class UserProfile(BaseModel):
        identity: UserIdentity = Field(default_factory=UserIdentity)
        preferences: UserPreferences = Field(default_factory=UserPreferences)
        key_rules: List[str] = Field(
            default_factory=lambda: [
                "Keep voice responses concise and suitable for Text-to-Speech playback.",
                "Address the user warmly as Li.",
                "Provide direct answers without unnecessary markdown boilerplate unless asked."
            ]
        )
        custom_facts: List[str] = Field(
            default_factory=lambda: [
                "Li is the primary developer and creator of this voice assistant project.",
                "Li values efficiency, clean architecture, and modular Python code."
            ]
        )

    class MemoryItem(BaseModel):
        id: Optional[int] = None
        category: MemoryCategory = MemoryCategory.FACT
        fact_text: str
        confidence_score: float = 1.0
        created_at: float = Field(default_factory=time.time)
        updated_at: float = Field(default_factory=time.time)

else:
    # Lightweight Dataclass fallback if pydantic is not installed
    from dataclasses import dataclass, field

    @dataclass
    class UserIdentity:
        name: str = "Li"
        preferred_name: str = "Li"
        bio: str = "Software Developer and AI enthusiast building personal AI voice tools."
        location: str = "London, UK"
        timezone: str = "UTC"

    @dataclass
    class UserPreferences:
        communication_style: str = "Concise, friendly, direct, and intelligent."
        units: str = "Metric (Celsius, km)"
        favorite_topics: List[str] = field(default_factory=lambda: ["AI & Machine Learning", "Python Development", "Technology", "Voice Assistants"])
        hobbies: List[str] = field(default_factory=lambda: ["Coding", "Tech Reading", "Music"])
        voice_tone: str = "Warm, natural, clear vocal responses."

    @dataclass
    class UserProfile:
        identity: UserIdentity = field(default_factory=UserIdentity)
        preferences: UserPreferences = field(default_factory=UserPreferences)
        key_rules: List[str] = field(default_factory=lambda: [
            "Keep voice responses concise and suitable for Text-to-Speech playback.",
            "Address the user warmly as Li.",
            "Provide direct answers without unnecessary markdown boilerplate unless asked."
        ])
        custom_facts: List[str] = field(default_factory=lambda: [
            "Li is the primary developer and creator of this voice assistant project.",
            "Li values efficiency, clean architecture, and modular Python code."
        ])

    @dataclass
    class MemoryItem:
        fact_text: str
        id: Optional[int] = None
        category: MemoryCategory = MemoryCategory.FACT
        confidence_score: float = 1.0
        created_at: float = field(default_factory=time.time)
        updated_at: float = field(default_factory=time.time)
