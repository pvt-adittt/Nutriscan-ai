import streamlit as st
from google import genai
import time
from PIL import Image

# --- 1. AUTHENTICATION ---
try:
    # This looks for the key in Streamlit's hidden vault
    MY_API_KEY = st.secrets["AIzaSyCkREMnMy7sGhxYAWSQerEYsnntVtN5Aok"]
    client = genai.Client(api_key=MY_API_KEY)
except Exception as e:
    st.error("API Key not found. Please add it to 'Advanced Settings > Secrets' in the Streamlit Dashboard.")
    st.stop()

# --- 2. UI SETUP ---
st.set_page_config(page_title="NutriScan AI", page_icon="🥗")
st.title("🥗 NutriScan AI")
st.write("Scan or upload food photos for instant nutrition facts.")

# --- 3. INPUT SELECTION ---
input_mode = st.radio("Choose Input:", ("Camera", "Upload File"))

img_file = None
if input_mode == "Camera":
    img_file = st.camera_input("Take a photo")
else:
    img_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])

# --- 4. ANALYSIS LOGIC ---
if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Ready for analysis", use_container_width=True)
    
    prompt = "Identify the food. Provide a table: Item, Calories, Protein, Carbs, Fats. Add a health tip."
    
    if st.button("Analyze Nutrition"):
        with st.spinner("AI is scanning... (Retrying if busy)"):
            for i in range(3): # Retry logic for 503 errors
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash", 
                        contents=[prompt, img]
                    )
                    st.subheader("📊 Macro Report")
                    st.markdown(response.text)
                    break 
                except Exception as e:
                    if "503" in str(e) and i < 2:
                        time.sleep(3)
                        continue
                    else:
                        st.error(f"Error: {e}")
                        break
