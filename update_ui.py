import re
import os

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Remove all st.markdown("""<style>...</style>""") calls
pattern = r'st\.markdown\(\s*f?"""\s*<style>.*?</style>\s*"""\s*,\s*unsafe_allow_html=True,?\s*\)'
content_cleaned = re.sub(pattern, '', content, flags=re.DOTALL)

# There is one with st.markdown(f"""...<style>...</style>...""") maybe? 
# Wait, let's just remove the <style>...</style> blocks themselves if they are embedded in larger markdown blocks, 
# but it seems they are usually in their own st.markdown calls.
# Let's see:
content_cleaned = re.sub(r'<style>.*?</style>', '', content_cleaned, flags=re.DOTALL)

# We still need to inject the Steep CSS at the top.
# Let's find: `os.environ["OPENAI_API_KEY"] = API_KEY` and insert after it.

STEEP_CSS = """
st.markdown('''
<style>
/* Steep UI Core Theme */
:root {
  --color-ink: #17191c;
  --color-pure-white: #ffffff;
  --color-fog: #f7f7f8;
  --color-ash: #4c4c4c;
  --color-graphite: #777b86;
  --color-dove: #a3a6af;
  --color-slate: #8b8c8d;
  --color-obsidian: #000000;
  --color-rust: #5d2a1a;
  --color-apricot-wash: #fbe1d1;
  --color-sky-wash: #d3e3fc;

  --font-signifier: 'GT Sectra', 'Tiempos Headline', 'Source Serif Pro', ui-serif, serif;
  --font-sohne: 'Inter', 'Untitled Sans', ui-sans-serif, system-ui, sans-serif;

  --shadow-subtle: rgba(4, 23, 43, 0.05) 0px 0px 0px 1px, rgba(0, 0, 0, 0.1) 0px 20px 25px -5px, rgba(0, 0, 0, 0.1) 0px 8px 10px -6px;
}

/* Global Reset */
.stApp {
    background-color: var(--color-fog);
    font-family: var(--font-sohne);
    color: var(--color-ink);
}
.stMain {
    background-color: var(--color-fog);
    max-width: 1200px;
    margin: 0 auto;
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-signifier);
    color: var(--color-ink) !important;
    font-weight: 400 !important;
}
h1 {
    font-size: 64px !important;
    letter-spacing: -1.6px !important;
    line-height: 1.1 !important;
}
h2 {
    font-size: 44px !important;
    letter-spacing: -0.66px !important;
    line-height: 1.1 !important;
}
p, span, div, label {
    font-family: var(--font-sohne);
    letter-spacing: -0.009em;
}

/* Text Links */
a {
    color: var(--color-ink) !important;
    text-decoration: none !important;
    border-bottom: 1px solid var(--color-slate);
}

/* Cards & Layout */
.card, .ds-card, .feature-card, .image-card {
    background: var(--color-pure-white);
    border-radius: 24px !important;
    padding: 20px 24px;
    box-shadow: var(--shadow-subtle) !important;
    border: none !important;
    margin-bottom: 24px;
    transition: transform 0.3s ease;
}

.section-header, .ds-section-header {
    background: none !important;
    color: var(--color-ink) !important;
    font-family: var(--font-signifier);
    font-size: 44px !important;
    font-weight: 400 !important;
    margin: 60px 0 20px 0 !important;
    padding: 0 !important;
    border-bottom: 1px solid var(--color-dove) !important;
    border-radius: 0 !important;
    text-align: left !important;
}

/* Buttons */
/* Primary filled button (Ink pill) */
.stButton > button, .btn-primary, .ds-btn-primary {
    background: var(--color-ink) !important;
    color: var(--color-pure-white) !important;
    border-radius: 9999px !important;
    padding: 10px 24px !important;
    border: none !important;
    font-weight: 450 !important;
    font-size: 15px !important;
    font-family: var(--font-sohne) !important;
    transition: opacity 0.2s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover, .btn-primary:hover, .ds-btn-primary:hover {
    opacity: 0.8 !important;
    transform: none !important;
}

/* Hero Section */
.hero {
    background: radial-gradient(circle at center, var(--color-apricot-wash) 0%, var(--color-pure-white) 70%) !important;
    border-radius: 24px;
    padding: 80px 40px !important;
    text-align: center;
    margin-bottom: 40px;
    box-shadow: none !important;
    color: var(--color-ink) !important;
    height: auto !important;
}
.hero h1, .hero-content h1 {
    font-size: 64px !important;
    margin-bottom: 16px !important;
    color: var(--color-ink) !important;
}
.hero p, .hero-content p {
    font-size: 18px !important;
    color: var(--color-ash) !important;
    font-weight: 400 !important;
}

/* Inputs & File Uploader */
.stTextInput input, .stSelectbox > div > div {
    border-radius: 16px !important;
    border: 1px solid var(--color-dove) !important;
    padding: 12px 16px !important;
}
.stFileUploader > div {
    border-radius: 16px !important;
    border: 1px solid var(--color-dove) !important;
    background-color: var(--color-pure-white) !important;
}
textarea {
    border: 1px solid var(--color-dove) !important;
    border-radius: 16px !important;
    padding: 16px !important;
}
textarea:focus, .stTextInput input:focus {
    border-color: var(--color-ink) !important;
    box-shadow: none !important;
}

/* Sidebar Navigation */
.stSidebar, [data-testid="stSidebar"] {
    background-color: var(--color-fog) !important;
    border-right: none !important;
}
.sidebar .nav-link {
    color: var(--color-ink) !important;
    font-weight: 450 !important;
    border-radius: 12px !important;
}
.sidebar .nav-link-selected {
    background-color: var(--color-pure-white) !important;
    color: var(--color-ink) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* Chat Input Field */
.stChatInputContainer {
    background: var(--color-pure-white) !important;
    border-radius: 16px !important;
    border: 1px solid var(--color-dove) !important;
}

/* Grid & Layout Tweaks */
.images-grid, .features {
    display: grid;
    gap: 24px;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}
.metric-value {
    color: var(--color-ink) !important;
    font-family: var(--font-signifier) !important;
}
.metric-label {
    color: var(--color-graphite) !important;
}
</style>
''', unsafe_allow_html=True)
"""

if 'os.environ["OPENAI_API_KEY"] = API_KEY' in content_cleaned:
    parts = content_cleaned.split('os.environ["OPENAI_API_KEY"] = API_KEY', 1)
    content_cleaned = parts[0] + 'os.environ["OPENAI_API_KEY"] = API_KEY\n\n' + STEEP_CSS + parts[1]

# Need to clean up the empty markdown blocks left behind
content_cleaned = re.sub(r'st\.markdown\(\s*f?"""\s*"""\s*,\s*unsafe_allow_html=True\s*\)', '', content_cleaned)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content_cleaned)
print("UI Styles updated successfully in app.py")
