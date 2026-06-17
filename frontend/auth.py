import streamlit as st
from backend.database import SessionLocal, User

def check_login_status():
    """
    Checks if user is logged in. Automatically authenticates without showing a login form.
    """
    st.session_state["logged_in"] = True
    st.session_state["user_email"] = "jane.doe@example.com"
    st.session_state["user_name"] = "Jane Doe"

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == st.session_state["user_email"]).first()
        if user:
            return user
        # Fallback if the user does not exist
        user = db.query(User).first()
        if user:
            st.session_state["user_email"] = user.email
            st.session_state["user_name"] = user.name
            return user
    finally:
        db.close()

def render_login_page():
    # Inject page config styling overrides for a consistent premium dark login look
    st.markdown("""
    <style>
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 60px;
    }
    .login-card {
        width: 100%;
        max-width: 440px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 20px;
        padding: 40px 32px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        backdrop-filter: blur(15px);
        text-align: center;
    }
    .login-logo {
        font-size: 42px;
        margin-bottom: 16px;
    }
    .login-title {
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 8px;
        background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .login-subtitle {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 32px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="login-logo">⚡</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">GES Intelligence</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Group Email Summarizer & Insights Platform</div>', unsafe_allow_html=True)
        
        email = st.text_input("Email Address", placeholder="jane.doe@example.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pwd")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign In to Workspace", type="primary", use_container_width=True):
            if not email or not password:
                st.error("⚠️ Please fill in all credentials.")
            else:
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.email == email.strip().lower()).first()
                    if user and user.password == password:
                        st.session_state["logged_in"] = True
                        st.session_state["user_email"] = user.email
                        st.session_state["user_name"] = user.name
                        st.success("✅ Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password. (Default password: admin)")
                finally:
                    db.close()
                    
        st.markdown('</div></div>', unsafe_allow_html=True)
