import streamlit as st
import datetime
from backend.database import SessionLocal, ExecutiveReport
from backend.ai_processor import generate_executive_report
from fpdf import FPDF
import io

st.set_page_config(page_title="Executive Report", page_icon="📈", layout="wide")

st.title("📈 Weekly Executive Intelligence Report")
st.markdown("Aggregate cross-thread intelligence to extract high-level trends, risks, and recommendations.")

def create_pdf(report: ExecutiveReport) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Executive Intelligence Report", ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Date Range: {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')}", ln=True, align="C")
    pdf.ln(10)
    
    sections = [
        ("Top Topics", report.top_topics),
        ("Key Decisions", report.key_decisions),
        ("Risks & Bottlenecks", report.risks_bottlenecks),
        ("Workload Summary", report.workload_summary),
        ("Recommendations", report.recommendations)
    ]
    
    for title, content in sections:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Helvetica", "", 12)
        
        # Sanitize string to prevent fpdf core font unicode crashes
        safe_content = str(content).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, text=safe_content)
        pdf.ln(5)
        
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Task Metrics", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Open Tasks: {report.open_tasks}", ln=True)
    pdf.cell(0, 8, f"Overdue Tasks: {report.overdue_tasks}", ln=True)
    
    return bytes(pdf.output())

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=7))
with col2:
    end_date = st.date_input("End Date", datetime.date.today())

if st.button("Generate Executive Report", type="primary"):
    with st.spinner("Aggregating threads and generating AI report..."):
        start_dt = datetime.datetime.combine(start_date, datetime.time.min)
        end_dt = datetime.datetime.combine(end_date, datetime.time.max)
        
        report_id = generate_executive_report(start_dt, end_dt)
        
        if report_id:
            st.success("Report generated successfully!")
            st.session_state["latest_report_id"] = report_id
        else:
            st.warning("No data found in this date range to generate a report.")

st.divider()

db = SessionLocal()
try:
    # Display the latest report or selected report
    reports = db.query(ExecutiveReport).order_by(ExecutiveReport.created_at.desc()).all()
    
    if reports:
        st.subheader("Report History")
        
        report_options = {f"Report {r.id}: {r.start_date.strftime('%Y-%m-%d')} to {r.end_date.strftime('%Y-%m-%d')}": r for r in reports}
        selected_report_str = st.selectbox("Select a report to view:", list(report_options.keys()))
        selected_report = report_options[selected_report_str]
        
        if selected_report:
            st.markdown(f"### Report for {selected_report.start_date.strftime('%Y-%m-%d')} to {selected_report.end_date.strftime('%Y-%m-%d')}")
            
            # Layout
            m1, m2 = st.columns(2)
            m1.metric("Open Tasks", int(selected_report.open_tasks)) # type: ignore
            m2.metric("Overdue Tasks", int(selected_report.overdue_tasks)) # type: ignore
            
            st.markdown("#### 📌 Top Topics")
            st.info(selected_report.top_topics)
            
            st.markdown("#### ✅ Key Decisions")
            st.success(selected_report.key_decisions)
            
            st.markdown("#### ⚠️ Risks & Bottlenecks")
            st.warning(selected_report.risks_bottlenecks)
            
            st.markdown("#### 👥 Team Workload")
            st.text(selected_report.workload_summary)
            
            st.markdown("#### 💡 Strategic Recommendations")
            st.info(selected_report.recommendations)
            
            # Export
            pdf_bytes = create_pdf(selected_report)
            st.download_button(
                label="📥 Export to PDF",
                data=pdf_bytes,
                file_name=f"Executive_Report_{selected_report.start_date.strftime('%Y%m%d')}_{selected_report.end_date.strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
            
    else:
        st.info("No reports generated yet. Use the button above to generate your first report.")
finally:
    db.close()
