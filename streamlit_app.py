import streamlit as st
import pandas as pd
import numpy as np

# Page configuration for a better look
st.set_page_config(
    page_title="My New App",
    page_icon="🎈",
    layout="wide"
)

st.title("🎈 My New App")
st.markdown(
    """
    Welcome! This is a **starter template** to help you get up and running. 
    Below you'll find examples of layout columns, interactive widgets, and data visualization.
    """
)

st.divider()

# Create two columns for a dynamic layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("💡 User Interaction")
    st.write("Try entering your name and clicking the button used below.")
    
    name = st.text_input("What is your name?", "Explorer")
    
    if st.button("Celebrate!", type="primary", use_container_width=True):
        st.balloons()
        st.toast(f"Welcome aboard, {name}!", icon="🎉")
        st.success(f"Hello, **{name}**! You've successfully interacted with the app.")

with col2:
    st.subheader("📊 Live Data Demo")
    st.write("Here's a simple random data chart generated on the fly.")
    
    # Generate sample data
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=["A", "B", "C"]
    )
    
    st.area_chart(chart_data, color=["#FF4B4B", "#1C83E1", "#FFA421"])

st.divider()
st.caption("🚀 Built with Streamlit • Edit `streamlit_app.py` to see changes instantly.")
