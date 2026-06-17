import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional
from backend.database import SessionLocal, Email, Task, Insight
from datetime import datetime
from tenacity import retry, wait_exponential, stop_after_attempt
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None # type: ignore
    CHROMADB_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip('"\'')

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    logger.warning("GEMINI_API_KEY is not set. Please set it in the .env file.")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here" else None

# Initialize local ChromaDB for semantic search conditionally
if CHROMADB_AVAILABLE:
    CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    insight_collection = chroma_client.get_or_create_collection(name="insights")
else:
    chroma_client = None
    insight_collection = None
    logger.warning("ChromaDB is not installed (likely on Vercel). Semantic Search embedding is disabled.")

class TaskExtraction(BaseModel):
    task_description: str
    owner: str
    due_date: Optional[str]
    status: str

class EmailAnalysis(BaseModel):
    summary: str
    tasks: List[TaskExtraction]
    decisions: Optional[str]
    follow_ups: Optional[str]
    topic: str

class ExecutiveReportAnalysis(BaseModel):
    top_topics: str
    key_decisions: str
    risks_bottlenecks: str
    workload_summary: str
    recommendations: str

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def analyze_thread(emails_in_thread: List[Email]) -> Optional[EmailAnalysis]:
    if not client:
        return None
        
    # Combine thread content for context
    thread_text = ""
    for email in sorted(emails_in_thread, key=lambda x: x.thread_sequence):
        thread_text += f"From: {email.from_name} ({email.from_email})\n"
        thread_text += f"Date: {email.sent_timestamp}\n"
        thread_text += f"Subject: {email.subject}\n"
        thread_text += f"Body: {email.email_body}\n"
        thread_text += "-" * 40 + "\n"
        
    prompt = f"""
    Analyze the following email thread and extract the required information:
    1. A concise summary of the discussion.
    2. Any action items/tasks, identifying the owner and due date if mentioned.
    3. Any key decisions made.
    4. Any pending follow-ups.
    5. A short classification topic for this thread.
    
    Email Thread:
    {thread_text}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are an expert AI assistant that extracts precise tasks, decisions, and summaries from business email threads.",
                response_mime_type="application/json",
                response_schema=EmailAnalysis,
                temperature=0.2,
            ),
        )
        if response.text:
            return EmailAnalysis.model_validate_json(response.text)
        return None
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise e # Let tenacity catch and retry

from backend.database import ExecutiveReport

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def generate_executive_report(start_date: datetime, end_date: datetime) -> Optional[int]:
    db = SessionLocal()
    try:
        insights = db.query(Insight).filter(Insight.created_date >= start_date, Insight.created_date <= end_date).all()
        
        # We find tasks that belong to emails sent in this date range
        # Or tasks that were created in this date range. Since tasks don't have created_at, 
        # we'll just pull tasks from emails sent in this date range.
        emails = db.query(Email).filter(Email.sent_timestamp >= start_date, Email.sent_timestamp <= end_date).all()
        email_ids = [e.id for e in emails]
        tasks = db.query(Task).filter(Task.email_id.in_(email_ids)).all() if email_ids else []

        if not insights and not tasks:
            logger.info("No data found for the given date range.")
            return None

        context_text = "--- Insights from Threads ---\n"
        for idx, insight in enumerate(insights):
            context_text += f"Thread {idx+1} Topic: {insight.topic}\nSummary: {insight.summary}\nDecisions: {insight.decisions}\nRisks/Follow-ups: {insight.follow_ups}\n\n"

        context_text += "--- Extracted Tasks ---\n"
        for task in tasks:
            context_text += f"Task: {task.task_description} | Owner: {task.owner} | Due: {task.due_date} | Status: {task.status}\n"

        prompt = f"""
        You are an expert executive analyst. Analyze the following aggregated data from email threads over a specific time period.
        Generate a highly professional macro-level intelligence report.
        
        Data:
        {context_text}
        """

        if not client:
            return None

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="Extract macro-level trends, top discussion topics, aggregated workload, key risks/bottlenecks, and provide strategic recommendations. Format output as JSON.",
                response_mime_type="application/json",
                response_schema=ExecutiveReportAnalysis,
                temperature=0.3,
            ),
        )
        
        if response.text:
            analysis = ExecutiveReportAnalysis.model_validate_json(response.text)
            
            # Calculate open and overdue tasks
            open_count = len([t for t in tasks if t.status.lower() != "completed" and t.status.lower() != "done"])
            
            # Simple heuristic for overdue (if due_date is present and we can parse it, but for simplicity, we'll let AI handle it or just do basic string check)
            # For now, let's just do a basic check if due_date is present and looks past, or assume 0 for MVP
            overdue_count = 0
            
            report = ExecutiveReport(
                start_date=start_date,
                end_date=end_date,
                top_topics=analysis.top_topics,
                key_decisions=analysis.key_decisions,
                risks_bottlenecks=analysis.risks_bottlenecks,
                workload_summary=analysis.workload_summary,
                recommendations=analysis.recommendations,
                open_tasks=open_count,
                overdue_tasks=overdue_count,
                created_at=datetime.now()
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            return int(report.id) # type: ignore
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating executive report: {e}")
        raise e
    finally:
        db.close()

def process_single_thread(thread_id: str):
    """
    Processes a single thread. Used by the webhook for real-time ingestion.
    """
    db = SessionLocal()
    try:
        logger.info(f"Processing thread dynamically: {thread_id}")
        thread_emails = db.query(Email).filter(Email.thread_id == thread_id).order_by(Email.thread_sequence).all()
        
        if not thread_emails:
            return
            
        unprocessed = [e for e in thread_emails if not e.processed_by_ai]
        if not unprocessed:
            logger.info("No unprocessed emails in this thread.")
            return
            
        analysis = analyze_thread(thread_emails)
        
        if analysis:
            latest_email = thread_emails[-1]
            
            # 1. Insert/Update Insight
            existing_insight = db.query(Insight).filter(Insight.thread_id == thread_id).first()
            if existing_insight:
                existing_insight.summary = analysis.summary # type: ignore
                existing_insight.topic = analysis.topic # type: ignore
                existing_insight.decisions = analysis.decisions # type: ignore
                existing_insight.follow_ups = analysis.follow_ups # type: ignore
                existing_insight.created_date = datetime.now() # type: ignore
            else:
                insight = Insight(
                    thread_id=thread_id,
                    topic=analysis.topic,
                    summary=analysis.summary,
                    decisions=analysis.decisions,
                    follow_ups=analysis.follow_ups,
                    created_date=datetime.now()
                )
                db.add(insight)
                db.commit() # Commit to get ID
                
            # Embed into ChromaDB for Semantic Search
            embed_text = f"Topic: {analysis.topic}. Summary: {analysis.summary}. Decisions: {analysis.decisions}"
            if client and insight_collection:
                try:
                    embed_response = client.models.embed_content(
                        model="gemini-embedding-2",
                        contents=embed_text
                    )
                    insight_collection.upsert(
                        ids=[thread_id],
                        embeddings=[embed_response.embeddings[0].values], # type: ignore
                        metadatas=[{"topic": analysis.topic}],
                        documents=[embed_text]
                    )
                except Exception as e:
                    logger.error(f"Failed to embed insight: {e}")
            else:
                logger.info("Skipping ChromaDB embedding because it is not installed or Gemini is disabled.")
            
            # 2. Insert Tasks
            for email in thread_emails:
                db.query(Task).filter(Task.email_id == email.id).delete()
                
            for t in analysis.tasks:
                task = Task(
                    email_id=latest_email.id,
                    task_description=t.task_description,
                    owner=t.owner,
                    due_date=t.due_date,
                    status=t.status
                )
                db.add(task)
        
        # Mark all as processed
        for email in unprocessed:
            email.processed_by_ai = True # type: ignore
        
        db.commit()
        logger.info(f"Successfully processed thread {thread_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during AI processing: {e}")
    finally:
        db.close()

def process_unprocessed_emails():
    """
    Legacy batch processing function.
    """
    db = SessionLocal()
    try:
        unprocessed = db.query(Email).filter(Email.processed_by_ai == False).all()
        if not unprocessed:
            return
        thread_ids = set([e.thread_id for e in unprocessed])
        for t_id in thread_ids:
            process_single_thread(str(t_id)) # type: ignore
    finally:
        db.close()


def process_all_threads_batch(progress_callback=None):
    """
    Batch-processes all unprocessed email threads with rate limiting.
    progress_callback(done, total, thread_id, status) is called after each thread.
    Returns a summary dict: {processed, skipped, failed, total}
    """
    import time

    db = SessionLocal()
    try:
        unprocessed_emails = db.query(Email).filter(Email.processed_by_ai == False).all()
        if not unprocessed_emails:
            return {"processed": 0, "skipped": 0, "failed": 0, "total": 0, "message": "All emails are already processed!"}

        # Group by thread_id
        thread_groups: dict = {}
        for email in unprocessed_emails:
            tid = str(email.thread_id)
            if tid not in thread_groups:
                thread_groups[tid] = []
            thread_groups[tid].append(email)

        total = len(thread_groups)
        processed = 0
        failed = 0
        skipped = 0

        logger.info(f"Starting batch processing of {total} threads...")

        for idx, (thread_id, _) in enumerate(thread_groups.items()):
            try:
                process_single_thread(thread_id)
                processed += 1
                status = "✅ Done"
                logger.info(f"Processed thread {thread_id} ({idx+1}/{total})")
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    failed += 1
                    status = f"⚠️ Quota hit — waiting 60s..."
                    logger.warning(f"Quota limit hit on thread {thread_id}. Waiting 60 seconds...")
                    if progress_callback:
                        progress_callback(idx + 1, total, thread_id, status)
                    time.sleep(60)
                    # Retry once after waiting
                    try:
                        process_single_thread(thread_id)
                        failed -= 1
                        processed += 1
                        status = "✅ Done (after retry)"
                    except Exception as e2:
                        status = f"❌ Failed: {str(e2)[:60]}"
                        logger.error(f"Thread {thread_id} failed even after retry: {e2}")
                else:
                    failed += 1
                    status = f"❌ Error: {err_str[:60]}"
                    logger.error(f"Error processing thread {thread_id}: {e}")

            if progress_callback:
                progress_callback(idx + 1, total, thread_id, status)

            # Rate limit: 1 second between API calls to stay within free tier
            if idx < total - 1:
                time.sleep(1.5)

        summary = {
            "processed": processed,
            "skipped": skipped,
            "failed": failed,
            "total": total,
            "message": f"Done! {processed}/{total} threads processed successfully."
        }
        logger.info(f"Batch processing complete: {summary}")
        return summary

    finally:
        db.close()


if __name__ == "__main__":
    process_unprocessed_emails()

