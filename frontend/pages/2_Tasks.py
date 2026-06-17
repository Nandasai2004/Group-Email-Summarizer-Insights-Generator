import streamlit as st
import pandas as pd
from backend.database import SessionLocal, Task
import plotly.express as px

st.set_page_config(
    page_title="Tasks",
    page_icon="✅",
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
st.title("✅ Task Management")

@st.cache_data(ttl=60)
def get_tasks_data():
    db = SessionLocal()
    try:
        tasks = db.query(Task).all()
        data = []
        for t in tasks:
            data.append({
                "Task": t.task_description,
                "Owner": t.owner,
                "Due Date": t.due_date,
                "Status": t.status
            })
        return pd.DataFrame(data)
    finally:
        db.close()

df_tasks = get_tasks_data()

if df_tasks.empty:
    st.info("No tasks extracted yet.")
else:
    # Filters
    st.sidebar.subheader("Filters")
    owner_filter = st.sidebar.multiselect("Filter by Owner", options=df_tasks["Owner"].unique())
    status_filter = st.sidebar.multiselect("Filter by Status", options=df_tasks["Status"].unique())

    filtered_df = df_tasks.copy()
    if owner_filter:
        filtered_df = filtered_df[filtered_df["Owner"].isin(owner_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]

    # Metrics
    open_tasks = len(filtered_df[filtered_df["Status"] == "Open"])
    st.subheader(f"Showing {len(filtered_df)} Tasks ({open_tasks} Open)")

    # Data Table
    st.dataframe(filtered_df, use_container_width=True)

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tasks by Owner")
        owner_counts = filtered_df["Owner"].value_counts().reset_index()
        owner_counts.columns = ["Owner", "Task Count"]
        fig = px.bar(owner_counts, x="Owner", y="Task Count", color="Owner")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Task Status Distribution")
        status_counts = filtered_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig2 = px.pie(status_counts, values="Count", names="Status", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
