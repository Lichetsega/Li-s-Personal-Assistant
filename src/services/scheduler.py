import asyncio
from typing import Callable, List, Dict, Any
from datetime import datetime

class ReminderScheduler:
    def __init__(self):
        self.reminders: List[Dict[str, Any]] = []

    def schedule_reminder(self, text: str, seconds: int, callback: Callable[[str], None] = None):
        reminder = {
            "text": text,
            "seconds": seconds,
            "created_at": datetime.now().isoformat()
        }
        self.reminders.append(reminder)
        
        async def _timer():
            await asyncio.sleep(seconds)
            print(f"[PROACTIVE REMINDER] 🔔 {text}")
            if callback:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(text)
                    else:
                        callback(text)
                except Exception as e:
                    print(f"[ReminderScheduler] Callback error: {e}")

        asyncio.create_task(_timer())
        return f"Reminder set for {seconds} seconds from now: '{text}'"
