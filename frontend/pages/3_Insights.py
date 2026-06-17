import streamlit as st
import pandas as pd
from backend.database import SessionLocal, Insight, Email
import plotly.express as px
from sqlalchemy import func

st.set_page_config(
    page_title="Insights & Trends",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from frontend.theme import inject_theme_manager
inject_theme_manager()

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
st.title("💡 Insights & Trends")

@st.cache_data(ttl=60)
def get_insights_data():
    db = SessionLocal()
    try:
        insights = db.query(Insight).all()
        data = []
        for i in insights:
            data.append({
                "Topic": i.topic,
                "Summary": i.summary,
                "Decisions": i.decisions,
                "Follow-ups": i.follow_ups,
                "Date": i.created_date
            })
        return pd.DataFrame(data)
    finally:
        db.close()

df_insights = get_insights_data()

if df_insights.empty:
    st.info("No insights extracted yet. Please run the AI Processor.")
else:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Topic Frequency")
        topic_counts = df_insights["Topic"].value_counts().reset_index()
        topic_counts.columns = ["Topic", "Count"]
        fig = px.bar(topic_counts, x="Topic", y="Count", color="Topic")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Bottleneck / Issues Analysis")
        # In a more advanced version, we could have an LLM extract specific bottlenecks.
        # For now, we search for negative keywords in topics/summaries as a proxy.
        bottlenecks = df_insights[df_insights["Summary"].str.contains("delay|issue|fail|error|pending|block", case=False, na=False)]
        st.metric("Total Identified Bottlenecks", len(bottlenecks))
        if not bottlenecks.empty:
            st.dataframe(bottlenecks[["Topic", "Summary"]], use_container_width=True)
            
    st.markdown("---")
    st.subheader("Recent Decisions")
    decisions = df_insights[df_insights["Decisions"].notna() & (df_insights["Decisions"] != "None")]
    for idx, row in decisions.iterrows():
        with st.expander(f"Decision in: {row['Topic']}"):
            st.write(row["Decisions"])
