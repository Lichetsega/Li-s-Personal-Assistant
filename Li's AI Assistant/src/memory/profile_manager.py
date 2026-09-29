import os
import json
import logging
from typing import Dict, Any

from src.memory.schema import UserProfile, HAS_PYDANTIC

logger = logging.getLogger("ProfileManager")

DEFAULT_PROFILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "user_profile.json")
)

class ProfileManager:
    """
    Manages loading, saving, validating, and retrieving Li's User Profile.
    """
    def __init__(self, profile_path: str = None):
        self.profile_path = profile_path or DEFAULT_PROFILE_PATH
        self.profile: UserProfile = self._load_or_create_profile()

    def _load_or_create_profile(self) -> UserProfile:
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)

        if not os.path.exists(self.profile_path):
            logger.info(f"User profile file not found. Creating default profile at {self.profile_path}")
            profile = UserProfile()
            self.save_profile(profile)
            return profile

        try:
            with open(self.profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if HAS_PYDANTIC:
                profile = UserProfile.model_validate(data) if hasattr(UserProfile, "model_validate") else UserProfile(**data)
            else:
                profile = UserProfile()
            logger.info("Successfully loaded User Profile.")
            return profile
        except Exception as e:
            logger.error(f"Error loading User Profile from {self.profile_path}: {e}. Falling back to default.")
            profile = UserProfile()
            return profile

    def get_profile(self) -> UserProfile:
        return self.profile

    def save_profile(self, profile: UserProfile = None) -> bool:
        if profile:
            self.profile = profile

        try:
            os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
            if HAS_PYDANTIC and hasattr(self.profile, "model_dump"):
                data = self.profile.model_dump()
            elif HAS_PYDANTIC and hasattr(self.profile, "dict"):
                data = self.profile.dict()
            else:
                data = {
                    "identity": self.profile.identity.__dict__,
                    "preferences": self.profile.preferences.__dict__,
                    "key_rules": self.profile.key_rules,
                    "custom_facts": self.profile.custom_facts
                }

            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved User Profile to {self.profile_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save User Profile to {self.profile_path}: {e}")
            return False

    def update_custom_fact(self, fact: str) -> bool:
        """Adds a new key fact to Li's custom facts list."""
        if fact and fact not in self.profile.custom_facts:
            self.profile.custom_facts.append(fact)
            return self.save_profile()
        return False
