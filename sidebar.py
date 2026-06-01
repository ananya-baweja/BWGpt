import streamlit as st
import audit_logger
import streamlit.components.v1 as components

def render_sidebar(rename_dialog_func, cookies):
    """
    Renders the sidebar with a sticky header, a smoothly scrolling history, 
    and a sticky footer locked to the bottom (Gemini-style).
    """
    compact_sidebar_style = """
    <style>
    /* 1. Pull the sidebar content to the absolute edges (Fixes the "higher up" issue) */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }

    /* 2. STICKY HEADER (Locks BWGpt & New Chat to the top) */
    div.stElementContainer:has(#sidebar-header) {
        position: sticky !important;
        top: 0px !important;
        background-color: var(--secondary-background-color, #f0f2f6) !important;
        z-index: 999 !important;
        padding-top: 1.5rem !important;
        padding-bottom: 10px !important;
        border-bottom: 1px solid rgba(128,128,128,0.1); /* Subtle visual separator */
    }

    /* 3. STICKY FOOTER (Locks Profile & Sign Out to the absolute bottom) */
    div.stElementContainer:has(#sidebar-footer) {
        position: sticky !important;
        bottom: 0px !important;
        background-color: var(--secondary-background-color, #f0f2f6) !important;
        z-index: 999 !important;
        padding-top: 15px !important;
        padding-bottom: 1.5rem !important;
        border-top: 1px solid rgba(128,128,128,0.1); /* Subtle visual separator */
    }
    
    /* 4. History container spacing */
    div.stElementContainer:has(#sidebar-history) {
        padding-top: 10px;
        padding-bottom: 10px;
    }

    /* Custom sleek scrollbar for the sidebar */
    [data-testid="stSidebarUserContent"]::-webkit-scrollbar {
        width: 4px;
    }
    [data-testid="stSidebarUserContent"]::-webkit-scrollbar-thumb {
        background-color: rgba(128, 128, 128, 0.3);
        border-radius: 4px;
    }
    
    /* Reduce default sidebar width */
    [data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    /* Compact styling for chat navigation rows */
    div.stButton > button[key^="switch_"] {
        padding: 4px 8px !important;
        font-size: 14px !important;
        text-align: left !important;
    }
    /* Shrink action popover triggers */
    div[data-testid="stPopover"] > button {
        padding: 2px 6px !important;
        font-size: 12px !important;
        line-height: 1.2 !important;
    }
    </style>
    """
    st.markdown(compact_sidebar_style, unsafe_allow_html=True)

    with st.sidebar:
        
        # -----------------------------------------
        # 1. FIXED HEADER
        # -----------------------------------------
        header_container = st.container()
        with header_container:
            # Invisible anchor used by CSS to glue this exact container to the top
            st.markdown("<div id='sidebar-header'></div>", unsafe_allow_html=True)
            
            st.markdown("<h2 style='margin-top: -15px; margin-bottom: 5px;'>🏢 BWGpt</h2>", unsafe_allow_html=True)
            if st.button("➕ New Chat", use_container_width=True, key="new_chat_top_btn"):
                base_name = "New Chat"
                new_chat_name = base_name
                counter = 1
                while new_chat_name in st.session_state.chats:
                    new_chat_name = f"{base_name} {counter}"
                    counter += 1
                updated_chats = {new_chat_name: []}
                updated_chats.update(st.session_state.chats)
                st.session_state.chats = updated_chats
                st.session_state.current_chat = new_chat_name
                st.rerun()

            st.markdown("---")
            if st.button("⚡ Flash Dashboard", use_container_width=True):
                st.session_state.show_flash_dashboard = True
                st.rerun()
            st.markdown("---")

            CUSTOMER_SUPPORT_URL = "https://www.kapture.cx/blog/what-is-customer-support/"  # Change this to your actual customer assistant URL

            st.link_button(
                "🎧 Customer Assistant",
                CUSTOMER_SUPPORT_URL,
                use_container_width=True
            )
                
        # 2. SCROLLABLE HISTORY (Middle)
        history_container = st.container()
        with history_container:
            # Invisible anchor for spacing
            st.markdown("<div id='sidebar-history'></div>", unsafe_allow_html=True)
            
            pinned = [c for c in st.session_state.pinned_chats if c in st.session_state.chats]
            unpinned = [c for c in st.session_state.chats.keys() if c not in pinned]
            ordered_chats = pinned + unpinned
            
            for chat_name in ordered_chats:
                col_chat, col_menu = st.columns([4.5, 1.5])
                with col_chat:
                    display_label = f"📌 {chat_name}" if chat_name in pinned else chat_name
                    is_active = (chat_name == st.session_state.current_chat)
                    if st.button(display_label, use_container_width=True, key=f"switch_{chat_name}", type="secondary" if not is_active else "primary"):
                        st.session_state.current_chat = chat_name
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
                            if chat_name in st.session_state.pinned_chats: 
                                st.session_state.pinned_chats.remove(chat_name)
                            if st.session_state.current_chat == chat_name:
                                if len(st.session_state.chats) > 0: 
                                    st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                                else:
                                    st.session_state.chats = {"New Chat": []}
                                    st.session_state.current_chat = "New Chat"
                            st.rerun()

        # 3. FIXED FOOTER (Profile & Sign Out)
        footer_container = st.container()
        with footer_container:
            # Invisible anchor used by CSS to glue this exact container to the bottom
            st.markdown("<div id='sidebar-footer'></div>", unsafe_allow_html=True)
            
            display_name = st.session_state.current_user
            display_dept = st.session_state.current_department
            display_email = st.session_state.get("current_email", "")
            initials = "".join([part[0].upper() for part in display_name.split() if part])[:2] if display_name else "U"
            
            profile_html = f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; padding: 4px;" title="Email: {display_email}">
                <div style="background-color: #10b981; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 15px;">
                    {initials}
                </div>
                <div style="line-height: 1.2;">
                    <div style="font-weight: bold; font-size: 15px; color: var(--text-color);">{display_name}</div>
                    <div style="color: gray; font-size: 13px;">💼 {display_dept}</div>
                </div>
            </div>
            """
            st.markdown(profile_html, unsafe_allow_html=True)
            
            if st.button("Sign Out", type="secondary", use_container_width=True, key="logout_embedded_btn"):
                audit_logger.log_user_logout(st.session_state.current_email, st.session_state.get("current_session_id"))
                # Clear all session state
                st.session_state.logged_in = False
                st.session_state.current_user = "User"
                st.session_state.current_department = ""
                st.session_state.current_email = ""
                st.session_state.current_session_id = None
                st.session_state.show_flash_dashboard = False
                st.session_state.dashboard_popup_shown = False
                st.session_state.chats = {"New Chat": []}
                st.session_state.current_chat = "New Chat"
                st.session_state.pinned_chats = []
                # Use the cookies object passed in from app.py (same instance)
                cookies["logged_in"] = "false"
                cookies["email"] = ""
                cookies["name"] = ""
                cookies["department"] = ""
                cookies.save()
                st.rerun()