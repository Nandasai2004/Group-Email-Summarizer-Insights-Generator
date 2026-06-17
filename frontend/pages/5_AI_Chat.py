import streamlit as st
from google import genai
from google.genai import types
import os
import urllib.parse
from dotenv import load_dotenv
from backend.database import SessionLocal, Insight, Task

load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def render_voice_option(text: str, key: str):
    encoded_text = urllib.parse.quote(text)
    html_code = f"""
    <div style="display: flex; gap: 8px; align-items: center; margin-top: 8px; margin-bottom: 4px;">
        <button id="btn-play-{key}" onclick="togglePlay()" style="background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.35); color: #a5b4fc; border-radius: 6px; padding: 5px 12px; font-size: 11px; cursor: pointer; transition: all 0.2s; font-family: 'Inter', sans-serif; display: flex; align-items: center; gap: 5px;">🔊 Read Response</button>
        <button id="btn-stop-{key}" onclick="stopSpeech()" style="background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.35); color: #fca5a5; border-radius: 6px; padding: 5px 12px; font-size: 11px; cursor: pointer; display: none; transition: all 0.2s; font-family: 'Inter', sans-serif;">⏹️ Stop</button>
    </div>
    <script>
    var synth = window.speechSynthesis || window.parent.speechSynthesis;
    var utterance = null;
    var rawText = decodeURIComponent("{encoded_text}");

    function togglePlay() {{
        if (!synth) {{
            alert("Text-to-speech is not supported in this browser.");
            return;
        }}
        
        synth.cancel();
        
        // Clean up markdown syntax so the voice reads it naturally
        var cleanText = rawText.replace(/[*#`_\-]/g, "")
                               .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1") // clean markdown links
                               .replace(/\\n/g, " ");

        utterance = new SpeechSynthesisUtterance(cleanText);
        
        var btnPlay = document.getElementById("btn-play-{key}");
        var btnStop = document.getElementById("btn-stop-{key}");
        
        utterance.onstart = function() {{
            btnPlay.innerText = "🔊 Playing...";
            btnPlay.style.background = "rgba(99,102,241,0.25)";
            btnStop.style.display = "inline-block";
        }};
        
        utterance.onend = function() {{
            resetUI();
        }};
        
        utterance.onerror = function() {{
            resetUI();
        }};
        
        synth.speak(utterance);
    }}

    function stopSpeech() {{
        if (synth) {{
            synth.cancel();
        }}
        resetUI();
    }}

    function resetUI() {{
        var btnPlay = document.getElementById("btn-play-{key}");
        var btnStop = document.getElementById("btn-stop-{key}");
        btnPlay.innerText = "🔊 Read Response";
        btnPlay.style.background = "rgba(99,102,241,0.12)";
        btnStop.style.display = "none";
    }}
    </script>
    """
    st.components.v1.html(html_code, height=36)

st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
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
st.title("🤖 AI Chat Assistant")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    st.error("Gemini API Key is not set. Please set it in the `.env` file to use the Chat Assistant.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_voice_option(message["content"], f"hist_{idx}")

def get_db_context():
    db = SessionLocal()
    try:
        # Fetch some insights and tasks to provide as context to the LLM
        insights = db.query(Insight).limit(10).all()
        tasks = db.query(Task).filter(Task.status == "Open").limit(20).all()
        
        context = "Current Database Context:\n\n"
        context += "Recent Insights/Topics:\n"
        for i in insights:
            context += f"- Topic: {i.topic}, Summary: {i.summary}, Decisions: {i.decisions}\n"
            
        context += "\nOpen Tasks:\n"
        for t in tasks:
            context += f"- Task: {t.task_description}, Owner: {t.owner}, Due: {t.due_date}\n"
            
        return context
    finally:
        db.close()

# React to user input
if prompt := st.chat_input("Ask me about pending issues, tasks, or trends..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    context = get_db_context()
    
    system_prompt = f"""
    You are an AI assistant for a corporate management team. You help them summarize and query their group emails.
    Use the following database context to answer the user's question. If the context doesn't contain the answer, say you don't know based on the current data.
    
    {context}
    """
    
    gemini_messages = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_messages.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=gemini_messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                ),
            )
            for chunk in response_stream:
                full_response += (chunk.text or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            render_voice_option(full_response, "current")
        except Exception as e:
            st.error(f"Error communicating with Gemini: {e}")
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
