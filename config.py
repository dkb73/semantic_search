import streamlit as st

# Read secrets from Streamlit deployment settings
MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = st.secrets["DB_NAME"]
COLLECTION_NAME = st.secrets["COLLECTION_NAME"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
