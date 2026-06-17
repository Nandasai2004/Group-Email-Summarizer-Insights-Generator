import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import SessionLocal, Email, Task, Insight
from sqlalchemy import func
import time

st.set_page_config(
    page_title="GES — Group Email Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from frontend.theme import inject_theme_manager
inject_theme_manager()

from frontend.auth import check_login_status
user = check_login_status()

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


/* ── NAV BUTTONS ── */
[data-testid="stBaseButton-secondary"] {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1)) !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    border-radius: 10px !important;
    color: #a5b4fc !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
    margin-top: 6px;
}
[data-testid="stBaseButton-secondary"]:hover {
    background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.25)) !important;
    border-color: rgba(99,102,241,0.7) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.25) !important;
    transform: translateY(-2px);
}


/* ── HERO SECTION ── */
.hero-container {
    text-align: center;
    padding: 60px 20px 40px;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 50px;
    margin-bottom: 24px;
    animation: pulse-badge 2s infinite;
}
@keyframes pulse-badge {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0.4); }
    50% { box-shadow: 0 0 0 10px rgba(99,102,241,0); }
}
.hero-title {
    font-size: clamp(36px, 5vw, 68px);
    font-weight: 900;
    line-height: 1.1;
    background: var(--title-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 20px;
}
.hero-subtitle {
    font-size: 18px;
    color: var(--text-muted);
    max-width: 600px;
    margin: 0 auto 40px;
    line-height: 1.7;
    font-weight: 400;
}
.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 50px;
    padding: 8px 20px;
    font-size: 13px;
    color: #10b981;
    font-weight: 500;
    margin-bottom: 16px;
}
.dot-live {
    width: 8px; height: 8px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    animation: blink 1.2s infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── STAT CARDS ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 32px 0;
}
.stat-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px 24px;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 20px 20px 0 0;
}
.stat-card.purple::before { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
.stat-card.blue::before   { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
.stat-card.green::before  { background: linear-gradient(90deg, #10b981, #34d399); }
.stat-card.orange::before { background: linear-gradient(90deg, #f59e0b, #f97316); }

.stat-card {
    cursor: pointer;
}
.stat-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255,255,255,0.25);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}
.stat-card.active {
    border: 1.5px solid rgba(99,102,241,0.8) !important;
    box-shadow: 0 10px 30px rgba(99,102,241,0.3) !important;
    background: rgba(99,102,241,0.08) !important;
    transform: translateY(-2px);
}
.stat-card.active.blue {
    border-color: rgba(59,130,246,0.8) !important;
    box-shadow: 0 10px 30px rgba(59,130,246,0.3) !important;
    background: rgba(59,130,246,0.08) !important;
}
.stat-card.active.green {
    border-color: rgba(16,185,129,0.8) !important;
    box-shadow: 0 10px 30px rgba(16,185,129,0.3) !important;
    background: rgba(16,185,129,0.08) !important;
}
.stat-card.active.orange {
    border-color: rgba(245,158,11,0.8) !important;
    box-shadow: 0 10px 30px rgba(245,158,11,0.3) !important;
    background: rgba(245,158,11,0.08) !important;
}
.stat-icon {
    font-size: 32px;
    margin-bottom: 12px;
    display: block;
}
.stat-number {
    font-size: 48px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 8px;
}
.stat-card.purple .stat-number { color: var(--stat-purple); }
.stat-card.blue .stat-number   { color: var(--stat-blue); }
.stat-card.green .stat-number  { color: var(--stat-green); }
.stat-card.orange .stat-number { color: var(--stat-orange); }
.stat-label {
    font-size: 13px;
    color: #64748b;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stat-sub {
    font-size: 11px;
    color: #475569;
    margin-top: 6px;
}

/* ── FEATURE CARDS ── */
.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 24px 0;
}
.feature-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: block;
    position: relative;
    overflow: hidden;
}
.feature-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 0%, rgba(99,102,241,0.08), transparent 60%);
    opacity: 0;
    transition: opacity 0.3s;
}
.feature-card:hover {
    transform: translateY(-3px);
    border-color: rgba(99,102,241,0.3);
    box-shadow: 0 12px 32px rgba(99,102,241,0.15);
}
.feature-card:hover::after { opacity: 1; }
.feature-icon {
    font-size: 36px;
    margin-bottom: 14px;
    display: block;
}
.feature-title {
    font-size: 16px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 13px;
    color: #64748b;
    line-height: 1.6;
}
.feature-arrow {
    margin-top: 16px;
    font-size: 12px;
    color: #6366f1;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── ACTIVITY FEED ── */
.activity-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 24px;
    margin: 16px 0;
}
.activity-header {
    font-size: 16px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.activity-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.activity-item:last-child { border-bottom: none; }
.activity-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}
.activity-dot.purple { background: #6366f1; }
.activity-dot.green  { background: #10b981; }
.activity-dot.blue   { background: #3b82f6; }
.activity-dot.orange { background: #f59e0b; }
.activity-text { font-size: 13px; color: #94a3b8; line-height: 1.5; flex: 1; }
.activity-text strong { color: #e2e8f0; }
.activity-time { font-size: 11px; color: #475569; white-space: nowrap; }

/* ── SECTION HEADERS ── */
.section-header {
    font-size: 22px;
    font-weight: 800;
    color: #e2e8f0;
    margin-bottom: 6px;
}
.section-sub {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 24px;
}

/* ── CTA BUTTON ── */
.cta-container {
    text-align: center;
    margin: 40px 0 20px;
}
.cta-text {
    font-size: 13px;
    color: #475569;
    margin-top: 12px;
}

/* ── DIVIDER ── */
.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent);
    margin: 40px 0;
    border: none;
}

/* ── TECH PILLS ── */
.tech-pills {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
    margin: 20px 0 40px;
}
.tech-pill {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 50px;
    padding: 6px 14px;
    font-size: 12px;
    color: #94a3b8;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ── Fetch Live Stats ─────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_live_stats():
    db = SessionLocal()
    try:
        total_emails   = db.query(func.count(Email.id)).scalar() or 0
        total_tasks    = db.query(func.count(Task.id)).scalar() or 0
        total_threads  = db.query(func.count(func.distinct(Email.thread_id))).scalar() or 0
        total_insights = db.query(func.count(Insight.id)).scalar() or 0
        ai_processed   = db.query(func.count(Email.id)).filter(Email.processed_by_ai == True).scalar() or 0
        latest_topics  = db.query(Insight).order_by(Insight.created_date.desc()).limit(4).all()
        latest_tasks   = db.query(Task).order_by(Task.id.desc()).limit(4).all()
        return {
            "emails": total_emails,
            "tasks": total_tasks,
            "threads": total_threads,
            "insights": total_insights,
            "ai_processed": ai_processed,
            "latest_topics": latest_topics,
            "latest_tasks": latest_tasks,
        }
    finally:
        db.close()

stats = get_live_stats()

# Read current selected view from query parameter
query_params = st.query_params
selected_view = query_params["view"] if "view" in query_params else None

# ── HERO ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-container">
    <div class="hero-badge">⚡ AI-Powered Intelligence Platform</div>
    <h1 class="hero-title">Group Email Summarizer<br>&amp; Insights Generator</h1>
    <div class="hero-status">
        <span class="dot-live"></span>
        {stats['ai_processed']} emails processed by AI &nbsp;·&nbsp; {stats['insights']} insights generated
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO SEARCH BAR ──────────────────────────────────────────────────────────
st.markdown("""
<style>
.search-wrapper {
    max-width: 680px;
    margin: 0 auto 32px;
    position: relative;
}
.search-wrapper [data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(99,102,241,0.4) !important;
    border-radius: 50px !important;
    color: #e2e8f0 !important;
    font-size: 15px !important;
    padding: 14px 24px 14px 52px !important;
    height: 52px !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.12) !important;
    transition: all 0.3s ease !important;
}
.search-wrapper [data-testid="stTextInput"] input:focus {
    border-color: rgba(99,102,241,0.8) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
    background: rgba(255,255,255,0.09) !important;
}
.search-wrapper [data-testid="stTextInput"] input::placeholder {
    color: #475569 !important;
}
</style>
""", unsafe_allow_html=True)

search_col1, search_col2, search_col3 = st.columns([1, 3, 1])
with search_col2:
    st.markdown('<div class="search-wrapper">', unsafe_allow_html=True)
    search_query = st.text_input("Search", placeholder="🔍  Search emails by subject, sender, or keyword...", key="hero_search", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if search_query and search_query.strip():
    db = SessionLocal()
    try:
        q = search_query.strip().lower()
        results = db.query(Email).filter(
            (Email.subject.ilike(f"%{q}%")) |
            (Email.from_name.ilike(f"%{q}%")) |
            (Email.email_body.ilike(f"%{q}%")) |
            (Email.department.ilike(f"%{q}%"))
        ).limit(8).all()
    finally:
        db.close()

    if results:
        st.markdown(f'<div class="section-header" style="text-align:center; margin-bottom:8px">🔎 {len(results)} results for "{search_query}"</div>', unsafe_allow_html=True)
        for r in results:
            with st.expander(f"📧 {r.subject} — {r.from_name} ({r.department})"):
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.markdown(f"**From:** {r.from_name}")
                    st.markdown(f"**To:** {r.to_group}")
                    st.markdown(f"**Dept:** {r.department}")
                    st.markdown(f"**Priority:** {r.priority}")
                with col_b:
                    st.markdown(r.email_body[:400] + ("..." if len(str(r.email_body)) > 400 else ""))
    else:
        st.info(f'No emails found for "{search_query}".')

# ── LIVE STATS GRID ──────────────────────────────────────────────────────────
active_emails = "active" if selected_view == "emails" else ""
active_threads = "active" if selected_view == "threads" else ""
active_tasks = "active" if selected_view == "tasks" else ""
active_insights = "active" if selected_view == "insights" else ""

st.markdown(f"""
<div class="stats-grid">
    <a href="?view=emails" target="_self" style="text-decoration: none; color: inherit;">
        <div class="stat-card purple {active_emails}">
            <span class="stat-icon">📧</span>
            <div class="stat-number">{stats['emails']}</div>
            <div class="stat-label">Total Emails</div>
            <div class="stat-sub">{stats['ai_processed']} AI-analyzed</div>
        </div>
    </a>
    <a href="?view=threads" target="_self" style="text-decoration: none; color: inherit;">
        <div class="stat-card blue {active_threads}">
            <span class="stat-icon">🧵</span>
            <div class="stat-number">{stats['threads']}</div>
            <div class="stat-label">Active Threads</div>
            <div class="stat-sub">Across all groups</div>
        </div>
    </a>
    <a href="?view=tasks" target="_self" style="text-decoration: none; color: inherit;">
        <div class="stat-card green {active_tasks}">
            <span class="stat-icon">✅</span>
            <div class="stat-number">{stats['tasks']}</div>
            <div class="stat-label">Tasks Extracted</div>
            <div class="stat-sub">By AI analysis</div>
        </div>
    </a>
    <a href="?view=insights" target="_self" style="text-decoration: none; color: inherit;">
        <div class="stat-card orange {active_insights}">
            <span class="stat-icon">💡</span>
            <div class="stat-number">{stats['insights']}</div>
            <div class="stat-label">Insights Generated</div>
            <div class="stat-sub">Thread summaries</div>
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

# ── SELECT-VIEW DRAWER/PANEL ────────────────────────────────────────────────
if selected_view:
    st.markdown("""
    <style>
    .details-panel {
        background: rgba(13, 20, 35, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 20px;
        padding: 24px;
        margin: 20px 0 32px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
    }
    .details-title {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .details-subtitle {
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        if selected_view == "emails":
            st.markdown('<div class="details-panel">', unsafe_allow_html=True)
            col_t, col_btn = st.columns([4, 1])
            with col_t:
                st.markdown(f'<div class="details-title">📬 Ingested Emails ({stats["emails"]})</div>', unsafe_allow_html=True)
                st.markdown('<div class="details-subtitle">All email communications stored in the platform database</div>', unsafe_allow_html=True)
            with col_btn:
                if st.button("❌ Close Panel", key="close_emails", use_container_width=True):
                    st.query_params.clear()
                    st.rerun()
            
            emails = db.query(Email).order_by(Email.sent_timestamp.desc()).all()
            if emails:
                email_search = st.text_input("🔍 Filter emails by subject, sender, or content...", "", key="panel_email_search")
                filtered_emails = emails
                if email_search.strip():
                    es_query = email_search.strip().lower()
                    filtered_emails = [
                        e for e in emails if 
                        es_query in (e.subject or "").lower() or 
                        es_query in (e.from_name or "").lower() or 
                        es_query in (e.email_body or "").lower() or
                        es_query in (e.department or "").lower()
                    ]
                
                st.markdown(f"**Showing {len(filtered_emails)} emails (Click any email to expand and read body):**")
                for email in filtered_emails[:30]:
                    date_str = email.sent_timestamp.strftime('%Y-%m-%d %H:%M') if email.sent_timestamp else 'Unknown Date'
                    with st.expander(f"✉️ {email.subject or 'No Subject'} — From: {email.from_name} ({email.department}) | {date_str}"):
                        c1, c2 = st.columns([1, 2.5])
                        with c1:
                            st.markdown(f"**Sender:** {email.from_name} ({email.from_email})")
                            st.markdown(f"**To Group:** {email.to_group or 'N/A'}")
                            st.markdown(f"**Department:** {email.department or 'N/A'}")
                            st.markdown(f"**Priority:** `{email.priority or 'Normal'}`")
                            st.markdown(f"**Thread sequence:** #{email.thread_sequence or 1}")
                        with c2:
                            st.markdown("**Message Body:**")
                            st.text(email.email_body)
                if len(filtered_emails) > 30:
                    st.info(f"Showing first 30 of {len(filtered_emails)} emails. Please use the filter above to find specific messages.")
            else:
                st.info("No emails found in the database.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif selected_view == "threads":
            st.markdown('<div class="details-panel">', unsafe_allow_html=True)
            col_t, col_btn = st.columns([4, 1])
            with col_t:
                st.markdown(f'<div class="details-title">🧵 Active Discussion Threads ({stats["threads"]})</div>', unsafe_allow_html=True)
                st.markdown('<div class="details-subtitle">Conversations grouped by thread identifier, sorted by latest activity</div>', unsafe_allow_html=True)
            with col_btn:
                if st.button("❌ Close Panel", key="close_threads", use_container_width=True):
                    st.query_params.clear()
                    st.rerun()

            threads_data = db.query(
                Email.thread_id,
                func.count(Email.id).label("email_count"),
                func.min(Email.sent_timestamp).label("started"),
                func.max(Email.sent_timestamp).label("last_activity"),
                func.max(Email.subject).label("subject"),
                func.max(Email.department).label("department")
            ).group_by(Email.thread_id).order_by(func.max(Email.sent_timestamp).desc()).all()

            if threads_data:
                st.markdown(f"**Showing {len(threads_data)} active conversation threads (Click to view full thread communication history):**")
                for t in threads_data:
                    start_str = t.started.strftime('%Y-%m-%d %H:%M') if t.started else 'Unknown'
                    last_str = t.last_activity.strftime('%Y-%m-%d %H:%M') if t.last_activity else 'Unknown'
                    with st.expander(f"🧵 {t.subject or 'Untitled Thread'} ({t.email_count} emails) | Dept: {t.department or 'General'} | Last Activity: {last_str}"):
                        st.markdown(f"**Thread ID:** `{t.thread_id}`")
                        st.markdown(f"**Started:** {start_str} &nbsp;·&nbsp; **Latest Update:** {last_str}")
                        st.markdown("---")
                        
                        thread_emails = db.query(Email).filter(Email.thread_id == t.thread_id).order_by(Email.thread_sequence.asc()).all()
                        for te in thread_emails:
                            te_date = te.sent_timestamp.strftime('%Y-%m-%d %H:%M') if te.sent_timestamp else 'Unknown'
                            st.markdown(f"📬 **Sequence #{te.thread_sequence}** | **{te.from_name}** | {te_date}")
                            st.text(te.email_body)
                            st.markdown("---")
            else:
                st.info("No active threads found.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif selected_view == "tasks":
            st.markdown('<div class="details-panel">', unsafe_allow_html=True)
            col_t, col_btn = st.columns([4, 1])
            with col_t:
                st.markdown(f'<div class="details-title">✅ AI-Extracted Tasks ({stats["tasks"]})</div>', unsafe_allow_html=True)
                st.markdown('<div class="details-subtitle">Action items automatically identified and extracted by Gemini AI from email threads</div>', unsafe_allow_html=True)
            with col_btn:
                if st.button("❌ Close Panel", key="close_tasks", use_container_width=True):
                    st.query_params.clear()
                    st.rerun()

            tasks = db.query(Task).order_by(Task.id.desc()).all()
            if tasks:
                st.markdown(f"**Showing {len(tasks)} extracted tasks:**")
                for task in tasks:
                    status_emoji = "🟢" if task.status == "Open" else "🔵"
                    with st.expander(f"📋 {task.task_description[:80]}... | Owner: {task.owner or 'Unassigned'} | {status_emoji} {task.status}"):
                        st.markdown(f"**Task Description:** {task.task_description}")
                        st.markdown(f"**Assigned Owner:** `{task.owner or 'Unassigned'}`")
                        st.markdown(f"**Due Date:** `{task.due_date or 'TBD'}`")
                        st.markdown(f"**Current Status:** `{task.status}`")
                        
                        if task.email_id:
                            email = db.query(Email).filter(Email.id == task.email_id).first()
                            if email:
                                st.markdown("---")
                                st.markdown(f"📧 **Source Email:** *{email.subject}* (From: {email.from_name} on {email.sent_timestamp.strftime('%Y-%m-%d') if email.sent_timestamp else 'Unknown Date'})")
                                st.text(email.email_body)
            else:
                st.info("No AI-extracted tasks found.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif selected_view == "insights":
            st.markdown('<div class="details-panel">', unsafe_allow_html=True)
            col_t, col_btn = st.columns([4, 1])
            with col_t:
                st.markdown(f'<div class="details-title">💡 Generated AI Insights ({stats["insights"]})</div>', unsafe_allow_html=True)
                st.markdown('<div class="details-subtitle">High-level discussion summaries, decisions, and follow-ups extracted by Gemini AI</div>', unsafe_allow_html=True)
            with col_btn:
                if st.button("❌ Close Panel", key="close_insights", use_container_width=True):
                    st.query_params.clear()
                    st.rerun()

            insights = db.query(Insight).order_by(Insight.created_date.desc()).all()
            if insights:
                st.markdown(f"**Showing {len(insights)} AI-generated topic insights:**")
                for ins in insights:
                    ins_date = ins.created_date.strftime('%Y-%m-%d %H:%M') if ins.created_date else 'Unknown'
                    with st.expander(f"💡 {ins.topic or 'Untitled Insight'} | {ins_date}"):
                        st.markdown(f"**Topic/Issue:** {ins.topic}")
                        st.markdown(f"**Discussion Summary:**  \n{ins.summary}")
                        if ins.decisions:
                            st.markdown(f"**Decisions Made:**  \n{ins.decisions}")
                        if ins.follow_ups:
                            st.markdown(f"**Follow-up Actions:**  \n{ins.follow_ups}")
                        st.markdown(f"**Thread ID:** `{ins.thread_id}`")
            else:
                st.info("No AI insights found.")
            st.markdown('</div>', unsafe_allow_html=True)

    finally:
        db.close()

st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

# ── RECENT ACTIVITY + MODULES ────────────────────────────────────────────────
col_left, col_right = st.columns([1.1, 1], gap="large")

with col_left:
    st.markdown('<div class="section-header">🗂️ Recent AI Activity</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Live feed of the latest AI-processed insights</div>', unsafe_allow_html=True)

    colors = ["purple", "green", "blue", "orange"]
    icons  = ["💡", "✅", "📌", "🔍"]

    if stats["latest_topics"]:
        items_html = ""
        for i, insight in enumerate(stats["latest_topics"]):
            color = colors[i % len(colors)]
            icon  = icons[i % len(icons)]
            summary_preview = (str(insight.summary)[:80] + "...") if insight.summary else "No summary."
            items_html += f"""
            <div class="activity-item">
                <div class="activity-dot {color}"></div>
                <div class="activity-text">
                    <strong>{icon} {insight.topic or 'Untitled'}</strong><br>
                    {summary_preview}
                </div>
            </div>"""

        if stats["latest_tasks"]:
            for i, task in enumerate(stats["latest_tasks"][:2]):
                items_html += f"""
                <div class="activity-item">
                    <div class="activity-dot green"></div>
                    <div class="activity-text">
                        <strong>✅ Task Extracted</strong><br>
                        {str(task.task_description)[:70]}... — <em>Owner: {task.owner or 'TBD'}</em>
                    </div>
                </div>"""

        st.markdown(f'<div class="activity-container"><div class="activity-header">📡 Live Feed</div>{items_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="activity-container">
            <div class="activity-header">📡 Live Feed</div>
            <div class="activity-item">
                <div class="activity-dot purple"></div>
                <div class="activity-text"><strong>No activity yet</strong><br>Send an email to the webhook to get started.</div>
            </div>
        </div>""", unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-header">🚀 Navigate Modules</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Click a button below to go to that module</div>', unsafe_allow_html=True)

    # Row 1
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Overview</div>
            <div class="feature-desc">Executive KPIs, email trends &amp; metrics at a glance.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Open Overview", key="nav_overview", use_container_width=True):
            st.switch_page("pages/1_Overview.py")

    with btn_col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">✅</span>
            <div class="feature-title">Tasks</div>
            <div class="feature-desc">AI-extracted tasks with owners, due dates &amp; status.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Open Tasks", key="nav_tasks", use_container_width=True):
            st.switch_page("pages/2_Tasks.py")

    # Row 2
    btn_col3, btn_col4 = st.columns(2)
    with btn_col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💡</span>
            <div class="feature-title">Insights</div>
            <div class="feature-desc">Discussion topics, decisions &amp; conversation trends.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Open Insights", key="nav_insights", use_container_width=True):
            st.switch_page("pages/3_Insights.py")

    with btn_col4:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">AI Chat</div>
            <div class="feature-desc">Ask the AI about pending issues, risks &amp; trends.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Open AI Chat", key="nav_chat2", use_container_width=True):
            st.switch_page("pages/5_AI_Chat.py")

    # Row 3 — Executive Report full width
    st.markdown("""
    <div class="feature-card" style="text-align:center">
        <span class="feature-icon">📋</span>
        <div class="feature-title">Executive Report</div>
        <div class="feature-desc">Generate macro-level intelligence reports &amp; summaries by date range.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("→ Open Executive Report", key="nav_report", use_container_width=True):
        st.switch_page("pages/6_Executive_Report.py")



# ── AUTO-REFRESH ─────────────────────────────────────────────────────────────
st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)
col_a, col_b, col_c = st.columns([1, 2, 1])
with col_b:
    auto_refresh = st.toggle("🔄 Auto-refresh every 30 seconds", value=False)
    if auto_refresh:
        st.success("✅ Live mode enabled — dashboard will refresh automatically!")
        time.sleep(30)
        st.rerun()

st.markdown('<div class="cta-text" style="text-align:center; color:#475569; font-size:12px; padding-bottom:40px;">GES Platform · Powered by Gemini 2.5 Flash · Built with FastAPI & Streamlit</div>', unsafe_allow_html=True)
