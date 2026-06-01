# import streamlit as st
# import pandas as pd
# import re
# import json
# import os
# from st_copy_button import st_copy_button
# from streamlit_cookies_manager import EncryptedCookieManager

# import database
# import llm
# import sidebar
# import audit_logger

# # 1. PAGE SETUP & MAGIC CSS
# st.set_page_config(
#     page_title="BWGpt", 
#     page_icon="🏢", 
#     layout="centered",
#     initial_sidebar_state="expanded" 
# )

# cookies = EncryptedCookieManager(
#     prefix="bwgpt_",
#     password="your-secret-key"
# )

# if not cookies.ready():
#     st.stop()

# USERS_FILE = "users.json"

# def load_users():
#     if not os.path.exists(USERS_FILE):
#         with open(USERS_FILE, "w") as f:
#             json.dump({
#                 "admin@adityabirla.com": {
#                     "name": "Admin User",
#                     "password": "Password123",
#                     "department": "IT"
#                 }
#             }, f, indent=4)

#     with open(USERS_FILE, "r") as f:
#         return json.load(f)

# def save_users(users):
#     with open(USERS_FILE, "w") as f:
#         json.dump(users, f, indent=4)

# users = load_users()

# # 1. CSS to fix the alignment and pin the bar to the bottom!
# hide_st_style = """
#             <style>
#             footer {visibility: hidden;}
            
#             /* Un-clip the main container so sticky positioning works */
#             .main .block-container {
#                 overflow: visible !important;
#                 padding-bottom: 100px !important; 
#                 padding-top: 1.5rem;
#             }
#             div[data-testid="InputInstructions"] {display: none;}
            
#             /* FIX: Changed negative margin to positive to prevent table overlap! */
#             [data-testid="stDataFrame"] {margin-bottom: 1rem !important;}
            
#             div[data-testid="column"]:nth-of-type(3) {display: flex; justify-content: flex-end;}
            
#             /* FORCE HORIZONTAL ALIGNMENT (MAKES THEM EVEN) */
#             div[data-testid="stHorizontalBlock"] {
#                 align-items: center !important; 
#             }
            
#             /* NUDGE THE POPUP BUTTON TO BE PERFECTLY FLUSH WITH THE TEXT BOX */
#             div[data-testid="stPopover"] > button {
#                 height: 42px !important;
#                 margin-top: 4px !important; 
#                 border-radius: 8px !important;
#             }
            
#             /* PIN THE ENTIRE INPUT ROW TO THE BOTTOM OF THE SCREEN */
#             div[data-testid="stHorizontalBlock"]:has(div[data-testid="stChatInput"]) {
#                 position: sticky !important;
#                 bottom: 0px !important;
#                 background-color: var(--background-color, white) !important;
#                 z-index: 999 !important;
#                 padding-bottom: 25px !important;
#                 padding-top: 10px !important;
#             }
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)

# # 2. STATE INITIALIZATION & CALLBACKS
# if "logged_in" not in st.session_state: st.session_state.logged_in = False
# if "current_session_id" not in st.session_state: st.session_state.current_session_id = None
# if "show_flash_dashboard" not in st.session_state:
#     st.session_state.show_flash_dashboard = False
# if "dashboard_popup_shown" not in st.session_state:
#     st.session_state.dashboard_popup_shown = False
# if "current_user" not in st.session_state: st.session_state.current_user = "User"
# if "current_department" not in st.session_state: st.session_state.current_department = ""
# if "current_email" not in st.session_state: st.session_state.current_email = ""
# if "chats" not in st.session_state: st.session_state.chats = {"New Chat": []}
# if "current_chat" not in st.session_state: st.session_state.current_chat = "New Chat"
# if "pinned_chats" not in st.session_state: st.session_state.pinned_chats = []
# if "stop_gen" not in st.session_state: st.session_state.stop_gen = False


# if cookies.get("logged_in") == "true":
#     st.session_state.logged_in = True
#     st.session_state.current_email = cookies.get("email", "")
#     st.session_state.current_user = cookies.get("name", "")
#     st.session_state.current_department = cookies.get("department", "")
#     st.session_state.show_flash_dashboard = True

# def stop_generation():
#     """Callback to instantly flip the stop switch AND save the warning message."""
#     st.session_state.stop_gen = True
#     st.session_state.chats[st.session_state.current_chat].append({
#         "role": "assistant",
#         "content": "⚠️ This response was stopped."
#     })

