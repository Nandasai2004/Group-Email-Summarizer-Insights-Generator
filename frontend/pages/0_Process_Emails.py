import streamlit as st
import sys, os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

st.set_page_config(
    page_title="Process Emails — GES",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from frontend.theme import inject_theme_manager
inject_theme_manager()

from frontend.auth import check_login_status
check_login_status()

from backend.database import SessionLocal, Email, Insight, Task
from sqlalchemy import func

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #0a1628 100%);
    color: #e2e8f0;
}
#MainMenu, footer, header { visibility: hidden; }
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
}
[data-testid="stSidebarCollapseButton"] { display: none !important; }

.stat-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 24px;
    text-align: center;
}
.stat-num {
    font-size: 40px;
    font-weight: 800;
    background: linear-gradient(135deg, #a5b4fc, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-label {
    font-size: 13px;
    color: #64748b;
    margin-top: 4px;
    font-weight: 500;
}
.thread-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    margin-bottom: 6px;
    font-size: 13px;
}
.info-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.08));
    border: 1px solid rgba(99,102,241,0.35);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 28px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding: 10px 0 24px 0;">
    <h1 style="font-size:32px; font-weight:800; background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #7c3aed 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin:0;">
        ⚡ AI Email Processor
    </h1>
    <p style="color:#64748b; font-size:15px; margin-top:6px;">
        Summarize all email threads using Gemini AI — extracts tasks, decisions, follow-ups and insights automatically.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Stats ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def get_stats():
    db = SessionLocal()
    try:
        total = db.query(func.count(Email.id)).scalar() or 0
        processed = db.query(func.count(Email.id)).filter(Email.processed_by_ai == True).scalar() or 0
        unprocessed = total - processed
        threads = db.query(func.count(func.distinct(Email.thread_id))).scalar() or 0
        unproc_threads_q = db.query(Email.thread_id).filter(Email.processed_by_ai == False).distinct()
        unproc_threads = unproc_threads_q.count()
        insights = db.query(func.count(Insight.id)).scalar() or 0
        tasks = db.query(func.count(Task.id)).scalar() or 0
        return {
            "total": total, "processed": processed, "unprocessed": unprocessed,
            "threads": threads, "unproc_threads": unproc_threads,
            "insights": insights, "tasks": tasks
        }
    finally:
        db.close()

stats = get_stats()

