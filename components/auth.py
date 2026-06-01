# components/auth.py
import streamlit as st
import audit_logger
from utils.helpers import validate_email, validate_password_complexity

def render_auth_ui():
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