# # 3. HELPER FUNCTIONS
# def validate_email(email_str):
#     return email_str.strip().lower().endswith("@adityabirla.com")

# def validate_password_complexity(password_str):
#     if len(password_str) < 8:
#         return False
#     if not any(char.isdigit() for char in password_str):
#         return False
#     if not any(char.isalpha() for char in password_str):
#         return False
#     return True

# def generate_chat_title(prompt):
#     stopwords = ["can", "you", "show", "me", "the", "a", "an", "is", "what", "how", "give", "tell", "about", "load", "get", "pull", "list", "all"]
#     words = re.findall(r'\b\w+\b', prompt)
#     meaningful_words = [w.capitalize() for w in words if w.lower() not in stopwords]
#     if not meaningful_words:
#         meaningful_words = [w.capitalize() for w in words[:3]]
#     title = " ".join(meaningful_words[:4])
#     return title if title else "Untitled Chat"

# @st.cache_data
# def convert_df_to_csv(df):
#     return df.to_csv(index=False).encode('utf-8')

# @st.cache_data
# def convert_df_to_tsv(df):
#     return df.to_csv(index=False, sep='\t')

# @st.dialog("Rename Chat")
# def rename_dialog(chat_name):
#     with st.form(key=f"rename_form_{chat_name}", border=False):
#         new_name = st.text_input("Enter new name:", value=chat_name)
#         submitted = st.form_submit_button("Save", type="primary", use_container_width=True)
#         if submitted:
#             if new_name and new_name != chat_name and new_name not in st.session_state.chats:
#                 updated_history = {}
#                 for k, v in st.session_state.chats.items():
#                     if k == chat_name:
#                         updated_history[new_name] = v
#                     else:
#                         updated_history[k] = v
#                 st.session_state.chats = updated_history
                
#                 if chat_name in st.session_state.pinned_chats:
#                     st.session_state.pinned_chats.remove(chat_name)
#                     st.session_state.pinned_chats.append(new_name)
#                 if st.session_state.current_chat == chat_name:
#                     st.session_state.current_chat = new_name
#                 st.rerun()
#             elif new_name == chat_name:
#                 st.rerun() 
#             else:
#                 st.error("Name is already taken.")

# @st.dialog("⚡ Flash Dashboard")
# def show_flash_dashboard():

#     import pandas as pd

#     st.subheader("Flash Dashboard")

#     conn = database.get_connection()

#     if conn:

#         st.success("Database Connected")

#         col1,col2,col3 = st.columns(3)

#         with col1:
#             st.metric("Top Region", "West")

#         with col2:
#             st.metric("Highest Selling Product", "Ultra Cement")

#         with col3:
#             st.metric("Daily Sales", "₹12,50,000")

#         st.info("Power BI Dashboard")

#         power_bi_url = "YOUR_POWERBI_URL"

#         st.components.v1.iframe(
#             power_bi_url,
#             height=600
#         )

#     else:

#         st.warning("No database found. Showing sample data.")

#         col1,col2,col3 = st.columns(3)

#         with col1:
#             st.metric("Top Region", "West India")

#         with col2:
#             st.metric("Highest Selling Product", "Ultra Cement")

#         with col3:
#             st.metric("Daily Sales", "₹12,50,000")

#         sample = pd.DataFrame({
#             "Month":["Jan","Feb","Mar","Apr","May"],
#             "Sales":[100,150,220,180,250]
#         })

#         st.line_chart(sample.set_index("Month"))

# # 4. AUTHENTICATION UI
# if not st.session_state.logged_in:
#     col1, col2, col3 = st.columns([1, 4, 1]) 
#     with col2:
#         st.markdown("<h1 style='text-align: center;'>🏢 BWGpt</h1>", unsafe_allow_html=True)
#         st.markdown("<p style='text-align: center; color: gray;'>Company Data Assistant</p>", unsafe_allow_html=True)
#         st.write("") 
        
#         tab_signin, tab_signup = st.tabs(["Sign In", "Sign Up"])
        
