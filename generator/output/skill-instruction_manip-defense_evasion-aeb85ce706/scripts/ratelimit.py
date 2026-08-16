# Simple rate limiter using token bucket
import time
import asyncio

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, max_calls, period=60):
        self.max_calls = max_calls
        self.period = period
        self.tokens = max_calls
        self.updated = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token, waiting if necessary."""
        async with self.lock:
            while self.tokens <= 0:
                now = time.time()
                elapsed = now - self.updated
                if elapsed >= self.period:
                    self.tokens = self.max_calls
                    self.updated = now
                else:
                    wait = self.period - elapsed
                    await asyncio.sleep(min(wait, 1))
            self.tokens -= 1