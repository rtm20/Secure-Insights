"""
Reusable Loading Component
Consistent loader across the entire application
"""

import streamlit as st

def show_loader(message="Loading data from Snowflake..."):
    """
    Display a consistent, visually appealing loader
    
    Args:
        message: Custom loading message to display
    """
    st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        margin: 2rem 0;
    ">
        <div style="
            width: 60px;
            height: 60px;
            border: 4px solid rgba(102, 126, 234, 0.2);
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1.5rem;
        "></div>
        <div style="
            color: #a78bfa;
            font-size: 1.1rem;
            font-weight: 500;
            text-align: center;
            margin-bottom: 0.5rem;
        ">
            ❄️ {message}
        </div>
        <div style="
            color: #94a3b8;
            font-size: 0.9rem;
            text-align: center;
        ">
            Querying live data from Snowflake databases...
        </div>
    </div>
    <style>
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)
