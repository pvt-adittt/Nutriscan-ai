import streamlit as st
from google import genai
import time
from PIL import Image
import os

# ── 1. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(page_title="NutriScan AI", layout="wide")

# ── 2. LOAD EXTERNAL CSS ──────────────────────────────────────────────────────
def load_css(filepath: str):
    """Read and inject a CSS file into the Streamlit app."""
    css_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css("style.css")

def render_profile_badge():
    uname = st.session_state.get("username", "User")
    initial = uname[0].upper()
    st.markdown(f"""
    <style>
    .profile-badge-wrap {{
        position: absolute;
        top: 20px;
        right: -30px;
        z-index: 2147483647;
    }}
    .profile-avatar {{
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6dbf4e 0%, #b5e550 100%);
        color: #0d1a0f;
        font-weight: 700;
        font-size: 1rem;
        display: flex !important;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        position: relative;
        box-shadow: 0 2px 12px rgba(100,200,80,0.35);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        user-select: none;
        visibility: visible !important;
        opacity: 1 !important;
    }}
    .profile-avatar:hover {{
        transform: scale(1.08);
        box-shadow: 0 4px 20px rgba(100,200,80,0.55);
    }}
    .profile-tooltip {{
        position: absolute;
        top: calc(100% + 8px);
        right: 0;
        background: #1a2e1d;
        border: 1px solid rgba(181,229,80,0.35);
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.82rem;
        font-weight: 500;
        color: #b5e550 !important;
        white-space: nowrap;
        pointer-events: none;
        opacity: 0;
        transform: translateY(-4px);
        transition: opacity 0.2s ease, transform 0.2s ease;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }}
    .profile-tooltip::before {{
        content: '';
        position: absolute;
        top: -5px;
        right: 12px;
        width: 8px;
        height: 8px;
        background: #1a2e1d;
        border-left: 1px solid rgba(181,229,80,0.35);
        border-top: 1px solid rgba(181,229,80,0.35);
        transform: rotate(45deg);
    }}
    .profile-avatar:hover .profile-tooltip {{
        opacity: 1;
        transform: translateY(0);
    }}
    </style>
    <div class="profile-badge-wrap">
      <div class="profile-avatar">
        {initial}
        <div class="profile-tooltip">👤 {uname}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── 3. SESSION STATE ──────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ── 4. SECURE API AUTHENTICATION ─────────────────────────────────────────────
try:
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=MY_API_KEY)
except Exception:
    st.error("⚠️ Missing GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "login":
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom: 2rem;">
          <div style="font-family:'Playfair Display',serif; font-size:2.5rem;
                      font-weight:900; color:#b5e550;">NutriScan AI</div>
          <div style="color:#a8b89e; font-size:0.95rem; margin-top:0.4rem;">
               Your AI-powered nutrition companion
          </div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter any username")
        password = st.text_input("Password", placeholder="Enter any password", type="password")

        if st.button("Login →", use_container_width=True):
            if username.strip() and password.strip():
                st.session_state.logged_in = True
                st.session_state.username = username.strip()  # ← ADD THIS
                st.session_state.page = "landing"
                st.rerun()
            else:
                st.error("Please enter both a username and password.")

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    render_profile_badge()   # ← ADD THIS
    st.markdown("""...""")
    
    st.markdown("""
    <div class="hero-section">

      <!-- Badge chip -->
      <div class="hero-badge">✦ AI-Powered Nutrition</div>

      <!-- Main headline -->
      <h1 class="hero-headline">
        Know What's<br>On Your <em>Plate.</em>
      </h1>

      <!-- Inspirational quote -->
      <p class="hero-quote">
        "Let food be thy medicine, and medicine be thy food."
      </p>

      <!-- Tagline -->
      <p class="hero-tagline">
        Snap a photo of any meal and get instant calorie, protein,
        carb &amp; fat breakdowns — powered Artificial Intelligence.
      </p>

    </div>
    """, unsafe_allow_html=True)

    # ── CTA Button (must be outside html block for Streamlit to render it)
    col_a, col_b, col_c = st.columns([2, 1.4, 2])
    with col_b:
        if st.button("Start Tracking", use_container_width=True):
            st.session_state.page = "app"
            st.rerun()

    # Feature pills row
    st.markdown("""
    <div class="feature-pills">
      <span class="feature-pill">📷 Camera &amp; Upload</span>
      <span class="feature-pill">⚡ Instant Results</span>
      <span class="feature-pill">🥦 Macro Breakdown</span>
      <span class="feature-pill">💡 Health Tips</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  APP PAGE
# ══════════════════════════════════════════════════════════════════════════════
else:
    render_profile_badge()   # ← ADD THIS

     # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="app-logo">NutriScan<span>AI</span></div>',
                    unsafe_allow_html=True)
        st.divider()

        input_mode = st.radio(
            "Input Method",
            ("📷 Camera", "📁 Upload File"),
            label_visibility="collapsed"
        )
        st.divider()
        st.info("💡 Tip: Good lighting and full plate visibility improve accuracy.")
        st.divider()

        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()

    # ── App header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="app-header">
      <span class="app-logo" style="font-size:1.25rem">NutriScan <span>— Instant Macro Analysis</span></span>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout ─────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("📸 Food Input")

        if input_mode == "📷 Camera":
            img_file = st.camera_input(" ", label_visibility="collapsed")
        else:
            img_file = st.file_uploader(
                " ",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed"
            )

        if img_file:
            img = Image.open(img_file)
            st.image(img, caption="Plate Preview", use_container_width=True)

    with col_right:
        st.subheader("📊 Nutrition Results")

        if img_file:
            if st.button("⚡ Analyze Nutrition", use_container_width=True):
                success = False
                for attempt in range(5):
                    with st.spinner(f"Your plate is being read… ({attempt + 1}/5)"):
                        try:
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=[
                                    "Identify the food items in this image. "
                                    "Provide a well-formatted markdown table with columns: "
                                    "Food Item | Calories (kcal) | Protein (g) | Carbs (g) | Fats (g). "
                                    "After the table, give a brief personalized health tip.",
                                    img
                                ]
                            )
                            st.success("✅ Analysis complete!")
                            st.markdown(
                                f'<div class="results-card">{response.text}</div>',
                                unsafe_allow_html=True
                            )
                            success = True
                            break

                        except Exception as e:
                            err = str(e)
                            if "503" in err or "429" in err:
                                time.sleep(4)
                                continue
                            else:
                                st.error(f"Technical error: {e}")
                                break

                if not success:
                    st.error(
                        "The AI server is currently busy. "
                        "Please wait 30 seconds and try again."
                    )
        else:
            st.markdown("""
            <div style="padding: 2rem 1.5rem; background: #1a2e1d; border: 1.5px dashed rgba(181,229,80,0.18);
                        border-radius: 14px; text-align: center; color: #5a7060; font-size: 0.95rem;">
              📷 Upload or capture a photo to begin analysis
            </div>
            """, unsafe_allow_html=True)

