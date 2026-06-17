import sqlite3
import chromadb
from google import genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# 1-7: Verify Database
conn = sqlite3.connect('ges.db')
cursor = conn.cursor()

cursor.execute("SELECT id, subject FROM emails ORDER BY sent_timestamp DESC LIMIT 2")
emails = cursor.fetchall()
print("=== EMAILS ===")
print(emails)

for email in emails:
    email_id, subject = email
    print(f"\n--- Email: {subject} ---")
    
    cursor.execute("""
        SELECT i.topic, i.summary, i.decisions, i.follow_ups 
        FROM insights i 
        JOIN emails e ON e.thread_id = i.thread_id 
        WHERE e.id = ?
    """, (email_id,))
    insight = cursor.fetchone()
    if insight:
        print(f"Topic: {insight[0]}")
        print(f"Summary: {insight[1]}")
        print(f"Decisions: {insight[2]}")
        print(f"Follow-ups: {insight[3]}")
    else:
        print("Insight: NONE FOUND")
        
    cursor.execute("SELECT task_description, owner, due_date, status FROM tasks WHERE email_id = ?", (email_id,))
    tasks = cursor.fetchall()
    print("Tasks:")
    for t in tasks:
        print(f" - {t[0]} | Owner: {t[1]} | Due: {t[2]} | Status: {t[3]}")

# 8-9: Verify ChromaDB
print("\n=== CHROMADB ===")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
insight_collection = chroma_client.get_collection(name="insights")
print(f"Total documents in Chroma: {insight_collection.count()}")

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

queries = [
    "database configuration",
    "performance reviews",
    "release notes"
]

for q in queries:
    print(f"\nSearching for: '{q}'")
    embed_response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=q
    )
    results = insight_collection.query(
        query_embeddings=[embed_response.embeddings[0].values],
        n_results=1
    )
    if results and results['documents'] and len(results['documents'][0]) > 0:
        print(f"Match: {results['documents'][0][0]}")
    else:
        print("Match: NONE")

conn.close()
