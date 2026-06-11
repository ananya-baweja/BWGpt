import streamlit as st
import re
import database
import llm
import audit_logger
from st_copy_button import st_copy_button
from streamlit_mic_recorder import speech_to_text
from utils.helpers import generate_chat_title, convert_df_to_csv, convert_df_to_tsv
from components.shared_ui import render_action_drawers, dashboard_modal

def abort_chat_generation():
    """Interrupts the chat generation and unlocks the UI."""
    st.session_state.stop_gen = True
    st.session_state.chat_is_generating = False
    st.session_state.chats[st.session_state.current_chat].append({
        "role": "assistant",
        "content": "⚠️ This response was stopped."
    })
    if "chat_pending_prompt" in st.session_state:
        del st.session_state.chat_pending_prompt

def render_chat_workspace():
    st.title("🏢 BWGpt")
    current_chat_key = st.session_state.current_chat
    current_chat_history = st.session_state.chats[current_chat_key]
    
    chat_container = st.container()
    
    with chat_container:
        if len(current_chat_history) == 0:
            st.markdown(f"<h1 style='text-align: center; margin-top: 10vh;'>Welcome, {st.session_state.current_user}!</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray; font-size: 1.2rem;'>Ask me anything about your company data.</p>", unsafe_allow_html=True)

        for i, message in enumerate(current_chat_history):
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                if message.get("is_dashboard") and st.button("📊 Reopen Dashboard", key=f"reopen_dash_{i}"):
                    dashboard_modal(filter_str=message.get("pbi_filter", ""))
                
                if "data_table" in message:
                    df = message["data_table"]
                    st.dataframe(df)
                    col1, _, col2 = st.columns([1.5, 6, 2.5])
                    with col1:
                        st_copy_button(text=convert_df_to_tsv(df), before_copy_label="📋 Copy", key=f"copy_{current_chat_key}_{i}")
                    with col2:
                        st.download_button(label="📥 Download", data=convert_df_to_csv(df), file_name=f"BWGpt_Export_{i}.csv", mime="text/csv", key=f"dl_{current_chat_key}_{i}")
                
                if "full_insights" in message:
                    render_action_drawers(message["full_insights"], unique_key=f"hist_{i}")

    # --- CONCURRENCY LOCK STATE ---
    is_generating = st.session_state.get("chat_is_generating", False)

    st.markdown("""
        <style>
        div[data-testid="stPopover"] > button {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            font-size: 1.2rem !important;
        }
        div[data-testid="stPopover"] > button:hover {
            background-color: rgba(128, 128, 128, 0.1) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    file_col, chat_col, mic_col = st.columns([1, 10, 1], vertical_alignment="center")
    
    with file_col:
        with st.popover("➕", help="Attach Context Files"):
            uploaded_files = st.file_uploader(
                "Upload files",
                type=["pdf", "xlsx", "docx", "xls", "doc"],
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="chat_file_uploader"
            )

    with chat_col:
        text_prompt = st.chat_input("Ask anything", disabled=is_generating)
        
    with mic_col:
        if is_generating:
            st.button("🎙️", disabled=True, key="dummy_mic_locked_chat")
            voice_prompt = None
        else:
            voice_prompt = speech_to_text(
                language='en',
                start_prompt="🎙️",
                stop_prompt="⏹️",
                just_once=True,
                key='voice_input'
            )
            
    # Combine Prompts
    user_prompt = text_prompt or voice_prompt

    # 1. CAPTURE PROMPT AND LOCK UI
    if user_prompt and not is_generating:
        if not user_prompt.strip():
            st.warning("⚠️ Please enter a valid question.")
            st.stop()
            
        st.session_state.chat_pending_prompt = user_prompt
        st.session_state.chat_is_generating = True
        st.rerun()

    # 2. EXECUTE LOCKED GENERATION PIPELINE
    if is_generating and "chat_pending_prompt" in st.session_state:
        prompt_to_process = st.session_state.chat_pending_prompt
        
        if current_chat_key.startswith("New Chat"):
            new_title = generate_chat_title(prompt_to_process)
            base_title = new_title
            counter = 1
            while new_title in st.session_state.chats:
                new_title = f"{base_title} ({counter})"
                counter += 1
            
            updated_chats = {new_title: st.session_state.chats.pop(current_chat_key)}
            updated_chats.update(st.session_state.chats)
            st.session_state.chats = updated_chats
            st.session_state.current_chat = new_title
            current_chat_key = new_title 

        st.session_state.chats[current_chat_key].append({"role": "user", "content": prompt_to_process})
        
        stop_button_placeholder = st.empty()
        st.session_state.stop_gen = False
        stop_button_placeholder.button("⏹ Stop Generation", type="primary", on_click=abort_chat_generation, key="interrupt_chat_trigger")

        with chat_container:
            with st.chat_message("user"):
                st.write(prompt_to_process)
                
            if not st.session_state.stop_gen:
                with st.chat_message("assistant"):
                    conn = database.get_connection()
                    if conn:
                        try:
                            db_schema = database.get_schema()
                            response_placeholder = st.empty()
                            
                            full_response_text = ""
                            interrupted = False
                            
                            for token in llm.stream_sql(prompt_to_process, db_schema):
                                if st.session_state.stop_gen:
                                    interrupted = True
                                    break
                                full_response_text += token
                                response_placeholder.code(full_response_text, language="sql")
                            
                            if interrupted:
                                response_placeholder.warning("⚠️ This response was stopped.")
                            else:
                                clean_sql = re.sub(r'```sql', '', full_response_text, flags=re.IGNORECASE)
                                clean_sql = re.sub(r'```', '', clean_sql).strip()
                                
                                response_placeholder.empty()

                                is_sql_query = any(keyword in clean_sql.upper() for keyword in ["SELECT", "EXEC ", "WITH ", "UPDATE ", "INSERT "])
                                
                                if is_sql_query:
                                    st.write("Here is the query I generated and ran:")
                                    st.code(clean_sql, language="sql")
                                    
                                    audit_logger.log_chat_query(
                                        login_id=st.session_state.current_email, 
                                        user_prompt=prompt_to_process, 
                                        generated_sql=clean_sql
                                    )
                                    
                                    df = database.execute_query(clean_sql, conn)
                                    
                                    if df is not None and not df.empty:
                                        st.dataframe(df)
                                        
                                        action_buttons_placeholder = st.empty()
                                        
                                        st.session_state.chats[current_chat_key].append({
                                            "role": "assistant", 
                                            "content": f"Here is the query I generated and ran:\n```sql\n{clean_sql}\n```",
                                            "data_table": df
                                        })

                                        st.markdown("### AI Business Insights")
                                        insights_placeholder = st.empty()
                                        
                                        data_for_llm = df.head(20).to_markdown(index=False)
                                        full_insights = ""
                                        has_content = False
                                        
                                        for token in llm.stream_insights(prompt_to_process, data_for_llm):
                                            if st.session_state.stop_gen:
                                                break
                                            if token:
                                                has_content = True
                                                full_insights += token
                                                insights_placeholder.markdown(full_insights)
                                        
                                        if not st.session_state.stop_gen:
                                            if not has_content:
                                                insights_placeholder.markdown("*No specific insights could be generated for this dataset.*")
                                            else:
                                                insights_placeholder.markdown(full_insights)
                                                
                                                st.session_state.chats[current_chat_key].append({
                                                    "role": "assistant",
                                                    "content": f"### AI Business Insights\n{full_insights}",
                                                    "full_insights": full_insights
                                                })
                                                
                                                render_action_drawers(full_insights, unique_key="fresh")

                                        with action_buttons_placeholder.container():
                                            col1, spacer, col2 = st.columns([1.5, 6, 2.5])
                                            with col1:
                                                copy_text = convert_df_to_tsv(df)
                                                st_copy_button(text=copy_text, before_copy_label="📋 Copy", after_copy_label="✅ Copied!", key="copy_fresh_query")
                                            with col2:
                                                csv = convert_df_to_csv(df)
                                                st.download_button(label="📥 Download", data=csv, file_name="BWGpt_Export.csv", mime="text/csv", key="dl_fresh_query")

                                    else:
                                        st.info("Query executed successfully, but no data was returned to analyze.")
                                        st.session_state.chats[current_chat_key].append({
                                            "role": "assistant", 
                                            "content": f"Query executed successfully, but no data returned:\n```sql\n{clean_sql}\n```"
                                        })
                                        
                                else:
                                    st.write(clean_sql)
                                    st.session_state.chats[current_chat_key].append({
                                        "role": "assistant", 
                                        "content": clean_sql
                                    })
                                
                        except Exception as e:
                            error_msg = f"Sorry, I encountered an error: {e}"
                            st.error(error_msg)
                            st.session_state.chats[current_chat_key].append({"role": "assistant", "content": error_msg})
                    else:
                        st.error("No database connection available.")
                        st.session_state.chats[current_chat_key].append({"role": "assistant", "content": "No database connection available."})

        # 3. UNLOCK UI
        stop_button_placeholder.empty()

        if st.session_state.get("chat_is_generating"):
            st.session_state.chat_is_generating = False
            del st.session_state.chat_pending_prompt
            st.rerun()