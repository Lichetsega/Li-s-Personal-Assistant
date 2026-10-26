import time
import threading
from typing import Dict, List, Tuple

class SimpleRateLimiter:
    """
    In-memory, sliding-window rate limiter designed for public portfolio deployments.
    Tracks requests per client IP to prevent API quota drainage without external dependencies.
    """
    def __init__(self):
        # Format: { (ip, endpoint): [timestamp1, timestamp2, ...] }
        self._requests: Dict[Tuple[str, str], List[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(
        self,
        ip: str,
        endpoint: str = "chat",
        limit: int = 25,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Checks if the request from the given IP is within allowed limits.
        Returns: (is_allowed: bool, retry_after_seconds: int)
        """
        now = time.time()
        cutoff = now - window_seconds
        key = (ip, endpoint)

        with self._lock:
            if key not in self._requests:
                self._requests[key] = [now]
                return True, 0

            # Filter out timestamps older than the window
            timestamps = [t for t in self._requests[key] if t > cutoff]

            if len(timestamps) >= limit:
                # Calculate remaining seconds until oldest request expires
                oldest = timestamps[0]
                retry_after = max(1, int(cutoff - oldest + window_seconds))
                self._requests[key] = timestamps
                return False, retry_after

            timestamps.append(now)
            self._requests[key] = timestamps
            return True, 0

    def cleanup(self):
        """Periodic cleanup to prevent unbounded memory growth."""
        now = time.time()
        with self._lock:
            keys_to_delete = []
            for key, timestamps in self._requests.items():
                active = [t for t in timestamps if now - t < 120]
                if not active:
                    keys_to_delete.append(key)
                else:
                    self._requests[key] = active
            for k in keys_to_delete:
                del self._requests[k]

rate_limiter = SimpleRateLimiter()
