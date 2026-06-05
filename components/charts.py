import streamlit as st
import plotly.express as px

def render_custom_chart(df, chart_config):
    """Draws a native Streamlit chart based on AI JSON config."""
    chart_type = chart_config.get("type", "bar")
    x_col = chart_config.get("x")
    y_col = chart_config.get("y")
    
    st.markdown("### 📊 ad-hoc data visualization")
    
    try:
        if chart_type == "bar":
            st.bar_chart(df, x=x_col, y=y_col)
        elif chart_type == "line":
            st.line_chart(df, x=x_col, y=y_col)
        elif chart_type == "scatter":
            st.scatter_chart(df, x=x_col, y=y_col)
        elif chart_type == "pie":
            # using plotly for pie charts since streamlit doesn't have st.pie_chart
            fig = px.pie(df, values=y_col, names=x_col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"chart type '{chart_type}' is not supported yet.")
    except Exception as e:
        st.error("Could not draw the requested chart. please check if the column names match the data.")