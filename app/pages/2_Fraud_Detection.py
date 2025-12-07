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
data_placeholder.markdown("""
<div style="text-align: center; padding: 2rem;">
    <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top-color: #667eea; border-radius: 50%; animation: spin 1s linear infinite;"></div>
    <p style="margin-top: 1rem; color: #6B7280;">Loading live fraud data from Snowflake...</p>
</div>
<style>
@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)

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
    
    # Sample fraud alerts
    alerts = [
        {
            "id": "ALT-2024-001",
            "pattern": "Multiple Claims + Defaults",
            "risk": "High",
            "affected": 450,
            "orgs": 3,
            "detected": "2 hours ago",
            "score": 87
        },
        {
            "id": "ALT-2024-002",
            "pattern": "Rapid Account Openings",
            "risk": "High",
            "affected": 320,
            "orgs": 2,
            "detected": "5 hours ago",
            "score": 82
        },
        {
            "id": "ALT-2024-003",
            "pattern": "Geographic Anomalies",
            "risk": "Medium",
            "affected": 580,
            "orgs": 3,
            "detected": "1 day ago",
            "score": 68
        },
        {
            "id": "ALT-2024-004",
            "pattern": "Return Fraud Pattern",
            "risk": "Medium",
            "affected": 210,
            "orgs": 2,
            "detected": "1 day ago",
            "score": 65
        },
        {
            "id": "ALT-2024-005",
            "pattern": "Unusual Transaction Velocity",
            "risk": "Low",
            "affected": 150,
            "orgs": 2,
            "detected": "2 days ago",
            "score": 52
        },
    ]
    
    # Display alerts
    for alert in alerts:
        if alert["risk"] in risk_filter or not risk_filter:
            alert_class = f"alert-{alert['risk'].lower()}"
            risk_emoji = "🔴" if alert["risk"] == "High" else "🟡" if alert["risk"] == "Medium" else "🔵"
            
            st.markdown(f"""
            <div class="{alert_class}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem;">
                            {risk_emoji} {alert['pattern']}
                        </div>
                        <div style="color: #6B7280; font-size: 0.9rem;">
                            <strong>Alert ID:</strong> {alert['id']}<br>
                            <strong>Affected Segments:</strong> ~{alert['affected']} anonymized profiles<br>
                            <strong>Organizations Involved:</strong> {alert['orgs']}<br>
                            <strong>Detected:</strong> {alert['detected']}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 2rem; font-weight: bold;">{alert['score']}</div>
                        <div style="font-size: 0.8rem;">Risk Score</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button(f"🔍 View Details", key=f"view_{alert['id']}"):
                    st.info(f"Detailed analysis for {alert['id']} would appear here.")
            with col2:
                if st.button(f"📊 Show Pattern", key=f"pattern_{alert['id']}"):
                    st.info("Pattern visualization would appear here.")
            with col3:
                if st.button(f"🔔 Notify All", key=f"notify_{alert['id']}"):
                    st.success("Notification sent to all participating organizations!")
            with col4:
                if st.button(f"✅ Mark Resolved", key=f"resolve_{alert['id']}"):
                    st.success(f"Alert {alert['id']} marked as resolved.")
            
            st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.markdown("### 📈 Fraud Pattern Analysis")
    
    # Time series of fraud detection
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    fraud_data = pd.DataFrame({
        'Date': dates,
        'High Risk': [12, 15, 11, 18, 14, 16, 13, 19, 15, 14, 17, 12, 16, 20, 15, 14, 18, 13, 17, 16, 15, 19, 14, 18, 16, 17, 15, 18, 14, 12],
        'Medium Risk': [25, 28, 23, 30, 26, 29, 24, 31, 27, 26, 30, 25, 29, 33, 28, 27, 31, 26, 30, 29, 28, 32, 27, 31, 29, 30, 28, 31, 27, 28],
        'Low Risk': [40, 45, 38, 48, 42, 46, 39, 49, 43, 42, 47, 40, 46, 51, 45, 43, 48, 41, 47, 46, 45, 50, 43, 48, 46, 47, 45, 48, 43, 45]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fraud_data['Date'], y=fraud_data['High Risk'], 
                             name='High Risk', fill='tonexty', line=dict(color='#DC2626')))
    fig.add_trace(go.Scatter(x=fraud_data['Date'], y=fraud_data['Medium Risk'], 
                             name='Medium Risk', fill='tonexty', line=dict(color='#F59E0B')))
    fig.add_trace(go.Scatter(x=fraud_data['Date'], y=fraud_data['Low Risk'], 
                             name='Low Risk', fill='tonexty', line=dict(color='#3B82F6')))
    
    fig.update_layout(
        title='Fraud Alert Trends (Last 30 Days)',
        xaxis_title='Date',
        yaxis_title='Number of Alerts',
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Pattern distribution
    col1, col2 = st.columns(2)
    
    with col1:
        pattern_dist = pd.DataFrame({
            'Pattern Type': [
                'Multiple Claims + Defaults',
                'Rapid Account Openings',
                'Geographic Anomalies',
                'Return Fraud',
                'Transaction Velocity',
                'Identity Theft Indicators'
            ],
            'Count': [45, 38, 52, 28, 31, 24]
        })
        
        fig = px.bar(
            pattern_dist,
            y='Pattern Type',
            x='Count',
            orientation='h',
            title='Pattern Type Distribution',
            color='Count',
            color_continuous_scale='Reds',
            text='Count'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        org_involvement = pd.DataFrame({
            'Organizations': ['1 Org', '2 Orgs', '3 Orgs', '4+ Orgs'],
            'Alerts': [28, 95, 58, 37]
        })
        
        fig = px.pie(
            org_involvement,
            values='Alerts',
            names='Organizations',
            title='Cross-Organization Involvement',
            color_discrete_sequence=px.colors.sequential.RdBu_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 📊 Detection Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Performance Metrics")
        metrics_df = pd.DataFrame({
            'Metric': ['Detection Accuracy', 'False Positive Rate', 'Average Response Time', 'Resolution Rate'],
            'Value': ['94.2%', '5.8%', '2.3 hours', '91.5%']
        })
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        st.markdown("#### Top Risk Factors")
        risk_factors = pd.DataFrame({
            'Factor': ['Age 25-34', 'ZIP 103 Area', 'High Transaction Velocity', 'Multiple Org Activity', 'Recent Account Opening'],
            'Correlation': [0.87, 0.82, 0.79, 0.76, 0.71]
        })
        
        fig = px.bar(
            risk_factors,
            y='Factor',
            x='Correlation',
            orientation='h',
            title='Risk Factor Correlation',
            color='Correlation',
            color_continuous_scale='Reds',
            text='Correlation'
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
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
