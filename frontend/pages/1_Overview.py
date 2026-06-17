import streamlit as st
import pandas as pd
from backend.database import SessionLocal, Email, Task, Insight
from sqlalchemy import func

st.set_page_config(
    page_title="Overview",
    page_icon="📊",
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
st.title("📊 Executive Overview")

@st.cache_data(ttl=60)
def get_kpis():
    db = SessionLocal()
    try:
        total_emails = db.query(func.count(Email.id)).scalar()
        total_tasks = db.query(func.count(Task.id)).scalar()
        open_tasks = db.query(func.count(Task.id)).filter(Task.status == "Open").scalar()
        active_threads = db.query(func.count(func.distinct(Email.thread_id))).scalar()
        
        # In a real scenario with parsed dates we could check overdue
        # For MVP we will count tasks with "High" priority emails as a proxy or just query by string date
        # Let's say all open tasks are pending
        
        return {
            "Total Emails": total_emails,
            "Open Tasks": open_tasks,
            "Active Threads": active_threads,
            "Total Extracted Tasks": total_tasks
        }
    finally:
        db.close()

kpis = get_kpis()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Emails", kpis["Total Emails"])
col2.metric("Open Tasks", kpis["Open Tasks"])
col3.metric("Active Threads", kpis["Active Threads"])
col4.metric("Extracted Tasks", kpis["Total Extracted Tasks"])

st.markdown("---")

st.subheader("Recent Email Flow")
@st.cache_data(ttl=60)
def get_email_trend():
    db = SessionLocal()
    try:
        emails = db.query(Email.sent_timestamp).all()
        if not emails:
            return pd.DataFrame()
        
        df = pd.DataFrame([{"date": e[0]} for e in emails if e[0] is not None])
        if df.empty:
            return df
            
        df['date'] = pd.to_datetime(df['date']).dt.date  # type: ignore
        trend = df.groupby('date').size().reset_index(name='count')
        return trend
    finally:
        db.close()

trend_df = get_email_trend()
if not trend_df.empty:
    st.bar_chart(data=trend_df, x="date", y="count")
else:
    st.info("No email data available for trend chart.")

st.markdown("---")
st.subheader("Recent Topics")
def get_recent_topics():
    db = SessionLocal()
    try:
        insights = db.query(Insight).order_by(Insight.created_date.desc()).limit(5).all()
        return insights
    finally:
        db.close()

topics = get_recent_topics()
if topics:
    for t in topics:
        with st.expander(f"{t.topic}"):
            st.write(t.summary)
else:
    st.info("No AI insights available yet. Please run the AI Processor.")
