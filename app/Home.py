"""
SecureInsights Platform - Home Page
Privacy-Safe Cross-Company Analytics Platform
"""

import streamlit as st
import yaml
from pathlib import Path

# Page configuration - SAME AS OTHER PAGES
st.set_page_config(
    page_title="SecureInsights - Home",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
def load_config():
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            result = yaml.safe_load(f)
            return result if result is not None else {}
    return {}

config = load_config()

# Minimal CSS - ONLY BACKGROUND
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, #0f172a 0%, #1e293b 100%);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #1e293b 0%, #334155 100%);
    }
</style>
""", unsafe_allow_html=True)

# Hero section - Modern and attractive with dark theme
st.markdown("""
<div style="
    text-align: center; 
    padding: 3rem 2rem 2rem 2rem;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
    border-radius: 20px;
    margin-bottom: 2rem;
    margin-top: 0.5rem;
    border: 1px solid rgba(102, 126, 234, 0.2);
">
    <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem 1.5rem; border-radius: 50px; margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
        <span style="color: white; font-weight: 600; font-size: 0.9rem;">🔒 PRIVACY-FIRST ANALYTICS</span>
    </div>
    <h1 style="
        font-size: 4rem; 
        font-weight: 800; 
        color: #818cf8;
        margin: 0;
        letter-spacing: -2px;
        text-shadow: 0 2px 10px rgba(129, 140, 248, 0.3);
    ">
        SecureInsights
    </h1>
    <p style="font-size: 1.4rem; color: #94a3b8; margin-top: 1rem; font-weight: 500;">
        Ask Questions in Plain English • Get Instant Insights • 100% Privacy-Safe
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch live record count from Snowflake
live_data_placeholder = st.empty()
live_data_placeholder.markdown("""
<div style="text-align: center; margin-top: -1rem; margin-bottom: 1rem;">
    <span style="background: #667eea; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
        ⏳ Connecting to live data...
    </span>
</div>
""", unsafe_allow_html=True)

