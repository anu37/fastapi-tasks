#  Design a FastAPI module that sends notifications asynchronously.

# Requirements:

# Create a /notify POST endpoint that accepts:

# { "email": "user@example.com", "message": "Welcome to FastAPI" }
# Use BackgroundTasks to simulate sending an email (async sleep + print/log).
# Store notification logs in a global list notification_log.
# Add a /from fastapi import FastAPI, HTTPException, BackgroundTasks
# Apply modular structure: routers, services, schemas, main.py.

from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
import asyncio
from typing import List

notification_log: List[str] = []
app = FastAPI(title="Notification Task", version="0.0.1")

class NotifyRequestModel(BaseModel):
    email: EmailStr
    message: str


async def send_notification(email, message):
    await asyncio.sleep(10)
    print("sent notification")
    return True



@app.post(path="/notify")
async def email(request:NotifyRequestModel, backgroundtask:BackgroundTasks):
    email = request['email']
    message = request['message']
    backgroundtask.add_task(send_notification, email, message)
    return {"detail": "Notification scheduled"}
        
@app.get("/notifications")
async def get_notification_log():
    return notification_log


