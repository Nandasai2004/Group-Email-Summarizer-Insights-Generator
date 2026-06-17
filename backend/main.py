from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from backend.database import SessionLocal, Email
import uuid
import logging

from backend.ai_processor import process_single_thread

app = FastAPI(title="GES Webhook API")

@app.get("/")
def root():
    return {"message": "hello world"}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailPayload(BaseModel):
    from_email: str
    from_name: Optional[str] = ""
    subject: str
    body: str
    thread_id: Optional[str] = None
    to_group: Optional[str] = ""

@app.post("/webhook/email")
async def receive_email(payload: EmailPayload, background_tasks: BackgroundTasks):
    """
    Real-world webhook endpoint to ingest live emails.
    """
    db = SessionLocal()
    try:
        # Generate a unique ID for the new email
        email_id = str(uuid.uuid4())
        
        # If no thread_id is provided, assume it's a new thread
        thread_id = payload.thread_id if payload.thread_id else str(uuid.uuid4())
        
        # Calculate sequence based on existing thread
        existing_thread_emails = db.query(Email).filter(Email.thread_id == thread_id).count()
        
        new_email = Email(
            id=email_id,
            thread_id=thread_id,
            thread_sequence=existing_thread_emails + 1,
            sent_timestamp=datetime.now(),
            from_name=payload.from_name,
            from_email=payload.from_email,
            to_group=payload.to_group,
            subject=payload.subject,
            email_body=payload.body,
            processed_by_ai=False
        )
        db.add(new_email)
        db.commit()
        
        logger.info(f"Ingested new email {email_id} into thread {thread_id}")
        
        # Trigger background processing so we return 200 OK immediately
        background_tasks.add_task(process_single_thread, thread_id)
        
        return {"status": "success", "email_id": email_id, "thread_id": thread_id}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