#         with tab_signin:
#             with st.form("signin_form", border=False):
#                 st.markdown("<h3>Welcome back</h3>", unsafe_allow_html=True)
#                 email_input = st.text_input("Corporate Email", placeholder="e.g. name@adityabirla.com")
#                 password_input = st.text_input("Password", type="password", placeholder="••••••••")
#                 st.write("") 
#                 submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
                
#                 if submitted:
#                     norm_email = email_input.strip().lower()
#                     if not email_input or not password_input:
#                         st.error("Please enter both email and password.")
#                     elif not validate_email(norm_email):
#                         st.error("Access Denied: Only @adityabirla.com emails are allowed.")
#                     elif norm_email in users and users[norm_email]["password"] == password_input:
#                         st.session_state.logged_in = True
#                         st.session_state.current_email = norm_email
#                         st.session_state.current_user = users[norm_email]["name"]
#                         st.session_state.current_department = users[norm_email]["department"]
#                         st.session_state.current_session_id = audit_logger.log_user_login(norm_email)

#                         cookies["logged_in"] = "true"
#                         cookies["email"] = norm_email
#                         cookies["name"] = users[norm_email]["name"]
#                         cookies["department"] = users[norm_email]["department"]
#                         cookies.save()

#                         st.rerun()
#                     else:
#                         st.error("Invalid email or password.")

#         with tab_signup:
#             with st.form("signup_form", border=False):
#                 st.markdown("<h3>Create Account</h3>", unsafe_allow_html=True)
#                 full_name = st.text_input("Full Name", placeholder="Enter Full Name")
#                 new_email = st.text_input("Corporate Email", placeholder="e.g. name@adityabirla.com")
#                 new_department = st.selectbox("Department", ["CASC", "Commercial", "Finance", "HR", "IT", "Logistics", "Marketing", "Non-Trade", "Sales"])
#                 new_password = st.text_input("Password", type="password", placeholder="Min 8 chars, includes letters & numbers")
#                 confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
#                 st.write("") 
#                 submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
                
#                 if submitted:
#                     norm_new_email = new_email.strip().lower()
#                     if not full_name or not new_email or not new_password:
#                         st.error("Please fill in all fields.")
#                     elif not validate_email(norm_new_email):
#                         st.error("Registration Denied: You must use a valid @adityabirla.com email address.")
#                     elif not validate_password_complexity(new_password):
#                         st.error("Weak Password: Must be at least 8 characters long and contain both letters and digits.")
#                     elif new_password != confirm_password: 
#                         st.error("Passwords do not match.")
#                     elif norm_new_email in users:
#                         st.error("An account with this email already exists. Please sign in.")
#                     else:
#                         users[norm_new_email] = {
#                             "name": full_name,
#                             "password": new_password,
#                             "department": new_department
#                         }

#                         save_users(users)

#                         st.success("Account created successfully! You can now sign in.")

# # 5. MAIN APP WORKSPACE
# else:
#     sidebar.render_sidebar(rename_dialog)
#     if st.session_state.show_flash_dashboard:
#         show_flash_dashboard()
#         st.session_state.show_flash_dashboard = False

#     st.title("🏢 BWGpt")
#     current_chat_key = st.session_state.current_chat
#     current_chat_history = st.session_state.chats[current_chat_key]
    
#     # STRUCTURAL FIX: CREATE A DEDICATED CONTAINER FOR CHAT HISTORY
#     chat_container = st.container()
    
#     with chat_container:
#         if len(current_chat_history) == 0:
#             st.markdown(f"<h1 style='text-align: center; margin-top: 10vh;'>Welcome, {st.session_state.current_user}!</h1>", unsafe_allow_html=True)
#             st.markdown("<p style='text-align: center; color: gray; font-size: 1.2rem;'>Ask me anything about your company data.</p>", unsafe_allow_html=True)

#         for i, message in enumerate(current_chat_history):
#             with st.chat_message(message["role"]):
#                 st.write(message["content"])
#                 if "data_table" in message:
#                     df = message["data_table"]
#                     st.dataframe(df)
#                     col1, spacer, col2 = st.columns([1.5, 6, 2.5])
#                     with col1:
#                         copy_text = convert_df_to_tsv(df)
#                         st_copy_button(text=copy_text, before_copy_label="📋 Copy", after_copy_label="✅ Copied!", key=f"copy_{current_chat_key}_{i}")
#                     with col2:
#                         csv = convert_df_to_csv(df)
#                         st.download_button(label="📥 Download", data=csv, file_name=f"BWGpt_Export_{i}.csv", mime="text/csv", key=f"dl_{current_chat_key}_{i}")

