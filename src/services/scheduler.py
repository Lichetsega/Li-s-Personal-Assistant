import time
import threading
import logging
from typing import List, Dict, Any, Callable, Optional

logger = logging.getLogger("ReminderScheduler")

class ReminderScheduler:
    """
    Proactive Background Timer & Reminder Engine.
    Schedules background tasks and triggers proactive alerts to voice TTS & Web UI.
    """
    def __init__(self):
        self.reminders: List[Dict[str, Any]] = []
        self.callbacks: List[Callable[[str], None]] = []

    def register_callback(self, callback: Callable[[str], None]):
        """Registers a callback function to notify when a reminder triggers."""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def set_reminder(self, reminder_text: str, delay_minutes: float) -> str:
        """
        Schedules a proactive reminder after delay_minutes.
        """
        if not reminder_text or delay_minutes <= 0:
            return "Please provide a valid reminder text and time delay."

        delay_seconds = delay_minutes * 60.0
        trigger_time = time.time() + delay_seconds
        trigger_str = time.strftime("%I:%M %p", time.localtime(trigger_time))

        reminder_item = {
            "id": len(self.reminders) + 1,
            "text": reminder_text,
            "delay_minutes": delay_minutes,
            "trigger_time": trigger_time,
            "trigger_str": trigger_str,
            "status": "pending"
        }
        self.reminders.append(reminder_item)

        # Launch background timer
        timer = threading.Timer(delay_seconds, self._trigger_reminder, args=(reminder_item,))
        timer.daemon = True
        timer.start()

        logger.info(f"Scheduled reminder: '{reminder_text}' in {delay_minutes} minute(s) at {trigger_str}")
        return f"Got it, Li! I've set a reminder for '{reminder_text}' in {delay_minutes} minute(s) (at {trigger_str})."

    def _trigger_reminder(self, reminder_item: Dict[str, Any]):
        """Internal handler called when timer expires."""
        reminder_item["status"] = "triggered"
        alert_msg = f"⏰ PROACTIVE REMINDER FOR LI: {reminder_item['text']}"
        logger.info(f"Triggered Proactive Reminder: {alert_msg}")

        # Execute registered callbacks (TTS & Web UI notification)
        for callback in self.callbacks:
            try:
                callback(alert_msg)
            except Exception as e:
                logger.error(f"Error executing reminder callback: {e}")

    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Returns active pending reminders."""
        return [r for r in self.reminders if r["status"] == "pending"]

    def list_reminders_summary(self) -> str:
        """Returns textual summary of pending reminders."""
        pending = self.get_pending_reminders()
        if not pending:
            return "You have no active pending reminders, Li."
        
        summary = "Here are your active reminders, Li:\n"
        for r in pending:
            summary += f"• '{r['text']}' at {r['trigger_str']}\n"
        return summary
