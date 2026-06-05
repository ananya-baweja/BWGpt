import re
import streamlit as st
import urllib.parse

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


def generate_outlook_link(recipient_email, subject, email_body):
    """
    Generates a safe mailto URL that automatically opens in the user's 
    desktop Outlook client with pre-filled fields.
    """
    # Safe encoding for spaces, newlines, and special characters
    params = {
        "subject": subject,
        "body": email_body
    }
    encoded_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    
    # Construct the final mailto string
    mailto_url = f"mailto:{recipient_email}?{encoded_params}"
    return mailto_url