import streamlit as st
from google import genai
import time
from PIL import Image
import io

# 1. PAGE CONFIG & STYLING (Ensure these are at the very top)
st.set_page_config(page_title="NutriScan AI", page_icon="🥗", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #2e7d32; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# 2. AUTHENTICATION
try:
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=MY_API_KEY)
except Exception:
    st.error("Missing API Key in Streamlit Secrets.")
    st.stop()

# 3. HELPER: Shrink image to save API resources
def process_image(uploaded_file):
    img = Image.open(uploaded_file)
    # Convert to RGB if necessary (handles PNG/RGBA)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    # Resize to a max dimension of 1024px while keeping aspect ratio
    img.thumbnail((1024, 1024))
    return img

# 4. SIDEBAR
with st.sidebar:
    st.title("🥗 NutriScan")
    st.write("Optimized Free Edition")
    st.divider()
    input_mode = st.radio("Input Method", ("Camera", "Upload File"))
    st.divider()
    st.info("Technical Note: This version uses image compression and multi-model fallback to bypass free-tier congestion.")

# 5. MAIN INTERFACE
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📸 Food Input")
    if input_mode == "Camera":
        raw_file = st.camera_input("Scanner", label_visibility="collapsed")
    else:
        raw_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if raw_file:
        processed_img = process_image(raw_file)
        st.image(processed_img, caption="Optimized Preview", use_container_width=True)

with col_right:
    st.subheader("📊 Analysis Results")
    
    if raw_file:
        if st.button("Analyze Nutrition"):
            # List of models to try in order of preference
            models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash-lite"]
            success = False
            
            for model_name in models_to_try:
                if success: break
                
                with st.spinner(f"Trying {model_name}..."):
                    for attempt in range(2): # 2 tries per model
                        try:
                            response = client.models.generate_content(
                                model=model_name, 
                                contents=["Identify the food. Provide a table: Item, Calories, Protein, Carbs, Fats. Add a health tip.", processed_img]
                            )
                            st.success(f"Success (via {model_name})")
                            st.markdown(response.text)
                            success = True
                            break
                        except Exception as e:
                            err_str = str(e).lower()
                            if "503" in err_str or "429" in err_str:
                                time.sleep(2 * (attempt + 1)) # Wait 2s then 4s
                                continue
                            else:
                                break # Move to next model for other errors
                                
            if not success:
                st.error("All free-tier lanes are busy. Please wait 60 seconds and try again.")
    else:
        st.info("Awaiting input image...")
