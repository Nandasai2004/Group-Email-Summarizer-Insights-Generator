import streamlit as st
from backend.database import SessionLocal, User

def check_login_status():
    """
    Automatically authenticates the user without showing a login form.
    Returns the User database object. Creates a default user if none exists.
    """
    st.session_state["logged_in"] = True
    st.session_state["user_email"] = "jane.doe@example.com"
    st.session_state["user_name"] = "Jane Doe"

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == st.session_state["user_email"]).first()
        if user:
            return user
        # Fallback if the default user does not exist — use first available user
        user = db.query(User).first()
        if user:
            st.session_state["user_email"] = user.email
            st.session_state["user_name"] = user.name
            return user
        # If no users exist at all, create a default one
        new_user = User(
            name="Jane Doe",
            email="jane.doe@example.com",
            role="Executive Director",
            department="Operations",
            password="admin"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        db.close()
