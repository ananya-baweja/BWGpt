import streamlit as st
import database
import llm
import audit_logger  
from components.charts import render_custom_chart
from utils.helpers import generate_chat_title
from streamlit_mic_recorder import speech_to_text

def abort_graph_generation():
    """Interrupts the graph generation and unlocks the UI."""
    st.session_state.stop_gen = True
    st.session_state.graph_is_generating = False
    st.session_state.chats[st.session_state.current_chat].append({
        "role": "assistant",
        "content": "⚠️ This response was stopped."
    })
    # Clear the pending prompt so it doesn't get processed again
    if "graph_pending_prompt" in st.session_state:
        del st.session_state.graph_pending_prompt

def render_graph_workspace():
    st.title("📊 AI Generated Insights & Graphs")
    st.markdown("Ask the AI to build visualizations dynamically from database records.")
    
    current_chat_key = st.session_state.current_chat
    current_chat_history = st.session_state.chats.get(current_chat_key, [])
    
    # 1. Render historical user-generated graphs
    chart_view_container = st.container()
    with chart_view_container:
        for item in current_chat_history:
            if item["role"] == "user":
                with st.chat_message("user"):
                    st.write(item["content"])
            elif item["role"] == "assistant":
                with st.chat_message("assistant"):
                    if "df" in item and "config" in item:
                        render_custom_chart(df=item["df"], chart_config=item["config"])
                    elif "content" in item:
                        st.write(item["content"])
                        
    # --- CONCURRENCY LOCK STATE ---
    is_generating = st.session_state.get("graph_is_generating", False)

    # Keeps the Mic and Upload buttons transparent
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

    # 2. UI INPUT ASSEMBLY
    chat_col, mic_col = st.columns([10, 1], vertical_alignment="center")
    
    with chat_col:
        # Dynamically disables the text box while generating!
        text_prompt = st.chat_input("Describe the chart you want...", disabled=is_generating)
        
    with mic_col:
        if is_generating:
            # Renders a disabled dummy button to prevent voice concurrency
            st.button("🎙️", disabled=True, key="dummy_mic_locked")
            voice_prompt = None
        else:
            voice_prompt = speech_to_text(
                language='en',
                start_prompt="🎙️",
                stop_prompt="⏹️",
                just_once=True,
                key='voice_input_graph' 
            )
            
    graph_prompt = text_prompt or voice_prompt

    # 3. CAPTURE NEW PROMPT AND LOCK UI
    if graph_prompt and not is_generating:
        if not graph_prompt.strip():
            st.warning("⚠️ Please enter a valid question.")
            st.stop()
            
        st.session_state.graph_pending_prompt = graph_prompt
        st.session_state.graph_is_generating = True
        st.rerun() # Instantly refreshes the page to lock the inputs

    # 4. EXECUTE GENERATION PIPELINE
    if is_generating and "graph_pending_prompt" in st.session_state:
        prompt_to_process = st.session_state.graph_pending_prompt
        
        # Auto-title generation engine logic
        if current_chat_key.startswith("New Graph Chat"):
            new_title = generate_chat_title(prompt_to_process)
            base_title = new_title
            counter = 1
            while new_title in st.session_state.chats:
                new_title = f"{base_title} ({counter})"
                counter += 1
            
            st.session_state.chats[new_title] = st.session_state.chats.pop(current_chat_key)
            
            if current_chat_key in st.session_state.graph_chats:
                idx = st.session_state.graph_chats.index(current_chat_key)
                st.session_state.graph_chats[idx] = new_title
            else:
                st.session_state.graph_chats.append(new_title)
                
            st.session_state.current_chat = new_title
            current_chat_key = new_title

        # Save user prompt to history
        st.session_state.chats[current_chat_key].append({"role": "user", "content": prompt_to_process})
        
        # Deploy Stop Generation Button
        stop_button_placeholder = st.empty()
        st.session_state.stop_gen = False
        stop_button_placeholder.button("⏹ Stop Generation", type="primary", on_click=abort_graph_generation, key="interrupt_graph_trigger")

        with chart_view_container:
            with st.chat_message("user"):
                st.write(prompt_to_process)
            
            if not st.session_state.stop_gen:
                with st.chat_message("assistant"):
                    with st.spinner("📊 Structuring graph data rules..."):
                        db_schema = database.get_schema()
                        spec = llm.generate_chart_spec(prompt_to_process, db_schema)
                        
                        if not st.session_state.stop_gen: 
                            if spec and "sql" in spec and "chart_config" in spec:
                                conn = database.get_connection()
                                if conn:
                                    audit_logger.log_chat_query(
                                        login_id=st.session_state.current_email, 
                                        user_prompt=prompt_to_process, 
                                        generated_sql=spec["sql"],
                                        session_id=st.session_state.get("current_session_id")
                                    )
                                    
                                    df = database.execute_query(spec["sql"], conn)
                                    if df is not None and not df.empty:
                                        render_custom_chart(df=df, chart_config=spec["chart_config"])
                                        
                                        st.session_state.chats[current_chat_key].append({
                                            "role": "assistant",
                                            "df": df,
                                            "config": spec["chart_config"]
                                        })
                                    else:
                                        st.info("The query successfully targeted structural rules but found zero entries to display.")
                                        st.session_state.chats[current_chat_key].append({
                                            "role": "assistant",
                                            "content": "⚠️ No records returned from query parameters to visualize."
                                        })
                                else:
                                    st.error("No database connection available.")
                            else:
                                st.error("Could not construct chart specification format. Please frame your query clearly with column fields.")
        
        stop_button_placeholder.empty()

        if st.session_state.get("graph_is_generating"):
            st.session_state.graph_is_generating = False
            del st.session_state.graph_pending_prompt
            st.rerun() 