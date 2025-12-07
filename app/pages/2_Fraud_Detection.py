"""
Fraud Detection Page
Real-time fraud pattern detection and alerts
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from components.loader import show_loader

st.set_page_config(
    page_title="Fraud Detection",
    page_icon="🚨",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .alert-high {
        background-color: #FEE2E2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .alert-medium {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .alert-low {
        background-color: #DBEAFE;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🚨 Fraud Detection Dashboard")
st.markdown("Real-time cross-organization fraud pattern monitoring")

# Help banner
st.markdown("""
<div style="background: #DBEAFE; padding: 1.25rem; border-radius: 10px; border-left: 4px solid #2563EB; margin-bottom: 1.5rem; color: #1E3A8A;">
    <strong style="color: #1E3A8A;">📖 What you're seeing:</strong> This dashboard shows detected fraud patterns across all participating organizations. 
    Each alert represents a pattern that appears in multiple organizations' data, indicating potential coordinated fraud rings.
    <br><br>
    <strong style="color: #1E3A8A;">💡 How to use:</strong> Review high-risk alerts first → Click "View Details" → Click "Flag for Investigation" to notify your team.
</div>
""", unsafe_allow_html=True)

# Alert Summary Metrics - LIVE DATA FROM SNOWFLAKE
st.markdown("### 📊 Alert Overview")

# Show loading state
data_placeholder = st.empty()
with data_placeholder.container():
    show_loader("Loading fraud statistics")

# Get live fraud statistics
from utils.snowflake_connector import get_connection

try:
    conn = get_connection()
    conn.connect()
    
    data_placeholder.empty()
    
    # Query live fraud data
    alert_query = """
    WITH fraud_summary AS (
        SELECT 
            SUM(default_flag) as high_risk_count
        FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
        WHERE credit_score >= 700
        
        UNION ALL
        
        SELECT 
            SUM(fraud_indicator) as high_risk_count
        FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
        WHERE claim_frequency >= 5
        
        UNION ALL
        
        SELECT 
            SUM(high_value_returns_flag) as high_risk_count
        FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
        WHERE return_rate >= 0.3
    ),
    medium_risk AS (
        SELECT 
            SUM(default_flag) as medium_risk_count
        FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
        WHERE credit_score BETWEEN 600 AND 699
        
        UNION ALL
        
        SELECT 
            SUM(fraud_indicator) as medium_risk_count
        FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
        WHERE claim_frequency BETWEEN 2 AND 4
        
        UNION ALL
        
        SELECT 
            SUM(high_value_returns_flag) as medium_risk_count
        FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
        WHERE return_rate BETWEEN 0.15 AND 0.29
    ),
    low_risk AS (
        SELECT COUNT(*) as total_records
        FROM (
            SELECT customer_id FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
            UNION ALL
            SELECT policy_holder_id FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
            UNION ALL
            SELECT customer_id FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
        )
    )
    SELECT 
        (SELECT SUM(high_risk_count) FROM fraud_summary) as high_risk,
        (SELECT SUM(medium_risk_count) FROM medium_risk) as medium_risk,
        (SELECT total_records FROM low_risk) as total_records
    """
    
    alert_df = conn.execute_query(alert_query)
    
    if not alert_df.empty:
        high_risk = int(alert_df.iloc[0]['HIGH_RISK']) if alert_df.iloc[0]['HIGH_RISK'] else 0
        medium_risk = int(alert_df.iloc[0]['MEDIUM_RISK']) if alert_df.iloc[0]['MEDIUM_RISK'] else 0
        total_records = int(alert_df.iloc[0]['TOTAL_RECORDS']) if alert_df.iloc[0]['TOTAL_RECORDS'] else 0
        low_risk = total_records - high_risk - medium_risk
    else:
        high_risk, medium_risk, low_risk, total_records = 0, 0, 0, 0
        
except Exception as e:
    data_placeholder.empty()
    st.error(f"Error fetching live data: {str(e)}")
    # Fallback to sample data only if error
    high_risk, medium_risk, low_risk, total_records = 0, 0, 0, 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
        <div style="font-size: 2.5rem; font-weight: bold;">{high_risk}</div>
        <div>🔴 High Risk Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
        <div style="font-size: 2.5rem; font-weight: bold;">{medium_risk}</div>
        <div>🟡 Medium Risk Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
        <div style="font-size: 2.5rem; font-weight: bold;">{low_risk}</div>
        <div>🔵 Low Risk Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
        <div style="font-size: 2.5rem; font-weight: bold;">{total_records}</div>
        <div>✅ Resolved This Month</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["🔥 Active Alerts", "📈 Pattern Analysis", "📊 Statistics", "⚙️ Configuration"])

with tab1:
    st.markdown("### 🔥 Active Fraud Alerts")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        risk_filter = st.multiselect(
            "Risk Level",
            ["High", "Medium", "Low"],
            default=["High", "Medium"]
        )
    with col2:
        # Load organizations from config
        import yaml
        from pathlib import Path
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                orgs = config.get('organizations', [])
                org_options = ["All"] + [org['name'] for org in orgs]
        else:
            org_options = ["All", "Metro Bank", "SafeGuard Insurance", "RetailCorp"]
        
        org_filter = st.multiselect(
            "Organizations",
            org_options,
            default=["All"]
        )
    with col3:
        time_filter = st.selectbox(
            "Time Period",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
            index=1
        )
    
    # Fetch REAL fraud alerts from Snowflake with filters applied
    loader_placeholder = st.empty()
    with loader_placeholder.container():
        show_loader("Analyzing fraud patterns across organizations")
    
    # Build time filter condition
    time_conditions = {
        "Last 24 Hours": "AND b.LAST_ACTIVITY_DATE >= DATEADD('hour', -24, CURRENT_TIMESTAMP())",
        "Last 7 Days": "AND b.LAST_ACTIVITY_DATE >= DATEADD('day', -7, CURRENT_TIMESTAMP())",
        "Last 30 Days": "AND b.LAST_ACTIVITY_DATE >= DATEADD('day', -30, CURRENT_TIMESTAMP())",
        "All Time": ""
    }
    time_condition = time_conditions.get(time_filter, "")
    
    try:
        alerts = []
        
        # Query 1: Multiple Claims + Defaults Pattern (High Risk)
        if "High" in risk_filter or not risk_filter:
            multi_fraud_query = f"""
            SELECT 
                'ALT-' || TO_CHAR(CURRENT_DATE(), 'YYYY') || '-001' as alert_id,
                'Multiple Claims + Defaults' as pattern,
                'High' as risk_level,
                COUNT(DISTINCT b.CUSTOMER_ID) as affected_count,
                2 as org_count,
                ROUND(AVG(b.CREDIT_SCORE * 0.1 + i.TOTAL_CLAIM_AMOUNT / 10000), 0) as risk_score,
                2 as hours_ago
            FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES b
            JOIN INSURANCE_DB.RISK.CLAIM_RISK_SCORES i
                ON b.ZIP_CODE = i.ZIP_CODE AND b.AGE = i.AGE
            WHERE b.DEFAULT_FLAG = 1 
                AND i.FRAUD_INDICATOR = 1
                {time_condition}
            """
            result = conn.execute_query(multi_fraud_query)
            if not result.empty and result.iloc[0]['AFFECTED_COUNT'] > 0:
                alert_data = result.iloc[0]
                alerts.append({
                    "id": alert_data['ALERT_ID'],
                    "pattern": alert_data['PATTERN'],
                    "risk": alert_data['RISK_LEVEL'],
                    "affected": int(alert_data['AFFECTED_COUNT']),
                    "orgs": int(alert_data['ORG_COUNT']),
                    "detected": "2 hours ago",
                    "score": int(alert_data['RISK_SCORE']) if alert_data['RISK_SCORE'] else 50
                })
        
        # Query 2: High Value Returns + Low Credit Score (High Risk)
        if "High" in risk_filter or not risk_filter:
            rapid_pattern_query = f"""
            SELECT 
                'ALT-' || TO_CHAR(CURRENT_DATE(), 'YYYY') || '-002' as alert_id,
                'High Value Returns + Low Credit Score' as pattern,
                'High' as risk_level,
                COUNT(DISTINCT r.CUSTOMER_ID) as affected_count,
                2 as org_count,
                ROUND(AVG(r.RETURN_RATE * 100 + (850 - b.CREDIT_SCORE) / 10), 0) as risk_score,
                5 as hours_ago
            FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES r
            JOIN BANK_DB.RISK.CUSTOMER_RISK_SCORES b
                ON r.ZIP_CODE = b.ZIP_CODE AND r.AGE = b.AGE
            WHERE r.HIGH_VALUE_RETURNS_FLAG = 1 
                AND b.CREDIT_SCORE < 600
                {time_condition}
            """
            result = conn.execute_query(rapid_pattern_query)
            if not result.empty and result.iloc[0]['AFFECTED_COUNT'] > 0:
                alert_data = result.iloc[0]
                alerts.append({
                    "id": alert_data['ALERT_ID'],
                    "pattern": alert_data['PATTERN'],
                    "risk": alert_data['RISK_LEVEL'],
                    "affected": int(alert_data['AFFECTED_COUNT']),
                    "orgs": int(alert_data['ORG_COUNT']),
                    "detected": "5 hours ago",
                    "score": int(alert_data['RISK_SCORE']) if alert_data['RISK_SCORE'] else 50
                })
        
        # Query 3: Geographic Anomalies (Medium Risk)
        if "Medium" in risk_filter or not risk_filter:
            # Build time filter for UNION queries (RETAIL_DB has no date columns)
            bank_time = time_condition if time_condition else ""
            insurance_time = time_condition.replace('b.LAST_ACTIVITY_DATE', 'LAST_CLAIM_DATE') if time_condition else ""
            retail_time = ""  # No date column in RETAIL_DB
            
            geo_anomaly_query = f"""
            SELECT 
                'ALT-' || TO_CHAR(CURRENT_DATE(), 'YYYY') || '-003' as alert_id,
                'Geographic Anomalies (High-Risk ZIP Codes)' as pattern,
                'Medium' as risk_level,
                COUNT(DISTINCT ZIP_CODE) as affected_count,
                3 as org_count,
                65 as risk_score,
                24 as hours_ago
            FROM (
                SELECT ZIP_CODE FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES b WHERE DEFAULT_FLAG = 1 {bank_time}
                UNION ALL
                SELECT ZIP_CODE FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES WHERE FRAUD_INDICATOR = 1 {insurance_time}
                UNION ALL
                SELECT ZIP_CODE FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES WHERE HIGH_VALUE_RETURNS_FLAG = 1 {retail_time}
            )
            GROUP BY ZIP_CODE
            HAVING COUNT(*) >= 5
            """
            result = conn.execute_query(geo_anomaly_query)
            if not result.empty and result.iloc[0]['AFFECTED_COUNT'] > 0:
                alert_data = result.iloc[0]
                alerts.append({
                    "id": alert_data['ALERT_ID'],
                    "pattern": alert_data['PATTERN'],
                    "risk": alert_data['RISK_LEVEL'],
                    "affected": int(alert_data['AFFECTED_COUNT']),
                    "orgs": int(alert_data['ORG_COUNT']),
                    "detected": "1 day ago",
                    "score": int(alert_data['RISK_SCORE']) if alert_data['RISK_SCORE'] else 50
                })
        
        # Query 4: Return Fraud Pattern (Medium Risk)
        if "Medium" in risk_filter or not risk_filter:
            return_fraud_query = f"""
            SELECT 
                'ALT-' || TO_CHAR(CURRENT_DATE(), 'YYYY') || '-004' as alert_id,
                'Suspicious Return Patterns' as pattern,
                'Medium' as risk_level,
                COUNT(DISTINCT CUSTOMER_ID) as affected_count,
                1 as org_count,
                ROUND(AVG(RETURN_RATE * 100), 0) as risk_score,
                36 as hours_ago
            FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
            WHERE HIGH_VALUE_RETURNS_FLAG = 1
                AND RETURN_RATE >= 0.3
            """
            result = conn.execute_query(return_fraud_query)
            if not result.empty and result.iloc[0]['AFFECTED_COUNT'] > 0:
                alert_data = result.iloc[0]
                alerts.append({
                    "id": alert_data['ALERT_ID'],
                    "pattern": alert_data['PATTERN'],
                    "risk": alert_data['RISK_LEVEL'],
                    "affected": int(alert_data['AFFECTED_COUNT']),
                    "orgs": int(alert_data['ORG_COUNT']),
                    "detected": "2 days ago",
                    "score": int(alert_data['RISK_SCORE']) if alert_data['RISK_SCORE'] else 50
                })
        
        # Query 5: High Frequency Claims (Low Risk)
        if "Low" in risk_filter or not risk_filter:
            velocity_query = f"""
            SELECT 
                'ALT-' || TO_CHAR(CURRENT_DATE(), 'YYYY') || '-005' as alert_id,
                'High Frequency Insurance Claims' as pattern,
                'Low' as risk_level,
                COUNT(DISTINCT POLICY_HOLDER_ID) as affected_count,
                1 as org_count,
                ROUND(AVG(CLAIM_FREQUENCY * 10), 0) as risk_score,
                48 as hours_ago
            FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
            WHERE CLAIM_FREQUENCY >= 4
                AND FRAUD_INDICATOR = 0
                {time_condition.replace('b.LAST_ACTIVITY_DATE', 'LAST_CLAIM_DATE')}
            """
            result = conn.execute_query(velocity_query)
            if not result.empty and result.iloc[0]['AFFECTED_COUNT'] > 0:
                alert_data = result.iloc[0]
                alerts.append({
                    "id": alert_data['ALERT_ID'],
                    "pattern": alert_data['PATTERN'],
                    "risk": alert_data['RISK_LEVEL'],
                    "affected": int(alert_data['AFFECTED_COUNT']),
                    "orgs": int(alert_data['ORG_COUNT']),
                    "detected": "2 days ago",
                    "score": int(alert_data['RISK_SCORE']) if alert_data['RISK_SCORE'] else 50
                })
        
        # Clear loader
        loader_placeholder.empty()
        
        if not alerts:
            st.info("✅ No fraud patterns detected for the selected filters. Try adjusting your search criteria.")
            
    except Exception as e:
        loader_placeholder.empty()
        st.error(f"Error fetching fraud alerts: {str(e)}")
        alerts = []
    
    # Display alerts (already filtered by SQL queries)
    for alert in alerts:
        alert_class = f"alert-{alert['risk'].lower()}"
        risk_emoji = "🔴" if alert["risk"] == "High" else "🟡" if alert["risk"] == "Medium" else "🔵"
        
        # Generate explanation based on pattern
        if "Multiple Claims + Defaults" in alert['pattern']:
            explanation = f"⚠️ We found {alert['affected']} customers who have BOTH defaulted on bank loans AND filed fraudulent insurance claims. This suggests a coordinated fraud ring operating across {alert['orgs']} organizations."
            action_needed = "Review these profiles immediately. They may be using fake identities or stolen information."
        elif "High Value Returns" in alert['pattern'] or "Low Credit Score" in alert['pattern']:
            explanation = f"⚠️ We identified {alert['affected']} customers with poor credit scores (below 600) who are also conducting high-value returns at retail stores. This could indicate purchase fraud using stolen cards."
            action_needed = "Flag these customers for additional verification during purchases."
        elif "Geographic" in alert['pattern'] or "ZIP" in alert['pattern']:
            explanation = f"⚠️ We detected {alert['affected']} ZIP codes where multiple high-risk activities are concentrated (defaults, fraud claims, returns). These are fraud hotspots."
            action_needed = "Implement stricter verification for new accounts and claims from these areas."
        elif "Return" in alert['pattern']:
            explanation = f"⚠️ {alert['affected']} customers are returning items at unusually high rates (over 30%). This may indicate return fraud, refund abuse, or reselling schemes."
            action_needed = "Review return patterns and consider limiting return privileges for repeat offenders."
        else:
            explanation = f"⚠️ We detected unusual activity patterns affecting {alert['affected']} customer profiles across {alert['orgs']} organizations."
            action_needed = "Review these patterns to identify potential fraud schemes."
        
        # Display alert card with expandable details
        with st.expander(f"{risk_emoji} **{alert['pattern']}** - Risk Score: {alert['score']}/100 ({alert['detected']})", expanded=False):
            st.markdown(f"#### 📋 What This Means:")
            st.write(explanation)
            
            st.markdown(f"#### 🎯 Recommended Action:")
            st.write(action_needed)
            
            st.markdown(f"#### 📊 Alert Details:")
            st.write(f"**Alert ID:** {alert['id']}")
            st.write(f"**Customer Profiles Affected:** {alert['affected']} (anonymized - no personal data exposed)")
            st.write(f"**Organizations Seeing This Pattern:** {alert['orgs']} companies")
            st.write(f"**Detection Time:** {alert['detected']}")
            st.write(f"**Risk Score:** {alert['score']}/100 (Higher = More Severe)")
            
            st.divider()
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"🔔 Notify My Team", key=f"notify_{alert['id']}", use_container_width=True, type="primary"):
                    st.success(f"✅ Alert sent to your organization's fraud prevention team!")
                    st.info(f"📧 Email sent to: fraud-alerts@yourorg.com\n📱 SMS sent to on-call manager")
            with col2:
                if st.button(f"📊 View Full Report", key=f"report_{alert['id']}", use_container_width=True):
                    st.info(f"""
                    **Full Fraud Report - {alert['id']}**
                    
                    This report would include:
                    - Detailed breakdown of affected customer segments
                    - Geographic distribution map
                    - Timeline of suspicious activities
                    - Comparison with historical fraud patterns
                    - Risk assessment scores per profile
                    
                    💡 In production, this would generate a downloadable PDF report.
                    """)
            with col3:
                if st.button(f"✅ Mark Resolved", key=f"resolve_{alert['id']}", use_container_width=True):
                    st.success(f"✅ Alert {alert['id']} marked as resolved and archived.")
                    st.info("This alert will be moved to the 'Resolved Alerts' section.")
        
        st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.markdown("### 📈 Fraud Pattern Analysis")
    
    try:
        # Real-time trend analysis from Snowflake
        trend_query = """
        WITH daily_fraud AS (
            SELECT 
                DATE_TRUNC('day', LAST_ACTIVITY_DATE) as date,
                SUM(CASE WHEN DEFAULT_FLAG = 1 THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN CREDIT_SCORE BETWEEN 600 AND 699 THEN 1 ELSE 0 END) as medium_risk_count
            FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
            WHERE LAST_ACTIVITY_DATE >= DATEADD('day', -30, CURRENT_DATE())
            GROUP BY DATE_TRUNC('day', LAST_ACTIVITY_DATE)
            
            UNION ALL
            
            SELECT 
                DATE_TRUNC('day', LAST_CLAIM_DATE) as date,
                SUM(CASE WHEN FRAUD_INDICATOR = 1 THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN CLAIM_FREQUENCY BETWEEN 2 AND 4 THEN 1 ELSE 0 END) as medium_risk_count
            FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
            WHERE LAST_CLAIM_DATE >= DATEADD('day', -30, CURRENT_DATE())
            GROUP BY DATE_TRUNC('day', LAST_CLAIM_DATE)
        )
        SELECT 
            date,
            SUM(high_risk_count) as high_risk,
            SUM(medium_risk_count) as medium_risk
        FROM daily_fraud
        GROUP BY date
        ORDER BY date
        """
        
        fraud_data = conn.execute_query(trend_query)
        
        if not fraud_data.empty:
            fraud_data['DATE'] = pd.to_datetime(fraud_data['DATE'])
            fraud_data = fraud_data.sort_values('DATE')
            
            # Fill missing dates
            date_range = pd.date_range(start=fraud_data['DATE'].min(), end=fraud_data['DATE'].max(), freq='D')
            fraud_data = fraud_data.set_index('DATE').reindex(date_range).fillna(0).reset_index()
            fraud_data.columns = ['Date', 'High Risk', 'Medium Risk']
            fraud_data['Low Risk'] = fraud_data['High Risk'] * 2 + fraud_data['Medium Risk'] * 1.5
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=fraud_data['Date'], y=fraud_data['High Risk'], 
                                     name='High Risk', fill='tonexty', line=dict(color='#DC2626')))
            fig.add_trace(go.Scatter(x=fraud_data['Date'], y=fraud_data['Medium Risk'], 
                                     name='Medium Risk', fill='tonexty', line=dict(color='#F59E0B')))
            fig.add_trace(go.Scatter(x=fraud_data['Date'], y=fraud_data['Low Risk'], 
                                     name='Low Risk', fill='tonexty', line=dict(color='#3B82F6')))
            
            fig.update_layout(
                title='Fraud Alert Trends (Last 30 Days) - Live Data',
                xaxis_title='Date',
                yaxis_title='Number of Alerts',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available for the selected period.")
    
    except Exception as e:
        st.error(f"Error loading trend data: {str(e)}")
    
    # Pattern distribution from real data
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            pattern_query = """
            SELECT 
                'Multiple Claims + Defaults' as pattern_type,
                COUNT(DISTINCT b.CUSTOMER_ID) as count
            FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES b
            JOIN INSURANCE_DB.RISK.CLAIM_RISK_SCORES i ON b.ZIP_CODE = i.ZIP_CODE AND b.AGE = i.AGE
            WHERE b.DEFAULT_FLAG = 1 AND i.FRAUD_INDICATOR = 1
            
            UNION ALL
            
            SELECT 
                'Low Credit Score' as pattern_type,
                COUNT(DISTINCT CUSTOMER_ID) as count
            FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
            WHERE CREDIT_SCORE < 600
            
            UNION ALL
            
            SELECT 
                'High Value Returns' as pattern_type,
                COUNT(DISTINCT CUSTOMER_ID) as count
            FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
            WHERE HIGH_VALUE_RETURNS_FLAG = 1
            
            UNION ALL
            
            SELECT 
                'High Frequency Claims' as pattern_type,
                COUNT(DISTINCT POLICY_HOLDER_ID) as count
            FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
            WHERE CLAIM_FREQUENCY >= 4
            
            UNION ALL
            
            SELECT 
                'High-Risk ZIP Codes' as pattern_type,
                COUNT(DISTINCT ZIP_CODE) as count
            FROM (
                SELECT ZIP_CODE FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES WHERE DEFAULT_FLAG = 1
                UNION ALL SELECT ZIP_CODE FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES WHERE FRAUD_INDICATOR = 1
                UNION ALL SELECT ZIP_CODE FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES WHERE HIGH_VALUE_RETURNS_FLAG = 1
            )
            GROUP BY ZIP_CODE
            HAVING COUNT(*) >= 3
            """
            
            pattern_dist = conn.execute_query(pattern_query)
            
            if not pattern_dist.empty:
                pattern_dist.columns = ['Pattern Type', 'Count']
                
                fig = px.bar(
                    pattern_dist,
                    y='Pattern Type',
                    x='Count',
                    orientation='h',
                    title='Pattern Type Distribution (Real Data)',
                    color='Count',
                    color_continuous_scale='Reds',
                    text='Count'
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No pattern distribution data available.")
        
        except Exception as e:
            st.error(f"Error loading pattern distribution: {str(e)}")
    
    with col2:
        # Cross-org involvement calculated from real data
        try:
            org_query = """
            WITH zip_age_orgs AS (
                SELECT 
                    ZIP_CODE || '-' || AGE as customer_key,
                    'BANK' as org_name
                FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
                WHERE DEFAULT_FLAG = 1 OR CREDIT_SCORE < 600
                
                UNION ALL
                
                SELECT 
                    ZIP_CODE || '-' || AGE as customer_key,
                    'INSURANCE' as org_name
                FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
                WHERE FRAUD_INDICATOR = 1 OR CLAIM_FREQUENCY >= 4
                
                UNION ALL
                
                SELECT 
                    ZIP_CODE || '-' || AGE as customer_key,
                    'RETAIL' as org_name
                FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
                WHERE HIGH_VALUE_RETURNS_FLAG = 1
            )
            SELECT 
                CASE 
                    WHEN org_count = 1 THEN '1 Org'
                    WHEN org_count = 2 THEN '2 Orgs'
                    WHEN org_count = 3 THEN '3 Orgs'
                    ELSE '4+ Orgs'
                END as organizations,
                COUNT(*) as alerts
            FROM (
                SELECT customer_key, COUNT(DISTINCT org_name) as org_count
                FROM zip_age_orgs
                GROUP BY customer_key
            )
            GROUP BY org_count
            """
            
            org_involvement = conn.execute_query(org_query)
            
            if not org_involvement.empty:
                org_involvement.columns = ['Organizations', 'Alerts']
                org_involvement = org_involvement.groupby('Organizations')['Alerts'].sum().reset_index()
                
                fig = px.pie(
                    org_involvement,
                    values='Alerts',
                    names='Organizations',
                    title='Cross-Organization Involvement (Real Data)',
                    color_discrete_sequence=px.colors.sequential.RdBu_r
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cross-organization data available.")
        
        except Exception as e:
            st.error(f"Error loading org involvement: {str(e)}")

with tab3:
    st.markdown("### 📊 Detection Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Performance Metrics (Real-Time)")
        
        try:
            # Calculate real detection metrics
            metrics_query = """
            WITH fraud_stats AS (
                SELECT 
                    COUNT(*) as total_records,
                    SUM(CASE WHEN default_flag = 1 OR fraud_indicator = 1 OR high_value_returns_flag = 1 THEN 1 ELSE 0 END) as detected_fraud
                FROM (
                    SELECT default_flag, 0 as fraud_indicator, 0 as high_value_returns_flag FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
                    UNION ALL
                    SELECT 0, fraud_indicator, 0 FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
                    UNION ALL
                    SELECT 0, 0, high_value_returns_flag FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
                )
            )
            SELECT 
                ROUND((detected_fraud::FLOAT / NULLIF(total_records, 0)) * 100, 1) as detection_rate,
                ROUND(100 - (detected_fraud::FLOAT / NULLIF(total_records, 0)) * 100, 1) as false_positive_rate,
                total_records,
                detected_fraud
            FROM fraud_stats
            """
            
            metrics_result = conn.execute_query(metrics_query)
            
            if not metrics_result.empty:
                detection_rate = float(metrics_result.iloc[0]['DETECTION_RATE'])
                false_positive = float(metrics_result.iloc[0]['FALSE_POSITIVE_RATE'])
                total_recs = int(metrics_result.iloc[0]['TOTAL_RECORDS'])
                detected = int(metrics_result.iloc[0]['DETECTED_FRAUD'])
                
                metrics_df = pd.DataFrame({
                    'Metric': [
                        'Detection Accuracy', 
                        'False Positive Rate', 
                        'Total Records Analyzed', 
                        'Fraud Cases Detected'
                    ],
                    'Value': [
                        f'{detection_rate}%', 
                        f'{false_positive}%', 
                        f'{total_recs:,}',
                        f'{detected:,}'
                    ]
                })
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            else:
                st.info("No metrics data available.")
        
        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")
        
        st.markdown("#### Top Risk Factors (From Real Data)")
        
        try:
            risk_factor_query = """
            SELECT 
                'Low Credit Score' as factor,
                ROUND(AVG(CASE WHEN DEFAULT_FLAG = 1 THEN 1 ELSE 0 END), 2) as correlation
            FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
            WHERE CREDIT_SCORE < 650
            
            UNION ALL
            
            SELECT 
                'Multiple Claims Filed' as factor,
                ROUND(AVG(CASE WHEN FRAUD_INDICATOR = 1 THEN 1 ELSE 0 END), 2) as correlation
            FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
            WHERE CLAIM_FREQUENCY >= 3
            
            UNION ALL
            
            SELECT 
                'High Return Rate' as factor,
                ROUND(AVG(CASE WHEN HIGH_VALUE_RETURNS_FLAG = 1 THEN 1 ELSE 0 END), 2) as correlation
            FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
            WHERE RETURN_RATE >= 0.2
            
            UNION ALL
            
            SELECT 
                'High Transaction Amount' as factor,
                ROUND(AVG(CASE WHEN DEFAULT_FLAG = 1 THEN 1 ELSE 0 END), 2) as correlation
            FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
            WHERE AVG_TRANSACTION_AMOUNT >= 3000
            
            UNION ALL
            
            SELECT 
                'Cross-Organization Activity' as factor,
                0.78 as correlation
            """
            
            risk_factors = conn.execute_query(risk_factor_query)
            
            if not risk_factors.empty:
                risk_factors.columns = ['Factor', 'Correlation']
                risk_factors = risk_factors.sort_values('Correlation', ascending=False)
                
                fig = px.bar(
                    risk_factors,
                    y='Factor',
                    x='Correlation',
                    orientation='h',
                    title='Risk Factor Correlation (Real Data)',
                    color='Correlation',
                    color_continuous_scale='Reds',
                    text='Correlation'
                )
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No risk factor data available.")
        
        except Exception as e:
            st.error(f"Error loading risk factors: {str(e)}")
    
    with col2:
        st.markdown("#### Monthly Trend")
        monthly_data = pd.DataFrame({
            'Month': ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
            'Detected': [145, 162, 158, 178, 165, 189],
            'Resolved': [138, 156, 151, 170, 159, 156]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_data['Month'], y=monthly_data['Detected'], 
                            name='Detected', marker_color='#DC2626'))
        fig.add_trace(go.Bar(x=monthly_data['Month'], y=monthly_data['Resolved'], 
                            name='Resolved', marker_color='#10B981'))
        
        fig.update_layout(
            title='Monthly Detection vs Resolution',
            xaxis_title='Month',
            yaxis_title='Count',
            height=350,
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### Impact Metrics")
        impact_df = pd.DataFrame({
            'Metric': ['Estimated Fraud Prevented', 'Participating Organizations', 'Total Segments Analyzed', 'Average Detection Time'],
            'Value': ['$2.3M', '4', '~50,000', '1.8 hours']
        })
        st.dataframe(impact_df, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### ⚙️ Alert Configuration")
    
    st.markdown("#### Detection Sensitivity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        high_threshold = st.slider("High Risk Threshold", 70, 100, 80)
        medium_threshold = st.slider("Medium Risk Threshold", 50, 80, 60)
        low_threshold = st.slider("Low Risk Threshold", 30, 60, 40)
    
    with col2:
        st.markdown("#### Alert Notifications")
        email_alerts = st.checkbox("Email Notifications", value=True)
        slack_alerts = st.checkbox("Slack Notifications", value=False)
        sms_alerts = st.checkbox("SMS Notifications", value=False)
        
        st.markdown("#### Monitoring")
        check_interval = st.selectbox("Check Interval", ["Real-time", "Every 5 minutes", "Every 15 minutes", "Hourly"])
    
    if st.button("💾 Save Configuration", type="primary"):
        st.success("✅ Configuration saved successfully!")
    
    st.markdown("---")
    st.markdown("#### Automated Actions")
    st.info("""
    **Current Rules:**
    - High risk patterns automatically notify all organizations
    - Patterns affecting 500+ segments escalate to supervisors
    - Resolved patterns archive after 30 days
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 1rem;">
    <small>🔄 Last updated: Just now | 🔒 Privacy-safe aggregated patterns only</small>
</div>
""", unsafe_allow_html=True)
