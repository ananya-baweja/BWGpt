import streamlit as st

# IMPORT CORE MODULES
import sidebar
from components.shared_ui import init_session_state, inject_custom_styles, rename_dialog, dashboard_modal
from components.auth import render_auth_ui

# IMPORT COMPONENT VIEWS
from components.chat_view import render_chat_workspace
from components.graph_view import render_graph_workspace

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="BWGpt", 
    page_icon="🏢", 
    layout="centered", 
    initial_sidebar_state="expanded" 
)

# 2. STATE & STYLE INITIALIZATION
init_session_state()
inject_custom_styles()

# 3. MAIN ROUTING MATRIX
if not st.session_state.logged_in:
    render_auth_ui()
else:
    # Render global sidebar navigation
    sidebar.render_sidebar(rename_dialog, dashboard_modal)

    # Catch and trigger PowerBI modal links if flagged
    if st.session_state.get("trigger_pbi_modal"):
        pbi_filter = st.session_state.pop("trigger_pbi_modal")
        dashboard_modal(filter_str=pbi_filter)

    # Initial login popup safety check
    if not st.session_state.has_seen_dashboard:
        st.session_state.has_seen_dashboard = True
        dashboard_modal()

    # View Router: Direct Traffic to Specific Functional Class Component Files
    if st.session_state.app_view == "ai_dashboard":
        render_graph_workspace()
    else:
        render_chat_workspace()