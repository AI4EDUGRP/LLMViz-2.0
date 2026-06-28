import os
import json
import base64
import html
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import streamlit as st
from streamlit_option_menu import option_menu
from lida import Manager, TextGenerationConfig, llm
from openai import OpenAI
from database import get_db
from auth import initialize_data_structure
from analytics import log_interaction, finalize_session
from chat_storage import (
    save_chat_message, save_generated_image, save_dataset_summary,
    get_chat_history, get_session_statistics, save_chart_refinement
)
from chart_generation import UploadedDatasetError, build_fast_chart_goal, load_dataset_csv
from design_system import inject_design_system
import time

# --------------------- Environment Setup ---------------------
img = Image.open('imggg.png')
st.set_page_config(initial_sidebar_state="expanded", layout="wide", page_title="VisualStats", page_icon=img)

load_dotenv()
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("Missing OpenAI API Key. Please set OPENAI_API_KEY in your environment.")
    st.stop()
    
# Many third-party libraries (like LIDA) rely on this being in os.environ
os.environ["OPENAI_API_KEY"] = API_KEY


inject_design_system()


# Professional Styling


# Initialize clients
client = OpenAI(api_key=API_KEY)
import tempfile
import os
os.environ["LOCALAPPDATA"] = os.path.join(tempfile.gettempdir(), "lida_appdata")
lida = Manager(text_gen=llm("openai"))
textgen_config = TextGenerationConfig(n=1, temperature=0.2, model="gpt-4o", use_cache=True)
validated = ""

# --------------------- Authentication Check ---------------------
initialize_data_structure()

# Development Auth Persistence (prevents needing to login after every Ctrl+F5)
import json
import os
DEV_SESSION_FILE = ".dev_session.json"

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
    
    # Try to load from persistent dev session
    if os.path.exists(DEV_SESSION_FILE):
        try:
            with open(DEV_SESSION_FILE, "r") as f:
                saved_session = json.load(f)
                st.session_state.is_authenticated = saved_session.get("is_authenticated", False)
                if "user" in saved_session:
                    st.session_state.user = saved_session["user"]
                if "role" in saved_session:
                    st.session_state.role = saved_session["role"]
                if "user_id" in saved_session:
                    st.session_state.user_id = saved_session["user_id"]
        except Exception:
            pass

# Helper to save session when user logs in (called in auth logic)
def save_dev_session():
    try:
        with open(DEV_SESSION_FILE, "w") as f:
            json.dump({
                "is_authenticated": st.session_state.get("is_authenticated", False),
                "user": st.session_state.get("user"),
                "role": st.session_state.get("role"),
                "user_id": st.session_state.get("user_id"),
            }, f)
    except Exception:
        pass

# Smooth dark-to-light transition overlay to prevent white flash after login
if st.session_state.is_authenticated:
    st.markdown("""
    <style>
        .page-transition-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            background: #F8FAFC;
            z-index: 999999;
            pointer-events: none;
            animation: fadeOutOverlay 0.6s ease-out forwards;
        }
        @keyframes fadeOutOverlay {
            0% { opacity: 1; }
            100% { opacity: 0; }
        }
    </style>
    <div class="page-transition-overlay"></div>
    """, unsafe_allow_html=True)

