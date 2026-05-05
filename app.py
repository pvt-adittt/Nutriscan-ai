import streamlit as st
from google import genai
import time  # Essential for the retry logic
from PIL import Image

# 1. AUTHENTICATION
# This tells the app to look in Streamlit's hidden secrets vault
try:
    MY_API_KEY = st.secrets["AIzaSyCkREMnMy7sGhxYAWSQerEYsnntVtN5Aok"]
    client = genai.Client(api_key=MY_API_KEY)
except Exception as e:
    st.error("API Key not found. Please add it to Streamlit Secrets.")
    st.stop()

# Initialize the 2026 Client
client = genai.Client(api_key=MY_API_KEY)

# 2. APP UI SETUP
st.set_page_config(page_title="NutriScan AI", page_icon="🥗")
st.title("🥗 NutriScan AI")
st.write("Scan or upload food photos for instant nutrition facts.")

# 3. INPUT SELECTION (Camera or File Upload)
input_mode = st.radio("Choose Input:", ("Camera", "Upload File"))

img_file = None
if input_mode == "Camera":
    img_file = st.camera_input("Take a photo")
else:
    img_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])

# 4. ANALYSIS LOGIC
if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Ready for analysis", use_container_width=True)
    
    prompt = "Identify the food. Provide a table: Item, Calories, Protein, Carbs, Fats. Add a health tip."
    
    if st.button("Analyze Nutrition"):
        # The 'spinner' shows the user that the AI is working
        with st.spinner("AI is scanning your plate... (Retrying if busy)"):
            success = False
            retries = 3  # Tries up to 3 times if the server is busy
            
            for i in range(retries):
                try:
                    # Using the current stable 2026 model
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=[prompt, img]
                    )
                    st.subheader("📊 Macro Report")
                    st.markdown(response.text)
                    success = True
                    break  # Exit the loop if successful
                    
                except Exception as e:
                    # If we get a 503 error (High Demand), wait 3 seconds and try again
                    if "503" in str(e) and i < retries - 1:
                        time.sleep(3)
                        continue
                    else:
                        st.error("The server is very busy right now. Please wait 10 seconds and try again.")
                        break