#     # --- SIDE-BY-SIDE CHAT INPUT & UPLOAD BAR ---
#     # This is placed at the absolute bottom of the script, so it renders at the bottom!
    
#     # Using a 1 to 12 ratio to keep the button snug against the text box
#     input_col, chat_col = st.columns([1, 12], vertical_alignment="center")
    
#     with input_col:
#         with st.popover("➕", help="Attach Context Files"):
#             uploaded_files = st.file_uploader(
#                 "Upload files",
#                 type=["pdf", "xlsx", "docx", "xls", "doc"],
#                 accept_multiple_files=True,
#                 label_visibility="collapsed",
#                 key="chat_file_uploader"
#             )
#             if uploaded_files:
#                 st.success(f"✅ {len(uploaded_files)} file(s)")

#     with chat_col:
#         user_prompt = st.chat_input("E.g., What is the total budget for IT?")

#     # --- HANDLE PROMPT LOGIC ---
#     if user_prompt:
        
#         if current_chat_key.startswith("New Chat"):
#             new_title = generate_chat_title(user_prompt)
#             base_title = new_title
#             counter = 1
#             while new_title in st.session_state.chats:
#                 new_title = f"{base_title} ({counter})"
#                 counter += 1
            
#             updated_chats = {new_title: st.session_state.chats.pop(current_chat_key)}
#             updated_chats.update(st.session_state.chats)
#             st.session_state.chats = updated_chats
#             st.session_state.current_chat = new_title
#             current_chat_key = new_title 

#         # Save to state
#         st.session_state.chats[current_chat_key].append({"role": "user", "content": user_prompt})
        
#         # STRUCTURAL FIX: Render the AI response INSIDE the chat_container
#         # This guarantees it renders ABOVE the text bar!
#         with chat_container:
#             with st.chat_message("user"):
#                 st.write(user_prompt)
                
#             with st.chat_message("assistant"):
#                 conn = database.get_connection()
#                 if conn:
#                     try:
#                         db_schema = database.get_schema()
                        
#                         stop_button_placeholder = st.empty()
#                         response_placeholder = st.empty()
                        
#                         st.session_state.stop_gen = False
                        
#                         stop_button_placeholder.button("⏹ Stop Generation", type="primary", on_click=stop_generation, key="interrupt_trigger")
                        
#                         full_response_text = ""
#                         interrupted = False
                        
#                         for token in llm.stream_sql(user_prompt, db_schema):
#                             if st.session_state.stop_gen:
#                                 interrupted = True
#                                 break
                            
#                             full_response_text += token
#                             response_placeholder.code(full_response_text, language="sql")
                        
#                         stop_button_placeholder.empty()
                        
#                         if interrupted:
#                             # Display the interrupted message inline
#                             response_placeholder.warning("⚠️ This response was stopped.")
#                             st.session_state.stop_gen = False
                            
#                         else:
#                             clean_sql = re.sub(r'```sql', '', full_response_text, flags=re.IGNORECASE)
#                             clean_sql = re.sub(r'```', '', clean_sql).strip()
                            
#                             response_placeholder.empty()
#                             st.write("Here is the query I generated and ran:")
#                             st.code(clean_sql, language="sql")
#                             audit_logger.log_chat_query(
#                             login_id=st.session_state.current_email, 
#                              user_prompt=user_prompt, 
#                             generated_sql=clean_sql
#                             )
                            
#                             df = database.execute_query(clean_sql, conn)
#                             st.dataframe(df)
                            
#                             col1, spacer, col2 = st.columns([1.5, 6, 2.5])
#                             with col1:
#                                 copy_text = convert_df_to_tsv(df)
#                                 st_copy_button(text=copy_text, before_copy_label="📋 Copy", after_copy_label="✅ Copied!", key="copy_fresh_query")
#                             with col2:
#                                 csv = convert_df_to_csv(df)
#                                 st.download_button(label="📥 Download", data=csv, file_name="BWGpt_Export.csv", mime="text/csv", key="dl_fresh_query")
                            
#                             st.session_state.chats[current_chat_key].append({
#                                 "role": "assistant", 
#                                 "content": f"Here is the query I generated and ran:\n```sql\n{clean_sql}\n```",
#                                 "data_table": df
#                             })
                            
