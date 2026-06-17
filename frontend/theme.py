import streamlit as st
import streamlit.components.v1 as components

def inject_theme_manager():
    # Define custom CSS variables and styling overrides for dark/light themes
    st.markdown("""
    <style>
    :root {
        --bg-gradient: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #0a1628 100%);
        --text-color: #e2e8f0;
        --card-bg: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        --card-border: rgba(255,255,255,0.08);
        --divider-color: rgba(99,102,241,0.4);
        --title-gradient: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #7c3aed 100%);
        --sidebar-bg: #090e1a;
        --input-bg: rgba(255,255,255,0.06);
        --input-border: rgba(99,102,241,0.4);
        --input-text: #e2e8f0;
    }

    [data-theme="light"] {
        --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 60%, #e2e8f0 100%);
        --text-color: #0f172a;
        --card-bg: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.5) 100%);
        --card-border: rgba(0,0,0,0.08);
        --divider-color: rgba(99,102,241,0.2);
        --title-gradient: linear-gradient(135deg, #0f172a 0%, #312e81 60%, #4f46e5 100%);
        --sidebar-bg: #f1f5f9;
        --input-bg: #ffffff;
        --input-border: rgba(99,102,241,0.4);
        --input-text: #0f172a;
    }

    [data-theme="dark"] {
        --bg-gradient: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 40%, #0a1628 100%);
        --text-color: #e2e8f0;
        --card-bg: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        --card-border: rgba(255,255,255,0.08);
        --divider-color: rgba(99,102,241,0.4);
        --title-gradient: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #7c3aed 100%);
        --sidebar-bg: #090e1a;
        --input-bg: rgba(255,255,255,0.06);
        --input-border: rgba(99,102,241,0.4);
        --input-text: #e2e8f0;
    }

    /* Apply styles dynamically using variables */
    .stApp {
        background: var(--bg-gradient) !important;
        color: var(--text-color) !important;
    }
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
    }
    h1, h2, h3, h4, h5, h6, .stMarkdown p, .stMarkdown span, .stMarkdown li, [data-testid="stWidgetLabel"] p {
        color: var(--text-color) !important;
    }
    .stat-card {
        background: var(--card-bg) !important;
        border-color: var(--card-border) !important;
        color: var(--text-color) !important;
    }
    .feature-card {
        background: var(--card-bg) !important;
        border-color: var(--card-border) !important;
    }
    .feature-title {
        color: var(--text-color) !important;
    }
    [data-testid="stTextInput"] input {
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border-color: var(--input-border) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Invisible iframe component executing the JS to inject the dropdown ⋮ menu in the top-right corner
    html_code = """
    <script>
    (function() {
        var doc;
        try {
            doc = window.parent.document;
        } catch (e) {
            doc = document;
        }

        // 1. Inject styling for menu and dropdown into document head
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
                    width: 160px;
                    display: none;
                    flex-direction: column;
                    gap: 4px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
                    backdrop-filter: blur(10px);
                }
                #theme-dropdown.show {
                    display: flex;
                }
                .theme-opt {
                    padding: 8px 12px;
                    font-size: 13px;
                    color: #94a3b8;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-family: system-ui, -apple-system, sans-serif;
                }
                .theme-opt:hover {
                    background: rgba(99, 102, 241, 0.15);
                    color: #ffffff;
                }
                .theme-opt.active {
                    background: rgba(99, 102, 241, 0.25);
                    color: #a5b4fc;
                    font-weight: 600;
                }

                /* Parent overrides depending on data-theme */
                html[data-theme="light"], body[data-theme="light"] {
                    --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 60%, #e2e8f0 100%) !important;
                    --text-color: #0f172a !important;
                    --sidebar-bg: #f1f5f9 !important;
                }
                html[data-theme="light"] #theme-menu-btn {
                    background: rgba(0, 0, 0, 0.05);
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    color: #0f172a;
                }
                html[data-theme="light"] #theme-dropdown {
                    background: rgba(255, 255, 255, 0.95);
                    border: 1px solid rgba(99, 102, 241, 0.25);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                }
                html[data-theme="light"] .theme-opt {
                    color: #475569;
                }
                html[data-theme="light"] .theme-opt:hover {
                    background: rgba(99, 102, 241, 0.1);
                    color: #0f172a;
                }
                html[data-theme="light"] .theme-opt.active {
                    background: rgba(99, 102, 241, 0.2);
                    color: #4f46e5;
                }
            `;
            doc.head.appendChild(styleEl);
        }

        // 2. Define theme apply function
        window.applyTheme = function(pref) {
            var theme = pref;
            if (pref === 'system') {
                theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            }
            
            // Set attributes
            doc.documentElement.setAttribute('data-theme', theme);
            document.documentElement.setAttribute('data-theme', theme);
            
            // Setup Light mode styles for native Streamlit iframe text elements
            var iframeStyleId = 'streamlit-iframe-theme-overrides';
            var iframeStyle = document.getElementById(iframeStyleId);
            if (!iframeStyle) {
                iframeStyle = document.createElement('style');
                iframeStyle.id = iframeStyleId;
                document.head.appendChild(iframeStyle);
            }
            
            if (theme === 'light') {
                iframeStyle.innerHTML = `
                    .stMarkdown, p, span, h1, h2, h3, h4, h5, h6, label, li, a, div[data-testid="stExpander"] {
                        color: #0f172a !important;
                    }
                    div[data-testid="stExpander"] details {
                        background-color: rgba(0, 0, 0, 0.03) !important;
                        border: 1px solid rgba(0, 0, 0, 0.08) !important;
                    }
                    /* Custom light mode stats backgrounds */
                    .stat-card.purple { background: rgba(99, 102, 241, 0.08) !important; }
                    .stat-card.blue   { background: rgba(59, 130, 246, 0.08) !important; }
                    .stat-card.green  { background: rgba(16, 185, 129, 0.08) !important; }
                    .stat-card.orange { background: rgba(245, 158, 11, 0.08) !important; }
                `;
            } else {
                iframeStyle.innerHTML = '';
            }

            // Update active styling in dropdown
            doc.querySelectorAll('.theme-opt').forEach(function(el) {
                if (el.getAttribute('data-val') === pref) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });
        };

        // 3. Setup container and ⋮ button in parent window
        var containerId = 'custom-theme-menu-container';
        var container = doc.getElementById(containerId);
        if (!container) {
            container = doc.createElement('div');
            container.id = containerId;
            container.innerHTML = `
                <div id="theme-menu-btn" title="Display Settings">⋮</div>
                <div id="theme-dropdown">
                    <div class="theme-opt" data-val="dark">🌑 Dark Mode</div>
                    <div class="theme-opt" data-val="light">☀️ Light Mode</div>
                    <div class="theme-opt" data-val="system">💻 System Default</div>
                </div>
            `;
            doc.body.appendChild(container);
            
            var btn = container.querySelector('#theme-menu-btn');
            var dropdown = container.querySelector('#theme-dropdown');
            
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                dropdown.classList.toggle('show');
            });
            
            doc.addEventListener('click', function() {
                dropdown.classList.remove('show');
            });
            
            container.querySelectorAll('.theme-opt').forEach(function(opt) {
                opt.addEventListener('click', function() {
                    var val = opt.getAttribute('data-val');
                    localStorage.setItem('theme-preference', val);
                    window.applyTheme(val);
                });
            });
        }

        // Apply theme preference on load
        var initialPref = localStorage.getItem('theme-preference') || 'system';
        window.applyTheme(initialPref);
        
        // Listen to system changes
        window.parent.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            if (localStorage.getItem('theme-preference') === 'system') {
                window.applyTheme('system');
            }
        });
    })();
    </script>
    """
    components.html(html_code, height=0)