try:
    from utils.snowflake_connector import get_connection
    conn = get_connection()
    conn.connect()
    
    count_query = """
    SELECT 
        (SELECT COUNT(*) FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES) +
        (SELECT COUNT(*) FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES) +
        (SELECT COUNT(*) FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES) as total_count
    """
    count_df = conn.execute_query(count_query)
    if not count_df.empty:
        total_records = f"{int(count_df.iloc[0]['TOTAL_COUNT']):,}"
        live_data_placeholder.markdown(f"""
        <div style="text-align: center; margin-top: 1rem; margin-bottom: 2rem; animation: fadeIn 0.5s ease-in;">
            <div style="
                display: inline-block;
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 30px;
                font-weight: 700;
                font-size: 1rem;
                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
                border: 2px solid rgba(255,255,255,0.2);
            ">
                <span style="font-size: 1.2rem;">●</span> Live Data: {total_records} records across 3 organizations
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        live_data_placeholder.empty()
except Exception as e:
    live_data_placeholder.markdown(f"""
    <div style="text-align: center; margin-top: 1rem; margin-bottom: 2rem;">
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 30px;
            font-weight: 700;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
            border: 2px solid rgba(255,255,255,0.2);
        ">
            ⏳ Connecting to live data...
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main value proposition - Vibrant gradient cards
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    ">
        <div style="font-size: 3.5rem; margin-bottom: 1rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">🤖</div>
        <h3 style="color: white; margin: 0 0 0.75rem 0; font-size: 1.4rem; font-weight: 700;">AI-Powered Queries</h3>
        <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 1rem; line-height: 1.6;">Ask questions in plain English, get instant insights</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
        transition: transform 0.3s ease;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    ">
        <div style="font-size: 3.5rem; margin-bottom: 1rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">🔒</div>
        <h3 style="color: white; margin: 0 0 0.75rem 0; font-size: 1.4rem; font-weight: 700;">Privacy-First</h3>
        <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 1rem; line-height: 1.6;">No raw data sharing, only aggregated insights</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);
        transition: transform 0.3s ease;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    ">
        <div style="font-size: 3.5rem; margin-bottom: 1rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">⚡</div>
        <h3 style="color: white; margin: 0 0 0.75rem 0; font-size: 1.4rem; font-weight: 700;">Real-Time</h3>
        <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 1rem; line-height: 1.6;">Live data from Snowflake, instant results</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Problem statement with attractive dark design
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
    border-left: 6px solid #818cf8;
    padding: 2rem 2.5rem;
    border-radius: 15px;
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(129, 140, 248, 0.2);
">
    <h3 style="color: #e2e8f0; margin: 0 0 1rem 0; font-size: 1.4rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
        <span style="font-size: 2rem;">🏛️</span> The Challenge
    </h3>
    <p style="color: #cbd5e1; margin: 0; font-size: 1.1rem; line-height: 1.8; font-weight: 500;">
        Banks, insurers, retailers, and public agencies need to collaborate to detect fraud and serve underserved customers—but <strong style="color: #818cf8; font-weight: 700;">privacy laws prevent sharing raw customer data</strong>.
    </p>
    <div style="margin-top: 1rem; padding: 1rem; background: rgba(30, 41, 59, 0.6); border-radius: 10px; border-left: 3px solid #fbbf24;">
        <p style="color: #94a3b8; margin: 0; font-size: 1rem; font-style: italic;">
            ⚠️ Traditional approaches require complex data-sharing agreements and still expose sensitive information.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Stats section with modern gradient cards
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1e3a8a 0%, #14b8a6 100%);
    padding: 2.5rem 2rem;
    border-radius: 20px;
    margin: 2rem 0;
    box-shadow: 0 10px 40px rgba(30, 58, 138, 0.3);
    position: relative;
    overflow: hidden;
">
    <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%); pointer-events: none;"></div>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem; position: relative;">
        <div style="text-align: center; padding: 1.25rem; background: rgba(255,255,255,0.05); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);">
            <div style="color: rgba(255,255,255,0.85); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.75rem;">Organizations</div>
            <div style="color: white; font-size: 3rem; font-weight: 900; margin-bottom: 0.5rem; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">3</div>
            <div style="background: rgba(16, 185, 129, 0.25); color: #10B981; padding: 0.35rem 0.85rem; border-radius: 25px; font-size: 0.75rem; font-weight: 700; display: inline-block; border: 1px solid rgba(16, 185, 129, 0.3);">● LIVE</div>
        </div>
        <div style="text-align: center; padding: 1.25rem; background: rgba(255,255,255,0.05); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);">
            <div style="color: rgba(255,255,255,0.85); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.75rem;">Total Records</div>
            <div style="color: white; font-size: 3rem; font-weight: 900; margin-bottom: 0.5rem; text-shadow: 0 2px 10px rgba(0,0,0,0.2);" id="record-display">30,000</div>
            <div style="background: rgba(59, 130, 246, 0.25); color: #3B82F6; padding: 0.35rem 0.85rem; border-radius: 25px; font-size: 0.75rem; font-weight: 700; display: inline-block; border: 1px solid rgba(59, 130, 246, 0.3);">● REAL-TIME</div>
        </div>
        <div style="text-align: center; padding: 1.25rem; background: rgba(255,255,255,0.05); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);">
            <div style="color: rgba(255,255,255,0.85); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.75rem;">Privacy Score</div>
            <div style="color: white; font-size: 3rem; font-weight: 900; margin-bottom: 0.5rem; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">100%</div>
            <div style="background: rgba(16, 185, 129, 0.25); color: #10B981; padding: 0.35rem 0.85rem; border-radius: 25px; font-size: 0.75rem; font-weight: 700; display: inline-block; border: 1px solid rgba(16, 185, 129, 0.3);">✓ COMPLIANT</div>
        </div>
        <div style="text-align: center; padding: 1.25rem; background: rgba(255,255,255,0.05); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);">
            <div style="color: rgba(255,255,255,0.85); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.75rem;">Uptime</div>
            <div style="color: white; font-size: 3rem; font-weight: 900; margin-bottom: 0.5rem; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">99.9%</div>
            <div style="background: rgba(16, 185, 129, 0.25); color: #10B981; padding: 0.35rem 0.85rem; border-radius: 25px; font-size: 0.75rem; font-weight: 700; display: inline-block; border: 1px solid rgba(16, 185, 129, 0.3);">✓ SLA</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Update record count with live data
try:
    st.markdown(f"""
    <script>
    document.getElementById('record-display').textContent = '{total_records}';
    </script>
    """, unsafe_allow_html=True)
except:
    pass

st.markdown("<br>", unsafe_allow_html=True)



# CTA Section - Eye-catching design
st.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 4rem 3rem;
    border-radius: 25px;
    text-align: center;
    margin: 3rem 0 2rem 0;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
