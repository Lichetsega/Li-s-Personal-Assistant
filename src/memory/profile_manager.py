import json
import shutil
from pathlib import Path
from src.config import USER_PROFILE_PATH, USER_PROFILE_EXAMPLE_PATH
from src.memory.schema import UserProfile

class ProfileManager:
    def __init__(self, profile_path: Path = USER_PROFILE_PATH, example_path: Path = USER_PROFILE_EXAMPLE_PATH):
        self.profile_path = profile_path
        self.example_path = example_path
        self._ensure_profile_exists()

    def _ensure_profile_exists(self):
        if not self.profile_path.exists():
            if self.example_path.exists():
                shutil.copy(self.example_path, self.profile_path)
            else:
                default_profile = UserProfile()
                self.save_profile(default_profile)

    def load_profile(self) -> UserProfile:
        try:
            if self.profile_path.exists():
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return UserProfile(**data)
        except Exception as e:
            print(f"[ProfileManager] Warning: Error loading user profile: {e}")
        return UserProfile()

    def save_profile(self, profile: UserProfile):
        try:
            self.profile_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.profile_path, "w", encoding="utf-8") as f:
                json.dump(profile.model_dump(), f, indent=2)
        except Exception as e:
            print(f"[ProfileManager] Error saving user profile: {e}")
