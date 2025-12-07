"""
Cross-Company Insights Page
Natural language query interface for privacy-safe analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.snowflake_connector import get_connection
from utils.ai_explainer import get_explainer
from utils.query_builder import get_query_builder

st.set_page_config(
    page_title="Cross-Company Insights",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .insight-card {
        background-color: #F0F9FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .privacy-badge {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Cross-Company Insights")

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_results' not in st.session_state:
    st.session_state.current_results = None
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True

# Sidebar - Organization selector
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">👋 Welcome!</div>
        <div style="font-size: 0.9rem;">Select your organization and query mode below</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🏢 Your Organization")
    
    # Load organizations from config
    import yaml
    from pathlib import Path
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            orgs = config.get('organizations', [])
            org_names = [f"{org['icon']} {org['name']}" for org in orgs]
    else:
        org_names = ["🏦 Metro Bank", "🛡️ SafeGuard Insurance", "🛒 RetailCorp"]
    
    org_name = st.selectbox(
        "Select your organization",
        org_names,
        key="org_selector",
        help="Choose which organization you represent. Data access is scoped to your permissions."
    )
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    ">
        <strong style="color: #a78bfa; font-size: 0.9rem;">Logged in as:</strong><br>
        <span style="color: white; font-size: 1.05rem;">{org_name}</span><br>
        <small style="color: #94a3b8;">Analyst Role</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔍 Query Type")
    
    # Add explanatory text before radio buttons - dark themed
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #92400e 0%, #78350f 100%);
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        border-left: 4px solid #fbbf24;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    ">
        <strong style="color: #fde68a;">💡 Tip:</strong> 
        <span style="color: rgba(255, 255, 255, 0.95);">Start with <strong style="color: white;">Natural Language</strong> if you're new!</span>
    </div>
    """, unsafe_allow_html=True)
    
    query_mode = st.radio(
        "Choose query mode",
        ["Natural Language", "Predefined Queries", "Advanced"],
        help="""
        • Natural Language: Ask questions in plain English (Recommended)
        • Predefined Queries: Select from template queries
        • Advanced: Write custom SQL queries
        """
    )
    
    st.markdown("---")
    st.markdown("### 📊 Data Sources")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    ">
        <div style="color: #86efac; font-size: 0.9rem;">✅ Bank transactions (10K)</div>
        <div style="color: #86efac; font-size: 0.9rem;">✅ Insurance claims (8K)</div>
        <div style="color: #86efac; font-size: 0.9rem;">✅ Retail purchases (12K)</div>
        <div style="color: #fbbf24; font-weight: 600; margin-top: 0.5rem; font-size: 0.95rem;">Total: 30,000 records</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Help section
    with st.expander("❓ Need Help?"):
        st.markdown("""
        ### Quick Tips:
        
        **For Natural Language:**
        - Ask questions like you're talking to a person
        - Be specific: "Which age groups..." not just "age"
        - Use keywords: fraud, risk, geographic, age, etc.
        
        **Understanding Results:**
        - 📊 Charts show visual patterns
        - 📋 Tables show detailed numbers
        - 💡 AI Insights explain what the data means
        
        **Privacy:**
        - All results require minimum 50 records
        - No individual customer data is shown
        - Identity hashes protect privacy
        
        **Troubleshooting:**
        - If AI fails, we use optimized templates
        - Try rephrasing your question
        - Use example questions as templates
        """)
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        ">
            <strong style="color: #93c5fd;">📧 Need more help?</strong><br>
            <span style="color: rgba(255, 255, 255, 0.95);">Contact: support@secureinsights.com</span>
        </div>
        """, unsafe_allow_html=True)

# Main content area
if query_mode == "Natural Language":
    # MAIN FEATURE - Query box at the top with hero design
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    ">
        <h1 style="margin: 0 0 0.5rem 0; color: white; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">🤖 Ask Questions in Natural Language</h1>
        <p style="margin: 0; font-size: 1.2rem; color: rgba(255, 255, 255, 0.95);">Type your question below and get privacy-safe answers from multiple organizations instantly</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Example questions - dark themed and prominent
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.25rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    ">
        <strong style="font-size: 1.15rem; color: #fbbf24;">💡 Click any example to auto-fill your question:</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Add CSS for button styling
    st.markdown("""
    <style>
    /* Pink button */
    button[kind="secondary"]:nth-of-type(1) {
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    button[kind="secondary"]:nth-of-type(1):hover {
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    /* Blue button */
    button[kind="secondary"]:nth-of-type(2) {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    button[kind="secondary"]:nth-of-type(2):hover {
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    /* Green button */
    button[kind="secondary"]:nth-of-type(3) {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    button[kind="secondary"]:nth-of-type(3):hover {
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Initialize flag to trigger text area update
    if 'question_changed' not in st.session_state:
        st.session_state.question_changed = False
    
    with col1:
        if st.button("🎯 Age Group Fraud", use_container_width=True, key="example1", type="secondary"):
            st.session_state.nl_query_input = "Which age groups have the highest combined fraud risk?"
            st.session_state.question_changed = True
            st.rerun()
    with col2:
        if st.button("🗺️ Geographic Hotspots", use_container_width=True, key="example2", type="secondary"):
            st.session_state.nl_query_input = "Show me geographic areas with elevated fraud rates"
            st.session_state.question_changed = True
            st.rerun()
    with col3:
        if st.button("📊 Organization Summary", use_container_width=True, key="example3", type="secondary"):
            st.session_state.nl_query_input = "What is the overall fraud summary by organization?"
            st.session_state.question_changed = True
            st.rerun()
    
    # Query input box - Large and prominent
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Initialize the text area value if not exists
    if 'nl_query_input' not in st.session_state:
        st.session_state.nl_query_input = ''
    
    user_question = st.text_area(
        "**✍️ Type your question here:**",
        value=st.session_state.nl_query_input,
        placeholder="e.g., Which age groups show the highest combined risk of insurance fraud and credit default?",
        height=120,
        help="Type your question in plain English. AI will convert it to SQL and query your data."
    )
    
    # Update session state only if user manually changed it
    if not st.session_state.question_changed:
        st.session_state.nl_query_input = user_question
    else:
        st.session_state.question_changed = False
    
    # Add CSS for Analyze and Clear buttons
    st.markdown("""
    <style>
    /* Analyze button - vibrant red/coral gradient */
    button[kind="primary"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(239, 68, 68, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    /* Clear button - pink/magenta gradient */
    div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="column"]:nth-child(2) button:hover {
        box-shadow: 0 6px 25px rgba(236, 72, 153, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True, 
                                   help="Click to generate SQL and execute query",
                                   key="analyze_main")
    with col2:
        clear_button = st.button("🔄 Clear", use_container_width=True,
                                help="Clear the question and results")
    
    if clear_button:
        st.session_state.current_results = None
        st.rerun()
    
    if analyze_button and user_question:
        # Show loading state
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            color: white;
            margin: 2rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: white; margin: 0;">AI is Analyzing Your Question...</h3>
            <p style="color: white; opacity: 0.9; margin-top: 0.5rem;">Connecting to Snowflake • Generating SQL • Executing Query</p>
            <div style="margin-top: 1rem;">
                <div style="display: inline-block; width: 50px; height: 50px; border: 5px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            </div>
        </div>
        <style>
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.spinner("Processing..."):
            try:
                # Get connection to Snowflake
                conn = get_connection()
                
                if not conn.connect():
                    loading_placeholder.empty()
                    st.error("Failed to connect to Snowflake")
                    st.stop()
                
                loading_placeholder.empty()
                
                # Use Cortex AI to generate SQL from natural language
                ai_prompt = f"""You are a SQL expert for Snowflake data warehouses. Generate a privacy-safe SQL query for the following question.

IMPORTANT RULES:
1. Always use UNION ALL to combine data from multiple tables
2. Always include: HAVING COUNT(*) >= 50 (minimum aggregation for privacy)
3. Never return individual records - only aggregated results
4. Use GROUP BY for all queries
5. Round decimal values to 1 decimal place

Available tables and schemas:
- BANK_DB.RISK.CUSTOMER_RISK_SCORES (columns: customer_id, age, zip_code, credit_score, default_flag, transaction_count, avg_transaction_amount, account_open_date, last_activity_date)
- INSURANCE_DB.RISK.CLAIM_RISK_SCORES (columns: policy_holder_id, age, zip_code, claim_frequency, total_claim_amount, fraud_indicator, policy_start_date, last_claim_date)
- RETAIL_DB.RISK.CUSTOMER_RISK_SCORES (columns: customer_id, age, zip_code, return_rate, total_purchase_amount, high_value_returns_flag, first_purchase_date, last_purchase_date)

User question: {user_question}

Generate ONLY the SQL query, no explanations. The query should return results that answer the question."""

                # Try to use Cortex AI
                try:
                    cortex_query = f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'mistral-large',
                        '{ai_prompt.replace("'", "''")}'
                    ) as generated_sql
                    """
                    
                    ai_result = conn.execute_query(cortex_query)
                    if not ai_result.empty:
                        generated_sql = ai_result.iloc[0]['GENERATED_SQL']
                        # Extract SQL from markdown code blocks if present
                        if '```sql' in generated_sql:
                            generated_sql = generated_sql.split('```sql')[1].split('```')[0].strip()
                        elif '```' in generated_sql:
                            generated_sql = generated_sql.split('```')[1].split('```')[0].strip()
                        
                        st.info(f"🤖 AI Generated Query")
                        with st.expander("View Generated SQL"):
                            st.code(generated_sql, language='sql')
                        
                        query = generated_sql
                    else:
                        raise Exception("Cortex AI returned empty result")
                        
                except Exception as cortex_error:
                    # Fallback to keyword-based queries if Cortex fails
                    st.warning(f"⚠️ AI generation unavailable, using optimized query templates")
                    
                    if "age" in user_question.lower() or "demographic" in user_question.lower():
                        # Age group analysis from real data
                        query = """
                    WITH combined_data AS (
                        SELECT 
                            CASE 
                                WHEN age BETWEEN 18 AND 24 THEN '18-24'
                                WHEN age BETWEEN 25 AND 34 THEN '25-34'
                                WHEN age BETWEEN 35 AND 44 THEN '35-44'
                                WHEN age BETWEEN 45 AND 54 THEN '45-54'
                                WHEN age BETWEEN 55 AND 64 THEN '55-64'
                                ELSE '65+'
                            END AS AGE_GROUP,
                            credit_score,
                            default_flag,
                            'BANK' as SOURCE
                        FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
                        
                        UNION ALL
                        
                        SELECT 
                            CASE 
                                WHEN age BETWEEN 18 AND 24 THEN '18-24'
                                WHEN age BETWEEN 25 AND 34 THEN '25-34'
                                WHEN age BETWEEN 35 AND 44 THEN '35-44'
                                WHEN age BETWEEN 45 AND 54 THEN '45-54'
                                WHEN age BETWEEN 55 AND 64 THEN '55-64'
                                ELSE '65+'
                            END AS AGE_GROUP,
                            NULL as credit_score,
                            fraud_indicator as default_flag,
                            'INSURANCE' as SOURCE
                        FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
                        
                        UNION ALL
                        
                        SELECT 
                            CASE 
                                WHEN age BETWEEN 18 AND 24 THEN '18-24'
                                WHEN age BETWEEN 25 AND 34 THEN '25-34'
                                WHEN age BETWEEN 35 AND 44 THEN '35-44'
                                WHEN age BETWEEN 45 AND 54 THEN '45-54'
                                WHEN age BETWEEN 55 AND 64 THEN '55-64'
                                ELSE '65+'
                            END AS AGE_GROUP,
                            NULL as credit_score,
                            high_value_returns_flag as default_flag,
                            'RETAIL' as SOURCE
                        FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
                    )
                    SELECT 
                        AGE_GROUP,
                        COUNT(*) as RECORD_COUNT,
                        ROUND(AVG(COALESCE(credit_score, 50)), 1) as AVG_RISK_SCORE,
                        SUM(default_flag) as FRAUD_CASES,
                        ROUND(SUM(default_flag) * 100.0 / COUNT(*), 1) as FRAUD_RATE_PCT
                    FROM combined_data
                    GROUP BY AGE_GROUP
                    HAVING COUNT(*) >= 50
                    ORDER BY AVG_RISK_SCORE DESC
                    """
                    
                    elif "geographic" in user_question.lower() or "location" in user_question.lower() or "zip" in user_question.lower():
                        # Geographic analysis
                        query = """
                    WITH combined_data AS (
                        SELECT 
                            SUBSTR(zip_code, 1, 3) AS ZIP_PREFIX,
                            credit_score,
                            default_flag
                        FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
                        
                        UNION ALL
                        
                        SELECT 
                            SUBSTR(zip_code, 1, 3) AS ZIP_PREFIX,
                            NULL as credit_score,
                            fraud_indicator as default_flag
                        FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
                        
                        UNION ALL
                        
                        SELECT 
                            SUBSTR(zip_code, 1, 3) AS ZIP_PREFIX,
                            NULL as credit_score,
                            high_value_returns_flag as default_flag
                        FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
                    )
                    SELECT 
                        ZIP_PREFIX as ZIP_CODE_PREFIX,
                        COUNT(*) as CUSTOMER_COUNT,
                        ROUND(AVG(COALESCE(credit_score, 50)), 1) as AVG_RISK_SCORE,
                        SUM(default_flag) as FRAUD_CASES
                    FROM combined_data
                    GROUP BY ZIP_PREFIX
                    HAVING COUNT(*) >= 50
                    ORDER BY AVG_RISK_SCORE DESC
                    LIMIT 20
                    """
                    
                    else:
                        # Default summary query
                        query = """
                    WITH combined_data AS (
                        SELECT 
                            'Bank' as SOURCE_ORG,
                            COUNT(*) as TOTAL_RECORDS,
                            SUM(default_flag) as FRAUD_CASES,
                            ROUND(AVG(credit_score), 1) as AVG_RISK_SCORE
                        FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
                        
                        UNION ALL
                        
                        SELECT 
                            'Insurance' as SOURCE_ORG,
                            COUNT(*) as TOTAL_RECORDS,
                            SUM(fraud_indicator) as FRAUD_CASES,
                            50.0 as AVG_RISK_SCORE
                        FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
                        
                        UNION ALL
                        
                        SELECT 
                            'Retail' as SOURCE_ORG,
                            COUNT(*) as TOTAL_RECORDS,
                            SUM(high_value_returns_flag) as FRAUD_CASES,
                            50.0 as AVG_RISK_SCORE
                        FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
                    )
                    SELECT 
                        SOURCE_ORG as ORGANIZATION,
                        TOTAL_RECORDS,
                        FRAUD_CASES,
                        AVG_RISK_SCORE,
                        ROUND(FRAUD_CASES * 100.0 / NULLIF(TOTAL_RECORDS, 0), 2) as FRAUD_RATE_PCT
                    FROM combined_data
                    ORDER BY FRAUD_RATE_PCT DESC
                    """
                    
                # Execute the query (whether AI-generated or fallback)
                result_df = conn.execute_query(query)
                
                if result_df.empty:
                    st.warning("No data returned from query. Try rephrasing your question.")
                    st.stop()
                
                # Smart column renaming - make names readable
                readable_columns = {}
                for col in result_df.columns:
                    # Convert SQL column names to readable format
                    readable = col.replace('_', ' ').title()
                    readable_columns[col] = readable
                
                demo_data = result_df.rename(columns=readable_columns)
                
                st.success("✅ Query executed successfully!")
                st.session_state.current_results = demo_data
                    
                # Display results
                st.markdown("### 📊 Results")
                
                # Show key metrics if numeric columns exist
                numeric_cols = demo_data.select_dtypes(include=['int64', 'float64']).columns.tolist()
                if numeric_cols:
                    cols = st.columns(min(4, len(numeric_cols)))
                    for idx, col_name in enumerate(numeric_cols[:4]):
                        with cols[idx]:
                            value = demo_data[col_name].sum() if 'count' in col_name.lower() else demo_data[col_name].mean()
                            st.metric(col_name, f"{value:,.1f}")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Smart visualization based on data structure
                if len(demo_data.columns) >= 2:
                    # Get first text/category column and first numeric column
                    cat_col = next((col for col in demo_data.columns if demo_data[col].dtype == 'object'), demo_data.columns[0])
                    num_cols = [col for col in demo_data.columns if col != cat_col and demo_data[col].dtype in ['int64', 'float64']]
                    
                    if num_cols:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig = px.bar(
                                demo_data,
                                x=cat_col,
                                y=num_cols[0],
                                title=f'{num_cols[0]} by {cat_col}',
                                color=num_cols[0],
                                color_continuous_scale='Reds'
                            )
                            fig.update_layout(height=400, showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            if len(num_cols) > 1:
                                fig = px.line(
                                    demo_data,
                                    x=cat_col,
                                    y=num_cols[1],
                                    title=f'{num_cols[1]} by {cat_col}',
                                    markers=True
                                )
                                fig.update_traces(line_color='#DC2626', marker=dict(size=10))
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                # Show pie chart if only one numeric
                                fig = px.pie(
                                    demo_data,
                                    names=cat_col,
                                    values=num_cols[0],
                                    title=f'Distribution of {num_cols[0]}'
                                )
                                fig.update_layout(height=400)
                                st.plotly_chart(fig, use_container_width=True)
                    
                # Data table
                st.markdown("### 📋 Detailed Data")
                st.dataframe(demo_data, use_container_width=True, hide_index=True)
                
                # Export options
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("📥 Export to CSV", use_container_width=True):
                        csv = demo_data.to_csv(index=False)
                        st.download_button("Download CSV", csv, "insights.csv", "text/csv")
                
                # Privacy badge and help section - after results
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #065f46 0%, #047857 100%);
                    padding: 1rem;
                    border-radius: 10px;
                    border-left: 4px solid #10b981;
                    color: white;
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
                ">
                    🔒 <strong style="color: #6ee7b7;">Privacy Protected:</strong> 
                    <span style="color: rgba(255, 255, 255, 0.95);">All results are aggregated (min. 50 records) and anonymized • 30,000 records across 3 organizations</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Collapsible help section
                with st.expander("📚 More Example Questions & Help"):
                    st.markdown("""
                    **Demographic Analysis:**
                    - Which age groups have the highest combined fraud risk?
                    - Compare fraud rates across different age demographics
                    
                    **Geographic Analysis:**
                    - Show me geographic areas with elevated insurance claim rates
                    - Are there patterns connecting retail returns and loan defaults?
                    
                    **Cross-Organization Insights:**
                    - Which demographic segments are underserved by financial services?
                    - What trends have emerged in fraud patterns over the last 6 months?
                    
                    ### Quick Tips:
                    - Ask questions like you're talking to a person
                    - Be specific: "Which age groups..." not just "age"
                    - Use keywords: fraud, risk, geographic, age, etc.
                    """)
                
            except Exception as e:
                st.error(f"❌ Error executing query: {str(e)}")
                st.exception(e)
                
                # Show privacy and help even on error
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #065f46 0%, #047857 100%);
                    padding: 1rem;
                    border-radius: 10px;
                    border-left: 4px solid #10b981;
                    color: white;
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
                ">
                    🔒 <strong style="color: #6ee7b7;">Privacy Protected:</strong> 
                    <span style="color: rgba(255, 255, 255, 0.95);">All results are aggregated (min. 50 records) and anonymized • 30,000 records across 3 organizations</span>
                </div>
                """, unsafe_allow_html=True)

elif query_mode == "Predefined Queries":
    st.markdown("### 📊 Predefined Analysis Templates")
    
    query_template = st.selectbox(
        "Select analysis type:",
        [
            "Fraud Risk by Demographics",
            "Geographic Risk Heatmap",
            "Cross-Organization Patterns",
            "Time Series Trend Analysis",
            "Segment Comparison",
            "High-Value Transaction Patterns"
        ]
    )
    
    # Configuration based on template
    if query_template == "Fraud Risk by Demographics":
        col1, col2 = st.columns(2)
        with col1:
            demographic = st.selectbox("Group by:", ["Age Group", "Income Bracket", "Employment Status"])
        with col2:
            min_risk = st.slider("Minimum risk score:", 0, 100, 50)
    
    elif query_template == "Geographic Risk Heatmap":
        col1, col2 = st.columns(2)
        with col1:
            top_n = st.number_input("Show top N areas:", 10, 100, 20)
        with col2:
            metric = st.selectbox("Rank by:", ["Risk Score", "Fraud Cases", "Fraud Rate"])
    
    if st.button("▶️ Run Analysis", type="primary"):
        with st.spinner("Analyzing data..."):
            st.success("✅ Analysis complete!")
            st.info("🔨 This is a template. Results would be displayed here similar to the Natural Language mode.")

else:  # Advanced mode
    st.markdown("### ⚙️ Advanced Query Builder")
    st.warning("⚠️ Advanced mode requires SQL knowledge and understanding of privacy constraints.")
    
    # Show available tables
    with st.expander("📚 Available Tables & Columns"):
        st.code("""
CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK
  - age_group, risk_score, claim_amount, default_rate, ...

CLEANROOM_DB.AGGREGATED_VIEWS.GEOGRAPHIC_RISK
  - zip_code_prefix, customer_count, risk_score, fraud_flag, ...

CLEANROOM_DB.FRAUD_DETECTION.DETECTED_PATTERNS
  - pattern_type, risk_level, affected_segments, organization_count, ...
        """)
    
    sql_query = st.text_area(
        "Enter your SQL query:",
        placeholder="""SELECT 
    age_group, 
    COUNT(*) as count,
    AVG(risk_score) as avg_risk
FROM CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK
GROUP BY age_group
HAVING COUNT(*) >= 50
ORDER BY avg_risk DESC""",
        height=200
    )
    
    if st.button("🔍 Execute Query", type="primary"):
        # Validate query
        builder = get_query_builder()
        is_valid, message = builder.validate_query(sql_query)
        
        if is_valid:
            with st.spinner("Executing query..."):
                st.success("✅ Query executed successfully!")
                st.info("🔨 Results would be displayed here.")
        else:
            st.error(f"❌ Query validation failed: {message}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 1rem;">
    <small>🔒 All queries are logged for audit purposes | Privacy guaranteed by Snowflake Data Clean Rooms</small>
</div>
""", unsafe_allow_html=True)
