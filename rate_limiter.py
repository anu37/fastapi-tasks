# .	Rate Limiting Middleware
# Build a simple in-memory rate limiter in FastAPI that:
# 	•	Limits each client IP to N requests per minute (say 10/min).
# 	•	Returns 429 when limit is exceeded.
# 	•	Use dependency injection or middleware, and demonstrate with a sample /ping endpoint.

from fastapi import FastAPI, HTTPException, Request
from datetime import datetime, timedelta

app = FastAPI()

class RateLimiter:
    def __init__(self, limit: int = 10, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window = timedelta(seconds=window_seconds)
        # ip -> (count, window_start)
        self.requests: dict[str, tuple[int, datetime]] = {}

    def check(self, request: Request) -> None:
        client_ip = request.client.host
        now = datetime.now()

        if client_ip not in self.requests:
            # first request from this IP
            self.requests[client_ip] = (1, now)
            return

        count, window_start = self.requests[client_ip]
        elapsed = now - window_start

        if elapsed >= self.window:
            # window expired → reset
            self.requests[client_ip] = (1, now)
            return

        # window still valid
        if count >= self.limit:
            # already hit the limit
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # increment within window
        self.requests[client_ip] = (count + 1, window_start)


rate_limiter = RateLimiter(limit=10, window_seconds=60)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    rate_limiter.check(request)
    response = await call_next(request)
    return response


@app.get("/ping")
async def ping():
    return {"message": "pong"}