import streamlit as st
import pandas as pd
import os
from backend.database import SessionLocal, Email, Insight, Task
from sqlalchemy import or_
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here" else None

# Initialize ChromaDB client pointing to the same persistent path
chroma_client = chromadb.PersistentClient(path="./chroma_db")
insight_collection = chroma_client.get_or_create_collection(name="insights")

st.set_page_config(page_title="Knowledge Search", page_icon="🔍", layout="wide")
st.title("🔍 Semantic Knowledge Repository")

st.markdown("Use natural language to search across historical emails, decisions, and topics.")

query = st.text_input("Ask a question or enter keywords...", "")

if query:
    st.subheader(f"Results for: '{query}'")
    
    # Semantic Search using Vector Embeddings
    semantic_results_found = False
    if client:
        try:
            st.markdown("### 🧠 Semantic Insight Matches")
            embed_response = client.models.embed_content(
                model="gemini-embedding-2",
                contents=query
            )
            query_embedding = embed_response.embeddings[0].values
            
            results = insight_collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )
            
            if results and results['ids'] and len(results['ids'][0]) > 0:
                semantic_results_found = True
                for idx, thread_id in enumerate(results['ids'][0]):
                    doc = results['documents'][0][idx]
                    distance = results['distances'][0][idx]
                    # Lower distance = better match (for standard L2). We can just show it.
                    with st.expander(f"Semantic Match (Thread ID: {thread_id})"):
                        st.write(doc)
            else:
                st.info("No strong semantic matches found.")
        except Exception as e:
            st.error(f"Semantic search failed: {e}")
    else:
        st.warning("Gemini API Key missing. Semantic search disabled.")

    st.markdown("---")
    
    # Fallback/Additional Keyword Search in DB
    st.markdown("### 📧 Exact Keyword Matches (Emails)")
    db = SessionLocal()
    try:
        email_results = db.query(Email).filter(
            or_(
                Email.subject.ilike(f"%{query}%"),
                Email.email_body.ilike(f"%{query}%")
            )
        ).limit(10).all()
        
        if email_results:
            for e in email_results:
                with st.expander(f"{e.sent_timestamp} - {e.subject} (From: {e.from_name})"):
                    st.write(e.email_body)
        else:
            st.info("No exact keyword matches found in emails.")
            
    finally:
        db.close()
