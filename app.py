import streamlit as st
from google import genai
import time
from PIL import Image
import os

# ── 1. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(page_title="NutriScan AI", layout="wide")

# ── 2. LOAD EXTERNAL CSS ──────────────────────────────────────────────────────
def load_css(filepath: str):
    css_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css("style.css")

# ── PROFILE BADGE ─────────────────────────────────────────────────────────────
def render_profile_badge():
    uname = st.session_state.get("username", "User")
    initial = uname[0].upper()

    st.markdown(f"""
    <style>
    div[data-testid="stHorizontalBlock"]:has(button[key="profile_btn"]) {{
        position: fixed !important;
        top: 8px !important;
        right: 5rem !important;
        z-index: 2147483647 !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(button[key="profile_btn"]) * {{
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        padding: 0 !important;
        margin: 0 !important;
        flex: unset !important;
        background: transparent !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(button[key="profile_btn"]) button {{
        border-radius: 50% !important;
        aspect-ratio: 1 / 1 !important;
        overflow: hidden !important;
        font-size: 1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: linear-gradient(135deg, #6dbf4e 0%, #b5e550 100%) !important;
        color: #0d1a0f !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 2px 12px rgba(100,200,80,0.35) !important;
        cursor: pointer !important;
    }}
    </style>

    <script>
    function makeCircle() {{
        const doc = window.parent.document;
        const allButtons = doc.querySelectorAll('button');
        for (const btn of allButtons) {{
            if (btn.innerText.trim() === '{initial}') {{
                btn.style.setProperty('width', '38px', 'important');
                btn.style.setProperty('height', '38px', 'important');
                btn.style.setProperty('min-width', '38px', 'important');
                btn.style.setProperty('max-width', '38px', 'important');
                btn.style.setProperty('min-height', '38px', 'important');
                btn.style.setProperty('max-height', '38px', 'important');
                btn.style.setProperty('border-radius', '50%', 'important');
                btn.style.setProperty('padding', '0', 'important');
                btn.style.setProperty('aspect-ratio', '1 / 1', 'important');
                btn.style.setProperty('overflow', 'hidden', 'important');
                btn.style.setProperty('line-height', '38px', 'important');
            }}
        }}
    }}
    makeCircle();
    setTimeout(makeCircle, 300);
    setTimeout(makeCircle, 800);
    setTimeout(makeCircle, 1500);
    </script>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([11, 1])
    with col2:
        if st.button(initial, key="profile_btn"):
            st.session_state.page = "profile"
            st.rerun()


# ── PARTICLE BACKGROUND ───────────────────────────────────────────────────────
def render_particle_background():
    st.markdown("""
    <canvas id="particle-canvas" style="
        position: fixed;
        top: 0; left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
        pointer-events: none;
    "></canvas>
    <script>
    (function() {
        const canvas = document.getElementById('particle-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        canvas.width  = window.innerWidth;
        canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {
            canvas.width  = window.innerWidth;
            canvas.height = window.innerHeight;
        });

        const PARTICLE_COUNT = 80;
        const MAX_DIST       = 150;
        const SPEED          = 0.5;
        const DOT_RADIUS     = 2.5;
        const DOT_COLOR      = 'rgba(181, 229, 80, 0.75)';
        const LINE_COLOR     = 'rgba(181, 229, 80, ';

        const particles = Array.from({ length: PARTICLE_COUNT }, () => ({
            x:  Math.random() * canvas.width,
            y:  Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * SPEED,
            vy: (Math.random() - 0.5) * SPEED,
        }));

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (const p of particles) {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0 || p.x > canvas.width)  p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
            }

            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx   = particles[i].x - particles[j].x;
                    const dy   = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < MAX_DIST) {
                        const alpha = (1 - dist / MAX_DIST) * 0.55;
                        ctx.beginPath();
                        ctx.strokeStyle = LINE_COLOR + alpha + ')';
                        ctx.lineWidth   = 0.8;
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }

            for (const p of particles) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, DOT_RADIUS, 0, Math.PI * 2);
                ctx.fillStyle = DOT_COLOR;
                ctx.fill();
            }

            requestAnimationFrame(animate);
        }

        animate();
    })();
    </script>
    """, unsafe_allow_html=True)


# ── 3. SESSION STATE ──────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []


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
#  PROFILE PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "profile":
    import re
    import datetime
    import plotly.graph_objects as go

    uname = st.session_state.get("username", "User")

    st.markdown(f"""
    <div style="text-align:center; padding: 3rem 0 2rem;">
        <div style="font-family:'Playfair Display',serif; font-size:3.5rem;
                    font-weight:900; color:#b5e550; letter-spacing:-0.02em;">
            {uname}
        </div>
        <div style="color:#a8b89e; font-size:1rem; margin-top:0.5rem;">
            🥗 NutriScan AI — Personal Scan History
        </div>
        <div style="width:60px; height:3px; background:linear-gradient(90deg,#6dbf4e,#b5e550);
                    border-radius:99px; margin: 1.2rem auto 0;">
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    history = st.session_state.get("scan_history", [])

    # ── MACRO PARSING HELPER ──────────────────────────────────────────────────
    def parse_macros(result_text):
        """Extract total calories, protein, carbs, fats from the markdown table."""
        calories = protein = carbs = fats = 0.0
        rows = re.findall(
            r'\|\s*(?!Food Item|[-\s|]+)(.+?)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',
            result_text
        )
        for row in rows:
            try:
                calories += float(row[1])
                protein  += float(row[2])
                carbs    += float(row[3])
                fats     += float(row[4])
            except ValueError:
                continue
        return {"calories": calories, "protein": protein, "carbs": carbs, "fats": fats}

    # ── AGGREGATE TODAY'S MACROS ──────────────────────────────────────────────
    today_str = datetime.datetime.now().strftime("%d %b %Y")
    today_macros = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
    all_macros   = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}

    for scan in history:
        m = parse_macros(scan["result"])
        for k in all_macros:
            all_macros[k] += m[k]
        if today_str in scan["time"]:
            for k in today_macros:
                today_macros[k] += m[k]

    if not history:
        st.markdown("""
        <div style="text-align:center; padding: 4rem 0; color:#5a7060; font-size:1rem;">
            📷 No scans yet. Go analyze a meal first!
        </div>
        """, unsafe_allow_html=True)

    else:
        # ── SUMMARY STAT CARDS ────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; color:#b5e550; font-size:0.85rem;
                    font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    margin-bottom:1rem;">
            Today's Totals
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        for col, label, value, unit, color in [
            (c1, "🔥 Calories", today_macros["calories"], "kcal", "#e8c96a"),
            (c2, "💪 Protein",  today_macros["protein"],  "g",    "#7aab7a"),
            (c3, "🌾 Carbs",    today_macros["carbs"],    "g",    "#b5e550"),
            (c4, "🥑 Fats",     today_macros["fats"],     "g",    "#e07b5a"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:#1a2e1d; border:1px solid rgba(181,229,80,0.15);
                            border-radius:14px; padding:1.2rem; text-align:center;">
                    <div style="font-size:0.8rem; color:#a8b89e; margin-bottom:0.3rem;">{label}</div>
                    <div style="font-size:2rem; font-weight:800; color:{color};
                                font-family:'Playfair Display',serif;">{value:.0f}</div>
                    <div style="font-size:0.75rem; color:#5a7060;">{unit}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── MACRO DONUT CHART (Today) ─────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; color:#b5e550; font-size:0.85rem;
                    font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    margin-bottom:0.5rem;">
            Today's Macro Split
        </div>
        """, unsafe_allow_html=True)

        col_chart1, col_chart2 = st.columns([1, 1])

        with col_chart1:
            donut = go.Figure(go.Pie(
                labels=["Protein", "Carbs", "Fats"],
                values=[
                    today_macros["protein"],
                    today_macros["carbs"],
                    today_macros["fats"]
                ],
                hole=0.65,
                marker=dict(colors=["#7aab7a", "#b5e550", "#e07b5a"],
                            line=dict(color="#0d1a0f", width=2)),
                textinfo="label+percent",
                textfont=dict(color="#f0ede4", size=12),
                hovertemplate="<b>%{label}</b><br>%{value:.1f}g<extra></extra>"
            ))
            donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
                height=280,
                annotations=[dict(
                    text=f"<b>{today_macros['calories']:.0f}</b><br>kcal",
                    x=0.5, y=0.5, font_size=16,
                    font_color="#e8c96a", showarrow=False
                )]
            )
            st.plotly_chart(donut, use_container_width=True, config={"displayModeBar": False})

        # ── BAR CHART — per scan macros ───────────────────────────────────────
        with col_chart2:
            scan_labels  = [f"Scan {i+1}" for i in range(len(history))]
            proteins     = [parse_macros(s["result"])["protein"]  for s in history]
            carbss       = [parse_macros(s["result"])["carbs"]    for s in history]
            fatss        = [parse_macros(s["result"])["fats"]     for s in history]

            bar = go.Figure()
            bar.add_trace(go.Bar(name="Protein", x=scan_labels, y=proteins,
                                 marker_color="#7aab7a"))
            bar.add_trace(go.Bar(name="Carbs",   x=scan_labels, y=carbss,
                                 marker_color="#b5e550"))
            bar.add_trace(go.Bar(name="Fats",    x=scan_labels, y=fatss,
                                 marker_color="#e07b5a"))
            bar.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#a8b89e", size=11),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a8b89e")),
                xaxis=dict(gridcolor="rgba(181,229,80,0.08)"),
                yaxis=dict(gridcolor="rgba(181,229,80,0.08)", title="grams"),
                margin=dict(t=20, b=20, l=20, r=20),
                height=280,
            )
            st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center; color:#a8b89e; font-size:0.9rem; margin-bottom:1.5rem;">
            {len(history)} scan(s) recorded this session
        </div>
        """, unsafe_allow_html=True)

        # ── SCAN HISTORY LIST ─────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; color:#b5e550; font-size:0.85rem;
                    font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    margin-bottom:1rem;">
            Scan History
        </div>
        """, unsafe_allow_html=True)

        for i, scan in enumerate(reversed(history)):
            m = parse_macros(scan["result"])
            st.markdown(f"""
            <div style="background:#1a2e1d; border:1px solid rgba(181,229,80,0.12);
                        border-radius:14px; padding:1.2rem 1.5rem; margin-bottom:0.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="color:#b5e550; font-size:0.78rem; font-weight:600;
                                letter-spacing:0.08em; text-transform:uppercase;">
                        Scan #{len(history) - i} &nbsp;·&nbsp; {scan['time']}
                    </div>
                    <div style="display:flex; gap:1.2rem; font-size:0.82rem; color:#a8b89e;">
                        <span>🔥 {m['calories']:.0f} kcal</span>
                        <span>💪 {m['protein']:.0f}g</span>
                        <span>🌾 {m['carbs']:.0f}g</span>
                        <span>🥑 {m['fats']:.0f}g</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_img, col_res = st.columns([1, 1], gap="large")
            with col_img:
                st.image(scan["image"], use_container_width=True)
            with col_res:
                st.markdown(
                    f'<div class="results-card">{scan["result"]}</div>',
                    unsafe_allow_html=True
                )
            st.markdown(
                "<hr style='border-color:rgba(181,229,80,0.1); margin:1.5rem 0;'>",
                unsafe_allow_html=True
            )

    st.stop()
    
# ══════════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    render_particle_background()
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
    render_particle_background()
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
                            # Save to scan history
                            import datetime
                            st.session_state.scan_history.append({
                                "image": img,
                                "result": response.text,
                                "time": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
                            })
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

