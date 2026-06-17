import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from backend.database import SessionLocal, Insight, Task

load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Chat Assistant")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    st.error("Gemini API Key is not set. Please set it in the `.env` file to use the Chat Assistant.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
        except Exception as e:
            st.error(f"Error communicating with Gemini: {e}")
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
