import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

def render_powerbi(filter_string=""):
    """
    Renders the Power BI dashboard inside an iframe.
    Accepts an optional URL filter string from the AI router.
    """
    base_url = "https://app.powerbi.com/view?r=eyJrIjoiMzU1MmRlODUtYjQ1ZC00YjdjLThkMWYtYzU4MTAzMTFhODVjIiwidCI6ImY4N2E1ZjVlLWY5N2UtNGFlYy1iYWI4LTZlNDE4N2VmNGYxYyIsImMiOjEwfQ%3D%3D"
    
    if filter_string:
        # Encode the filter string to safely handle spaces and special characters
        safe_filter = urllib.parse.quote(filter_string)
        
        # Check if the base URL already has parameters to determine if we need a ? or &
        connector = "&" if "?" in base_url else "?"
        
        embed_url = f"{base_url}{connector}$filter={safe_filter}"
    else:
        embed_url = base_url
        
    # Display the iframe
    components.iframe(embed_url, height=650, scrolling=True)