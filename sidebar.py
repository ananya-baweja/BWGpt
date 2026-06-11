import streamlit as st
import audit_logger

def render_sidebar(rename_dialog_func, dashboard_modal_func=None):
    """
    Renders the sidebar with a fixed header, scrolling history, 
    and a strictly bottom-pinned Teams-style profile footer.
    """
    compact_sidebar_style = """
    <style>
    div.stButton > button[key^="switch_"] {
        padding: 4px 8px !important;
        font-size: 14px !important;
        text-align: left !important;
    }
    /* Style the new Teams-style profile popover trigger */
    div[data-testid="stPopover"]:has(button[key="profile_popover"]) > button {
        padding: 8px 12px !important;
        font-size: 15px !important;
        font-weight: bold !important;
        justify-content: flex-start !important;
        background-color: transparent !important;
        border: none !important;
        color: var(--text-color) !important;
    }
    div[data-testid="stPopover"]:has(button[key="profile_popover"]) > button:hover {
        background-color: rgba(128,128,128,0.1) !important;
    }
    </style>
    """
    st.markdown(compact_sidebar_style, unsafe_allow_html=True)

    with st.sidebar:
        
        # 1. HEADER
        header_container = st.container()
        with header_container:
            st.markdown("<div id='sidebar-header'></div>", unsafe_allow_html=True)
            st.markdown("<h2 style='margin-top: -10px; margin-bottom: 5px;'>🏢 BWGpt</h2>", unsafe_allow_html=True)
            
            # --- THE PERMANENT DASHBOARD BUTTON ---
            if dashboard_modal_func and st.button("📊 View Live Dashboard", use_container_width=True, type="primary"):
                dashboard_modal_func()
            
            st.divider()
            
            # --- NAVIGATION WORKSPACE SWITCHER ---
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💬 Chat", use_container_width=True, type="primary" if st.session_state.get("app_view", "chat") == "chat" else "secondary"):
                    st.session_state.app_view = "chat"
                    st.rerun()
            with col2:
                if st.button("📊 AI Graphs", use_container_width=True, type="primary" if st.session_state.get("app_view") == "ai_dashboard" else "secondary"):
                    st.session_state.app_view = "ai_dashboard"
                    
                    # Ensure we have a graph chat active when clicking the tab
                    if st.session_state.current_chat not in st.session_state.get("graph_chats", []):
                        base_name = "New Graph Chat"
                        new_chat_name = base_name
                        counter = 1
                        while new_chat_name in st.session_state.chats:
                            new_chat_name = f"{base_name} {counter}"
                            counter += 1
                        
                        st.session_state.chats[new_chat_name] = []
                        if "graph_chats" not in st.session_state:
                            st.session_state.graph_chats = []
                        st.session_state.graph_chats.append(new_chat_name)
                        st.session_state.current_chat = new_chat_name
                    
                    st.rerun()
                
            # --- CONTEXT-AWARE NEW CHAT BUTTON ---
            if st.button("➕ New Chat", use_container_width=True, key="new_chat_top_btn", type="secondary"):
                is_graph_view = st.session_state.get("app_view") == "ai_dashboard"
                base_name = "New Graph Chat" if is_graph_view else "New Chat"
                
                new_chat_name = base_name
                counter = 1
                while new_chat_name in st.session_state.chats:
                    new_chat_name = f"{base_name} {counter}"
                    counter += 1
                    
                updated_chats = {new_chat_name: []}
                updated_chats.update(st.session_state.chats)
                st.session_state.chats = updated_chats
                st.session_state.current_chat = new_chat_name
                
                # If generated from the graph view, register it as a graph chat
                if is_graph_view:
                    if "graph_chats" not in st.session_state:
                        st.session_state.graph_chats = []
                    st.session_state.graph_chats.append(new_chat_name)
                    
                st.rerun() 
                
        # 2. SCROLLABLE HISTORY
        history_container = st.container()
        with history_container:
            st.markdown("<div id='sidebar-history'></div>", unsafe_allow_html=True)
            
            pinned = [c for c in st.session_state.pinned_chats if c in st.session_state.chats]
            unpinned = [c for c in st.session_state.chats.keys() if c not in pinned]
            ordered_chats = pinned + unpinned
            
            for chat_name in ordered_chats:
                col_chat, col_menu = st.columns([4.5, 1.5])
                with col_chat:
                    is_graph = chat_name in st.session_state.get("graph_chats", [])
                    
                    # Add adaptive icons for graph history
                    if is_graph:
                        display_label = f"📌 📊 {chat_name}" if chat_name in pinned else f"📊 {chat_name}"
                    else:
                        display_label = f"📌 {chat_name}" if chat_name in pinned else chat_name
                        
                    is_active = (chat_name == st.session_state.current_chat)
                    if st.button(display_label, use_container_width=True, key=f"switch_{chat_name}", type="secondary" if not is_active else "primary"):
                        st.session_state.current_chat = chat_name
                        if is_graph:
                            st.session_state.app_view = "ai_dashboard"
                        else:
                            st.session_state.app_view = "chat"
                        st.rerun()
                with col_menu:
                    with st.popover("⋮", use_container_width=True, key=f"pop_{chat_name}"):
                        if chat_name in pinned:
                            if st.button("Unpin", use_container_width=True, key=f"unpin_{chat_name}"):
                                st.session_state.pinned_chats.remove(chat_name)
                                st.rerun()
                        else:
                            if st.button("Pin", use_container_width=True, key=f"pin_{chat_name}"):
                                st.session_state.pinned_chats.append(chat_name)
                                st.rerun()
                        if st.button("Rename", use_container_width=True, key=f"ren_btn_{chat_name}"):
                            rename_dialog_func(chat_name)
                        if st.button("Delete", use_container_width=True, key=f"del_{chat_name}"):
                            del st.session_state.chats[chat_name]
                            if "graph_chats" in st.session_state and chat_name in st.session_state.graph_chats:
                                st.session_state.graph_chats.remove(chat_name)
                            if chat_name in st.session_state.pinned_chats: 
                                st.session_state.pinned_chats.remove(chat_name)
                            if st.session_state.current_chat == chat_name:
                                if len(st.session_state.chats) > 0: 
                                    st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                                    if st.session_state.current_chat in st.session_state.get("graph_chats", []):
                                        st.session_state.app_view = "ai_dashboard"
                                    else:
                                        st.session_state.app_view = "chat"
                                else:
                                    st.session_state.chats = {"New Chat": []}
                                    st.session_state.current_chat = "New Chat"
                                    st.session_state.app_view = "chat"
                            st.rerun()

        # 3. TEAMS-STYLE PROFILE (FLEX PUSHED TO BOTTOM)
        footer_container = st.container()
        with footer_container:
            st.markdown("<div id='sidebar-footer'></div>", unsafe_allow_html=True)
            
            display_name = st.session_state.current_user
            display_dept = st.session_state.current_department
            display_email = st.session_state.get("current_email", "")
            initials = "".join([part[0].upper() for part in display_name.split() if part])[:2] if display_name else "U"
            
            with st.popover(f"🟢 {initials} \u2002 {display_name}", use_container_width=True, key="profile_popover"):
                st.write(f"**{display_name}**")
                st.caption(f"📧 {display_email}")
                st.caption(f"💼 Department: {display_dept}")
                
                st.divider()
                
                if st.button("Sign Out", type="secondary", use_container_width=True, key="logout_embedded_btn"):
                    audit_logger.log_user_logout(st.session_state.current_email, st.session_state.get("current_session_id"))
                    st.session_state.logged_in = False
                    st.session_state.current_user = "User"
                    st.session_state.current_department = ""
                    st.session_state.current_email = ""
                    st.session_state.current_session_id = None
                    st.rerun()