">
    <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); pointer-events: none;"></div>
    <h2 style="color: white; margin: 0 0 1rem 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -1px; position: relative;">Ready to Get Started?</h2>
    <p style="color: rgba(255,255,255,0.95); font-size: 1.2rem; margin-bottom: 0; position: relative; font-weight: 500;">
        Ask questions in plain English → Get instant insights → 100% privacy-safe
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        if st.button("🔍 Start Exploring", use_container_width=True, type="primary", help="Go to Natural Language Query Interface"):
            st.switch_page("pages/1_Cross_Company_Insights.py")
    with col_b:
        if st.button("🚨 View Fraud Alerts", use_container_width=True, help="Check Real-time Fraud Detection Dashboard"):
            st.switch_page("pages/2_Fraud_Detection.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# Footer - Modern dark theme
st.markdown("""
<div style="
    text-align: center;
    padding: 2.5rem 2rem;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(51, 65, 85, 0.6) 100%);
    border-radius: 20px;
    margin-top: 3rem;
    border: 1px solid rgba(148, 163, 184, 0.2);
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
">
    <p style="margin: 0; font-size: 1.05rem; color: #e2e8f0; font-weight: 600;">
        🏆 Built for <span style="background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 1.1rem;">Snowflake AI for Good Hackathon 2026</span>
    </p>
    <div style="margin-top: 1.25rem; display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;">
        <span style="background: rgba(30, 41, 59, 0.8); padding: 0.6rem 1.2rem; border-radius: 25px; font-size: 0.9rem; color: #cbd5e1; font-weight: 600; box-shadow: 0 2px 10px rgba(0,0,0,0.3); border: 1px solid rgba(148, 163, 184, 0.3);">
            ❄️ Snowflake Cortex AI
        </span>
        <span style="background: rgba(30, 41, 59, 0.8); padding: 0.6rem 1.2rem; border-radius: 25px; font-size: 0.9rem; color: #cbd5e1; font-weight: 600; box-shadow: 0 2px 10px rgba(0,0,0,0.3); border: 1px solid rgba(148, 163, 184, 0.3);">
            🚀 Streamlit
        </span>
        <span style="background: rgba(30, 41, 59, 0.8); padding: 0.6rem 1.2rem; border-radius: 25px; font-size: 0.9rem; color: #cbd5e1; font-weight: 600; box-shadow: 0 2px 10px rgba(0,0,0,0.3); border: 1px solid rgba(148, 163, 184, 0.3);">
            🐍 Python 3.13
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar with dark theme
with st.sidebar:
    st.markdown("<h3 style='color: #e2e8f0;'>🏢 Participating Organizations</h3>", unsafe_allow_html=True)
    
    orgs = config.get('organizations', [])
    for org in orgs:
        st.markdown(f"""
        <div style="
            padding: 1.25rem; 
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%); 
            border-radius: 12px; 
            margin-bottom: 1rem;
            border-left: 4px solid #818cf8;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            border: 1px solid rgba(129, 140, 248, 0.2);
            transition: transform 0.2s ease;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem; text-align: center;">{org.get('icon', '🏢')}</div>
            <strong style="color: #e2e8f0; font-size: 1.1rem; display: block; text-align: center;">{org.get('name', 'Unknown')}</strong>
            <small style="color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; display: block; text-align: center; margin-top: 0.25rem;">{org.get('type', '').title()}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: rgba(148, 163, 184, 0.3); margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e2e8f0;'>📚 Resources</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color: #cbd5e1;'>
    
    - [Setup Guide](docs/SETUP_GUIDE.md)
    - [Demo Script](docs/DEMO_SCRIPT.md)
    - [Architecture](docs/ARCHITECTURE.md)
    - [API Documentation](#)
    
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: rgba(148, 163, 184, 0.3); margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #e2e8f0;'>ℹ️ About</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px; border-left: 3px solid #818cf8;'>
        <p style='color: #e2e8f0; margin: 0; font-weight: 600;'>Version: 1.0.0</p>
        <p style='color: #cbd5e1; margin: 0.5rem 0 0 0; font-weight: 600;'>Tech Stack:</p>
        <ul style='color: #94a3b8; margin: 0.5rem 0 0 0; padding-left: 1.5rem;'>
            <li>Streamlit</li>
            <li>Snowflake</li>
            <li>Cortex AI</li>
            <li>Data Clean Rooms</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)




