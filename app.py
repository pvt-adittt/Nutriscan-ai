import streamlit as st
from google import genai
import time
from PIL import Image
import io
import random

# 1. PAGE CONFIG (Must be first)
st.set_page_config(page_title="NutriScan AI", page_icon="🥑", layout="wide")

# 2. LOAD EXTERNAL CSS
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.warning("Could not load CSS file. Proceeding with default styles.")

load_css("style.css")

# 3. SESSION STATE INITIALIZATION
# This acts as our "Page Router"
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Function to switch pages instantly
def change_page(page_name):
    st.session_state.current_page = page_name

# 4. BACKEND LOGIC (Your final boss AI logic)
def get_rotated_client():
    try:
        keys = st.secrets["KEYS"]
        selected_key = random.choice(keys)
        return genai.Client(api_key=selected_key)
    except Exception:
        st.error("Missing 'KEYS' in Streamlit Secrets.")
        st.stop()

@st.cache_data(show_spinner=False)
def analyze_image_with_cache(image_bytes):
    img_for_ai = Image.open(io.BytesIO(image_bytes))
    prompt = "Identify the food. Provide a table: Item, Calories, Protein, Carbs, Fats. Add a health tip."
    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
    last_error = ""
    
    for model_name in models_to_try:
        for attempt in range(4): 
            current_client = get_rotated_client()
            try:
                response = current_client.models.generate_content(
                    model=model_name, contents=[prompt, img_for_ai]
                )
                return response.text
            except Exception as e:
                err_msg = str(e).lower()
                last_error = str(e)
                if "503" in err_msg or "429" in err_msg:
                    time.sleep(random.uniform(3, 7))
                    continue
                else:
                    raise Exception(f"Technical Error: {e}")
    raise Exception(f"All API lanes congested. Last issue: {last_error}")

# ==========================================
# UI RENDERING - PAGE 1: THE LANDING PAGE
# ==========================================
if st.session_state.current_page == 'home':
    # Using the CSS classes we defined in style.css
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-quote">"Fuel your body. Elevate your life."</h1>
            <p class="hero-subtitle">Instantly track your macros with AI vision.</p>
        </div>
        <br><br>
    """, unsafe_allow_html=True)
    
    # Center the button using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # When clicked, it changes the state to 'scanner' and re-runs the script
        if st.button("📸 Launch Food Scanner"):
            change_page('scanner')
            st.rerun()

# ==========================================
# UI RENDERING - PAGE 2: THE MAIN APP
# ==========================================
elif st.session_state.current_page == 'scanner':
    
    # Sidebar
    with st.sidebar:
        # A button to go back to the landing page
        if st.button("← Back to Home"):
            change_page('home')
            st.rerun()
            
        st.divider()
        st.title("⚙️ Settings")
        input_mode = st.radio("Select Input Method", ("Camera", "Upload File"))
        st.divider()
        st.info("Tip: Good lighting and clear food visibility improve accuracy.")

    # Main Interface
    st.markdown("<h2 style='color: #064e3b; text-align: center; margin-bottom: 2rem;'>Nutritional Analysis</h2>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        if input_mode == "Camera":
            img_file = st.camera_input("Scanner", label_visibility="collapsed")
        else:
            img_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

        if img_file:
            img = Image.open(img_file)
            st.image(img, caption="Plate Preview", use_container_width=True)

    with col_right:
        if img_file:
            if st.button("Analyze Nutrition"):
                with st.spinner("AI is processing the image..."):
                    try:
                        result_text = analyze_image_with_cache(img_file.getvalue())
                        st.success("Analysis Complete!")
                        with st.container():
                            st.markdown(result_text)
                    except Exception as e:
                        st.error(str(e))
        else:
            st.markdown("<div style='text-align:center; padding:3rem; background:white; border-radius:15px; color:#64748b;'>Awaiting image input...</div>", unsafe_allow_html=True)