col1, col2, col3, col4 = st.columns(4)
for col, label, val, color in [
    (col1, "Total Emails", stats["total"], "#a5b4fc"),
    (col2, "Unprocessed", stats["unprocessed"], "#fbbf24"),
    (col3, "Insights Generated", stats["insights"], "#6ee7b7"),
    (col4, "Tasks Extracted", stats["tasks"], "#f9a8d4"),
]:
    with col:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-num" style="background: linear-gradient(135deg, {color}, {color}cc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">{val}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Info Banner ─────────────────────────────────────────────────────────────
if stats["unproc_threads"] > 0:
    st.markdown(f"""
    <div class="info-banner">
        <div style="font-size:15px; font-weight:700; color:#a5b4fc;">📬 {stats["unproc_threads"]} email thread(s) waiting to be processed</div>
        <div style="font-size:13px; color:#64748b; margin-top:6px;">
            Click <strong style="color:#e2e8f0;">"Process All Email Threads"</strong> below. Gemini AI will read each thread and extract summaries, action items, decisions, and follow-ups.
            <br>⏱ Estimated time: ~{max(1, stats["unproc_threads"])} – {max(2, stats["unproc_threads"] * 2)} minutes (rate limit: 1.5s between threads).
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success("✅ All email threads have been processed! Check the Insights and Tasks pages to view results.")

# ── Process Button ──────────────────────────────────────────────────────────
st.markdown("---")

col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])
with col_btn1:
    run_all = st.button(
        "⚡ Process All Email Threads",
        type="primary",
        use_container_width=True,
        disabled=(stats["unproc_threads"] == 0),
        help="Sends all unprocessed threads to Gemini AI for analysis"
    )

with col_btn2:
    reprocess = st.button(
        "🔄 Re-Process Already Done Threads",
        use_container_width=True,
        help="Mark all emails as unprocessed and re-run AI on everything"
    )

with col_btn3:
    refresh = st.button("🔁 Refresh Stats", use_container_width=True)

if refresh:
    st.cache_data.clear()
    st.rerun()

# Re-process: mark all as unprocessed
if reprocess:
    db = SessionLocal()
    try:
        db.query(Email).update({"processed_by_ai": False})
        db.commit()
        st.success("✅ All emails marked as unprocessed. You can now re-run the AI processor.")
        st.cache_data.clear()
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        db.close()

# ── Main Processing Logic ────────────────────────────────────────────────────
if run_all:
    from backend.ai_processor import process_all_threads_batch

    st.markdown("---")
    st.markdown("### 🔄 Processing in progress...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.container()
    log_lines = []

    def update_progress(done, total, thread_id, status):
        pct = done / total if total > 0 else 0
        progress_bar.progress(pct)
        status_text.markdown(
            f"<div style='color:#94a3b8; font-size:13px;'>Processing thread <code style='color:#a5b4fc'>{thread_id}</code> — {done}/{total} &nbsp;|&nbsp; {status}</div>",
            unsafe_allow_html=True
        )
        log_lines.append(f"{done}/{total} | Thread `{thread_id}` → {status}")
        # Show last 5 log lines
        with log_container:
            st.markdown("\n".join([f"- {l}" for l in log_lines[-8:]]))

    with st.spinner("Gemini AI is analyzing your emails..."):
        try:
            result = process_all_threads_batch(progress_callback=update_progress)
        except Exception as e:
            result = {"processed": 0, "skipped": 0, "failed": 0, "total": 0, "message": f"Error: {e}"}

    progress_bar.progress(1.0)

    st.markdown("---")
    st.markdown("### ✅ Processing Complete")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Total Threads", result.get("total", 0))
    r2.metric("✅ Processed", result.get("processed", 0))
    r3.metric("❌ Failed", result.get("failed", 0))
    r4.metric("⏭️ Skipped", result.get("skipped", 0))

    msg = result.get("message", "")
    if result.get("failed", 0) > 0:
        st.warning(f"⚠️ {msg}\n\nSome threads failed (likely API quota). Click **Re-Process** above to retry the failed ones after a minute.")
    else:
        st.success(f"🎉 {msg}")

    st.info("💡 Head to the **Insights**, **Tasks**, or **Overview** pages to explore the AI-generated intelligence!")
    
    st.cache_data.clear()

# ── Pending Threads Preview ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Unprocessed Email Threads")

db = SessionLocal()
try:
    pending_threads = (
        db.query(Email.thread_id, Email.subject, func.count(Email.id).label("count"))
        .filter(Email.processed_by_ai == False)
        .group_by(Email.thread_id, Email.subject)
        .all()
    )
    if not pending_threads:
        st.info("No pending threads. All emails are processed!")
    else:
        st.markdown(f"<div style='color:#64748b; font-size:13px; margin-bottom:12px;'>{len(pending_threads)} thread(s) pending</div>", unsafe_allow_html=True)
        for row in pending_threads:
            st.markdown(f"""
            <div class="thread-row">
                <span style="color:#a5b4fc; font-weight:600; font-family:monospace;">{row.thread_id}</span>
                <span style="color:#e2e8f0; flex:1; margin: 0 16px;">{row.subject or 'No subject'}</span>
                <span style="background:rgba(251,191,36,0.15); color:#fbbf24; border:1px solid rgba(251,191,36,0.3); padding:3px 10px; border-radius:20px; font-size:12px;">{row.count} email(s)</span>
            </div>
            """, unsafe_allow_html=True)
finally:
    db.close()

# ── Processed Threads Summary ───────────────────────────────────────────────
with st.expander("✅ View Already-Processed Threads"):
    db = SessionLocal()
    try:
        done_threads = (
            db.query(Email.thread_id, Email.subject, func.count(Email.id).label("count"))
            .filter(Email.processed_by_ai == True)
            .group_by(Email.thread_id, Email.subject)
            .all()
        )
        if not done_threads:
            st.info("No processed threads yet.")
        else:
            for row in done_threads:
                st.markdown(f"""
                <div class="thread-row">
                    <span style="color:#6ee7b7; font-weight:600; font-family:monospace;">{row.thread_id}</span>
                    <span style="color:#e2e8f0; flex:1; margin: 0 16px;">{row.subject or 'No subject'}</span>
                    <span style="background:rgba(110,231,183,0.12); color:#6ee7b7; border:1px solid rgba(110,231,183,0.3); padding:3px 10px; border-radius:20px; font-size:12px;">{row.count} email(s) ✓</span>
                </div>
                """, unsafe_allow_html=True)
    finally:
        db.close()
