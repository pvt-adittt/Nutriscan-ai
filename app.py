import streamlit as st
from google import genai
import time
from PIL import Image
import io
import random

# 1. PAGE CONFIG & MODERN UI STYLING
st.set_page_config(page_title="NutriScan AI", page_icon="🥗", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# 2. HELPER: KEY ROTATION
def get_rotated_client():
    """Picks a random key from the secrets list to avoid rate limits."""
    try:
        keys = st.secrets["KEYS"]
        selected_key = random.choice(keys)
        return genai.Client(api_key=selected_key)
    except Exception:
        st.error("Key Rotation Error: Ensure 'KEYS' is a list in your Streamlit Secrets.")
        st.stop()

# 3. CACHED ANALYSIS FUNCTION (UPDATED)
@st.cache_data(show_spinner=False)
def analyze_image_with_cache(image_bytes):
    img_for_ai = Image.open(io.BytesIO(image_bytes))
    prompt = "Identify the food. Provide a table: Item, Calories, Protein, Carbs, Fats. Add a health tip."
    
    last_error = ""
    
    # Attempt cycle
    for attempt in range(5):
        # NEW: Fetch a new random key for EVERY attempt, not just once at the start.
        # If Key A gives a 429 error, Attempt 2 might use Key B to bypass it instantly.
        current_client = get_rotated_client()
        
        try:
            response = current_client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=[prompt, img_for_ai]
            )
            return response.text
            
        except Exception as e:
            err_msg = str(e).lower()
            last_error = str(e)
            
            if "503" in err_msg or "429" in err_msg:
                # Sleep briefly before the loop restarts and grabs a new key
                time.sleep(2) 
                continue
            else:
                # If it's a completely different error (like an invalid key), stop immediately
                raise Exception(f"Technical Error: {e}")
                
    # If all 5 attempts fail across multiple keys, show the last actual error from Google
    raise Exception(f"All API lanes congested. Last issue: {last_error}")
    
# 4. SIDEBAR
with st.sidebar:
    st.title("🥗 NutriScan")
    st.write("Multi-Lane AI Edition")
    st.divider()
    input_mode = st.radio("Select Input Method", ("Camera", "Upload File"))
    st.divider()
    st.info("Technical Status: Key Rotation & Image Caching are ACTIVE.")

# 5. MAIN INTERFACE
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📸 Food Input")
    if input_mode == "Camera":
        img_file = st.camera_input("Scanner", label_visibility="collapsed")
    else:
        img_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Plate Preview", use_container_width=True)

with col_right:
    st.subheader("📊 Analysis Results")
    
    if img_file:
        if st.button("Analyze Nutrition"):
            with st.spinner("Rotating API keys and processing..."):
                try:
                    # Logic: If image bytes match a previous scan, 
                    # it returns the result without calling ANY key.
                    result_text = analyze_image_with_cache(img_file.getvalue())
                    
                    st.success("Analysis Complete!")
                    st.markdown(result_text)
                    
                except Exception as e:
                    st.error(str(e))
    else:
        st.info("Awaiting input image...")
