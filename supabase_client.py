import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    """Initialize and return a Supabase client using Streamlit secrets or env vars."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except (FileNotFoundError, KeyError):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
    if not url or not key:
        st.error("Missing Supabase credentials. Please add them to .streamlit/secrets.toml or .env")
        st.stop()
        
    return create_client(url, key)
