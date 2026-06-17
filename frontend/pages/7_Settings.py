import streamlit as st
import streamlit.components.v1 as components
from backend.database import SessionLocal, User
from frontend.auth import check_login_status
from frontend.theme import inject_theme_manager

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Theme Manager ──
inject_theme_manager()

# ── Auth check ──
user = check_login_status()
assert user is not None  # check_login_status() calls st.stop() if not logged in

st.title("⚙️ Workspace Settings")
st.markdown("Manage your personal profile, display preferences, notifications, and security.")

tab1, tab2, tab3, tab4 = st.tabs([
    "👤 Profile Management", 
    "🎨 Display Theme", 
    "🔔 Notification Preferences", 
    "🔒 Security & Password"
])

# 👤 PROFILE MANAGEMENT
with tab1:
    st.subheader("User Profile Management")
    st.markdown("Update your personal account information and professional role.")
    
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.markdown(f"""
        <div style="text-align: center; padding: 32px 24px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 15px; margin-top: 10px;">
            <div style="font-size: 72px; margin-bottom: 15px;">👤</div>
            <h3 style="margin: 0; color: #ffffff;">{user.name}</h3>
            <p style="color: #8b5cf6; font-size: 14px; font-weight: 600; margin: 4px 0 16px;">{user.role}</p>
            <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px;">
                <p style="color: #64748b; font-size: 13px; margin: 2px 0;"><strong>Dept:</strong> {user.department}</p>
                <p style="color: #64748b; font-size: 13px; margin: 2px 0;"><strong>Email:</strong> {user.email}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        new_name = st.text_input("Full Name", value=str(user.name or ""))
        new_email = st.text_input("Email Address", value=str(user.email or ""))
        new_role = st.text_input("Role / Job Title", value=str(user.role or ""))
        new_dept = st.text_input("Department", value=str(user.department or ""))
        
        if st.button("Save Profile Settings", type="primary", use_container_width=True):
            if not new_name.strip() or not new_email.strip():
                st.error("⚠️ Name and Email fields cannot be empty.")
            else:
                db = SessionLocal()
                try:
                    db_user = db.query(User).filter(User.id == user.id).first()
                    if db_user:
                        db_user.name = new_name.strip()  # type: ignore[assignment]
                        db_user.email = new_email.strip().lower()  # type: ignore[assignment]
                        db_user.role = new_role.strip()  # type: ignore[assignment]
                        db_user.department = new_dept.strip()  # type: ignore[assignment]
                        db.commit()
                        
                        st.session_state["user_name"] = db_user.name
                        st.session_state["user_email"] = db_user.email
                        st.success("✅ Profile updated successfully!")
                        st.rerun()
                finally:
                    db.close()

# 🎨 DISPLAY THEME
with tab2:
    st.subheader("Theme Customization")
    st.markdown("Customize your workspace visual experience. Changes apply instantly across all pages.")
    
    st.markdown("<br>", unsafe_allow_html=True)

    theme_options = ["Dark Mode", "Light Mode", "System Default"]
    theme_descriptions = {
        "Dark Mode": "Deep navy gradients with soft glowing accents. Optimized for low-light environments and extended screen time.",
        "Light Mode": "Clean, bright interface with subtle shadows. Ideal for well-lit workspaces and daytime use.",
        "System Default": "Automatically matches your operating system's display preference (light or dark)."
    }
    theme_icons = {"Dark Mode": "🌑", "Light Mode": "☀️", "System Default": "💻"}

    col_t1, col_t2, col_t3 = st.columns(3)
    for col, opt in zip([col_t1, col_t2, col_t3], theme_options):
        with col:
            is_active = "border: 2px solid #6366f1; box-shadow: 0 0 20px rgba(99,102,241,0.25);" if opt == theme_options[0] else "border: 1px solid rgba(255,255,255,0.06);"
            st.markdown(f"""
            <div style="text-align: center; padding: 28px 20px; background: rgba(255,255,255,0.03); {is_active} border-radius: 16px; min-height: 180px;">
                <div style="font-size: 36px; margin-bottom: 12px;">{theme_icons[opt]}</div>
                <div style="font-size: 16px; font-weight: 700; margin-bottom: 8px;">{opt}</div>
                <div style="font-size: 12px; color: #64748b; line-height: 1.5;">{theme_descriptions[opt]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    selected_theme = st.radio("Choose Display Mode:", theme_options, index=0, horizontal=True)
    
    theme_val = "dark" if selected_theme == "Dark Mode" else ("light" if selected_theme == "Light Mode" else "system")
    
    js_code = f"""
    <script>
    (function() {{
        var val = "{theme_val}";
        localStorage.setItem('theme-preference', val);
        if (window.parent && window.parent.applyTheme) {{
            window.parent.applyTheme(val);
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0)
    st.success(f"✅ Theme set to **{selected_theme}** — synced across all pages via the ⋮ menu.")

# 🔔 NOTIFICATIONS
with tab3:
    st.subheader("Notification Preferences")
    st.markdown("Configure how and when you receive intelligence summaries.")
    
    email_alerts = st.toggle("Email Alerts", value=bool(user.email_alerts), help="Receive instant email notifications for critical threads.")
    daily_summaries = st.toggle("Daily Digests", value=bool(user.daily_summaries), help="Receive a daily digest of all email thread summaries.")
    slack_notifications = st.toggle("Slack Channel Integration", value=bool(user.slack_notifications), help="Push insights to the connected team Slack channel.")
    priority_only = st.toggle("Priority-Only Filtering", value=bool(user.priority_only), help="Only alert for emails flagged as High priority by Gemini.")
    
    if st.button("Save Notification Preferences", type="primary", use_container_width=True):
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.id == user.id).first()
            if db_user:
                db_user.email_alerts = email_alerts  # type: ignore[assignment]
                db_user.daily_summaries = daily_summaries  # type: ignore[assignment]
                db_user.slack_notifications = slack_notifications  # type: ignore[assignment]
                db_user.priority_only = priority_only  # type: ignore[assignment]
                db.commit()
                st.success("✅ Notification preferences updated successfully!")
                st.rerun()
        finally:
            db.close()

# 🔒 SECURITY
with tab4:
    st.subheader("Account Security & API Settings")
    st.markdown("Manage credentials, API access keys, and passwords.")
    
    col_sec1, col_sec2 = st.columns(2)
    
    with col_sec1:
        st.markdown("#### Change Password")
        curr_pwd = st.text_input("Current Password", type="password")
        new_pwd = st.text_input("New Password", type="password")
        conf_pwd = st.text_input("Confirm New Password", type="password")
        
        if st.button("Update Password", use_container_width=True):
            if not curr_pwd or not new_pwd or not conf_pwd:
                st.error("⚠️ All password fields are required.")
            elif curr_pwd != str(user.password):
                st.error("❌ Current password is incorrect.")
            elif new_pwd != conf_pwd:
                st.error("❌ New passwords do not match.")
            elif len(new_pwd) < 4:
                st.error("❌ Password must be at least 4 characters long.")
            else:
                db = SessionLocal()
                try:
                    db_user = db.query(User).filter(User.id == user.id).first()
                    if db_user:
                        db_user.password = new_pwd  # type: ignore[assignment]
                        db.commit()
                        st.success("✅ Password changed successfully!")
                finally:
                    db.close()
                    
    with col_sec2:
        st.markdown("#### Security Options")
        api_key_enabled = st.toggle("Enable API Key Access", value=bool(user.api_key_enabled), help="Enable programmatic access to the database using an API token.")
        two_factor_enabled = st.toggle("Require Multi-Factor Authentication (MFA)", value=bool(user.two_factor_enabled), help="Enforce two-factor verification for security.")
        
        if st.button("Save Security Settings", use_container_width=True):
            db = SessionLocal()
            try:
                db_user = db.query(User).filter(User.id == user.id).first()
                if db_user:
                    db_user.api_key_enabled = api_key_enabled  # type: ignore[assignment]
                    db_user.two_factor_enabled = two_factor_enabled  # type: ignore[assignment]
                    db.commit()
                    st.success("✅ Security preferences updated!")
                    st.rerun()
            finally:
                db.close()
