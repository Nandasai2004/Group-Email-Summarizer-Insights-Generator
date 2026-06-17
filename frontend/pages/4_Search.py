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
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
insight_collection = chroma_client.get_or_create_collection(name="insights")

st.set_page_config(
    page_title="Knowledge Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #0a1628 100%);
    color: #e2e8f0;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* ── HAMBURGER MENU BUTTON ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    top: 14px !important;
    left: 14px !important;
    width: 42px !important;
    height: 42px !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.5) !important;
    transition: all 0.25s ease !important;
}
[data-testid="collapsedControl"]:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    box-shadow: 0 6px 25px rgba(99,102,241,0.7) !important;
    transform: scale(1.08) !important;
}
[data-testid="collapsedControl"] svg {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
}
/* Hide sidebar collapse arrow when open */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
</style>
""", unsafe_allow_html=True)
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
            
            if not embed_response.embeddings:
                st.error("No embeddings returned.")
                st.stop()
                
            query_embedding = embed_response.embeddings[0].values
            assert query_embedding is not None, "Query embedding values are None"
            
            results = insight_collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )
            
            if results and results.get('ids') and results['ids'] and len(results['ids'][0]) > 0:
                semantic_results_found = True
                ids_list = results['ids'][0]
                docs_list = results.get('documents', [[None]])
                dists_list = results.get('distances', [[None]])
                
                for idx, thread_id in enumerate(ids_list):
                    doc = docs_list[0][idx] if docs_list and docs_list[0] else "No document"
                    distance = dists_list[0][idx] if dists_list and dists_list[0] else 0.0
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