if not st.session_state.is_authenticated:
    # Hide Streamlit UI to make it full screen
    st.markdown("""
    <style>
        header {display:none !important;}
        .stSidebar {display:none !important;}
        [data-testid="stSidebar"] {display:none !important;}
        [data-testid="stHeader"] {display:none !important;}
        /* Hide the 'Running...' status widget */
        [data-testid="stStatusWidget"] {display:none !important;}
        /* Hide any Streamlit loading spinners */
        .stSpinner {display:none !important;}
        .stApp {background-color: black !important;}
        .stMainBlockContainer {padding: 0 !important; max-width: 100% !important;}
        /* Ensure the iframe is full screen */
        iframe {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 999999 !important;
            border: none !important;
            background-color: transparent !important;
            /* Prevent Streamlit from applying opacity or grayscale filters during load */
            opacity: 1 !important;
            filter: none !important;
        }
        /* Hide Streamlit's translucent layover div that is placed over components while running */
        iframe + div {
            display: none !important;
            opacity: 0 !important;
            background: transparent !important;
        }
        /* Hide any element with stComponentLoading */
        [data-testid="stComponentLoading"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    from magic_wrapper import render_magic_auth
    auth_data = render_magic_auth(key="magic_auth", error_message=st.session_state.get("auth_error", None))
    
    # Clear error after displaying once
    if "auth_error" in st.session_state:
        del st.session_state["auth_error"]
    
    if auth_data:
        timestamp = auth_data.get("timestamp")
        last_timestamp = st.session_state.get("last_auth_timestamp")
        
        if timestamp and timestamp != last_timestamp:
            st.session_state.last_auth_timestamp = timestamp
            action = auth_data.get("action")
            username = auth_data.get("username", "")
            pin = auth_data.get("pin", "")
            master_code = auth_data.get("master_code", "")
            is_admin = auth_data.get("is_admin", False)
            
            from auth import authenticate_user, create_session, create_guest_user, login_admin, register_admin
            
            if action == "guest":
                guest_user = create_guest_user()
                st.session_state.is_authenticated = True
                st.session_state.user_info = guest_user
                st.session_state.user_id = guest_user.get("user_id")
                st.session_state.username = guest_user.get("username")
                st.session_state.role = guest_user.get("role", "guest")
                st.session_state.session_token = create_session(st.session_state.user_id, guest_user.get("username"), "guest")
                st.session_state.auth_message = "Logged in as Guest. Your session data will not be permanently saved. 🕵️‍♂️"
                st.rerun()
                
            elif action == "login":
                if not username or not pin or len(pin) != 4 or not pin.isdigit():
                    st.session_state.auth_error = "Please enter a username and a valid 4-digit PIN."
                    st.rerun()
                elif is_admin:
                    if not master_code:
                        st.session_state.auth_error = "Master code is required to login as Admin."
                        st.rerun()
                    else:
                        result = login_admin(username, pin, master_code)
                        if isinstance(result, str):
                            st.session_state.auth_error = result
                            st.rerun()
                        else:
                            st.session_state.is_authenticated = True
                            st.session_state.user_info = result
                            st.session_state.user_id = result.get("user_id")
                            st.session_state.username = result.get("username")
                            st.session_state.role = "admin"
                            st.session_state.session_token = create_session(st.session_state.user_id, result.get("username"), "admin")
                            st.session_state.auth_message = f"Welcome back, Admin {result.get('username')}! 🛡️"
                            save_dev_session()
                            st.rerun()
                else:
                    result = authenticate_user(username, pin)
                    if isinstance(result, str):
                        st.session_state.auth_error = result
                        st.rerun()
                    else:
                        st.session_state.is_authenticated = True
                        st.session_state.user_info = result
                        st.session_state.user_id = result.get("user_id", "unknown")
                        st.session_state.username = result.get("username", "unknown")
                        st.session_state.role = result.get("role", "user")
                        st.session_state.session_token = create_session(st.session_state.user_id, result.get("username", "unknown"), st.session_state.role)
                        if result.get("is_new"):
                            st.session_state.auth_message = f"Welcome! Account newly created for {result.get('username')}. 🎉"
                        else:
                            st.session_state.auth_message = f"Welcome back, {result.get('username')}! 👋"
                        save_dev_session()
                        st.rerun()
                        
            elif action == "register":
                if not is_admin:
                    pass
                else:
                    if not username or not pin or len(pin) != 4 or not pin.isdigit():
                        st.session_state.auth_error = "Please enter a username and a valid 4-digit PIN."
                        st.rerun()
                    elif not master_code:
                        st.session_state.auth_error = "Master code is required to register an admin."
                        st.rerun()
                    else:
                        result = register_admin(username, pin, master_code)
                        if result is None:
                            st.session_state.auth_error = "Registration failed. Invalid master code or username already taken."
                            st.rerun()
                        else:
                            st.success("Admin registered successfully! Logging in...")
                            st.session_state.is_authenticated = True
                            st.session_state.user_info = result
                            st.session_state.user_id = result.get("admin_id")
                            st.session_state.username = result.get("admin_username")
                            st.session_state.role = "admin"
                            st.session_state.session_token = create_session(st.session_state.user_id, result.get("admin_username"), "admin")
                            st.session_state.auth_message = f"Admin account '{result.get('admin_username')}' created. Welcome to the dashboard! 🛡️"
                            save_dev_session()
                            st.rerun()

    st.stop()
    
# Show success toast from login if exists
if "auth_message" in st.session_state:
    st.toast(st.session_state.auth_message, icon="✅")
    del st.session_state.auth_message

# --------------------- Database Initialization ---------------------
db = get_db()


def go_to_menu(label: str, index: int):
    """Programmatically switch Streamlit's option menu on the next rerun."""
    st.session_state.menu_choice = label
    st.session_state.force_menu_index = index
    st.rerun()


def handle_nav_event(nav_event):
    """Handle navigation events emitted from React components."""
    if not nav_event:
        return

    action = nav_event.get("action")
    target = nav_event.get("target")
    timestamp = nav_event.get("timestamp")
    last_ts = st.session_state.get("last_nav_timestamp")

    if not timestamp or timestamp == last_ts:
        return

    st.session_state.last_nav_timestamp = timestamp
    if action == "logout":
        perform_logout()
    elif action == "navigate" and target == "home":
        go_to_menu("Home", 0)
    elif action == "navigate" and target == "viz_generator":
        go_to_menu("Viz Generator", 1)
    elif action == "navigate" and target == "viz_evaluator":
        go_to_menu("Viz Evaluator", 2)
    elif action == "navigate" and target == "analytics_dashboard":
        go_to_menu("Analytics Dashboard", 3)


def perform_logout():
    """End the auth session and return to the login screen."""
    from auth import end_session

    if st.session_state.get("session_id"):
        finalize_session(
            st.session_state.get("user_id") or st.session_state.get("admin_id"),
            st.session_state.session_id,
        )
    if st.session_state.get("session_token"):
        end_session(st.session_state.session_token)
    st.session_state.clear()
    if os.path.exists(DEV_SESSION_FILE):
        try:
            os.remove(DEV_SESSION_FILE)
        except OSError:
            pass
    st.success("Logged out successfully!")
    time.sleep(1)
    st.rerun()


def render_page_actions(active="home"):
    """Dashboard-style top navigation shown on tool pages."""
    import importlib
    import magic_wrapper

    magic_wrapper = importlib.reload(magic_wrapper)

    nav_event = magic_wrapper.render_magic_page_nav(
        active=active,
        is_admin=st.session_state.get("role") == "admin",
        key=f"page_nav_{active}",
    )
    handle_nav_event(nav_event)


def inject_magic_page_styles(page_type: str):
    """Premium SynthAI-inspired styling for Streamlit-native widgets on tool pages."""
    accent = {
        "generator": "#6d5bd0",
        "evaluator": "#5b8c5a",
        "analytics": "#6d5bd0",
    }.get(page_type, "#6d5bd0")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: #fbfbfa !important;
            overflow-x: hidden !important;
        }}
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {{
            display: none !important;
        }}
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .stMain {{
            width: 100% !important;
            max-width: 100vw !important;
            margin: 0 !important;
            background: #fbfbfa !important;
            overflow-x: hidden !important;
        }}
        [data-testid="stAppViewContainer"] > section.main {{
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .stMainBlockContainer {{
            max-width: 100% !important;
            width: 100% !important;
            padding-top: 0.5rem !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            padding-bottom: 1.5rem !important;
        }}
        iframe[title="magic_hub.magic_hub"] {{
            width: 100% !important;
            max-width: 100% !important;
            border: none !important;
            display: block !important;
            overflow: hidden !important;
        }}
        div[data-testid="stCustomComponentV1"] {{
            width: 100% !important;
            max-width: 100% !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [data-testid="stVerticalBlock"] {{
            gap: 0.65rem !important;
        }}
        .stMainBlockContainer > div > div:not([data-testid="stCustomComponentV1"]) {{
            padding-left: clamp(1.5rem, 6vw, 5rem) !important;
            padding-right: clamp(1.5rem, 6vw, 5rem) !important;
        }}

        /* Top page action buttons */
        .stButton > button {{
            border-radius: 14px !important;
            border: 1px solid rgba(17, 24, 39, 0.10) !important;
            background: rgba(255, 255, 255, 0.88) !important;
            color: #111827 !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            box-shadow: 0 10px 32px rgba(17, 24, 39, 0.06) !important;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease !important;
        }}
        .stButton > button:hover {{
            transform: translateY(-1px) !important;
            border-color: {accent}55 !important;
            box-shadow: 0 16px 42px rgba(17, 24, 39, 0.10) !important;
        }}
        .stFormSubmitButton > button,
        .stDownloadButton > button {{
            border-radius: 14px !important;
            border: 1px solid rgba(17, 24, 39, 0.10) !important;
            box-shadow: 0 10px 32px rgba(17, 24, 39, 0.06) !important;
            font-weight: 700 !important;
        }}
        .stFormSubmitButton > button[kind="primary"],
        .stButton > button[kind="primary"] {{
            background: #111827 !important;
            color: white !important;
            border-color: #111827 !important;
        }}

        /* Uploaders */
        [data-testid="stFileUploader"] {{
            border-radius: 22px !important;
            border: 1px solid rgba(17, 24, 39, 0.06) !important;
            background:
              radial-gradient(360px 160px at 90% 0%, {accent}22, transparent 70%),
              rgba(255, 255, 255, 0.88) !important;
            padding: 0.65rem !important;
            box-shadow: 0 12px 36px rgba(80, 70, 160, 0.07) !important;
        }}
        [data-testid="stFileUploaderDropzone"] {{
            border: 1.5px dashed {accent}66 !important;
            border-radius: 18px !important;
            background: rgba(255, 255, 255, 0.72) !important;
            padding: 0.9rem !important;
        }}
        [data-testid="stFileUploaderDropzone"] button {{
            border-radius: 12px !important;
            background: #111827 !important;
            color: white !important;
        }}

        /* Chat and forms */
        [data-testid="stChatMessage"] {{
            border-radius: 18px !important;
            border: 1px solid rgba(17, 24, 39, 0.06) !important;
            background: rgba(255,255,255,0.84) !important;
            box-shadow: 0 10px 30px rgba(17, 24, 39, 0.04) !important;
            padding: .4rem .7rem !important;
            margin-bottom: .45rem !important;
        }}
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
            color: #374151 !important;
            font-size: .94rem !important;
            line-height: 1.55 !important;
        }}
        [data-testid="stForm"] {{
            border-radius: 20px !important;
            border: 1px solid rgba(17, 24, 39, 0.06) !important;
            background: rgba(255, 255, 255, 0.82) !important;
            box-shadow: 0 14px 42px rgba(17, 24, 39, 0.05) !important;
            padding: .75rem !important;
        }}
        .stTextInput input,
        textarea {{
            border-radius: 16px !important;
            border: 1px solid rgba(17, 24, 39, 0.10) !important;
            background: rgba(255, 255, 255, 0.92) !important;
            min-height: 46px !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.7) !important;
        }}
        .stTextInput input:focus,
        textarea:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 4px {accent}22 !important;
        }}

        /* Cards, expanders, generated chart output */
        .ds-card,
        [data-testid="stExpander"] {{
            border-radius: 20px !important;
            border: 1px solid rgba(17, 24, 39, 0.06) !important;
            background: rgba(255, 255, 255, 0.88) !important;
            box-shadow: 0 18px 55px rgba(80, 70, 160, 0.08) !important;
        }}
        .viz-output-pane {{
            position: sticky;
            top: 0.75rem;
        }}
        .assistant-workspace {{
            margin-top: 0.85rem;
            padding: 1rem;
            border-radius: 24px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background:
              radial-gradient(520px 220px at 88% 0%, {accent}18, transparent 70%),
              rgba(255, 255, 255, 0.76);
            box-shadow: 0 18px 55px rgba(80, 70, 160, 0.08);
        }}
        .eval-guidance-card,
        .eval-empty-state {{
            border-radius: 22px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background:
              radial-gradient(420px 180px at 88% 0%, {accent}1f, transparent 70%),
              rgba(255, 255, 255, 0.86);
            box-shadow: 0 18px 55px rgba(80, 70, 160, 0.08);
        }}
        .eval-guidance-card {{
            margin: 0.15rem 0 0.65rem 0;
            padding: 0.85rem 1rem;
            color: #4b5563;
            font-size: 0.9rem;
            line-height: 1.55;
        }}
        .eval-empty-state {{
            padding: clamp(1.25rem, 4vw, 2rem);
            min-height: 320px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .eval-empty-state .eyebrow {{
            width: fit-content;
            margin: 0 0 0.8rem 0;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background: rgba(255,255,255,0.72);
            color: {accent};
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}
        .eval-empty-state h3 {{
            margin: 0;
            max-width: 560px;
            color: #111827;
            font-size: clamp(1.45rem, 2.2vw, 2rem);
            line-height: 1.12;
            letter-spacing: -0.04em;
        }}
        .eval-empty-state p:not(.eyebrow) {{
            margin: 0.8rem 0 0 0;
            max-width: 620px;
            color: #6b7280;
            font-size: 0.96rem;
            line-height: 1.7;
        }}
        .analytics-section-card {{
            margin-top: 0.8rem;
            border-radius: 24px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background:
              radial-gradient(520px 220px at 88% 0%, {accent}18, transparent 70%),
              rgba(255, 255, 255, 0.82);
            box-shadow: 0 18px 55px rgba(80, 70, 160, 0.08);
            padding: 1.1rem 1.2rem;
        }}
        .analytics-explorer-card {{
            margin-top: 1.25rem;
        }}
        .analytics-section-heading span,
        .analytics-filter-heading span {{
            display: inline-flex;
            width: fit-content;
            margin-bottom: 0.45rem;
            padding: 0.32rem 0.62rem;
            border-radius: 999px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background: rgba(255, 255, 255, 0.72);
            color: {accent};
            font-size: 0.67rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}
        .analytics-section-heading h3 {{
            margin: 0;
            color: #111827;
            font-size: clamp(1.35rem, 2vw, 1.9rem);
            line-height: 1.1;
            letter-spacing: -0.04em;
        }}
        .analytics-section-heading p,
        .analytics-filter-heading p {{
            margin: 0.45rem 0 0 0;
            color: #6b7280;
            font-size: 0.95rem;
            line-height: 1.6;
        }}
        .analytics-user-overview {{
            margin: 0.9rem 0 1.25rem 0;
            border-radius: 28px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background:
              radial-gradient(520px 260px at 92% 0%, rgba(109, 91, 208, 0.16), transparent 70%),
              radial-gradient(420px 220px at 8% 100%, rgba(91, 140, 90, 0.13), transparent 70%),
              rgba(255, 255, 255, 0.82);
            box-shadow: 0 22px 70px rgba(80, 70, 160, 0.10);
            padding: clamp(1rem, 2.4vw, 1.45rem);
        }}
        .analytics-user-summary {{
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            margin-bottom: 1rem;
        }}
        .analytics-user-summary span,
        .analytics-audit-console span {{
            width: fit-content;
            border-radius: 999px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background: rgba(255, 255, 255, 0.72);
            color: {accent};
            padding: 0.32rem 0.62rem;
            font-size: 0.67rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}
        .analytics-user-summary h3,
        .analytics-audit-console h3 {{
            margin: 0;
            color: #111827;
            font-size: clamp(1.3rem, 2vw, 1.85rem);
            line-height: 1.1;
            letter-spacing: -0.04em;
        }}
        .analytics-user-summary p,
        .analytics-audit-console p {{
            margin: 0;
            max-width: 680px;
            color: #6b7280;
            font-size: 0.94rem;
            line-height: 1.65;
        }}
        .analytics-user-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
        }}
        @media (max-width: 900px) {{
            .analytics-user-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}
        @media (max-width: 620px) {{
            .analytics-user-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        .analytics-user-card {{
            position: relative;
            overflow: hidden;
            border-radius: 22px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background: rgba(255, 255, 255, 0.78);
            padding: 1rem;
            box-shadow: 0 14px 42px rgba(17, 24, 39, 0.05);
        }}
        .analytics-user-card::before {{
            content: "";
            position: absolute;
            inset: -40% -20% auto auto;
            width: 150px;
            height: 150px;
            border-radius: 999px;
            opacity: 0.18;
            filter: blur(10px);
        }}
        .analytics-user-card.violet::before {{ background: #6d5bd0; }}
        .analytics-user-card.emerald::before {{ background: #5b8c5a; }}
        .analytics-user-card.amber::before {{ background: #d6a247; }}
        .analytics-user-card.rose::before {{ background: #d06b9c; }}
        .analytics-user-card.blue::before {{ background: #3b82f6; }}
        .analytics-user-card.slate::before {{ background: #64748b; }}
        .analytics-user-card-top {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
        }}
        .analytics-avatar {{
            display: flex;
            width: 42px;
            height: 42px;
            align-items: center;
            justify-content: center;
            border-radius: 16px;
            background: #111827;
            color: white;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }}
        .analytics-user-card-top span {{
            border-radius: 999px;
            background: rgba(17, 24, 39, 0.06);
            color: #374151;
            padding: 0.25rem 0.55rem;
            font-size: 0.72rem;
            font-weight: 800;
        }}
        .analytics-user-card h4 {{
            position: relative;
            margin: 0.85rem 0 0.18rem 0;
            color: #111827;
            font-size: 1rem;
            line-height: 1.25;
            overflow-wrap: anywhere;
        }}
        .analytics-user-card p {{
            position: relative;
            margin: 0;
            color: #9ca3af;
            font-size: 0.78rem;
            overflow-wrap: anywhere;
        }}
        .analytics-user-metric {{
            position: relative;
            display: flex;
            align-items: baseline;
            gap: 0.45rem;
            margin-top: 0.85rem;
        }}
        .analytics-user-metric strong {{
            color: #111827;
            font-size: 1.55rem;
            line-height: 1;
        }}
        .analytics-user-metric span {{
            color: #6b7280;
            font-size: 0.8rem;
            font-weight: 700;
        }}
        .analytics-user-bar {{
            position: relative;
            margin-top: 0.8rem;
            height: 0.45rem;
            overflow: hidden;
            border-radius: 999px;
            background: rgba(17, 24, 39, 0.07);
        }}
        .analytics-user-bar i {{
            display: block;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #6d5bd0, #a78bfa, #5b8c5a);
        }}
        .analytics-audit-console {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: 0.9rem 0 0.7rem 0;
            padding: clamp(1rem, 2.3vw, 1.4rem);
            border-radius: 26px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background:
              radial-gradient(420px 210px at 92% 0%, rgba(91, 140, 90, 0.18), transparent 70%),
              rgba(255, 255, 255, 0.86);
            box-shadow: 0 18px 55px rgba(80, 70, 160, 0.08);
        }}
        .analytics-audit-console > div:first-child {{
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}
        .analytics-audit-stat {{
            min-width: 138px;
            border-radius: 22px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background: #111827;
            color: white;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 16px 42px rgba(17, 24, 39, 0.16);
        }}
        .analytics-audit-stat strong {{
            display: block;
            font-size: 2rem;
            line-height: 1;
        }}
        .analytics-audit-stat small {{
            display: block;
            margin-top: 0.35rem;
            color: rgba(255, 255, 255, 0.58);
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }}
        @media (max-width: 720px) {{
            .analytics-audit-console {{
                align-items: stretch;
                flex-direction: column;
            }}
            .analytics-audit-stat {{
                width: 100%;
            }}
        }}
        .analytics-filter-heading {{
            margin: 0.4rem 0 0.75rem 0;
            padding: 1rem;
            border-radius: 20px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 14px 42px rgba(17, 24, 39, 0.05);
        }}
        .analytics-image-card {{
            margin: 0.8rem 0;
            padding: 1rem;
            border-radius: 22px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background: rgba(255, 255, 255, 0.86);
            box-shadow: 0 18px 55px rgba(80, 70, 160, 0.08);
        }}
        .analytics-selector-panel {{
            margin: 1rem 0 0.7rem 0;
            padding: clamp(1rem, 2.4vw, 1.5rem);
            border-radius: 28px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background:
              radial-gradient(440px 220px at 90% 0%, rgba(109, 91, 208, 0.16), transparent 70%),
              radial-gradient(380px 220px at 8% 100%, rgba(91, 140, 90, 0.13), transparent 70%),
              rgba(255, 255, 255, 0.86);
            box-shadow: 0 20px 65px rgba(80, 70, 160, 0.09);
        }}
        .analytics-selector-panel span,
        .analytics-sheet-title span {{
            display: inline-flex;
            width: fit-content;
            margin-bottom: 0.5rem;
            border-radius: 999px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background: rgba(255,255,255,0.72);
            color: {accent};
            padding: 0.32rem 0.62rem;
            font-size: 0.67rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}
        .analytics-selector-panel h3,
        .analytics-sheet-title h3 {{
            margin: 0;
            color: #111827;
            font-size: clamp(1.35rem, 2vw, 1.9rem);
            line-height: 1.1;
            letter-spacing: -0.04em;
        }}
        .analytics-selector-panel p,
        .analytics-sheet-title p {{
            margin: 0.55rem 0 0 0;
            max-width: 760px;
            color: #6b7280;
            font-size: 0.95rem;
            line-height: 1.65;
        }}
        .analytics-selector-panel b {{
            display: inline-flex;
            margin-top: 0.9rem;
            border-radius: 999px;
            background: #111827;
            color: white;
            padding: 0.48rem 0.8rem;
            font-size: 0.72rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }}
        .analytics-sheet {{
            margin-top: 1rem;
            overflow: hidden;
            border-radius: 28px;
            border: 1px solid rgba(17, 24, 39, 0.06);
            background:
              radial-gradient(500px 260px at 88% 0%, {accent}14, transparent 72%),
              rgba(255, 255, 255, 0.9);
            box-shadow: 0 22px 70px rgba(80, 70, 160, 0.10);
        }}
        .analytics-sheet-title {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.15rem 1.2rem;
            border-bottom: 1px solid rgba(17, 24, 39, 0.06);
        }}
        .analytics-sheet-title strong {{
            min-width: 62px;
            border-radius: 20px;
            background: #111827;
            color: white;
            padding: 0.78rem 0.9rem;
            text-align: center;
            font-size: 1.35rem;
            line-height: 1;
            box-shadow: 0 14px 35px rgba(17, 24, 39, 0.16);
        }}
        .analytics-sheet-head {{
            display: grid;
            gap: 0.65rem;
            padding: 0.8rem 1rem;
            background: rgba(17, 24, 39, 0.03);
            color: #6b7280;
            font-size: 0.68rem;
            font-weight: 900;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}
        .analytics-sheet-body {{
            display: flex;
            flex-direction: column;
            gap: 0.55rem;
            padding: 0.85rem;
        }}
        .analytics-sheet-row {{
            display: grid;
            grid-template-columns: repeat(var(--sheet-cols), minmax(0, 1fr));
            gap: 0.65rem;
            align-items: center;
            border-radius: 20px;
            border: 1px solid rgba(17, 24, 39, 0.05);
            background: rgba(255, 255, 255, 0.86);
            padding: 0.85rem;
            box-shadow: 0 10px 28px rgba(17, 24, 39, 0.04);
            animation: analytics-row-in 0.45s ease both;
            animation-delay: var(--row-delay);
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        }}
        .analytics-sheet-row:hover {{
            transform: translateY(-2px);
            border-color: {accent}44;
            box-shadow: 0 16px 42px rgba(80, 70, 160, 0.12);
        }}
        .analytics-sheet-cell {{
            min-width: 0;
            color: #374151;
            font-size: 0.86rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
        }}
        .analytics-sheet-cell.badge-cell {{
            width: fit-content;
            max-width: 100%;
            border-radius: 999px;
            background: rgba(109, 91, 208, 0.10);
            color: #5b4ac4;
            padding: 0.36rem 0.62rem;
            font-size: 0.78rem;
            font-weight: 800;
        }}
        @keyframes analytics-row-in {{
            from {{
                opacity: 0;
                transform: translateY(8px) scale(0.99);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}
        @media (max-width: 820px) {{
            .analytics-sheet-head {{
                display: none;
            }}
            .analytics-sheet-row {{
                grid-template-columns: 1fr;
            }}
            .analytics-sheet-title {{
                align-items: flex-start;
                flex-direction: column;
            }}
        }}
        .compact-label h4,
        .compact-label h3 {{
            margin-bottom: .15rem !important;
        }}
        [data-testid="stExpander"] details {{
            border: none !important;
        }}
        .stImage img {{
            border-radius: 22px !important;
            box-shadow: 0 18px 48px rgba(17, 24, 39, 0.10) !important;
        }}

        /* Admin tables and tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: .55rem !important;
            border-radius: 18px !important;
            background: rgba(255,255,255,.76) !important;
            padding: .35rem !important;
            border: 1px solid rgba(17,24,39,.06) !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 14px !important;
            color: #6b7280 !important;
            font-weight: 700 !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: #111827 !important;
            color: white !important;
        }}
        [data-testid="stDataFrame"] {{
            border-radius: 24px !important;
            overflow: hidden !important;
            border: 1px solid rgba(17, 24, 39, 0.06) !important;
            box-shadow: 0 18px 55px rgba(80, 70, 160, 0.08) !important;
        }}
        .stSelectbox > div > div,
        .stDateInput input {{
            border-radius: 16px !important;
            border: 1px solid rgba(17,24,39,.10) !important;
            background: rgba(255,255,255,.9) !important;
        }}

        @keyframes subtle-float {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-4px); }}
        }}
        [data-testid="stSpinner"] {{
            border-radius: 20px !important;
            background: rgba(255,255,255,.88) !important;
            box-shadow: 0 18px 55px rgba(80, 70, 160, 0.08) !important;
            padding: .75rem 1rem !important;
            animation: subtle-float 2.4s ease-in-out infinite;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Initialize analytics session (keep for backward compatibility with existing analytics)
if "analytics_initialized" not in st.session_state:
    st.session_state.analytics_initialized = True
    st.session_state.interaction_count = {
        "datasets_uploaded": 0,
        "visualizations_created": 0,
        "queries_made": 0
    }
    # For backward compatibility with existing DB logging
    # Create a mapping session for the analytics system
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{int(time.time())}"

# Initialize chat storage for current session
if "chat_initialized" not in st.session_state:
    st.session_state.chat_initialized = True
    st.session_state.chat_messages = []  # In-memory chat history for current session
    # Chat will auto-save to disk via chat_storage module
# --------------------- Utility Functions ---------------------
def convert_to_csv(input_file: str, output_file: str = None) -> str:
    """Convert various file formats to CSV."""
    ext = os.path.splitext(input_file)[1].lower()
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + ".csv"

    try:
        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(input_file)
        elif ext == ".json":
            with open(input_file, "r") as f:
                data = json.load(f)
            df = pd.json_normalize(data)
        elif ext == ".xml":
            tree = ET.parse(input_file)
            root = tree.getroot()
            df = pd.DataFrame([{elem.tag: elem.text for elem in child} for child in root])
        elif ext == ".txt":
            df = pd.read_csv(input_file, engine="python")  # Attempts delimiter autodetect
        elif ext == ".csv":
            return input_file
        else:
            st.error(f"Unsupported file type: {ext}")
            st.stop()

        df.to_csv(output_file, index=False)
        return output_file

    except Exception as e:
        st.error(f"Error converting file: {e}")
        return None


def prepare_dataframe_for_lida(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize dataframe types that LIDA's summarizer cannot safely inspect."""
    safe_df = df.copy()
    for column in safe_df.columns:
        series = safe_df[column]
        non_null = series.dropna()

        # LIDA's datetime probing calls pd.to_datetime(..., errors="raise") on
        # object columns and catches ValueError, but pandas raises TypeError for
        # bool objects. Treat booleans as categorical text for stable summaries.
        if pd.api.types.is_bool_dtype(series):
            safe_df[column] = series.map(lambda value: "" if pd.isna(value) else str(bool(value)))
            continue

        if series.dtype == object and not non_null.empty:
            has_bool_values = non_null.map(lambda value: isinstance(value, bool)).any()
            if has_bool_values:
                safe_df[column] = series.map(lambda value: "" if pd.isna(value) else str(value))

    return safe_df

def gen_summary(data_summary, model="gpt-4o"):
    prompt = f"""
    You are a data analyst and visualization expert.

    Dataset Summary:
    {json.dumps(data_summary, indent=2)}

    Task:
    - Clearly state what this dataset represents and give a overview of its contents.
    - List each column and explain its contents in the form of bullets.
    - Use direct, factual language—do not hedge or use phrases like “I think” or “I guess.”
    - Keep your response concise, in 5–6 clear sentences.
    """

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ],
    max_tokens=2000,
    temperature=0.2
)

    return response.choices[0].message.content

    


@st.cache_data
def validate_user_query(user_query, data_summary, validation_rules, model="gpt-4o"):
    prompt = f"""
    You are a highly skilled data analyst and visualization expert.

    Dataset Summary:
    {json.dumps(data_summary, indent=2)}

    User Query:
    "{user_query}"

    Validation Rules:
    {json.dumps(validation_rules, indent=2)}

    Your task:

    1. **Validate the Query only based on data summary**:
       - Check if the query references only fields that exist in the data summary.
       - If the query is invalid or cannot be to be answered with the available data, return:
         ```
         {{
           "Valid": "No",
           "Reason": "Clearly explain why the query is not valid (e.g., missing field, ambiguous question, etc.)"
         }}
         ```

    2. **Interpret the Query (If Valid)**:
       - Identify all the variables involved in the query.
       - Analyze and explain all possible types of relationships (e.g., correlation, causation, conditional, nonlinear, interaction effects, spurious, independence, etc.) that can exist between the variables in a detailed and comprehensive way.
       - Match against the validation rules to suggest a suitable chart type.
       - Identify if a chart type is mentioned in the prompt.
       - Recomended chart types seperated by comma.
       - Return a dict response with the structure:
         ```
         {{
           "Valid": "Yes",
           "All Variables involved": "<list of variables involved in the query>",
           "Relationship between variables": "<Detailed explanation of all the different relationships that can exist between the variables, not limited to correlation.>",
           "Chart mentioned in prompt": "<chart type if mentioned, else 'Not mentioned'>",
           "Recommended chart": "<what are all the recommended chart types seperated by comma>",
           "All Chart Types": "<comma separated string of mentioned chart type and recommended chart types>",
           "Justification": "<brief reasoning for why this chart is appropriate based on validation rules and data types>"
         }}
         ```
    Do not include any extra annotations, or language tags like "json" before the output. Only return the raw dict object.
    
    """

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": "You are an expert data analyst specializing in data interpretation and visualization."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"Valid": "No", "Reason": "Invalid JSON response from LLM"}

def load_json(path: str) -> dict:
    """Load JSON data from a file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {path}: {e}")
        return {}


def base64_to_image(base64_string: str) -> Image.Image:
    """Convert a base64 encoded string to a PIL Image."""
    return Image.open(BytesIO(base64.b64decode(base64_string)))


def summary_to_dict(summary):
    """Return a JSON-friendly dict while preserving the original LIDA Summary object elsewhere."""
    if isinstance(summary, dict):
        return summary
    if hasattr(summary, "dict"):
        return summary.dict()
    if hasattr(summary, "model_dump"):
        return summary.model_dump()
    return dict(getattr(summary, "__dict__", {}))


def encode_image(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def generate_image_validation_prompt(encoded_image: str, visualization_rules: dict) -> (str, str):
    """
    Create a validation prompt for LLM using visualization rules and encoded image.
    Returns a tuple of (prompt, encoded_image)
    """
    prompt = f"""
You are an expert in data visualization quality assessment. Your task is to analyze the provided chart image and check if it adheres to visualization best practices.

**Visualization Quality Rules:**
{json.dumps(visualization_rules, indent=2)}

**Your Task:**
- Return the evaluation in the exact structure below, using concise plain markdown.
- Do not wrap the response in code fences.
- Score strictly from 0 to 100 based on clarity, labeling, color, layout, readability, and interpretability.
- Be direct and practical. Avoid vague comments.

OVERALL SCORE: <number>/100

SUMMARY:
<2-3 sentences interpreting the chart and overall quality.>

STRENGTHS:
- <specific strength>
- <specific strength>
- <specific strength>

ISSUES:
- <specific issue or "No major issue found">
- <specific issue>

RECOMMENDATIONS:
- <actionable improvement>
- <actionable improvement>
- <actionable improvement>

CHECKLIST:
- Title: Pass/Needs work - <short reason>
- Axis labels: Pass/Needs work - <short reason>
- Legend: Pass/Needs work - <short reason>
- Color contrast: Pass/Needs work - <short reason>
- Font readability: Pass/Needs work - <short reason>
- Layout / cropping: Pass/Needs work - <short reason>
- Chart type fit: Pass/Needs work - <short reason>
    """
    return prompt, encoded_image


def validate_visualization_image_with_llm(image_path: str, visualization_rules: dict) -> str:
    """Validate visualization quality using OpenAI GPT-4o with image input."""
    encoded_image = encode_image(image_path)
    img_type = "image/png"

    prompt, _ = generate_image_validation_prompt(encoded_image, visualization_rules)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{img_type};base64,{encoded_image}"}}
                ]
            }
        ],
        max_tokens=3000,
        temperature=0.2
    )

    return response.choices[0].message.content


# --------------------- Streamlit Stateful Utility ---------------------
def stateful_button(label: str, key: str, state_key: str = None) -> bool:
    """
    A stateful button that toggles its state in session_state.
    Uses a separate key (state_key) to store the toggle value to avoid conflicts with widget keys.
    """
    if state_key is None:
        state_key = key + "_state"

    if state_key not in st.session_state:
        st.session_state[state_key] = False

    if st.button(label, key=key):
        st.session_state[state_key] = not st.session_state[state_key]

    return st.session_state[state_key]


def render_visual_activity_sheet(
    df: pd.DataFrame,
    columns: list,
    labels: dict,
    title: str,
    subtitle: str,
):
    """Render analytics records as a polished HTML activity sheet."""
    visible_columns = [column for column in columns if column in df.columns]
    if not visible_columns or df.empty:
        st.info("No activity records found for this view.")
        return

    header_cells = "".join(
        f'<span>{html.escape(labels.get(column, column.replace("_", " ").title()))}</span>'
        for column in visible_columns
    )
    rows_html = []
    for row_index, (_, row) in enumerate(df[visible_columns].head(75).iterrows()):
        cells = []
        for column in visible_columns:
            value = row.get(column, "")
            if pd.isna(value):
                display_value = "N/A"
            elif isinstance(value, bool):
                display_value = "Yes" if value else "No"
            else:
                display_value = str(value)

            escaped_value = html.escape(display_value)
            cell_class = "analytics-sheet-cell"
            if column in {"visualization_generated", "chart_type", "action_type"}:
                cell_class += " badge-cell"
            cells.append(f'<div class="{cell_class}">{escaped_value}</div>')

        rows_html.append(
            f'<div class="analytics-sheet-row" style="--row-delay:{min(row_index, 18) * 0.035}s">'
            f'{"".join(cells)}'
            f'</div>'
        )

    st.markdown(
        f'<div class="analytics-sheet">'
        f'<div class="analytics-sheet-title">'
        f'<div><span>Activity Sheet</span><h3>{html.escape(title)}</h3><p>{html.escape(subtitle)}</p></div>'
        f'<strong>{len(df)}</strong>'
        f'</div>'
        f'<div class="analytics-sheet-head" style="grid-template-columns: repeat({len(visible_columns)}, minmax(0, 1fr));">{header_cells}</div>'
        f'<div class="analytics-sheet-body" style="--sheet-cols:{len(visible_columns)};">{"".join(rows_html)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def refine_query(query, chart_selected):
    prompt = f"""
    You are an expert in data visualization and analytics.

    User Query:
    "{query}"

    Task:
    - Rewrite the user's query to make it clear, concise, and well-suited for visualization using this exact chart type: "{chart_selected}".
    - Do not switch to a different chart type unless "{chart_selected}" is impossible for the available data.
    - Ensure the refined query is specific and actionable for chart generation.
    - Include clear encoding guidance such as what should be on x-axis, y-axis, color/grouping, and aggregation if needed.
    - Briefly explain why "{chart_selected}" is appropriate for this query, referencing the validation details if relevant.
    - Make the query robust for rendering: avoid overcrowded labels, choose readable grouping, and prefer top categories when too many categories exist.
    - Return your response as two parts: 
        1. The improved/refined query.
        2. A short justification for the chart choice.
    """
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an expert data analyst specializing in data interpretation and visualization."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)


    return response.choices[0].message.content


# --------------------- Viz Evaluator UI ---------------------

def run_viz_evaluator():
    from magic_wrapper import render_magic_evaluator_header, render_magic_feedback

    inject_magic_page_styles("evaluator")
    render_page_actions(active="viz_evaluator")
    render_magic_evaluator_header(key="eval_header")

    eval_left, eval_right = st.columns([0.95, 1.35], gap="medium")
    with eval_left:
        st.markdown("<div class='compact-label'>", unsafe_allow_html=True)
        st.markdown("#### Upload chart image")
        st.caption("PNG, JPG, or JPEG.")
        uploaded_file = st.file_uploader("Upload your visualization image", type=["png", "jpg", "jpeg"])
        st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_file:
        current_eval_file = f"{uploaded_file.name}:{uploaded_file.size}"
        if st.session_state.get("latest_eval_file") != current_eval_file:
            st.session_state.latest_eval_file = current_eval_file
            st.session_state.latest_eval_feedback = None

        try:
            image = Image.open(uploaded_file)
        except Exception as e:
            st.error(f"Error processing the uploaded image: {e}")
            return
        
        # Save the uploaded image to a temporary file
        temp_image_path = "output_image.png"
        image.save(temp_image_path)
        with eval_left:
            st.markdown("<div class='ds-card'>", unsafe_allow_html=True)
            st.image(temp_image_path, caption="Uploaded Visualization", use_container_width=True)
            st.caption(f"{uploaded_file.name} · {image.width} x {image.height}px")
            st.markdown("</div>", unsafe_allow_html=True)
        
        visualization_quality_rules = load_json("quality_rules.json").get("VISUALIZATION_QUALITY_RULES", {})
        
        # Add a button to trigger the evaluation
        with eval_left:
            st.markdown(
                """
                <div class="eval-guidance-card">
                    <span>AI will check labels, legend, colors, layout, cropping, readability, and chart-type fit.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            evaluate_clicked = st.button("Scan Visualization", type="primary", use_container_width=True)

        if evaluate_clicked:
            # Save the uploaded image to a persistent file
            persistent_image_path = temp_image_path
            try:
                import io
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_data = img_byte_arr.getvalue()
                
                saved_img = save_generated_image(
                    st.session_state.user_id,
                    st.session_state.session_id,
                    img_data,
                    chart_type="uploaded_evaluation",
                    query=f"Evaluate visualization: {uploaded_file.name}",
                    image_format="png"
                )
                if saved_img:
                    persistent_image_path = saved_img.get("path")
                    # Log as a visualization uploaded by user
                    db.log_visualization(
                        st.session_state.user_id,
                        st.session_state.get("current_dataset_id", "unknown"),
                        "uploaded_evaluation",
                        [],
                        f"Evaluate visualization: {uploaded_file.name}",
                        "evaluated",
                        image_path=persistent_image_path,
                        source_type='uploaded'
                    )
            except Exception as e:
                print(f"Error saving uploaded image to storage: {e}")

            # Log visualization evaluation
            eval_start_time = time.time()
            try:
                db.log_interaction(st.session_state.user_id, "visualization_evaluated", {
                    "filename": uploaded_file.name
                }, "Viz Evaluator")
            except Exception as e:
                st.warning(f"Could not log evaluation: {e}")

            with st.spinner("🔍 Evaluating visualization quality..."):
                feedback = validate_visualization_image_with_llm(temp_image_path, visualization_quality_rules)
                st.session_state.latest_eval_feedback = feedback
                eval_response_time = time.time() - eval_start_time
                
                # Log to analytics module - chart evaluation
                try:
                    log_interaction(
                        st.session_state.get("user_id") or st.session_state.get("admin_id"),
                        st.session_state.username,
                        st.session_state.session_id,
                        "chart_evaluation",
                        {
                            "filename": uploaded_file.name,
                            "response_time_seconds": round(eval_response_time, 2),
                            "model_used": "GPT-4o"
                        }
                    )
                except Exception as e:
                    pass
                
                # Log evaluation feedback
                try:
                    db.log_ai_conversation(
                        st.session_state.user_id,
                        f"Evaluate visualization: {uploaded_file.name}",
                        feedback,
                        False,
                        "evaluation"
                    )
                except Exception as e:
                    st.warning(f"Could not log feedback: {e}")
        with eval_right:
            st.markdown("<div class='viz-output-pane'>", unsafe_allow_html=True)
            if st.session_state.get("latest_eval_feedback"):
                render_magic_feedback(feedback_text=st.session_state.latest_eval_feedback, key="eval_feedback")
            else:
                st.markdown(
                    """
                    <div class="eval-empty-state">
                        <p class="eyebrow">Ready to review</p>
                        <h3>Run the scan to get your quality report.</h3>
                        <p>The report will summarize the chart, score it, list issues, and give concrete recommendations.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        with eval_right:
            st.markdown("<div class='viz-output-pane'>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="eval-empty-state">
                    <p class="eyebrow">Visualization evaluator</p>
                    <h3>Upload a chart image to begin.</h3>
                    <p>Once uploaded, VisualStats will inspect readability, labels, legend placement, colors, and layout issues.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

def deduplicate(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]


def get_chart_type_choices() -> list:
    """Flatten configured chart types into a user-facing selector."""
    choices = []
    try:
        chart_rules = load_json("chart_selection.json").get("VALIDATION_RULES", {})
        for category in chart_rules.values():
            for charts in category.values():
                choices.extend(charts)
    except Exception:
        pass

    fallback = [
        "Bar/Column Chart",
        "Line Chart",
        "Scatter Plot",
        "Pie Chart",
        "Histogram",
        "Box Plot",
        "Heatmap",
        "Area Chart",
    ]
    return ["Auto (recommended)"] + deduplicate(choices or fallback)

# --------------------- Viz Generator UI ---------------------
def run_viz_generator():
    """Run the visualization generator interface with a Split View UI."""
    from magic_wrapper import render_magic_workspace_header, render_magic_empty_canvas

    inject_magic_page_styles("generator")
    render_page_actions(active="viz_generator")
    render_magic_workspace_header(
        title="Visualization Workspace",
        subtitle="Upload your data, describe what you want to see, and refine charts through conversation.",
        icon="generator",
        key="viz_header",
    )

    col_left, col_right = st.columns([1.0, 1.35], gap="medium")

    with col_left:
        st.markdown("<div class='compact-label'>", unsafe_allow_html=True)
        st.markdown("#### Dataset")
        st.caption("Upload CSV, Excel, JSON, XML, or text.")
        uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "xlsx", "xls", "json", "xml", "txt"])
        st.markdown("</div>", unsafe_allow_html=True)
    
    if not uploaded_file:
        with col_right:
            render_magic_empty_canvas(key="empty_canvas")
        return

    with col_left:
        # Save & convert
        file_path = uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Log dataset upload once
        if st.session_state.get("last_uploaded_file") != uploaded_file.name:
            try:
                file_size = len(uploaded_file.getvalue())
                dataset_id = db.log_dataset_upload(
                    st.session_state.user_id, uploaded_file.name, uploaded_file.type,
                    file_size, 0, 0, []
                )
                st.session_state.current_dataset_id = dataset_id
                st.session_state.last_uploaded_file = uploaded_file.name
                st.session_state.interaction_count["datasets_uploaded"] += 1
                log_interaction(
                    st.session_state.get("user_id") or st.session_state.get("admin_id"),
                    st.session_state.username, st.session_state.session_id,
                    "file_upload", {"filename": uploaded_file.name, "file_size_mb": round(file_size / (1024 * 1024), 2)}
                )
            except Exception as e:
                pass

        csv_path = convert_to_csv(file_path)
        if not csv_path:
            st.error("Could not convert file to CSV.")
            st.stop()

        # Streamlit reruns recreate the global LIDA Manager, so keep its in-memory
        # dataframe attached on every run. Use a sanitized copy for LIDA because
        # its summarizer can crash on object columns that contain booleans.
        try:
            raw_df = load_dataset_csv(csv_path)
        except UploadedDatasetError as e:
            st.error(str(e))
            st.stop()
        df = prepare_dataframe_for_lida(raw_df)
        lida.data = df
        lida_csv_path = os.path.splitext(csv_path)[0] + "_lida_safe.csv"
        df.to_csv(lida_csv_path, index=False)
        summary_cache_key = f"{csv_path}:lida_safe_v1"

        # Load & summarize
        if "summary" not in st.session_state or st.session_state.get("summary_file") != summary_cache_key:
            with st.spinner("Analyzing dataset..."):
                summary_obj = lida.summarize(lida_csv_path, summary_method="default", textgen_config=textgen_config)
                summary = summary_to_dict(summary_obj)
                for field in summary.get("fields", []):
                    col_name = field.get("column")
                    props = field.get("properties", {})
                    dtype = props.get("dtype", "").lower()
                    if dtype == "number": props["semantic_type"] = "quantitative"
                    elif dtype == "category": props["semantic_type"] = "categorical"
                    elif "date" in col_name.lower() or dtype == "datetime": props["semantic_type"] = "temporal"
                    else: props["semantic_type"] = "text"
                    props["description"] = props.get("description", "").strip() or f"{col_name.replace('_', ' ').capitalize()}"
                
                overview = gen_summary(summary)
                st.session_state.summary_obj = summary_obj
                st.session_state.summary = summary
                st.session_state.overview = overview
                st.session_state.summary_file = summary_cache_key
                
                # Fetch goals
                st.session_state.goals = lida.goals(summary_obj, n=2, textgen_config=textgen_config)
                goals = st.session_state.goals
                
                # Save to db
                try: save_dataset_summary(st.session_state.user_id, st.session_state.session_id, summary)
                except: pass
        else:
            summary_obj = st.session_state.get("summary_obj")
            if summary_obj is None or not hasattr(summary_obj, "file_name"):
                summary_obj = lida.summarize(lida_csv_path, summary_method="default", textgen_config=textgen_config)
                st.session_state.summary_obj = summary_obj
            summary = st.session_state.summary
            overview = st.session_state.overview
            goals = st.session_state.get("goals", [])

        with st.expander("Data Overview & Schema", expanded=False):
            st.write(overview)
            st.json(summary)

        st.markdown("<div class='assistant-workspace'>", unsafe_allow_html=True)
        st.markdown("<div class='compact-label'>", unsafe_allow_html=True)
        st.markdown("#### Recommended Questions")
        st.caption("Pick one to send it into the assistant chat.")
        st.markdown("</div>", unsafe_allow_html=True)

        sg_col1, sg_col2 = st.columns(2)
        with sg_col1:
            if goals and len(goals) > 0 and st.button(f"{goals[0].question}", key="goal_0", use_container_width=True):
                st.session_state.chat_input_val = goals[0].question
        with sg_col2:
            if goals and len(goals) > 1 and st.button(f"{goals[1].question}", key="goal_1", use_container_width=True):
                st.session_state.chat_input_val = goals[1].question

        st.markdown("<div class='compact-label'>", unsafe_allow_html=True)
        st.markdown("#### AI Chat Assistant")
        st.caption("Generate charts and refine your analysis through conversation.")
        st.markdown("</div>", unsafe_allow_html=True)

        chat_container = st.container(height=430)

        if "workspace_chat" not in st.session_state:
            st.session_state.workspace_chat = [
                {"role": "assistant", "content": "Hello! I've analyzed your data. What would you like to visualize?"}
            ]

        with chat_container:
            for msg in st.session_state.workspace_chat:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        chart_type_choices = get_chart_type_choices()
        with st.form(key="chat_form", clear_on_submit=True):
            chart_type_choice = st.selectbox(
                "Visualization type",
                options=chart_type_choices,
                index=0,
                help="Choose Auto to let the AI select the best chart, or force a specific visualization type.",
            )
            user_input = st.text_input("Message the assistant...", placeholder="E.g. Plot a bar chart of sales by region")
            col_sb1, col_sb2 = st.columns([4, 1])
            with col_sb1:
                submit_chat = st.form_submit_button("Generate Chart", type="primary", use_container_width=True)
            with col_sb2:
                clear_chat = st.form_submit_button("Clear", use_container_width=True)

        if clear_chat:
            st.session_state.workspace_chat = [{"role": "assistant", "content": "Hello! I've analyzed your data. What would you like to visualize?"}]
            st.session_state.chart_raster = None
            st.session_state.chart_code = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Determine if we should run generation
    query = user_input if submit_chat and user_input else st.session_state.get("chat_input_val")
    generate_trigger = submit_chat and user_input or st.session_state.get("chat_input_val")
    
    # Consume chat_input_val so it doesn't loop
    if "chat_input_val" in st.session_state:
        del st.session_state["chat_input_val"]

    with col_right:
        st.markdown("<div class='viz-output-pane'>", unsafe_allow_html=True)
        chart_container = st.container()
        
        # Trigger Generation
        if generate_trigger and query:
            # Append user message
            st.session_state.workspace_chat.append({"role": "user", "content": query})
            
            with chart_container:
                with st.spinner("Analyzing query and generating chart..."):
                    # Validate
                    validated = validate_user_query(query, summary, load_json("chart_selection.json")["VALIDATION_RULES"])
                    if validated.get("Valid") != "Yes":
                        error_msg = f"Invalid query: {validated.get('Reason', 'Unknown error')}"
                        st.error(error_msg)
                        st.session_state.workspace_chat.append({"role": "assistant", "content": f"❌ {error_msg}"})
                    else:
                        st.session_state.validated = validated
                        chart_types_str = validated.get('All Chart Types', validated.get('Recommended chart', 'Bar/Column Chart'))
                        st.session_state.chart_options = [c.strip() for c in chart_types_str.split(",") if c.strip()] or ["Bar Chart"]

                        chart_selected = (
                            chart_type_choice
                            if chart_type_choice and chart_type_choice != "Auto (recommended)"
                            else st.session_state.chart_options[0]
                        )
                        refined = build_fast_chart_goal(query, chart_selected)
                        
                        st.session_state.last_refined_query = refined
                        st.session_state.last_chart_selected = chart_selected
                        
                        st.session_state.workspace_chat.append({"role": "assistant", "content": f"Generating a `{chart_selected}` chart..."})

                        query_start = time.time()
                        charts = lida.visualize(summary=summary_obj, goal=refined, textgen_config=textgen_config, library="seaborn")
                        
                        if charts:
                            final_chart = charts[0]
                            generation_seconds = time.time() - query_start
                            st.session_state.chart_code = final_chart.code
                            st.session_state.chart_raster = final_chart.raster
                            
                            st.session_state.workspace_chat.append({"role": "assistant", "content": f"✅ Chart generated in {generation_seconds:.1f}s. You can view it on the right and refine it below if needed."})
                            
                            # Logging
                            try:
                                img_data = BytesIO()
                                img = base64_to_image(final_chart.raster)
                                img.save(img_data, format='PNG')
                                db.log_visualization(st.session_state.user_id, st.session_state.current_dataset_id, chart_selected, [], query, "generated")
                                save_chat_message(st.session_state.user_id, st.session_state.session_id, "user", query)
                            except: pass
            st.rerun()

        # Render Chart if exists
        if st.session_state.get("chart_raster"):
            with chart_container:
                img = base64_to_image(st.session_state.chart_raster)
                st.markdown("<div class='compact-label'>", unsafe_allow_html=True)
                st.markdown("#### Generated Chart")
                st.caption("The latest visualization generated from your assistant conversation.")
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='ds-card' style='margin-bottom: 15px;'>", unsafe_allow_html=True)
                st.image(img, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("#### Refine Your Chart")
                with st.form(key="refine_form", clear_on_submit=True):
                    extra = st.text_input("Additional instructions", placeholder="e.g. 'Make the bars green'")
                    refine_btn = st.form_submit_button("Update Chart", use_container_width=True)

                if st.session_state.get("validated"):
                    with st.expander("AI Visualization Details"):
                        v = st.session_state.validated
                        st.write(f"**Variables:** {v.get('All Variables involved', '')}")
                        st.write(f"**Relationship:** {v.get('Relationship between variables', '')}")
                        st.write(f"**Recommended Chart:** {v.get('Recommended chart', '')}")
                        st.write(f"**Justification:** {v.get('Justification', '')}")

                with st.expander("View Generated Code"):
                    st.code(st.session_state.chart_code, language="python")

                if refine_btn and extra.strip() and st.session_state.get("chart_code"):
                    st.session_state.workspace_chat.append({"role": "user", "content": f"Update chart: {extra}"})
                    with st.spinner("Applying refinements..."):
                        instr = [
                            "Keep the existing chart type and data mappings unless the user explicitly asks to change them.",
                            "Keep the chart readable and fully fitted in the rendered image.",
                            "Use a large readable figure size, tight_layout/constrained_layout, non-overlapping legend placement, and rotated/wrapped labels when needed.",
                            "Additionally apply this user request:",
                            extra,
                        ]
                        updated_charts = lida.edit(code=st.session_state.chart_code, summary=summary_obj, instructions=instr, library="seaborn", textgen_config=textgen_config)
                        if updated_charts:
                            st.session_state.chart_code = updated_charts[0].code
                            st.session_state.chart_raster = updated_charts[0].raster
                            st.session_state.workspace_chat.append({"role": "assistant", "content": "✅ Chart updated successfully!"})
                        else:
                            st.warning("⚠️ Refinement failed.")
                            st.session_state.workspace_chat.append({"role": "assistant", "content": "⚠️ Failed to apply refinement."})
                    st.rerun()
        else:
            with chart_container:
                if not generate_trigger:
                    render_magic_empty_canvas(
                        title="Visualization Canvas",
                        description="Your generated chart will appear here. Ask a question in the chat to get started.",
                        key="empty_canvas_loaded",
                    )
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------- Main App Setup ---------------------





# --------------------- Shared CSS ---------------------


# ——— Sidebar ———
with st.sidebar:
    # App title / logo area

    # Load and encode
    with open("home_icon.png", "rb") as f:
        data = f.read()
    b64_home = base64.b64encode(data).decode()

    st.markdown(f"""
<div style="text-align: center; padding: 0.5rem 0 0.25rem 0; border-bottom: 1px solid #E2E8F0;">
  <img src="data:image/png;base64,{b64_home}" alt="VisualStats logo" width="72"
    style="margin: 0.5rem auto; display: block;" />
  <h2 style="margin: 0.25rem 0 0.75rem; color: #1E40AF; font-family: 'Fira Sans', sans-serif; font-size: 1.25rem; font-weight: 700;">
    VisualStats
  </h2>
</div>
""", unsafe_allow_html=True)

    # Build menu options based on role
    menu_options = ["Home", "Viz Generator", "Viz Evaluator"]
    menu_icons = ["house-fill", "bar-chart-fill", "check2-circle"]
    
    # Admin sees Analytics option
    if st.session_state.get("role") == "admin":
        menu_options.append("Analytics Dashboard")
        menu_icons.append("graph-up")
    
    # Add logout option
    menu_options.append("Logout")
    menu_icons.append("box-arrow-right")
    
    # Determine the current index for programmatic navigation.
    # On normal Streamlit reruns (file upload, form submit, chart generation), option_menu
    # recreates itself. Preserve the last selected menu instead of falling back to Home.
    if "force_menu_index" in st.session_state:
        default_index = st.session_state["force_menu_index"]
    else:
        current_choice = st.session_state.get("menu_choice", "Home")
        default_index = menu_options.index(current_choice) if current_choice in menu_options else 0
    if "force_menu_index" in st.session_state:
        del st.session_state["force_menu_index"]

    menu = option_menu(
    menu_title=None,
    options=menu_options,
    icons=menu_icons,
    default_index=default_index,
    orientation="vertical",
    styles={
        "container": {
            "padding": "0.75rem 0.5rem",
            "background-color": "transparent",
        },
        "nav-link-icon": {
            "color": "#3B82F6",
            "font-size": "1.1rem",
            "margin": "0 0.5rem 0 0"
        },
        "nav-link": {
            "font-size": "0.95rem",
            "text-align": "left",
            "margin": "0.2rem 0",
            "padding": "0.5rem 0.75rem",
            "border-radius": "8px",
            "color": "#334155"
        },
        "nav-link:hover": {
            "background-color": "#F1F5F9",
            "color": "#1E40AF"
        },
        "nav-link-selected": {
            "background-color": "#1E40AF",
            "color": "#FFFFFF",
            "font-weight": "600"
        },
        "nav-link-selected-icon": {
            "color": "#FFFFFF"
        }
    }
)

    st.session_state.menu_choice = menu

    # ---------------- Sidebar Enhancements ----------------
    user_id = st.session_state.get("user_id")
    
    st.markdown("#### Active Datasets")
    if user_id:
        try:
            datasets = db.get_user_datasets(user_id, limit=5)
            if datasets:
                for d in datasets:
                    size_kb = d.get('file_size_bytes', 0) / 1024
                    st.markdown(
                        f"<div class='sidebar-section'><b>{d['dataset_name']}</b><br><span style='color:#64748B'>{size_kb:.1f} KB</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No datasets uploaded yet.")
        except Exception:
            st.caption("No datasets uploaded yet.")

    st.markdown("<hr style='margin: 1rem 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("#### Recent Sessions")
    if user_id:
        sessions = db.get_user_conversations(user_id, limit=3)
        if sessions:
            for s in sessions:
                q = s.get("user_query", "Session")
                if len(q) > 25:
                    q = q[:25] + "..."
                st.markdown(f"<div class='sidebar-section'>{q}</div>", unsafe_allow_html=True)
        else:
            st.caption("No chat history yet.")

    st.markdown("<hr style='margin: 1rem 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("#### Saved Visualizations")
    if user_id:
        viz = db.get_user_visualizations(user_id, limit=3)
        if viz:
            for v in viz:
                st.markdown(
                    f"<div class='sidebar-section'>{v.get('viz_type', 'Chart')}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No saved visualizations yet.")

    st.markdown("<hr style='margin: 1rem 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("#### Profile")
    st.markdown(
        f"<div class='sidebar-section'><b>{st.session_state.get('username', 'Guest')}</b><br>"
        f"<span style='color:#64748B'>{str(st.session_state.get('role', 'User')).capitalize()}</span></div>",
        unsafe_allow_html=True,
    )
    
# --------------------- Home Page Renderer ---------------------

def render_home():
    """Renders the React-powered task-first dashboard."""
    from magic_wrapper import render_magic_dashboard
    from platform_stats import get_platform_dashboard_stats

    st.markdown("""
    <style>
        /* Full-bleed home — hide sidebar so landing uses the whole viewport */
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        .stApp, .stMain, [data-testid="stAppViewContainer"] {
            background-color: #fbfbfa !important;
            max-width: 100vw !important;
            overflow-x: hidden !important;
        }
        [data-testid="stAppViewContainer"] > section.main {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .stMainBlockContainer {
            padding: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
            background-color: #fbfbfa !important;
        }
        [data-testid="stMain"] {
            padding: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
        }
        .stMainBlockContainer > div { gap: 0 !important; }
        iframe[title="magic_hub.magic_hub"] {
            width: 100% !important;
            max-width: 100% !important;
            border: none !important;
            display: block !important;
            overflow: hidden !important;
        }
        div[data-testid="stCustomComponentV1"] {
            background-color: #fbfbfa !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
        }
        [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            width: 100% !important;
        }
        [data-testid="stElementContainer"] {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

    is_admin = st.session_state.get("role") == "admin"
    username = st.session_state.get("username", "Guest")

    user_id = st.session_state.get("user_id")
    recent_datasets = []
    recent_sessions = []
    recent_viz = []

    if user_id:
        try:
            db_conn = get_db()
            recent_datasets = db_conn.get_user_datasets(user_id, limit=3)
            recent_sessions = db_conn.get_user_conversations(user_id, limit=3)
            recent_viz = db_conn.get_user_visualizations(user_id, limit=3)
            all_datasets = db_conn.get_user_datasets(user_id, limit=100)
            all_sessions = db_conn.get_user_conversations(user_id, limit=100)
            all_viz = db_conn.get_user_visualizations(user_id, limit=100)
        except Exception as e:
            print(f"Error fetching recent activity for dashboard: {e}")
            all_datasets, all_sessions, all_viz = [], [], []
    else:
        all_datasets, all_sessions, all_viz = [], [], []

    chart_type_counts: dict = {}
    for v in all_viz:
        vt = v.get("viz_type") or "Unknown"
        chart_type_counts[vt] = chart_type_counts.get(vt, 0) + 1
    user_chart_types = [
        {"viz_type": k, "count": c}
        for k, c in sorted(chart_type_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    ]

    supported_charts: list = []
    try:
        chart_rules = load_json("chart_selection.json").get("VALIDATION_RULES", {})
        for category in chart_rules.values():
            for charts in category.values():
                supported_charts.extend(charts)
        supported_charts = list(dict.fromkeys(supported_charts))
    except Exception:
        supported_charts = [
            "Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart",
            "Histogram", "Heatmap", "Box Plot", "Area Chart",
        ]

    # All-time platform totals from Supabase + local SQLite
    platform_stats = get_platform_dashboard_stats()
    top_chart_types = platform_stats.get("top_chart_types") or user_chart_types

    dashboard_stats = {
        "datasets": platform_stats.get("datasets", 0),
        "sessions": platform_stats.get("chat_queries", 0),
        "visualizations": platform_stats.get("visualizations", 0),
        "users": platform_stats.get("users", 0),
        "interactions": platform_stats.get("interactions", 0),
    }

    nav_event = render_magic_dashboard(
        key="magic_dashboard",
        is_admin=is_admin,
        username=username,
        datasets=recent_datasets,
        sessions=recent_sessions,
        visualizations=recent_viz,
        stats=dashboard_stats,
        chart_types=top_chart_types,
        supported_charts=supported_charts,
    )
    
    # Handle navigation events from the mode card "Get Started" buttons
    if nav_event:
        action = nav_event.get("action")
        target = nav_event.get("target")
        timestamp = nav_event.get("timestamp")
        last_ts = st.session_state.get("last_nav_timestamp")
        
        if timestamp and timestamp != last_ts:
            st.session_state.last_nav_timestamp = timestamp
            if action == "logout":
                perform_logout()
            elif action == "navigate" and target == "home":
                st.session_state.menu_choice = "Home"
                st.session_state.force_menu_index = 0
                st.rerun()
            elif action == "navigate" and target == "viz_generator":
                # Trigger a menu option switch
                st.session_state.menu_choice = "Viz Generator"
                # Need to force a rerun so the sidebar menu updates and the app routes properly
                # Normally with option_menu, switching programmatically requires passing default_index
                # We'll set a state var to override the index
                st.session_state.force_menu_index = 1
                st.rerun()
            elif action == "navigate" and target == "viz_evaluator":
                st.session_state.menu_choice = "Viz Evaluator"
                st.session_state.force_menu_index = 2
                st.rerun()
            elif action == "navigate" and target == "analytics_dashboard":
                st.session_state.menu_choice = "Analytics Dashboard"
                st.session_state.force_menu_index = 3
                st.rerun()

# --------------------- Analytics Dashboard Renderer ---------------------
def render_analytics():
    """Render the analytics dashboard with platform statistics from Supabase."""
    from magic_wrapper import render_magic_analytics
    from analytics import get_all_sessions
    from chat_storage import get_all_user_chats, get_chat_history
    from auth import get_all_user_profiles
    from platform_stats import get_platform_dashboard_stats

    inject_magic_page_styles("analytics")
    render_page_actions(active="analytics_dashboard")

    user_profiles = get_all_user_profiles()
    total_users = len(user_profiles)

    all_sessions = get_all_sessions()
    total_visualizations = 0
    total_datasets = 0
    total_interactions = 0
    total_duration_seconds = 0
    duration_count = 0

    action_counts = {}
    chart_counts = {}

    for s in all_sessions:
        interactions = s.get("interactions", [])
        total_interactions += len(interactions)

        for i in interactions:
            action = i.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

            if action in ["dataset_upload", "file_upload"]:
                total_datasets += 1
            elif action in ["chart_generated", "ai_query", "chart_refinement", "chart_evaluation"]:
                total_visualizations += 1

        dur = s.get("duration_seconds")
        if dur is not None:
            total_duration_seconds += dur
            duration_count += 1

    all_chats = []
    for uid in user_profiles.keys():
        user_chats = get_all_user_chats(uid)
        all_chats.extend(user_chats)

    for c in all_chats:
        chat_hist = get_chat_history(c.get("user_id", uid), c.get("session_id", ""))
        if chat_hist:
            for img in chat_hist.get("generated_images", []):
                ctype = img.get("chart_type", "Unknown")
                chart_counts[ctype] = chart_counts.get(ctype, 0) + 1

    avg_session_duration = total_duration_seconds / duration_count if duration_count > 0 else 0
    avg_display = f"{int(avg_session_duration // 60)}m {int(avg_session_duration % 60)}s" if avg_session_duration else "—"

    platform_stats = get_platform_dashboard_stats()
    total_users = max(total_users, platform_stats.get("users", 0))
    total_visualizations = max(total_visualizations, platform_stats.get("visualizations", 0))
    total_datasets = max(total_datasets, platform_stats.get("datasets", 0))
    total_interactions = max(total_interactions, platform_stats.get("interactions", 0))
    top_chart_types = platform_stats.get("top_chart_types") or [
        {"viz_type": k, "count": v}
        for k, v in sorted(chart_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    ]

    render_magic_analytics(
        total_users=total_users,
        total_visualizations=total_visualizations,
        total_datasets=total_datasets,
        total_interactions=total_interactions,
        avg_session_duration=avg_display,
        top_chart_types=top_chart_types,
        key="analytics_header",
    )

    active_user_ids = list(user_profiles.keys())
    
    if active_user_ids:
        # Create a display mapping: display_name -> user_id
        user_options = {}
        for uid in active_user_ids:
            name = user_profiles.get(uid, f"Guest / Unknown ({uid[:8]})")
            user_options[f"{name}"] = uid

        st.markdown(
            f'<div class="analytics-selector-panel">'
            f'<span>User Activity</span>'
            f'<h3>Select a user to inspect activity.</h3>'
            f'<p>Choose a user, then review their questions, platform actions, generated charts, and evaluator uploads in the visual activity sheet below.</p>'
            f'<b>{len(user_options)} users available</b>'
            f'</div>',
            unsafe_allow_html=True,
        )
        selected_label = st.selectbox("Select User Activity:", options=["-- Select a User --"] + list(user_options.keys()))
        
        if selected_label and selected_label != "-- Select a User --":
            selected_user_id = user_options[selected_label]
            
            import datetime
            st.markdown(
                """
                <div class="analytics-filter-heading">
                    <span>Filter Activity</span>
                    <p>Narrow the audit window before reviewing conversations, clicks, and visual assets.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_date = st.date_input("Start Date", value=datetime.date.today() - datetime.timedelta(days=30))
            with col_d2:
                end_date = st.date_input("End Date", value=datetime.date.today())
                
            start_dt = datetime.datetime.combine(start_date, datetime.time.min)
            end_dt = datetime.datetime.combine(end_date, datetime.time.max)
            
            tab1, tab2, tab3 = st.tabs(["Questions & AI Conversations", "Platform Interactions", "Visualizations & Images"])

            with tab1:
                from chat_storage import get_all_user_chats, get_chat_history
                
                chats = get_all_user_chats(selected_user_id)
                conv_data = []
                for chat in chats:
                    chat_hist = get_chat_history(selected_user_id, chat.get("session_id", ""))
                    if chat_hist:
                        for msg in chat_hist.get("messages", []):
                            if msg.get("role") == "user":
                                timestamp_str = msg.get("timestamp")
                                if timestamp_str:
                                    try:
                                        dt = pd.to_datetime(timestamp_str).to_pydatetime()
                                        # Remove timezone info if present to compare with naive datetime
                                        if dt.tzinfo is not None:
                                            dt = dt.replace(tzinfo=None)
                                        if not (start_dt <= dt <= end_dt):
                                            continue
                                    except:
                                        pass
                                
                                conv_data.append({
                                    "timestamp": timestamp_str,
                                    "user_query": msg.get("content"),
                                    "chart_type": msg.get("metadata", {}).get("chart_type", "N/A"),
                                    "visualization_generated": True if "chart_type" in msg.get("metadata", {}) else False
                                })
                
                if conv_data:
                    df_conv = pd.DataFrame(conv_data)
                    if not df_conv.empty:
                        if "timestamp" in df_conv.columns:
                            df_conv["timestamp"] = pd.to_datetime(df_conv["timestamp"], errors='coerce')
                            df_conv = df_conv.sort_values("timestamp", ascending=False)
                            df_conv["timestamp"] = df_conv["timestamp"].dt.strftime("%b %d, %Y - %I:%M %p")
                            
                        cols_to_show = ["timestamp", "user_query", "chart_type", "visualization_generated"]
                        cols_to_show = [c for c in cols_to_show if c in df_conv.columns]
                        render_visual_activity_sheet(
                            df_conv[cols_to_show],
                            cols_to_show,
                            {
                                "timestamp": "Time",
                                "user_query": "Question Asked",
                                "chart_type": "Chart Generated",
                                "visualization_generated": "Success",
                            },
                            "Questions & AI Conversations",
                            "Recent user prompts and whether they produced a visualization.",
                        )
                else:
                    st.info("No questions or conversations logged in this date range.")
                    
            with tab2:
                from analytics import get_all_user_sessions
                user_sessions = get_all_user_sessions(selected_user_id)
                int_data = []
                for s in user_sessions:
                    for i in s.get("interactions", []):
                        timestamp_str = i.get("timestamp")
                        if timestamp_str:
                            try:
                                dt = pd.to_datetime(timestamp_str).to_pydatetime()
                                if dt.tzinfo is not None:
                                    dt = dt.replace(tzinfo=None)
                                if not (start_dt <= dt <= end_dt):
                                    continue
                            except:
                                pass
                                
                        int_data.append({
                            "timestamp": timestamp_str,
                            "action_type": i.get("action"),
                            "action_details": str(i.get("details", ""))
                        })
                
                if int_data:
                    df_int = pd.DataFrame(int_data)
                    if not df_int.empty:
                        if "timestamp" in df_int.columns:
                            df_int["timestamp"] = pd.to_datetime(df_int["timestamp"], errors='coerce')
                            df_int = df_int.sort_values("timestamp", ascending=False)
                            df_int["timestamp"] = df_int["timestamp"].dt.strftime("%b %d, %Y - %I:%M %p")
                            
                        cols_to_interact = ["timestamp", "action_type", "action_details"]
                        cols_to_interact = [c for c in cols_to_interact if c in df_int.columns]
                        render_visual_activity_sheet(
                            df_int[cols_to_interact],
                            cols_to_interact,
                            {
                                "timestamp": "Time",
                                "action_type": "Action",
                                "action_details": "Details",
                            },
                            "Platform Interactions",
                            "Tracked clicks, uploads, generations, refinements, and evaluator activity.",
                        )
                else:
                    st.info("No clicks or interactions logged in this date range.")
                    
            with tab3:
                chats = get_all_user_chats(selected_user_id)
                found_images = False
                
                if chats:
                    st.markdown(
                        """
                        <div class="analytics-filter-heading">
                            <span>User Visualizations</span>
                            <p>Images generated by the AI platform and images uploaded by the user for evaluation.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    for chat in chats:
                        chat_hist = get_chat_history(selected_user_id, chat.get("session_id", ""))
                        if chat_hist:
                            images = chat_hist.get("generated_images", [])
                            for img in images:
                                gen_time = img.get('generated_at', '')
                                if gen_time:
                                    try:
                                        dt = pd.to_datetime(gen_time).to_pydatetime()
                                        if dt.tzinfo is not None:
                                            dt = dt.replace(tzinfo=None)
                                        if not (start_dt <= dt <= end_dt):
                                            continue
                                    except:
                                        pass
                                        
                                found_images = True
                                st.markdown("<div class='analytics-image-card'>", unsafe_allow_html=True)
                                st.write(f"**Query/Context:** {img.get('user_query', 'N/A')}")
                                
                                if gen_time:
                                    try:
                                        gen_time = pd.to_datetime(gen_time).strftime("%b %d, %Y - %I:%M %p")
                                    except:
                                        pass
                                st.write(f"**Time:** {gen_time}")
                                
                                st.caption(f"**Chart:** {img.get('chart_type', 'Unknown')}")
                                try:
                                    url = img.get("path")
                                    if url:
                                        st.image(url, use_container_width=True)
                                except Exception as e:
                                    st.error(f"Could not load image: {e}")
                                st.markdown("</div>", unsafe_allow_html=True)
                
                if not found_images:
                    st.info("No saved images found for this user in this date range.")
    else:
        st.info("No active users found in the database yet.")

    st.write("")
    # Refresh button
    if st.button("Refresh Statistics", type="primary"):
        st.rerun()

# --------------------- Page Routing ---------------------
if menu == "Logout":
    perform_logout()
elif menu == "Home":
    render_home()
elif menu == "Viz Generator":
    run_viz_generator()
elif menu == "Viz Evaluator":
    run_viz_evaluator()
elif menu == "Analytics Dashboard":
    if st.session_state.get("role") == "admin":
        render_analytics()
    else:
        st.error("❌ Access Denied: Analytics is only available for administrators")

# Put this once at the top of your app to inject the CSS


def render_footer():
    st.markdown(
        """
        <div class="footer">
            © 2026 VisualStats. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

render_footer()
