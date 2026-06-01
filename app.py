import streamlit as st
import pandas as pd
import re
from st_copy_button import st_copy_button
from streamlit_mic_recorder import speech_to_text

# --- IMPORT YOUR CUSTOM MODULES ---
import database
import llm
import sidebar
import audit_logger

# ==========================================
# 1. PAGE SETUP & MAGIC CSS
# ==========================================
st.set_page_config(
    page_title="BWGpt", 
    page_icon="🏢", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

hide_st_style = """
            <style>
            footer {visibility: hidden;}
            
            /* FORCE CODE BLOCKS TO WORD-WRAP INSTEAD OF SCROLLING */
            div[data-testid="stCodeBlock"] pre {
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
            }

            /* FORCE ALERTS AND ERROR MESSAGES TO WORD-WRAP */
            div[data-testid="stAlert"] {
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
            }
            
            /* Un-clip the main container so sticky positioning works */
            .main .block-container {
                overflow: visible !important;
                padding-bottom: 100px !important; 
                padding-top: 1.5rem;
            }
            div[data-testid="InputInstructions"] {display: none;}
            
            /* FIX: Changed negative margin to positive to prevent table overlap! */
            [data-testid="stDataFrame"] {margin-bottom: 1rem !important;}
            
            /* --- THE ELEGANT ALIGNMENT FIX --- */
            /* 1. Set iframe container to exactly 44px */
            iframe[title*="streamlit_mic_recorder"] {
                height: 44px !important;
                min-height: 44px !important;
                margin-bottom: 0px !important; 
                display: block !important;
            }

            /* 2. Force BOTH buttons to exactly 44px to perfectly match the text input */
            div[data-testid="stPopover"] > button,
            div.stButton > button {
                height: 44px !important;
                border-radius: 8px !important;
                margin: 0px !important;
                padding: 0px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }

            /* 3. Strip hidden padding from the columns */
            div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlockBorderWrapper"] {
                margin: 0 !important;
                padding: 0 !important;
            }

            div[data-testid="column"]:nth-of-type(3) {display: flex; justify-content: flex-end;}
            
            /* PIN THE ENTIRE INPUT ROW TO THE BOTTOM OF THE SCREEN */
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stChatInput"]) {
                position: sticky !important;
                bottom: 0px !important;
                background-color: var(--background-color, white) !important;
                z-index: 999 !important;
                padding-bottom: 25px !important;
                padding-top: 10px !important;
                align-items: center !important; /* Natural center alignment now works perfectly */
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ==========================================
# 2. STATE INITIALIZATION & CALLBACKS
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_session_id" not in st.session_state: st.session_state.current_session_id = None
if "current_user" not in st.session_state: st.session_state.current_user = "User"
if "current_department" not in st.session_state: st.session_state.current_department = ""
if "current_email" not in st.session_state: st.session_state.current_email = ""
if "chats" not in st.session_state: st.session_state.chats = {"New Chat": []}
if "current_chat" not in st.session_state: st.session_state.current_chat = "New Chat"
if "pinned_chats" not in st.session_state: st.session_state.pinned_chats = []
if "stop_gen" not in st.session_state: st.session_state.stop_gen = False

if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "admin@adityabirla.com": {
            "name": "Admin User",
            "password": "Password123", 
            "department": "IT"
        }
    } 

def stop_generation():
    """Callback to instantly flip the stop switch AND save the warning message."""
    st.session_state.stop_gen = True
    st.session_state.chats[st.session_state.current_chat].append({
        "role": "assistant",
        "content": "⚠️ This response was stopped."
    })

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def validate_email(email_str):
    return email_str.strip().lower().endswith("@adityabirla.com")

def validate_password_complexity(password_str):
    if len(password_str) < 8:
        return False
    if not any(char.isdigit() for char in password_str):
        return False
    if not any(char.isalpha() for char in password_str):
        return False
    return True

def generate_chat_title(prompt):
    stopwords = ["can", "you", "show", "me", "the", "a", "an", "is", "what", "how", "give", "tell", "about", "load", "get", "pull", "list", "all"]
    words = re.findall(r'\b\w+\b', prompt)
    meaningful_words = [w.capitalize() for w in words if w.lower() not in stopwords]
    if not meaningful_words:
        meaningful_words = [w.capitalize() for w in words[:3]]
    title = " ".join(meaningful_words[:4])
    return title if title else "Untitled Chat"

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def convert_df_to_tsv(df):
    return df.to_csv(index=False, sep='\t')

@st.dialog("Rename Chat")
def rename_dialog(chat_name):
    with st.form(key=f"rename_form_{chat_name}", border=False):
        new_name = st.text_input("Enter new name:", value=chat_name)
        submitted = st.form_submit_button("Save", type="primary", use_container_width=True)
        if submitted:
            if new_name and new_name != chat_name and new_name not in st.session_state.chats:
                updated_history = {}
                for k, v in st.session_state.chats.items():
                    if k == chat_name:
                        updated_history[new_name] = v
                    else:
                        updated_history[k] = v
                st.session_state.chats = updated_history
                
                if chat_name in st.session_state.pinned_chats:
                    st.session_state.pinned_chats.remove(chat_name)
                    st.session_state.pinned_chats.append(new_name)
                if st.session_state.current_chat == chat_name:
                    st.session_state.current_chat = new_name
                st.rerun()
            elif new_name == chat_name:
                st.rerun() 
            else:
                st.error("Name is already taken.")

# ==========================================
# 4. AUTHENTICATION UI
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 4, 1]) 
    with col2:
        st.markdown("<h1 style='text-align: center;'>🏢 BWGpt</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Company Data Assistant</p>", unsafe_allow_html=True)
        st.write("") 
        
        tab_signin, tab_signup = st.tabs(["Sign In", "Sign Up"])
        
        with tab_signin:
            with st.form("signin_form", border=False):
                st.markdown("<h3>Welcome back</h3>", unsafe_allow_html=True)
                email_input = st.text_input("Corporate Email", placeholder="e.g. name@adityabirla.com")
                password_input = st.text_input("Password", type="password", placeholder="••••••••")
                st.write("") 
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
                
                if submitted:
                    norm_email = email_input.strip().lower()
                    if not email_input or not password_input:
                        st.error("Please enter both email and password.")
                    elif not validate_email(norm_email):
                        st.error("Access Denied: Only @adityabirla.com emails are allowed.")
                    elif norm_email in st.session_state.user_db and st.session_state.user_db[norm_email]["password"] == password_input:
                        st.session_state.logged_in = True
                        st.session_state.current_email = norm_email
                        st.session_state.current_user = st.session_state.user_db[norm_email]["name"]
                        st.session_state.current_department = st.session_state.user_db[norm_email]["department"]
                        st.session_state.current_session_id = audit_logger.log_user_login(norm_email)
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with tab_signup:
            with st.form("signup_form", border=False):
                st.markdown("<h3>Create Account</h3>", unsafe_allow_html=True)
                full_name = st.text_input("Full Name", placeholder="Enter Full Name")
                new_email = st.text_input("Corporate Email", placeholder="e.g. name@adityabirla.com")
                new_department = st.selectbox("Department", ["CASC", "Commercial", "Finance", "HR", "IT", "Logistics", "Marketing", "Non-Trade", "Sales"])
                new_password = st.text_input("Password", type="password", placeholder="Min 8 chars, includes letters & numbers")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                st.write("") 
                submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
                
                if submitted:
                    norm_new_email = new_email.strip().lower()
                    if not full_name or not new_email or not new_password:
                        st.error("Please fill in all fields.")
                    elif not validate_email(norm_new_email):
                        st.error("Registration Denied: You must use a valid @adityabirla.com email address.")
                    elif not validate_password_complexity(new_password):
                        st.error("Weak Password: Must be at least 8 characters long and contain both letters and digits.")
                    elif new_password != confirm_password: 
                        st.error("Passwords do not match.")
                    elif norm_new_email in st.session_state.user_db:
                        st.error("An account with this email already exists. Please sign in.")
                    else:
                        st.session_state.user_db[norm_new_email] = {
                            "name": full_name,
                            "password": new_password,
                            "department": new_department
                        }
                        st.success("Account created successfully! You can now sign in.")

# ==========================================
# 5. MAIN APP WORKSPACE
# ==========================================
else:
    sidebar.render_sidebar(rename_dialog)

    st.title("🏢 BWGpt")
    current_chat_key = st.session_state.current_chat
    current_chat_history = st.session_state.chats[current_chat_key]
    
    # STRUCTURAL FIX: CREATE A DEDICATED CONTAINER FOR CHAT HISTORY
    chat_container = st.container()
    
    with chat_container:
        if len(current_chat_history) == 0:
            st.markdown(f"<h1 style='text-align: center; margin-top: 10vh;'>Welcome, {st.session_state.current_user}!</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray; font-size: 1.2rem;'>Ask me anything about your company data.</p>", unsafe_allow_html=True)

        for i, message in enumerate(current_chat_history):
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "data_table" in message:
                    df = message["data_table"]
                    st.dataframe(df)
                    col1, spacer, col2 = st.columns([1.5, 6, 2.5])
                    with col1:
                        copy_text = convert_df_to_tsv(df)
                        st_copy_button(text=copy_text, before_copy_label="📋 Copy", after_copy_label="✅ Copied!", key=f"copy_{current_chat_key}_{i}")
                    with col2:
                        csv = convert_df_to_csv(df)
                        st.download_button(label="📥 Download", data=csv, file_name=f"BWGpt_Export_{i}.csv", mime="text/csv", key=f"dl_{current_chat_key}_{i}")

    # --- SIDE-BY-SIDE CHAT INPUT & UPLOAD BAR ---
    file_col, mic_col, chat_col = st.columns([1, 1, 10], vertical_alignment="center")
    
    with file_col:
        with st.popover("➕", help="Attach Context Files"):
            uploaded_files = st.file_uploader(
                "Upload files",
                type=["pdf", "xlsx", "docx", "xls", "doc"],
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="chat_file_uploader"
            )
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s)")

    with mic_col:
        voice_prompt = speech_to_text(
            language='en',
            start_prompt="🎤",
            stop_prompt="🛑",
            use_container_width=True,
            just_once=True,
            key='voice_input'
        )

    with chat_col:
        text_prompt = st.chat_input("E.g., What is the total budget for IT?")

    # --- HANDLE PROMPT LOGIC ---
    user_prompt = text_prompt or voice_prompt

    if user_prompt:
        
        # GUARDRAIL: Check if the text is empty or just spaces
        if not user_prompt.strip():
            st.warning("⚠️ Please enter a valid question.")
            st.stop()
        
        if current_chat_key.startswith("New Chat"):
            new_title = generate_chat_title(user_prompt)
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

        # Save to state
        st.session_state.chats[current_chat_key].append({"role": "user", "content": user_prompt})
        
        # Render the AI response INSIDE the chat_container
        with chat_container:
            with st.chat_message("user"):
                st.write(user_prompt)
                
            with st.chat_message("assistant"):
                conn = database.get_connection()
                if conn:
                    try:
                        db_schema = database.get_schema()
                        
                        stop_button_placeholder = st.empty()
                        response_placeholder = st.empty()
                        
                        st.session_state.stop_gen = False
                        
                        stop_button_placeholder.button("⏹ Stop Generation", type="primary", on_click=stop_generation, key="interrupt_trigger")
                        
                        full_response_text = ""
                        interrupted = False
                        
                        for token in llm.stream_sql(user_prompt, db_schema):
                            if st.session_state.stop_gen:
                                interrupted = True
                                break
                            
                            full_response_text += token
                            response_placeholder.code(full_response_text, language="sql")
                        
                        stop_button_placeholder.empty()
                        
                        if interrupted:
                            response_placeholder.warning("⚠️ This response was stopped.")
                            st.session_state.stop_gen = False
                            
                        else:
                            clean_sql = re.sub(r'```sql', '', full_response_text, flags=re.IGNORECASE)
                            clean_sql = re.sub(r'```', '', clean_sql).strip()
                            
                            response_placeholder.empty()

                            # --- GUARDRAIL: Check if response is conversational text or a SQL query ---
                            is_sql_query = any(keyword in clean_sql.upper() for keyword in ["SELECT", "EXEC ", "WITH ", "UPDATE ", "INSERT "])
                            
                            if is_sql_query:
                                st.write("Here is the query I generated and ran:")
                                st.code(clean_sql, language="sql")
                                
                                # SILENTLY LOG TO DATABASE
                                audit_logger.log_chat_query(
                                    login_id=st.session_state.current_email, 
                                    user_prompt=user_prompt, 
                                    generated_sql=clean_sql
                                )
                                
                                df = database.execute_query(clean_sql, conn)
                                st.dataframe(df)
                                
                                col1, spacer, col2 = st.columns([1.5, 6, 2.5])
                                with col1:
                                    copy_text = convert_df_to_tsv(df)
                                    st_copy_button(text=copy_text, before_copy_label="📋 Copy", after_copy_label="✅ Copied!", key="copy_fresh_query")
                                with col2:
                                    csv = convert_df_to_csv(df)
                                    st.download_button(label="📥 Download", data=csv, file_name="BWGpt_Export.csv", mime="text/csv", key="dl_fresh_query")
                                
                                st.session_state.chats[current_chat_key].append({
                                    "role": "assistant", 
                                    "content": f"Here is the query I generated and ran:\n```sql\n{clean_sql}\n```",
                                    "data_table": df
                                })

                                # PHASE 2: AI INSIGHTS GENERATION 
                                if not df.empty and len(df) > 0:
                                    st.markdown("### 🧠 AI Business Insights")
                                    insights_placeholder = st.empty()
                                    
                                    # Temporary loading message so the screen isn't blank
                                    insights_placeholder.markdown("*(Analyzing data... waking up local AI...)*")
                                    
                                    data_for_llm = df.head(20).to_markdown(index=False)
                                    
                                    full_insights = ""
                                    has_content = False
                                    
                                    for token in llm.stream_insights(user_prompt, data_for_llm):
                                        if token:
                                            has_content = True
                                            full_insights += token
                                            insights_placeholder.markdown(full_insights)
                                    
                                    if not has_content:
                                        insights_placeholder.markdown("*No specific insights could be generated for this dataset.*")
                                    else:
                                        st.session_state.chats[current_chat_key].append({
                                            "role": "assistant",
                                            "content": f"### 🧠 AI Business Insights\n{full_insights}"
                                        })
                                else:
                                    st.info("Query executed successfully, but no data was returned to analyze.")
                            else:
                                # It's a casual chatbot response (like "hi" or a greeting)
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
                
        # Force a rerun to clean up state
        st.rerun()