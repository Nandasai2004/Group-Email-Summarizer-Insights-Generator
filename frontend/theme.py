import streamlit as st
import streamlit.components.v1 as components


def inject_theme_manager():
    """
    Injects a complete theme management system with CSS variables,
    a ⋮ dropdown menu in the top-right corner, and JavaScript to
    persist theme preference in localStorage.
    Supports: Dark Mode, Light Mode, System Default.
    """

    # ── CSS Variables & Streamlit Element Overrides ──────────────
    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════
       DEFAULT / ROOT — DARK MODE
       ═══════════════════════════════════════════════ */
    :root {
        --bg-gradient: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #0a1628 100%);
        --text-color: #e2e8f0;
        --text-muted: #94a3b8;
        --card-bg: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        --card-bg-solid: rgba(15, 23, 42, 0.6);
        --card-border: rgba(255,255,255,0.08);
        --divider-color: rgba(99,102,241,0.4);
        --title-gradient: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #7c3aed 100%);
        --sidebar-bg: #090e1a;
        --input-bg: rgba(255,255,255,0.06);
        --input-border: rgba(99,102,241,0.4);
        --input-text: #e2e8f0;
        --btn-bg: rgba(99,102,241,0.15);
        --btn-border: rgba(99,102,241,0.4);
        --btn-text: #a5b4fc;
        --tab-text: #64748b;
        --tab-active-text: #a5b4fc;
        --tab-active-border: #6366f1;
        --toggle-bg: rgba(255,255,255,0.08);
        --expander-bg: rgba(255,255,255,0.03);
        --expander-border: rgba(255,255,255,0.06);
        --selectbox-bg: rgba(255,255,255,0.06);
        --selectbox-text: #e2e8f0;
        --metric-value: #ffffff;
        --metric-label: #94a3b8;
        --success-bg: rgba(16,185,129,0.1);
        --error-bg: rgba(239,68,68,0.1);
        --info-bg: rgba(59,130,246,0.1);
        --warning-bg: rgba(245,158,11,0.1);
        --shadow-color: rgba(0,0,0,0.3);
        --stat-purple: #a5b4fc;
        --stat-blue: #93c5fd;
        --stat-green: #6ee7b7;
        --stat-orange: #fcd34d;
    }

    /* ═══════════════════════════════════════════════
       LIGHT MODE OVERRIDES
       ═══════════════════════════════════════════════ */
    [data-theme="light"] {
        --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 60%, #e2e8f0 100%);
        --text-color: #0f172a;
        --text-muted: #475569;
        --card-bg: linear-gradient(135deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.6) 100%);
        --card-bg-solid: rgba(255, 255, 255, 0.75);
        --card-border: rgba(0,0,0,0.08);
        --divider-color: rgba(99,102,241,0.2);
        --title-gradient: linear-gradient(135deg, #0f172a 0%, #312e81 60%, #4f46e5 100%);
        --sidebar-bg: #f1f5f9;
        --input-bg: #ffffff;
        --input-border: rgba(99,102,241,0.3);
        --input-text: #0f172a;
        --btn-bg: rgba(99,102,241,0.08);
        --btn-border: rgba(99,102,241,0.3);
        --btn-text: #4f46e5;
        --tab-text: #475569;
        --tab-active-text: #4f46e5;
        --tab-active-border: #4f46e5;
        --toggle-bg: rgba(0,0,0,0.05);
        --expander-bg: rgba(0,0,0,0.02);
        --expander-border: rgba(0,0,0,0.06);
        --selectbox-bg: #ffffff;
        --selectbox-text: #0f172a;
        --metric-value: #0f172a;
        --metric-label: #475569;
        --success-bg: rgba(16,185,129,0.08);
        --error-bg: rgba(239,68,68,0.08);
        --info-bg: rgba(59,130,246,0.08);
        --warning-bg: rgba(245,158,11,0.08);
        --shadow-color: rgba(0,0,0,0.06);
        --stat-purple: #4f46e5;
        --stat-blue: #2563eb;
        --stat-green: #059669;
        --stat-orange: #d97706;
    }

    /* DARK MODE explicit — same as :root */
    [data-theme="dark"] {
        --bg-gradient: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #0a1628 100%);
        --text-color: #e2e8f0;
        --text-muted: #94a3b8;
        --card-bg: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        --card-bg-solid: rgba(15, 23, 42, 0.6);
        --card-border: rgba(255,255,255,0.08);
        --divider-color: rgba(99,102,241,0.4);
        --title-gradient: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #7c3aed 100%);
        --sidebar-bg: #090e1a;
        --input-bg: rgba(255,255,255,0.06);
        --input-border: rgba(99,102,241,0.4);
        --input-text: #e2e8f0;
        --btn-bg: rgba(99,102,241,0.15);
        --btn-border: rgba(99,102,241,0.4);
        --btn-text: #a5b4fc;
        --tab-text: #64748b;
        --tab-active-text: #a5b4fc;
        --tab-active-border: #6366f1;
        --toggle-bg: rgba(255,255,255,0.08);
        --expander-bg: rgba(255,255,255,0.03);
        --expander-border: rgba(255,255,255,0.06);
        --selectbox-bg: rgba(255,255,255,0.06);
        --selectbox-text: #e2e8f0;
        --metric-value: #ffffff;
        --metric-label: #94a3b8;
        --success-bg: rgba(16,185,129,0.1);
        --error-bg: rgba(239,68,68,0.1);
        --info-bg: rgba(59,130,246,0.1);
        --warning-bg: rgba(245,158,11,0.1);
        --shadow-color: rgba(0,0,0,0.3);
        --stat-purple: #a5b4fc;
        --stat-blue: #93c5fd;
        --stat-green: #6ee7b7;
        --stat-orange: #fcd34d;
    }

    /* ═══════════════════════════════════════════════
       GLOBAL LAYOUT OVERRIDES
       ═══════════════════════════════════════════════ */

    /* Background */
    .stApp {
        background: var(--bg-gradient) !important;
        color: var(--text-color) !important;
        transition: background 0.4s ease, color 0.3s ease;
    }

    /* Hide default Streamlit header, deploy button, and options dots */
    header, [data-testid="stHeader"], .stAppDeployButton, [data-testid="stAppDeployButton"] {
        display: none !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        transition: background-color 0.4s ease;
    }

    /* ── Typography ─────────────────────────────── */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown a,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stMetricValue"],
    label {
        color: var(--text-color) !important;
        transition: color 0.3s ease;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
    }

    /* ── Input Fields ───────────────────────────── */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border-color: var(--input-border) !important;
        transition: all 0.3s ease;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
    }

    /* ── Select / Dropdown ──────────────────────── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        background-color: var(--selectbox-bg) !important;
        color: var(--selectbox-text) !important;
        border-color: var(--input-border) !important;
    }

    /* ── Tabs ────────────────────────────────────── */
    [data-testid="stTabs"] [data-baseweb="tab-list"] button {
        color: var(--tab-text) !important;
        transition: color 0.2s ease;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: var(--tab-active-text) !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: var(--tab-active-border) !important;
    }

    /* ── Expanders ──────────────────────────────── */
    [data-testid="stExpander"] details {
        background-color: var(--expander-bg) !important;
        border: 1px solid var(--expander-border) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stExpander"] summary {
        color: var(--text-color) !important;
    }

    /* ── Buttons ────────────────────────────────── */
    [data-testid="stBaseButton-secondary"] {
        background-color: var(--btn-bg) !important;
        border-color: var(--btn-border) !important;
        color: var(--btn-text) !important;
        transition: all 0.25s ease;
    }
    [data-testid="stBaseButton-secondary"]:hover {
        background-color: rgba(99,102,241,0.2) !important;
        transform: translateY(-1px);
    }

    /* ── Toggles ────────────────────────────────── */
    [data-testid="stToggle"] label > div {
        transition: all 0.3s ease;
    }

    /* ── Data Frames / Tables ──────────────────── */
    [data-testid="stDataFrame"] {
        border-color: var(--card-border) !important;
    }

    /* ── Custom Cards ──────────────────────────── */
    .stat-card, .feature-card {
        background: var(--card-bg) !important;
        border-color: var(--card-border) !important;
        color: var(--text-color) !important;
        box-shadow: 0 4px 15px var(--shadow-color) !important;
        transition: all 0.3s ease;
    }
    .feature-title {
        color: var(--text-color) !important;
    }

    /* ── Alert Boxes ───────────────────────────── */
    [data-testid="stAlert"] {
        transition: all 0.3s ease;
    }

    /* ── Radio buttons ─────────────────────────── */
    [data-testid="stRadio"] label {
        color: var(--text-color) !important;
    }
    [data-testid="stRadio"] label span {
        color: var(--text-color) !important;
    }

    /* ── Checkbox ───────────────────────────────── */
    [data-testid="stCheckbox"] label span {
        color: var(--text-color) !important;
    }

    /* ── Toast / Notifications ─────────────────── */
    [data-testid="stToast"] {
        background-color: var(--card-bg-solid) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--card-border) !important;
    }

    /* ── Scrollbar styling ─────────────────────── */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(99,102,241,0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99,102,241,0.5);
    }
    </style>
    <script>
    (function() {
        try {
            var pref = localStorage.getItem('theme-preference') || 'dark';
            document.documentElement.setAttribute('data-theme', pref);
            if (window.parent && window.parent.document) {
                window.parent.document.documentElement.setAttribute('data-theme', pref);
            }
        } catch(e) {}
    })();
    </script>
    """, unsafe_allow_html=True)

    # ── JavaScript: ⋮ Dropdown Menu + Theme Engine ──────────────
    html_code = """
    <script>
    (function() {
        var doc;
        var parentWin;
        try {
            doc = window.parent.document;
            parentWin = window.parent;
        } catch (e) {
            doc = document;
            parentWin = window;
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 1. Inject styles for the ⋮ dropdown menu
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        var styleId = 'custom-theme-menu-styles';
        if (!doc.getElementById(styleId)) {
            var styleEl = doc.createElement('style');
            styleEl.id = styleId;
            styleEl.innerHTML = `
                #custom-theme-menu-container {
                    position: fixed;
                    top: 14px;
                    right: 14px;
                    z-index: 999999;
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
                }
                #theme-menu-btn {
                    width: 42px;
                    height: 42px;
                    border-radius: 10px;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    color: #e2e8f0;
                    font-size: 22px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    user-select: none;
                    transition: all 0.25s ease;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                }
                #theme-menu-btn:hover {
                    background: rgba(99, 102, 241, 0.15);
                    border-color: rgba(99, 102, 241, 0.4);
                    color: #a5b4fc;
                    transform: scale(1.05);
                }
                #theme-dropdown {
                    position: absolute;
                    top: 50px;
                    right: 0;
                    background: rgba(15, 23, 42, 0.95);
                    border: 1px solid rgba(99, 102, 241, 0.35);
                    border-radius: 12px;
                    padding: 8px;
                    width: 180px;
                    display: none;
                    flex-direction: column;
                    gap: 4px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
                    backdrop-filter: blur(15px);
                    -webkit-backdrop-filter: blur(15px);
                    animation: dropIn 0.2s ease;
                }
                @keyframes dropIn {
                    from { opacity: 0; transform: translateY(-8px) scale(0.96); }
                    to   { opacity: 1; transform: translateY(0)   scale(1); }
                }
                #theme-dropdown.show {
                    display: flex;
                }
                .theme-opt {
                    padding: 10px 14px;
                    font-size: 13px;
                    color: #94a3b8;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-weight: 500;
                }
                .theme-opt:hover {
                    background: rgba(99, 102, 241, 0.15);
                    color: #ffffff;
                }
                .theme-opt.active {
                    background: rgba(99, 102, 241, 0.25);
                    color: #a5b4fc;
                    font-weight: 700;
                }
                .theme-opt .opt-check {
                    margin-left: auto;
                    font-size: 14px;
                    display: none;
                }
                .theme-opt.active .opt-check {
                    display: inline;
                }

                /* ── Light mode adaptations for the menu itself ── */
                html[data-theme="light"] #theme-menu-btn,
                body[data-theme="light"] #theme-menu-btn {
                    background: rgba(0, 0, 0, 0.04);
                    border: 1px solid rgba(0, 0, 0, 0.08);
                    color: #334155;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
                }
                html[data-theme="light"] #theme-menu-btn:hover,
                body[data-theme="light"] #theme-menu-btn:hover {
                    background: rgba(99, 102, 241, 0.1);
                    border-color: rgba(99, 102, 241, 0.3);
                    color: #4f46e5;
                }
                html[data-theme="light"] #theme-dropdown,
                body[data-theme="light"] #theme-dropdown {
                    background: rgba(255, 255, 255, 0.96);
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }
                html[data-theme="light"] .theme-opt,
                body[data-theme="light"] .theme-opt {
                    color: #475569;
                }
                html[data-theme="light"] .theme-opt:hover,
                body[data-theme="light"] .theme-opt:hover {
                    background: rgba(99, 102, 241, 0.08);
                    color: #0f172a;
                }
                html[data-theme="light"] .theme-opt.active,
                body[data-theme="light"] .theme-opt.active {
                    background: rgba(99, 102, 241, 0.15);
                    color: #4f46e5;
                }

                /* ── Parent-level variable overrides for light ── */
                html[data-theme="light"], body[data-theme="light"] {
                    --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 60%, #e2e8f0 100%) !important;
                    --text-color: #0f172a !important;
                    --text-muted: #475569 !important;
                    --sidebar-bg: #f1f5f9 !important;
                    --card-bg: linear-gradient(135deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.6) 100%) !important;
                    --card-bg-solid: rgba(255, 255, 255, 0.75) !important;
                    --card-border: rgba(0,0,0,0.08) !important;
                    --input-bg: #ffffff !important;
                    --input-border: rgba(99,102,241,0.3) !important;
                    --input-text: #0f172a !important;
                    --shadow-color: rgba(0,0,0,0.06) !important;
                }
            `;
            doc.head.appendChild(styleEl);
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 2. Theme apply function
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        window.applyTheme = function(pref) {
            var theme = pref;
            if (pref === 'system') {
                theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            }

            // Set on parent doc and iframe doc
            doc.documentElement.setAttribute('data-theme', theme);
            document.documentElement.setAttribute('data-theme', theme);

            // Force Streamlit parent overrides for light mode
            var parentStyleId = 'streamlit-parent-theme-overrides';
            var parentStyle = doc.getElementById(parentStyleId);
            if (!parentStyle) {
                parentStyle = doc.createElement('style');
                parentStyle.id = parentStyleId;
                doc.head.appendChild(parentStyle);
            }

            if (theme === 'light') {
                parentStyle.innerHTML = `
                    /* Light mode: override Streamlit's dark defaults inside iframes */
                    .stMarkdown, p, span, h1, h2, h3, h4, h5, h6,
                    label, li, a, td, th,
                    div[data-testid="stExpander"] summary span,
                    div[data-testid="stMetricValue"],
                    div[data-testid="stMetricDelta"] {
                        color: #0f172a !important;
                    }
                    div[data-testid="stMetricLabel"],
                    div[data-testid="stCaptionContainer"] {
                        color: #475569 !important;
                    }
                    div[data-testid="stExpander"] details {
                        background-color: rgba(0, 0, 0, 0.02) !important;
                        border: 1px solid rgba(0, 0, 0, 0.06) !important;
                    }
                    /* Custom stat card light overrides */
                    .stat-card.purple { background: rgba(99, 102, 241, 0.07) !important; border-color: rgba(99,102,241,0.15) !important; }
                    .stat-card.blue   { background: rgba(59, 130, 246, 0.07) !important; border-color: rgba(59,130,246,0.15) !important; }
                    .stat-card.green  { background: rgba(16, 185, 129, 0.07) !important; border-color: rgba(16,185,129,0.15) !important; }
                    .stat-card.orange { background: rgba(245, 158, 11, 0.07) !important; border-color: rgba(245,158,11,0.15) !important; }
                    
                    .stat-card.purple .stat-number { color: #4f46e5 !important; }
                    .stat-card.blue .stat-number   { color: #2563eb !important; }
                    .stat-card.green .stat-number  { color: #059669 !important; }
                    .stat-card.orange .stat-number { color: #d97706 !important; }
                    
                    .stat-card .stat-label { color: #475569 !important; }
                    .stat-card .stat-sub { color: #64748b !important; }

                    /* Hero typography overrides */
                    .hero-title {
                        background: linear-gradient(135deg, #0f172a 0%, #312e81 60%, #4f46e5 100%) !important;
                        -webkit-background-clip: text !important;
                        -webkit-text-fill-color: transparent !important;
                        background-clip: text !important;
                    }
                    .hero-subtitle {
                        color: #475569 !important;
                    }

                    /* Details panel overrides */
                    .details-panel {
                        background: rgba(255, 255, 255, 0.8) !important;
                        border-color: rgba(99, 102, 241, 0.2) !important;
                        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05) !important;
                    }
                    .details-title {
                        color: #0f172a !important;
                    }
                    .details-subtitle {
                        color: #475569 !important;
                    }
                `;
            } else {
                parentStyle.innerHTML = '';
            }

            // Highlight active option in dropdown
            doc.querySelectorAll('.theme-opt').forEach(function(el) {
                if (el.getAttribute('data-val') === pref) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });
        };

        // Expose on parent window so persistent parent elements can invoke it
        if (window.parent) {
            window.parent.applyTheme = window.applyTheme;
        }

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 3. Create the ⋮ dropdown menu in parent
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        var containerId = 'custom-theme-menu-container';
        var container = doc.getElementById(containerId);
        if (container) {
            container.remove();
        }

        container = doc.createElement('div');
        container.id = containerId;
        container.innerHTML = `
            <div id="theme-menu-btn" title="Display Settings">⋮</div>
            <div id="theme-dropdown">
                <div class="theme-opt" data-val="dark">🌑 Dark Mode<span class="opt-check">✓</span></div>
                <div class="theme-opt" data-val="light">☀️ Light Mode<span class="opt-check">✓</span></div>
                <div class="theme-opt" data-val="system">💻 System Default<span class="opt-check">✓</span></div>
            </div>
        `;
        doc.body.appendChild(container);

        var btn = container.querySelector('#theme-menu-btn');
        var dropdown = container.querySelector('#theme-dropdown');

        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdown.classList.toggle('show');
        });

        if (parentWin.closeThemeDropdown) {
            doc.removeEventListener('click', parentWin.closeThemeDropdown);
        }
        parentWin.closeThemeDropdown = function() {
            var dp = doc.getElementById('theme-dropdown');
            if (dp) dp.classList.remove('show');
        };
        doc.addEventListener('click', parentWin.closeThemeDropdown);

        container.querySelectorAll('.theme-opt').forEach(function(opt) {
            opt.addEventListener('click', function(e) {
                e.stopPropagation();
                var val = opt.getAttribute('data-val');
                localStorage.setItem('theme-preference', val);
                if (parentWin && typeof parentWin.applyTheme === 'function') {
                    parentWin.applyTheme(val);
                } else {
                    window.applyTheme(val);
                }
                dropdown.classList.remove('show');
            });
        });

        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        // 4. Apply saved preference on load
        // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        var initialPref = localStorage.getItem('theme-preference') || 'dark';
        if (window.parent && typeof window.parent.applyTheme === 'function') {
            window.parent.applyTheme(initialPref);
        } else {
            window.applyTheme(initialPref);
        }

        // Listen for system preference changes
        try {
            window.parent.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function() {
                if (localStorage.getItem('theme-preference') === 'system') {
                    window.applyTheme('system');
                }
            });
        } catch(e) {}
    })();
    </script>
    """
    components.html(html_code, height=0)