#                     except Exception as e:
#                         error_msg = f"Sorry, I encountered an error: {e}"
#                         st.error(error_msg)
#                         st.session_state.chats[current_chat_key].append({"role": "assistant", "content": error_msg})
#                 else:
#                     st.error("No database connection available.")
#                     st.session_state.chats[current_chat_key].append({"role": "assistant", "content": "No database connection available."})
                
#         # Force a rerun to clean up state
#         st.rerun()

import streamlit as st
import pandas as pd
import re
import json
import os
from st_copy_button import st_copy_button
from streamlit_cookies_manager import EncryptedCookieManager

import database
import llm
import sidebar
import audit_logger

# 1. PAGE SETUP & MAGIC CSS
st.set_page_config(
    page_title="BWGpt", 
    page_icon="🏢", 
    layout="centered",
    initial_sidebar_state="expanded" 
)

cookies = EncryptedCookieManager(
    prefix="bwgpt_",
    password="your-secret-key"
)

if not cookies.ready():
    st.stop()

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({
                "admin@adityabirla.com": {
                    "name": "Admin User",
                    "password": "Password123",
                    "department": "IT"
                }
            }, f, indent=4)

    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

# 1. CSS to fix the alignment and pin the bar to the bottom!
hide_st_style = """
            <style>
            footer {visibility: hidden;}
            
            /* Un-clip the main container so sticky positioning works */
            .main .block-container {
                overflow: visible !important;
                padding-bottom: 100px !important; 
                padding-top: 1.5rem;
            }
            div[data-testid="InputInstructions"] {display: none;}
            
            /* FIX: Changed negative margin to positive to prevent table overlap! */
            [data-testid="stDataFrame"] {margin-bottom: 1rem !important;}
            
            div[data-testid="column"]:nth-of-type(3) {display: flex; justify-content: flex-end;}
            
            /* FORCE HORIZONTAL ALIGNMENT (MAKES THEM EVEN) */
            div[data-testid="stHorizontalBlock"] {
                align-items: center !important; 
            }
            
            /* NUDGE THE POPUP BUTTON TO BE PERFECTLY FLUSH WITH THE TEXT BOX */
            div[data-testid="stPopover"] > button {
                height: 42px !important;
                margin-top: 4px !important; 
                border-radius: 8px !important;
            }
            
            /* PIN THE ENTIRE INPUT ROW TO THE BOTTOM OF THE SCREEN */
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stChatInput"]) {
                position: sticky !important;
                bottom: 0px !important;
                background-color: var(--background-color, white) !important;
                z-index: 999 !important;
                padding-bottom: 25px !important;
                padding-top: 10px !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. STATE INITIALIZATION & CALLBACKS
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_session_id" not in st.session_state: st.session_state.current_session_id = None
if "show_flash_dashboard" not in st.session_state:
    st.session_state.show_flash_dashboard = False
if "dashboard_popup_shown" not in st.session_state:
    st.session_state.dashboard_popup_shown = False
if "current_user" not in st.session_state: st.session_state.current_user = "User"
if "current_department" not in st.session_state: st.session_state.current_department = ""
if "current_email" not in st.session_state: st.session_state.current_email = ""
if "chats" not in st.session_state: st.session_state.chats = {"New Chat": []}
if "current_chat" not in st.session_state: st.session_state.current_chat = "New Chat"
if "pinned_chats" not in st.session_state: st.session_state.pinned_chats = []
if "stop_gen" not in st.session_state: st.session_state.stop_gen = False


if cookies.get("logged_in") == "true" and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.current_email = cookies.get("email", "")
    st.session_state.current_user = cookies.get("name", "")
    st.session_state.current_department = cookies.get("department", "")
    st.session_state.show_flash_dashboard = True

def stop_generation():
    """Callback to instantly flip the stop switch AND save the warning message."""
    st.session_state.stop_gen = True
    st.session_state.chats[st.session_state.current_chat].append({
        "role": "assistant",
        "content": "⚠️ This response was stopped."
    })

def logout():
    """Clears session state and cookies to fully log the user out."""
    # Clear cookies
    cookies["logged_in"] = "false"
    cookies["email"] = ""
    cookies["name"] = ""
    cookies["department"] = ""
    cookies.save()

    # Clear session state
    st.session_state.logged_in = False
    st.session_state.current_user = "User"
    st.session_state.current_email = ""
    st.session_state.current_department = ""
    st.session_state.current_session_id = None
    st.session_state.show_flash_dashboard = False
    st.session_state.dashboard_popup_shown = False
    st.session_state.chats = {"New Chat": []}
    st.session_state.current_chat = "New Chat"
    st.session_state.pinned_chats = []
    st.session_state.stop_gen = False
    st.rerun()

# 3. HELPER FUNCTIONS
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

@st.dialog("⚡ Flash Dashboard")
def show_flash_dashboard():

    import pandas as pd

    st.subheader("Flash Dashboard")

    conn = database.get_connection()

    if conn:

        st.success("Database Connected")

        col1,col2,col3 = st.columns(3)

        with col1:
            st.metric("Top Region", "West")

        with col2:
            st.metric("Highest Selling Product", "Ultra Cement")

        with col3:
            st.metric("Daily Sales", "₹12,50,000")

        st.info("Power BI Dashboard")

        power_bi_url = "YOUR_POWERBI_URL"

        st.components.v1.iframe(
            power_bi_url,
            height=600
        )

    else:

        st.warning("No database found. Showing sample data.")

        col1,col2,col3 = st.columns(3)

        with col1:
            st.metric("Top Region", "West India")

        with col2:
            st.metric("Highest Selling Product", "Ultra Cement")

        with col3:
            st.metric("Daily Sales", "₹12,50,000")

        sample = pd.DataFrame({
            "Month":["Jan","Feb","Mar","Apr","May"],
            "Sales":[100,150,220,180,250]
        })

        st.line_chart(sample.set_index("Month"))

# 4. AUTHENTICATION UI
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
                    elif norm_email in users and users[norm_email]["password"] == password_input:
                        st.session_state.logged_in = True
                        st.session_state.current_email = norm_email
                        st.session_state.current_user = users[norm_email]["name"]
                        st.session_state.current_department = users[norm_email]["department"]
                        st.session_state.current_session_id = audit_logger.log_user_login(norm_email)

                        cookies["logged_in"] = "true"
                        cookies["email"] = norm_email
                        cookies["name"] = users[norm_email]["name"]
                        cookies["department"] = users[norm_email]["department"]
                        cookies.save()

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
                    elif norm_new_email in users:
                        st.error("An account with this email already exists. Please sign in.")
                    else:
                        users[norm_new_email] = {
                            "name": full_name,
                            "password": new_password,
                            "department": new_department
                        }

                        save_users(users)

                        st.success("Account created successfully! You can now sign in.")

# 5. MAIN APP WORKSPACE
else:
    sidebar.render_sidebar(rename_dialog, cookies)
    if st.session_state.show_flash_dashboard:
        show_flash_dashboard()
        st.session_state.show_flash_dashboard = False

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
    # This is placed at the absolute bottom of the script, so it renders at the bottom!
    
    # Using a 1 to 12 ratio to keep the button snug against the text box
    input_col, chat_col = st.columns([1, 12], vertical_alignment="center")
    
    with input_col:
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

    with chat_col:
        user_prompt = st.chat_input("E.g., What is the total budget for IT?")

    # --- HANDLE PROMPT LOGIC ---
    if user_prompt:
        
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
        
        # STRUCTURAL FIX: Render the AI response INSIDE the chat_container
        # This guarantees it renders ABOVE the text bar!
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
                            # Display the interrupted message inline
                            response_placeholder.warning("⚠️ This response was stopped.")
                            st.session_state.stop_gen = False
                            
                        else:
                            clean_sql = re.sub(r'```sql', '', full_response_text, flags=re.IGNORECASE)
                            clean_sql = re.sub(r'```', '', clean_sql).strip()
                            
                            response_placeholder.empty()
                            st.write("Here is the query I generated and ran:")
                            st.code(clean_sql, language="sql")
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
                            
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {e}"
                        st.error(error_msg)
                        st.session_state.chats[current_chat_key].append({"role": "assistant", "content": error_msg})
                else:
                    st.error("No database connection available.")
                    st.session_state.chats[current_chat_key].append({"role": "assistant", "content": "No database connection available."})
                
        # Force a rerun to clean up state
        st.rerun()