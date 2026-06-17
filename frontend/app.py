import streamlit as st


st.set_page_config(
    page_title="Email Summarizer & Insights",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Group Email Summarizer & Insights Generator")
st.markdown("""
Welcome to the Executive Dashboard.

This application automatically collects group emails, analyzes conversations, extracts tasks, and generates insights.
Use the sidebar to navigate through the different modules:
- **1 Overview**: Executive KPIs and high-level metrics.
- **2 Tasks**: Detailed view of open and overdue tasks extracted by AI.
- **3 Insights**: Discussion topics and conversation trends.
- **4 Search**: Semantic/Keyword search repository for historical knowledge.
- **5 AI Chat**: Ask questions directly to the AI about pending issues and trends.
""")

st.info("👈 Please select a page from the sidebar to continue.")
