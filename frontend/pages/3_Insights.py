import streamlit as st
import pandas as pd
from backend.database import SessionLocal, Insight, Email
import plotly.express as px
from sqlalchemy import func

st.set_page_config(page_title="Insights & Trends", page_icon="💡", layout="wide")
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
