import streamlit as st
from st_copy_button import st_copy_button

st.subheader("Copy to Clipboard Component Demo")

# Basic Example
st.write("### Basic Example")
text = st.text_input("Enter text to copy", value="Hello World")
copied = st_copy_button(text, key="basic")
st.write(f"Text copied: {copied}")

# Custom Labels
st.write("### Custom Labels")
copied_custom = st_copy_button(
    text,
    before_copy_label="📋 Push to copy",
    after_copy_label="✅ Text copied!",
    key="custom",
)
st.write(f"Text copied: {copied_custom}")

# With Visible Text
st.write("### With Visible Text")
copied_visible = st_copy_button(text, show_text=True, key="visible")
st.write(f"Text copied: {copied_visible}")
