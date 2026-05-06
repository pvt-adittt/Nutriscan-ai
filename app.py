import streamlit as st
from google import genai
import time
from PIL import Image
import io  # Added to handle image bytes for caching

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

# 2. SECURE AUTHENTICATION
try:
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=MY_API_KEY)
except Exception:
    st.error("Missing API Key in Streamlit Secrets.")
    st.stop()

# --- NEW: CACHED ANALYSIS FUNCTION ---
# show_spinner=False because we use our own spinner below
@st.cache_data(show_spinner=False)
def analyze_image_with_cache(image_bytes):
    """
    Sends the image to the AI. If successful, Streamlit remembers the answer.
    If it fails after 5 tries, it raises an error so the failure isn't cached.
    """
    # Rebuild the image from bytes for the AI
    img_for_ai = Image.open(io.BytesIO(image_bytes))
    prompt = "Identify the food. Provide a table: Item, Calories, Protein, Carbs, Fats. Add a health tip."
    
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=[prompt, img_for_ai]
            )
            return response.text # Success! This result gets cached forever for this specific image.
            
        except Exception as e:
            if "503" in str(e) or "429" in str(e):
                time.sleep(4) # Wait and try again
                continue
            else:
                raise Exception(f"Technical Error: {e}") # Other errors
                
    # If it fails 5 times, trigger the overloaded error
    raise Exception("The AI server is currently overloaded. Please wait 30 seconds and try again.")
# -------------------------------------

# 3. SIDEBAR (Clears up the main screen)
with st.sidebar:
    st.title("🥗 NutriScan")
    st.write("Instant Nutritional Intelligence")
    st.divider()
    input_mode = st.radio("Select Input Method", ("Camera", "Upload File"))
    st.divider()
    st.info("Tip: Good lighting and clear food visibility improve accuracy.")

# 4. MAIN INTERFACE LAYOUT
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
            with st.spinner("AI is processing (Pulling from cache if already scanned)..."):
                try:
                    # Pass the raw bytes of the image to the cached function
                    # If this exact byte-pattern was scanned before, it returns instantly!
                    result_text = analyze_image_with_cache(img_file.getvalue())
                    
                    st.success("Analysis Complete!")
                    st.markdown(result_text)
                    
                except Exception as e:
                    # This catches the errors raised inside the cached function
                    st.error(str(e))
    else:
        st.info("Awaiting input image...")
