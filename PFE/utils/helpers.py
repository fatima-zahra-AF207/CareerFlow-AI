import streamlit as st
try:
    from streamlit_option_menu import option_menu
except ImportError:
    option_menu = None
import os

def setup_sidebar():
    """Create consistent sidebar navigation across all pages"""
    
    # Logo and title
    st.sidebar.image("assets/logo.png", width=150) if os.path.exists("assets/logo.png") else None
    st.sidebar.title("🇲🇦 ForsaFlow MA")
    st.sidebar.markdown("---")
    
    # Navigation menu using option_menu for better UI
    with st.sidebar:
        if option_menu:
            selected = option_menu(
                menu_title="Navigation",
                options=["🏠 Profil & Diagnostic", "✨ Optimisation", "📊 Suivi & Candidatures", "📈 Statistiques", "🤖 Coach IA", "⚙️ Paramètres"],
                icons=["person", "magic", "list-task", "graph-up", "chat-dots", "gear"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "#FF6B35", "font-size": "20px"},
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
                    "nav-link-selected": {"background-color": "#FF6B35"},
                }
            )
        else:
            selected = st.radio("Navigation", ["🏠 Profil & Diagnostic", "✨ Optimisation", "📊 Suivi & Candidatures", "📈 Statistiques", "🤖 Coach IA", "⚙️ Paramètres"])
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("Version 2.2.0 (Morocco)")
    st.sidebar.caption("Powered by ForsaFlow AI")
    
    return selected
