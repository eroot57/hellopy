import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Hello App",
    page_icon="👋",
    layout="centered"
)

# Display the hello message
st.title("Hello")

# Optional: Add some styling or additional content
st.markdown("---")
st.write("Welcome to this simple Streamlit app!")

# Optional: Add some interactivity
if st.button("Click me!"):
    st.balloons()
    st.success("Hello there! 👋")
