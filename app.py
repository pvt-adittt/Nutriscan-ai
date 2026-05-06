import streamlit as st
from google import genai
import time
from PIL import Image

# 1. PAGE CONFIG & MODERN UI STYLING
st.set_page_config(page_title="NutriScan AI", page_icon="🥗", layout="wide")

# Custom CSS for a cleaner, engineering-grade look
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
            # Increased retry count to handle 503 spikes
            success = False
            for attempt in range(5): 
                with st.spinner(f"AI is processing (Attempt {attempt + 1}/5)..."):
                    try:
                        # Using 2.5-flash as confirmed by your dashboard
                        response = client.models.generate_content(
                            model="gemini-2.5-flash", 
                            contents=["Identify the food. Provide a table: Item, Calories, Protein, Carbs, Fats. Add a health tip.", img]
                        )
                        st.success("Analysis Complete!")
                        st.markdown(response.text)
                        success = True
                        break
                    except Exception as e:
                        if "503" in str(e) or "429" in str(e):
                            time.sleep(4) # Wait longer between retries
                            continue
                        else:
                            st.error(f"Technical Error: {e}")
                            break
            if not success:
                st.error("The AI server is currently overloaded. Please wait 30 seconds and try again.")
    else:
        st.info("Awaiting input image...")
