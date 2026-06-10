import streamlit as st
import urllib.parse

def render_powerbi(filter_string=""):
    """
    Render the Power BI dashboard.
    Optionally accepts a Power BI filter string.
    """

    try:
        base_url = st.secrets["POWERBI_URL"]

    except KeyError:
        st.error(
            "Power BI URL not found in .streamlit/secrets.toml"
        )
        return

    if filter_string:
        safe_filter = urllib.parse.quote(filter_string)

        connector = "&" if "?" in base_url else "?"

        embed_url = (
            f"{base_url}{connector}$filter={safe_filter}"
        )
    else:
        embed_url = base_url

    st.iframe(
        embed_url,
        height=650,
    )