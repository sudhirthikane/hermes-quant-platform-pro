import streamlit as st
import sys
import os
import datetime

# --- PATH RESOLVER FOR STREAMLIT CLOUD ---
# This forces Linux to recognize the root directory so it can find the 'utils' folder.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

st.set_page_config(
    page_title="TaxMaximizer Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.theme import apply_global_styles

# --- ROUTE PROTECTION ---
if not st.session_state.get("authenticated", False):
    st.switch_page("pages/0_Login.py")
    
# Force Hot Reload
from utils.theme import apply_global_styles, render_header
apply_global_styles()
render_header()

# Custom CSS for Premium FinTech Look
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #f8fafc; /* Light sleek slate background */
        color: #0f172a;
    }
    
    /* Elegant Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.02) !important;
    }
    
    /* Add borders to main block elements */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    /* Hide top header and footer for cleaner look */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom Gradient Title */
    .premium-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-align: center;
        letter-spacing: -1px;
    }
    
    .premium-subtitle {
        text-align: center;
        color: #475569;
        font-size: 1.1rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* Custom Card Design */
    .tax-card {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(12px);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        margin-bottom: 15px;
    }
    
    .tax-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px -10px rgba(37, 99, 235, 0.2);
        border-color: rgba(37, 99, 235, 0.4);
    }

    .card-icon {
        font-size: 2.8rem;
        margin-bottom: 16px;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    
    .card-desc {
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.6;
        flex-grow: 1;
    }
    
    /* Tweaking Streamlit's native page link container to flow nicely under cards */
    div[data-testid="stPageLink"] {
        margin-top: -5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="premium-title">TaxMaximizer Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="premium-subtitle">Select your Income Tax Return (ITR) Profile for Assessment Year 2026-27</div>', unsafe_allow_html=True)

# Row 1
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="tax-card">
        <div class="card-icon">🟢</div>
        <div class="card-title">ITR-1 (Sahaj)</div>
        <div class="card-desc">For Salaried Individuals, Pensioners, and those with ONE House Property. Features automated Form 16 OCR scanning.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_ITR_1_Salary.py", label="Start ITR-1 Filing", icon="▶️")

with c2:
    st.markdown("""
    <div class="tax-card">
        <div class="card-icon">🟡</div>
        <div class="card-title">ITR-2 (CapGains)</div>
        <div class="card-desc">For Investors. Upload Broker P&L statements for automatic Short-Term (20%) and Long-Term (12.5%) special rate computations.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_ITR_2_CapGains.py", label="Start ITR-2 Filing", icon="▶️")

with c3:
    st.markdown("""
    <div class="tax-card">
        <div class="card-icon">🔴</div>
        <div class="card-title">ITR-3 (Business)</div>
        <div class="card-desc">For Active Traders (F&O) and Business Owners maintaining full Books of Accounts. Includes Draft Save functionality.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_ITR_3_Business.py", label="Start ITR-3 Filing", icon="▶️")


st.write("") # Spacing

# Row 2
c4, c5, c6 = st.columns(3)

with c4:
    st.markdown("""
    <div class="tax-card">
        <div class="card-icon">🔵</div>
        <div class="card-title">ITR-4 (Sugam)</div>
        <div class="card-desc">For Freelancers & Professionals claiming Presumptive Taxation (Sec 44AD/44ADA) without maintaining complex books.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_ITR_4_Sugam.py", label="Start ITR-4 Filing", icon="▶️")

with c5:
    st.markdown("""
    <div class="tax-card">
        <div class="card-icon">🟣</div>
        <div class="card-title">ITR-5 (Firms)</div>
        <div class="card-desc">For Partnership Firms & LLPs. Calculates Flat 30% Corporate Tax and enforces strict Section 40(b) Remuneration limits.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/5_ITR_5_Firms.py", label="Start ITR-5 Filing", icon="▶️")

with c6:
    st.markdown("""
    <div class="tax-card" style="background: linear-gradient(145deg, rgba(255, 255, 255, 0.9) 0%, rgba(37, 99, 235, 0.05) 100%);">
        <div class="card-icon">✨</div>
        <div class="card-title">AI Tax Optimizer</div>
        <div class="card-desc">Our proprietary AI engine runs automatically across all forms to analyze your 80C, 80D, and NPS gaps to maximize your refunds.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True) # Invisible spacer to align visually

st.divider()
st.markdown(f"<div style='text-align: center; color: #94a3b8; font-size: 0.85rem; font-family: monospace;'>🛡️ Secure SSL Environment | V2.0 Enterprise MPA Build | © {datetime.date.today().year} TaxMaximizer Pro</div>", unsafe_allow_html=True)
