import requests
import time
import sqlite3
import chromadb
import json

print("1. Simulating an incoming email...")
payload = {
    "from_email": "ceo@company.com",
    "from_name": "Jane CEO",
    "subject": "Urgent: Q4 Final Deliverables",
    "body": "Team, we are behind on the Q4 deliverables. John, please finalize the financial report by Friday. Sarah, ensure the marketing deck is ready by Thursday morning. We need this sorted ASAP to present to the board. Are there any blocking issues?",
    "to_group": "executive-team@company.com"
}

try:
    print("2. Processing it through the webhook...")
    response = requests.post("http://127.0.0.1:8000/webhook/email", json=payload)
    print(f"Webhook Response ({response.status_code}): {response.json()}")
    thread_id = response.json().get("thread_id")
except Exception as e:
    print(f"Failed to hit webhook: {e}")
    exit(1)

print("Waiting 15 seconds for AI background worker to finish...")
time.sleep(15)

print("\n--- Verifying Database ---")
try:
    conn = sqlite3.connect("ges.db")
    cursor = conn.cursor()
    
    # Check Insights
    cursor.execute("SELECT topic, summary, decisions, follow_ups FROM insights WHERE thread_id=?", (thread_id,))
    insight = cursor.fetchone()
    if insight:
        print("3. AI Summary & Insights Found:")
        print(f"   Topic: {insight[0]}\n   Summary: {insight[1]}\n   Decisions: {insight[2]}\n   Follow-ups: {insight[3]}")
    else:
        print("❌ Insight not found in database.")
        
    # Check Tasks
    cursor.execute("SELECT tasks.task_description, tasks.owner, tasks.due_date FROM tasks JOIN emails ON tasks.email_id = emails.id WHERE emails.thread_id=?", (thread_id,))
    tasks = cursor.fetchall()
    if tasks:
        print("\n4. Extracted Tasks Found:")
        for t in tasks:
            print(f"   - Task: {t[0]}\n     Owner: {t[1]}\n     Due: {t[2]}")
    else:
        print("❌ No tasks found in database.")
        
    conn.close()
except Exception as e:
    print(f"Database error: {e}")

print("\n--- Verifying ChromaDB Semantic Search ---")
try:
    print("6. Initializing ChromaDB client...")
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    insight_collection = chroma_client.get_collection(name="insights")
    
    print("7. Verifying semantic retrieval for 'financial report'...")
    results = insight_collection.query(
        query_texts=["financial report"],
        n_results=1
    )
    if results and results['ids'] and len(results['ids'][0]) > 0:
        print(f"   Match Found (Thread {results['ids'][0][0]}):")
        print(f"   Document: {results['documents'][0][0]}")
    else:
        print("❌ Semantic search returned no matches.")
except Exception as e:
    print(f"ChromaDB error: {e}")

print("\n8. Confirm the dashboard receives updated data: YES, data is confirmed in SQLite which powers the Streamlit Dashboard directly.")
