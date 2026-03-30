import os
import json
import base64
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

# Professional Styling
st.markdown("""
    <style>
        /* Color scheme */
        :root {
            --primary: #0066CC;
            --primary-dark: #0052A3;
            --secondary: #10B981;
            --danger: #EF4444;
            --warning: #F59E0B;
            --light: #F8FAFC;
            --border: #E2E8F0;
            --text: #1E293B;
            --text-secondary: #64748B;
        }
        
        .stApp {
            background-color: #F8FAFC;
        }
        
        /* Main content area */
        .stMain {
            background-color: #F8FAFC;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #1E293B;
            font-weight: 700;
        }
        
        /* Section headers */
        .section-header {
            background: linear-gradient(135deg, #0066CC, #0052A3);
            color: white !important;
            padding: 20px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 700;
            margin: 20px 0;
        }
        
        /* Cards & Containers */
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #E2E8F0;
            margin-bottom: 15px;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            border: none;
            font-weight: 600;
            transition: all 0.3s ease;
            background: linear-gradient(135deg, #0066CC, #0052A3);
            color: white !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 102, 204, 0.3);
        }
        
        /* File uploader */
        .stFileUploader {
            border-radius: 8px;
            border: 2px dashed #0066CC;
        }
        
        /* Text input & Select */
        .stTextInput, .stSelectbox, .stDateInput {
            border-radius: 8px;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: white;
            border-bottom: 2px solid #E2E8F0;
            font-weight: 600;
            color: #64748B;
        }
        
        .stTabs [aria-selected="true"] {
            color: #0066CC;
            border-bottom: 3px solid #0066CC !important;
        }
        
        /* Metric cards */
        .stMetric {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Alert boxes */
        .stAlert {
            border-radius: 8px;
            padding: 15px 20px;
        }
        
        /* Sidebar */
        .stSidebar {
            background: white;
            border-right: 1px solid #E2E8F0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize clients
client = OpenAI(api_key=API_KEY)
lida = Manager(text_gen=llm("openai"))
textgen_config = TextGenerationConfig(n=1, temperature=0.2, model="gpt-4o", use_cache=True)
validated = ""

# --------------------- Authentication Check ---------------------
initialize_data_structure()

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

@st.dialog("Welcome to VisualStats", width="large")
def auth_dialog():
    st.markdown("<h3 style='text-align: center; color: #1E293B;'>Secure Access</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B;'>Select an access method below to continue.</p>", unsafe_allow_html=True)
    
    st.write("")
    tab1, tab2 = st.tabs(["👤 User Login", "🛡️ Admin Portal"])
    
    with tab1:
        st.markdown("<p style='color: #64748B;'>Sign in, register instantly with your PIN, or continue as guest.</p>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username", key="user_name")
        pin = st.text_input("4-Digit PIN", type="password", max_chars=4, placeholder="****", key="user_pin")
        
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login / Register", use_container_width=True, type="primary"):
                if not username or not pin or len(pin) != 4 or not pin.isdigit():
                    st.error("Please enter a username and a valid 4-digit PIN.")
                else:
                    from auth import authenticate_user, create_session
                    result = authenticate_user(username, pin)
                    if isinstance(result, str):
                        st.error(result)  # e.g., Invalid PIN or purely alphabetical
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
                        
                        st.rerun()
        with col2:
            if st.button("Continue as Guest", use_container_width=True):
                from auth import create_guest_user, create_session
                guest_user = create_guest_user()
                st.session_state.is_authenticated = True
                st.session_state.user_info = guest_user
                st.session_state.user_id = guest_user.get("user_id")
                st.session_state.username = guest_user.get("username")
                st.session_state.role = guest_user.get("role", "guest")
                st.session_state.session_token = create_session(st.session_state.user_id, guest_user.get("username"), "guest")
                st.session_state.auth_message = "Logged in as Guest. Your session data will not be permanently saved. 🕵️‍♂️"
                st.rerun()

    with tab2:
        st.markdown("<p style='color: #64748B;'>Enter your Admin credentials and the Master Code to access the dashboard.</p>", unsafe_allow_html=True)
        admin_user = st.text_input("Admin Username", placeholder="Enter admin username", key="admin_user_input")
        admin_pin = st.text_input("Admin 4-Digit PIN", type="password", max_chars=4, placeholder="****", key="admin_pin_input")
        master_code = st.text_input("Admin Master Code", type="password", placeholder="Enter 6-digit master code", key="admin_master_code")
        
        st.write("")
        col3, col4 = st.columns(2)
        with col3:
            if st.button("Login as Admin", use_container_width=True, type="primary"):
                if not admin_user or not admin_pin or len(admin_pin) != 4 or not admin_pin.isdigit():
                    st.error("Please enter a username and a valid 4-digit PIN.")
                elif not master_code:
                    st.error("Master code is required to login as Admin.")
                else:
                    from auth import login_admin, create_session
                    result = login_admin(admin_user, admin_pin, master_code)
                    if isinstance(result, str):
                        st.error(result)
                    else:
                        st.session_state.is_authenticated = True
                        st.session_state.user_info = result
                        st.session_state.user_id = result.get("user_id")
                        st.session_state.username = result.get("username")
                        st.session_state.role = "admin"
                        st.session_state.session_token = create_session(st.session_state.user_id, result.get("username"), "admin")
                        st.session_state.auth_message = f"Welcome back, Admin {result.get('username')}! 🛡️"
                        st.rerun()
        with col4:
            if st.button("Register New Admin", use_container_width=True):
                if not admin_user or not admin_pin or len(admin_pin) != 4 or not admin_pin.isdigit():
                    st.error("Please enter a username and a valid 4-digit PIN.")
                elif not master_code:
                    st.error("Master code is required to register an admin.")
                else:
                    from auth import register_admin, create_session
                    result = register_admin(admin_user, admin_pin, master_code)
                    if result is None:
                        st.error("Registration failed. Invalid master code or username already taken.")
                    else:
                        st.success("Admin registered successfully! Logging in...")
                        st.session_state.is_authenticated = True
                        st.session_state.user_info = result
                        st.session_state.user_id = result.get("admin_id")
                        st.session_state.username = result.get("admin_username")
                        st.session_state.role = "admin"
                        st.session_state.session_token = create_session(st.session_state.user_id, result.get("admin_username"), "admin")
                        st.session_state.auth_message = f"Admin account '{result.get('admin_username')}' created. Welcome to the dashboard! 🛡️"
                        st.rerun()

if not st.session_state.is_authenticated:
    # Add a blurred background effect or a clean overlay if desired
    st.markdown("""
    <style>
        .stMain { filter: blur(5px); pointer-events: none; }
    </style>
    """, unsafe_allow_html=True)
    auth_dialog()
    st.stop()
    
# Show success toast from login if exists
if "auth_message" in st.session_state:
    st.toast(st.session_state.auth_message, icon="✅")
    del st.session_state.auth_message

# --------------------- Database Initialization ---------------------
db = get_db()

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
- Provide a brief interpretation of the chart in 3-4 sentences, summarizing its main insights.
- Verify if the chart has proper x-axis and y-axis labels that are completely visible and a title.
- Check whether labels and titles are properly aligned (centered).
- Ensure the chart size is appropriate (width and height).
- Evaluate if the color palette is distinct and accessible (avoid red-green conflicts).
- Assess the readability of fonts (size between 10-20 and clear fonts).
- Verify consistent axis scaling with ticks.
- Confirm that the legend is present, well-positioned, and clear.

If all checks pass, respond with: "Visualization quality validation completed."
Otherwise, provide specific feedback on what needs to be improved.
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


def refine_query(query, chart_selected):
    prompt = f"""
    You are an expert in data visualization and analytics.

    User Query:
    "{query}"

    Task:
    - Rewrite the user's query to make it clear, concise, and well-suited for visualization using the recommended chart type: "{chart_selected}".
    - Ensure the refined query is specific and actionable for chart generation.
    - Briefly explain why "{chart_selected}" is the most appropriate chart type for this query, referencing the validation details if relevant.
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
        # ----- Global CSS -----
    st.markdown(
        """
        <style>
        /* Hide Streamlit footer & menu */
        #MainMenu, footer {visibility: hidden;}

        /* Hero section */
        .hero {
            background: linear-gradient(135deg, #0066CC, #0052A3);
            color: white;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            height: 22vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .hero h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2.8rem;
            font-weight: 800;
        }
        .hero p {
            font-size: 1.1rem;
            margin: 0;
            opacity: 0.95;
            font-weight: 500;
        }

        /* Section headers */
        .section-header {
            color: #0066CC;
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #0066CC;
        }

        /* Card style for goals & summaries */
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            margin-bottom: 1.5rem;
            border: 1px solid #E2E8F0;
        }
        .card h4 {
            color: #0052A3;
            margin-top: 0;
        }
        .card p {
            margin: 0.75rem 0;
            color: #1E293B;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Textarea styling override */
        textarea {
            border: 2px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            font-size: 14px !important;
        }
        textarea:focus {
            border-color: #0066CC !important;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ----- Hero -----
    st.markdown(
        """
        <div class="hero">
          <h1>Visualization Evaluator</h1>
          <p>Upload your visualizations - LLM will inspect every element and provide smart, actionable feedback</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    uploaded_file = st.file_uploader("📂 Upload your  image file", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
        except Exception as e:
            st.error(f"Error processing the uploaded image: {e}")
            return
        
        # Save the uploaded image to a temporary file
        temp_image_path = "output_image.png"
        image.save(temp_image_path)
        st.image(temp_image_path, caption="Uploaded Visualization", use_container_width=True)
        
        visualization_quality_rules = load_json("quality_rules.json").get("VISUALIZATION_QUALITY_RULES", {})
        
        # Add a button to trigger the evaluation
        if st.button("Evaluate Visualization"):
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
                
                st.markdown("## ✅ Visualization Quality Feedback")
                # Styled feedback card
                st.markdown(
                    f"""
                    <div style="background-color: #F0FDF4; border-left: 4px solid #10B981; padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                        <h4 style="color: #10B981; margin-top: 0;">📋 Feedback Summary</h4>
                        <p style="font-size: 0.95rem; line-height: 1.7; color: #1E293B; margin: 0;">{feedback}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

def deduplicate(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

# --------------------- Viz Generator UI ---------------------
def run_viz_generator():
    """Run the visualization generator interface with enhanced UI styling."""

    # ----- Global CSS -----
    st.markdown(
        """
        <style>
        /* Hide Streamlit footer & menu */
        #MainMenu, footer {visibility: hidden;}

        /* Hero section */
        .hero {
            background: linear-gradient(135deg, #0066CC, #0052A3);
            color: white;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            height: 22vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .hero h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2.8rem;
            font-weight: 800;
        }
        .hero p {
            font-size: 1.1rem;
            margin: 0;
            opacity: 0.95;
            font-weight: 500;
        }

        /* Section headers */
        .section-header {
            color: #0066CC;
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #0066CC;
        }

        /* Card style for goals & summaries */
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            margin-bottom: 1.5rem;
            border: 1px solid #E2E8F0;
        }
        .card h4 {
            color: #0052A3;
            margin-top: 0;
        }
        .card p {
            margin: 0.75rem 0;
            color: #1E293B;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Textarea styling override */
        textarea {
            border: 2px solid #E2E8F0 !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            font-size: 14px !important;
        }
        textarea:focus {
            border-color: #0066CC !important;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ----- Hero -----
    st.markdown(
        """
        <div class="hero">
          <h1>Visualization Generator</h1>
          <p>Turn your data into visuals and insights and have conversations with your charts</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- File Uploader -----
    uploaded_file = st.file_uploader("📂 Upload your dataset", type=["csv", "xlsx", "xls", "json", "xml", "txt"])
    if not uploaded_file:
        return

    # Save & convert
    file_path = uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Log dataset upload
    try:
        file_size = len(uploaded_file.getvalue())
        dataset_id = db.log_dataset_upload(
            st.session_state.user_id,
            uploaded_file.name,
            uploaded_file.type,
            file_size,
            0,  # Will be updated after reading CSV
            0,  # Will be updated after reading CSV
            []  # Will be updated after reading CSV
        )
        st.session_state.current_dataset_id = dataset_id
        
        db.log_interaction(st.session_state.user_id, "dataset_upload", {
            "filename": uploaded_file.name,
            "file_size": file_size,
            "dataset_id": dataset_id
        }, "Viz Generator")
        
        # Log to analytics module (new system)
        log_interaction(
            st.session_state.get("user_id") or st.session_state.get("admin_id"),
            st.session_state.username,
            st.session_state.session_id,
            "file_upload",
            {
                "filename": uploaded_file.name,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "file_type": uploaded_file.type or "unknown"
            }
        )
        
        st.session_state.interaction_count["datasets_uploaded"] += 1
    except Exception as e:
        st.warning(f"Could not log interaction: {e}")

    csv_path = convert_to_csv(file_path)
    if not csv_path:
        st.error("Could not convert file to CSV.")
        st.stop()

    # Load & summarize
    df = pd.read_csv(csv_path)
    
    summary = lida.summarize(csv_path, summary_method="default", textgen_config=textgen_config)
    st.markdown('<div class="section-header">Data Overview</div>', unsafe_allow_html=True)
    
    for field in summary.get("fields", []):
        col_name = field.get("column")
        props = field.get("properties", {})
        dtype = props.get("dtype", "").lower()

        # Auto-infer semantic type
        if dtype == "number":
            semantic_type = "quantitative"
        elif dtype == "category":
            semantic_type = "categorical"
        elif "date" in col_name.lower() or dtype == "datetime":
            semantic_type = "temporal"
        else:
            semantic_type = "text"

        # Generate description if missing or empty
        description = props.get("description", "").strip()
        if not description:
            description = f"{col_name.replace('_', ' ').capitalize()} of the record"

        # Update the properties
        props["semantic_type"] = semantic_type
        props["description"] = description
    
    
    overview = gen_summary(summary)
    st.write(overview)

    with st.expander("📋 Full Data Summary"):
        st.json(summary)
    
    # Save dataset summary to chat storage
    try:
        save_dataset_summary(
            st.session_state.user_id,
            st.session_state.session_id,
            summary
        )
    except Exception as e:
        print(f"Error saving dataset summary: {e}")

    # ----- Suggested Goals -----
    goals = lida.goals(summary, n=2, textgen_config=textgen_config)
    st.markdown('<div class="section-header">💡 Suggested Goals</div>', unsafe_allow_html=True)
    for goal in goals:
        st.markdown(
            f"""
            <div class="card">
              <h4 style="color:#ff7f0e;">🎯 Goal {goal.index+1}</h4>
              <p><strong>🔍 Question:</strong> {goal.question}</p>
              <p><strong>📊 Visualization:</strong> {goal.visualization}</p>
              <p><strong>🧠 Rationale:</strong> {goal.rationale}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ----- User Query & Validation -----
    st.markdown('<div class="section-header">📝 Define Your Own Goal</div>', unsafe_allow_html=True)
    query = st.text_area("Ask a question or describe your chart goal", height=150)

    if "chart_options" not in st.session_state:
        st.session_state.chart_options = []
    
    if "validated" not in st.session_state:
        st.session_state.validated = {}

    if st.button("Generate Graph"):
        # Log user query
        try:
            db.log_interaction(st.session_state.user_id, "query_submitted", {
                "query": query
            }, "Viz Generator")
            st.session_state.interaction_count["queries_made"] += 1
        except Exception as e:
            st.warning(f"Could not log query: {e}")
        
        # Save user query to chat history
        save_chat_message(
            st.session_state.user_id,
            st.session_state.session_id,
            "user",
            query,
            metadata={"source": "viz_generator"}
        )
        
        validated = validate_user_query(query, summary, load_json("chart_selection.json")["VALIDATION_RULES"])
        
        # Safe extraction with fallback in case the LLM misses the key
        all_chart_types_str = validated.get('All Chart Types', validated.get('Recommended chart', ''))
        print(all_chart_types_str)

        if validated.get("Valid") != "Yes":
            st.error(f"Invalid query: {validated.get('Reason', 'Unknown error')}")
            st.stop()
        st.session_state.validated = validated
        
        # Split string safely, avoiding empty strings
        st.session_state.chart_options = [c.strip() for c in all_chart_types_str.split(",") if c.strip()]
        
        # Fallback if somehow completely empty
        if not st.session_state.chart_options:
            st.session_state.chart_options = ["Bar/Column Chart"]
            
        print(st.session_state.chart_options)
  

    if st.session_state.chart_options:
        validated = st.session_state.validated
        with st.expander("🔍 Visualization Details", expanded=True):
            st.markdown(f"""
            **🔍 Variables Involved:**  
            {", ".join(validated.get("All Variables involved", [])) if isinstance(validated.get("All Variables involved", []), list) else validated.get("All Variables involved", "")}

            **🔗 Relationship Between Variables:**  
            {validated.get("Relationship between variables", "")}

            **📊 Chart Mentioned in Prompt:**  
            {validated.get("Chart mentioned in prompt", "")}

            **✅ Recommended Chart Type:**  
            {validated.get("Recommended chart", "")}

            **🧠 Justification:**  
            {validated.get("Justification", "")}
                            """)
            
            validated = st.session_state.validated
            
        chart_selected = st.selectbox(
            'Select chart type',
            st.session_state.chart_options,
            index=0,
            key="chart_selected"
        )

        refined = refine_query(query, chart_selected)
        
        # Log AI interaction
        try:
            db.log_ai_conversation(
                st.session_state.user_id,
                query,
                refined,
                True,
                chart_selected
            )
        except Exception as e:
            st.warning(f"Could not log AI conversation: {e}")
        
        # Save refined query to chat history
        save_chat_message(
            st.session_state.user_id,
            st.session_state.session_id,
            "assistant",
            refined,
            metadata={
                "response_time_seconds": 0,
                "model": "gpt-4o",
                "chart_type": chart_selected,
                "source": "viz_generator"
            }
        )
        
        st.info(f"{refined}")
            
        # generate initial chart
        query_start_time = time.time()
        charts = lida.visualize(
            summary=summary,
            goal=refined,
            textgen_config=textgen_config,
            library="seaborn"
        )
        ai_response_time = time.time() - query_start_time
        if charts:
            base_instructions = [
                    "Don't change the chart type until explicitly mentioned in the instructions.",
                    "Ensure that long x-axis or y-axis labels are not truncated. Rotate or wrap them if needed.",
                    "Adjust the chart margins and layout so that x-axis and y-axis titles are fully visible and not cut off. If required move them closer to the chart.",
                    "Fit the complete chart within the canvas, including all labels and axis titles.",
                    "Ensure the x-axis title is fully visible by adjusting bottom padding or layout.",
                    "If the x-axis labels are long, rotate them or reduce font size to avoid overlap.",
                    "Use colors that are aesthetically pleasing and have good contrast for accessibility.",
                    "Maintain appropriate font sizes for readability without crowding the chart.",
                    "Avoid clutter and minimize grid lines or unnecessary visual elements.",
                    "Use consistent spacing and alignment for a clean, professional look.",
                    "Keep the chart simple and easy to understand, avoiding unnecessary complexity.",
                ]
            st.session_state["chart_code"] = charts[0].code
            st.session_state["base_edit_instructions"] = base_instructions
            chart_placeholder = st.empty()
            

            with st.spinner("Generating final chart..."):
                final_charts_list = lida.edit(
                    code=charts[0].code,
                    summary=summary,
                    instructions=base_instructions,
                    library="seaborn",
                    textgen_config=textgen_config
                )
                
                if final_charts_list and len(final_charts_list) > 0:
                    final_chart = final_charts_list[0]
                else:
                    # Fallback to the initial chart if LIDA edit engine fails
                    st.warning("⚠️ Could not apply all stylistic refinements. Displaying the base chart.")
                    final_chart = charts[0]
                    
            img = base64_to_image(final_chart.raster)
            chart_placeholder.image(img, use_container_width=True)
            st.session_state["chart_code"] = final_chart.code
            
            # Save generated image to chat storage
            image_metadata = None
            try:
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_data = img_byte_arr.getvalue()

                image_metadata = save_generated_image(
                    st.session_state.user_id,
                    st.session_state.session_id,
                    img_data,
                    chart_type=chart_selected,
                    query=query,
                    image_format="png"
                )
                if image_metadata:
                    st.session_state.interaction_count["visualizations_created"] += 1
            except Exception as e:
                print(f"Error saving generated image: {e}")
            # Log visualization creation
            try:
                db.log_visualization(
                    st.session_state.user_id,
                    st.session_state.get("current_dataset_id", "unknown"),
                    chart_selected,
                    validated.get("All Variables involved", []),
                    query,
                    "generated",
                    image_path=image_metadata.get("path") if image_metadata else None,
                    source_type='generated'
                )
            except Exception as e:
                print(f"Error logging visualization: {e}")
                
                # Log to analytics module (new system) - AI query
                log_interaction(
                    st.session_state.get("user_id") or st.session_state.get("admin_id"),
                    st.session_state.username,
                    st.session_state.session_id,
                    "ai_query",
                    {
                        "user_query": query[:100],
                        "response_time_seconds": round(ai_response_time, 2),
                        "model_used": "GPT-4o",
                        "chart_type": chart_selected
                    }
                )
                
                st.session_state.interaction_count["visualizations_created"] += 1
            except Exception as e:
                st.warning(f"Could not log visualization: {e}")

            # ----- Chart Tweaks -----
            st.markdown('<div class="section-header">✏️ Refine Your Chart</div>', unsafe_allow_html=True)
            extra = st.text_area("Additional instructions", height=100)
            if st.button("Update Chart", key="update_chart") and extra.strip():
                if "chart_code" not in st.session_state:
                    st.error("Generate a chart first!")
                else:
                    # Log chart refinement
                    refine_start_time = time.time()
                    try:
                        db.log_interaction(st.session_state.user_id, "chart_refined", {
                            "refinement_instructions": extra
                        }, "Viz Generator")
                    except Exception as e:
                        st.warning(f"Could not log refinement: {e}")
                    
                    with st.spinner("Generating final chart..."):
                        chart_code = st.session_state.get("chart_code")
                        instr = ["Keep all the properties of the existing chart, additionally add:"] + [extra]
                        updated_list = lida.edit(
                            code=chart_code,
                            summary=summary,
                            instructions=instr,
                            library="seaborn",
                            textgen_config=textgen_config
                        )
                        if not updated_list:
                            st.warning("⚠️ Refinement failed. Please try phrasing your request differently.")
                            st.stop()
                        updated = updated_list[0]
                        refine_response_time = time.time() - refine_start_time
                        updated_img = base64_to_image(updated.raster)
                        chart_placeholder.image(updated_img, use_container_width=True)
                        
                        # Log to analytics module - chart refinement
                        try:
                            log_interaction(
                                st.session_state.get("user_id") or st.session_state.get("admin_id"),
                                st.session_state.username,
                                st.session_state.session_id,
                                "chart_refinement",
                                {
                                    "instruction_preview": extra[:50],
                                    "response_time_seconds": round(refine_response_time, 2)
                                }
                            )
                        except Exception as e:
                            pass

# --------------------- Main App Setup ---------------------





# --------------------- Shared CSS ---------------------
st.markdown(
    """
    <style>
    :root {
        --brand-primary: #4F46E5;   /* Indigo 600 */
        --brand-accent: #10B981;    /* Emerald 500 */
        --text-light: #F8FAFC;      /* Slate 50 */
        --text-mid: #CBD5E1;        /* Slate 300 */
        --bg-hero-start: #3730A3;   /* Indigo 700 */
        --bg-hero-end: #047857;     /* Emerald 700 */
    }

    /* Sidebar menu overrides */
    .sidebar .menu-container {
        padding: 1rem 0;
    }
    .sidebar .nav-link {
        font-size: 1rem !important;
        color: var(--brand-primary) !important;
        margin: 0.5rem 0 !important;
    }
    .sidebar .nav-link:hover {
        background-color: rgba(79, 70, 229, 0.1) !important;
    }
    .sidebar .nav-link-selected {
        background-color: var(--brand-primary) !important;
        color: var(--text-light) !important;
    }
    .sidebar .icon {
        color: var(--brand-primary) !important;
        font-size: 1.25rem !important;
    }

    /* (Rest of your Home page CSS here…) */
    /* Hero, features, buttons, footer… */
    /* … */
    </style>
    """,
    unsafe_allow_html=True
)

# ——— Sidebar ———
with st.sidebar:
    # App title / logo area

    # Load and encode
    with open("home_icon.png", "rb") as f:
        data = f.read()
    b64_home = base64.b64encode(data).decode()

    st.markdown(f"""
<div style="
    text-align: center;
    padding: 0.5rem 0 0.25rem 0;
    background-color: #FFFFFF;
    border-bottom: 0.5px solid #E3E3E3;
">
  <img
    src="data:image/png;base64,{b64_home}"
    alt="logo"
    width="80"
    style="
      margin: 0.5 0 0 0.1rem;  
      width: 80px;
      height: auto;
    "
  />
  <h2 style="
      margin: 0 2rem 0 0;             /* no top or bottom margin */
      color: #0066CC;
      font-family: Arial, sans-serif;
      line-height: 1.2;      /* tighten line height */
  ">
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
    
    menu = option_menu(
    menu_title=None,
    options=menu_options,
    icons=menu_icons,
    default_index=0,
    orientation="vertical",
    styles={
        "container": {
            "padding": "1rem 0.5rem",
            "background-color": "#FFFFFF",
            "border-right": "1px solid #E3E3E3"
        },
        # default icon color
        "nav-link-icon": {
            "color": "#0066CC",
            "font-size": "1.3rem",
            "margin": "0 0.5rem 0 0"
        },
        # each link (text)
        "nav-link": {
            "font-size": "1.05rem",
            "text-align": "left",
            "margin": "0.25rem 0",
            "padding": "0.5rem 1rem",
            "border-radius": "0.5rem",
            "color": "#333333"
        },
        # hover state (link + icon both pick this up)
        "nav-link:hover": {
            "background-color": "#F1F1F1",
            "color": "#000000"
        },
        # selected link background + text
        "nav-link-selected": {
            "background-color": "#0066CC",
            "color": "#FFFFFF",
            "font-weight": "bold"
        },
        # and here’s the magic – selected icon turns white
        "nav-link-selected-icon": {
            "color": "#FFFFFF"
        }
    }
)

# --------------------- Home Page Renderer ---------------------

# Load and encode images
with open("viz_gen.png", "rb") as f:
    data = f.read()
b64_gen = base64.b64encode(data).decode()

with open("viz_eval.png", "rb") as f:
    data = f.read()
b64_eval = base64.b64encode(data).decode()

def render_home():
    st.markdown(
        """
        <style>
        /* Hero */
        .hero {
            position: relative;
            background: linear-gradient(135deg, #0066CC, #0052A3);
            height: 25vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
        }
        .hero-content h1 {
            font-size: 3.5rem;
            margin: 0.5rem 0;
            font-weight: 800;
        }
        .hero-content p {
            font-size: 1.3rem;
            margin: 1rem 0 0;
            color: rgba(255,255,255,0.95);
            font-weight: 500;
        }
        .btn-primary, .btn-secondary {
            border: none;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        .btn-primary {
            background-color: var(--brand-primary);
            color: var(--text-light);
        }
        .btn-primary:hover { opacity: 0.85; }
        .btn-secondary {
            background-color: var(--text-light);
            color: var(--brand-primary);
            border: 2px solid var(--brand-primary);
        }
        .btn-secondary:hover { opacity: 0.85; }

        /* Features grid */
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        .feature-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            padding: 2rem 1.5rem;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid #E2E8F0;
        }
        .feature-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 12px 24px rgba(0, 102, 204, 0.15);
        }
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .feature-title {
            font-size: 1.2rem;
            margin-bottom: 0.75rem;
            color: #1E293B;
            font-weight: 700;
        }
        .feature-desc {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 1.5rem 0;
            color: var(--text-mid);
            font-size: 0.875rem;
        }
        .footer a {
            color: var(--brand-primary);
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
         /* Images grid */
        .images-grid {
            margin: 3rem 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2.5rem;
        }
        .image-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            overflow: hidden;
            border: 1px solid #E2E8F0;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .image-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 102, 204, 0.12);
        }
        .image-card img {
            width: 100%;
            height: auto;
            display: block;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Hero
    st.markdown(
        """
        <div class="hero">
          <div class="hero-content">
            <h1>VisualStats</h1>
            <p>Bridge Gap Between Data & Decision with AI‑Driven Visualizations</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # new images grid
    # 3) Inject your images via an f‑string
    html = f"""
    
    <div class="images-grid">
    <div class="image-card">
        <img src="data:image/png;base64,{b64_gen}" alt="Viz Generator"/>
    </div>
    <div class="image-card">
        <img src="data:image/png;base64,{b64_eval}" alt="Viz Evaluator"/>
    </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --------------------- Analytics Dashboard Renderer ---------------------
def render_analytics():
    """Render the analytics dashboard with platform statistics."""
    st.markdown(
        """
        <style>
        /* Hero section */
        .hero {
            background: linear-gradient(135deg, #0c2d55 100%, #0c2d55 100%);
            color: white;
            padding: 0.5rem 0.5rem;
            border-radius: 0.75rem;
            text-align: center;
            margin-bottom: 2rem;
            height: 15vh;
        }
        .hero h1 {
            margin-top: 1rem;
            font-size: 3rem;
        }
        .hero p {
            font-size: 1.25rem;
            margin-bottom: 2rem;
        }
        /* Metric card */
        .metric-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 1rem;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #0066CC;
            margin: 0.5rem 0;
        }
        .metric-label {
            color: #666;
            font-size: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
        <div class="hero">
          <h1>📊 Analytics Dashboard</h1>
          <p>Platform Statistics & User Behavior Insights</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Get statistics from database
    stats = db.get_dashboard_stats()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">👥 Total Users</div>
                <div class="metric-value">{stats['total_users']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">📊 Total Visualizations</div>
                <div class="metric-value">{stats['total_visualizations']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">📂 Total Datasets</div>
                <div class="metric-value">{stats['total_datasets']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">📈 Total Interactions</div>
                <div class="metric-value">{stats['total_interactions']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Top chart types
    st.subheader("📊 Top Chart Types Used")
    if stats['top_chart_types']:
        import pandas as pd
        import plotly.express as px
        
        df_charts = pd.DataFrame(stats['top_chart_types'])
        
        # Create a beautiful Plotly bar chart
        fig = px.bar(
            df_charts, 
            x='viz_type', 
            y='count',
            color='viz_type',
            text='count',
            labels={'viz_type': 'Chart Type', 'count': 'Visualizations Generated'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='outside', textfont_size=14)
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Count",
            showlegend=False,
            height=400,
            margin=dict(t=20, b=20, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("View Detailed List"):
            for idx, item in enumerate(stats['top_chart_types'], 1):
                st.write(f"{idx}. **{item['viz_type']}**: {item['count']} visualizations")
    # Average session duration
    st.subheader("⏱️ Session Statistics")
    if stats['avg_session_duration']:
        minutes = int(stats['avg_session_duration'] // 60)
        seconds = int(stats['avg_session_duration'] % 60)
        st.metric("Average Session Duration", f"{minutes}m {seconds}s")
    else:
        st.info("No session data available yet.")
    
    # Top actions
    st.subheader("🎯 Most Common User Actions")
    if stats['top_actions']:
        action_data = [(item['action_type'], item['count']) for item in stats['top_actions']]
        for idx, (action, count) in enumerate(action_data, 1):
            st.write(f"{idx}. **{action}**: {count} times")
    else:
        st.info("No interaction data available yet.")
    
    st.markdown("---")
    st.subheader("👤 Detailed User Analysis")
    st.markdown("Select a user to review their specific questions asked and visualizations generated.")
    
    from auth import get_all_user_profiles
    user_profiles = get_all_user_profiles()
    active_user_ids = db.get_all_active_users()
    
    if active_user_ids:
        # Create a display mapping: display_name -> user_id
        # Fallback to just the user_id if they are a guest or deleted
        user_options = {}
        for uid in active_user_ids:
            name = user_profiles.get(uid, f"Guest / Unknown ({uid[:8]})")
            user_options[f"{name}"] = uid
            
        selected_label = st.selectbox("Select User Activity:", options=["-- Select a User --"] + list(user_options.keys()))
        
        if selected_label and selected_label != "-- Select a User --":
            selected_user_id = user_options[selected_label]
            
            tab1, tab2, tab3 = st.tabs(["💬 Questions & AI Conversations", "🖱️ Platform Interactions", "🖼️ Visualizations & Images"])

            with tab1:
                conversations = db.get_user_conversations(selected_user_id)
                if conversations:
                    df_conv = pd.DataFrame(conversations)
                    if not df_conv.empty:
                        if "timestamp" in df_conv.columns:
                            df_conv["timestamp"] = pd.to_datetime(df_conv["timestamp"], errors='coerce').dt.strftime("%b %d, %Y - %I:%M %p")
                            
                        cols_to_show = ["timestamp", "user_query", "chart_type", "visualization_generated"]
                        cols_to_show = [c for c in cols_to_show if c in df_conv.columns]
                        st.dataframe(
                            df_conv[cols_to_show].sort_values("timestamp", ascending=False),
                            use_container_width=True,
                            column_config={
                                "timestamp": "Time",
                                "user_query": "Question Asked",
                                "chart_type": "Chart Generated",
                                "visualization_generated": "Success"
                            }
                        )
                else:
                    st.info("No questions or conversations logged for this user.")
                    
            with tab2:
                interactions = db.get_user_interactions(selected_user_id)
                if interactions:
                    df_int = pd.DataFrame(interactions)
                    if not df_int.empty:
                        if "timestamp" in df_int.columns:
                            df_int["timestamp"] = pd.to_datetime(df_int["timestamp"], errors='coerce').dt.strftime("%b %d, %Y - %I:%M %p")
                            
                        cols_to_interact = ["timestamp", "action_type", "action_details"]
                        cols_to_interact = [c for c in cols_to_interact if c in df_int.columns]
                        st.dataframe(
                            df_int[cols_to_interact].sort_values("timestamp", ascending=False), 
                            use_container_width=True,
                            column_config={
                                "timestamp": "Time",
                                "action_type": "Action",
                                "action_details": "Details"
                            }
                        )
                else:
                    st.info("No clicks or interactions logged for this user.")
                    
            with tab3:
                visualizations = db.get_user_visualizations(selected_user_id)
                if visualizations:
                    st.markdown("### User Visualizations")
                    st.markdown("Images generated by the AI platform and images uploaded by the user for evaluation.")
                    
                    found_images = False
                    for viz in visualizations:
                        path_str = viz.get("image_path")
                        if path_str and os.path.exists(path_str):
                            found_images = True
                            st.markdown("---")
                            st.write(f"**Query/Context:** {viz.get('user_query', 'N/A')}")
                            
                            gen_time = viz.get('generated_at', '')
                            if gen_time:
                                try:
                                    gen_time = pd.to_datetime(gen_time).strftime("%b %d, %Y - %I:%M %p")
                                except:
                                    pass
                            st.write(f"**Time:** {gen_time}")
                            
                            source = viz.get("source_type", "generated")
                            st.caption(f"**Type:** {'Uploaded for Evaluation' if source == 'uploaded' else 'AI Generated Platform Chart'} | **Chart:** {viz.get('viz_type', 'Unknown')}")
                            try:
                                import PIL.Image as Image
                                user_img = Image.open(path_str)
                                st.image(user_img, use_container_width=True)
                            except Exception as e:
                                st.error(f"Could not load image: {e}")
                    
                    if not found_images:
                        st.info("No saved images found for this user. New images will appear here once generated or uploaded.")
                else:
                    st.info("No visualizations logged for this user.")
    else:
        st.info("No active users found in the database yet.")

    st.write("")
    # Refresh button
    if st.button("🔄 Refresh Statistics", type="primary"):
        st.rerun()

# --------------------- Page Routing ---------------------
if menu == "Logout":
    # Finalize current session in analytics
    from auth import end_session
    finalize_session(st.session_state.get("user_id") or st.session_state.get("admin_id"), st.session_state.session_id)
    if "session_token" in st.session_state:
        end_session(st.session_state.session_token)
    st.session_state.clear()
    st.success("Logged out successfully!")
    import time
    time.sleep(1)
    st.rerun()
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
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 10rem;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #444;
        text-align: center;
        padding: 0.5rem 0;
        font-size: 0.875rem;
        box-shadow: 0 -1px 4px rgba(0,0,0,0.1);
        z-index: 100;
    }
    /* Add some padding to the bottom of the main content so it doesn't get hidden */
    .main-content {
        padding-bottom: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

def render_footer():
    st.markdown(
        """
        <div class="footer">
            © 2025 VisualStats. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

render_footer()
