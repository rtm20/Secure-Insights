"""
Reports Page
Export and reporting functionality
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Reports & Export")
st.markdown("Generate and export privacy-safe reports")

# Help banner
st.markdown("""
<div style="background: #D1FAE5; padding: 1.25rem; border-radius: 10px; border-left: 4px solid #059669; margin-bottom: 1.5rem; color: #065F46;">
    <strong style="color: #065F46;">📖 What you can do here:</strong> Generate professional reports from your query results and export them in various formats.
    <br><br>
    <strong style="color: #065F46;">💡 How to use:</strong> 
    <ol style="margin: 0.5rem 0 0 1.5rem; padding: 0; color: #065F46; line-height: 1.8;">
        <li>Select report type (Executive Summary is great for management)</li>
        <li>Choose time period</li>
        <li>Configure what to include (charts, tables, AI insights)</li>
        <li>Click "Generate Report" and then download in your preferred format</li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Report Type Selection
st.markdown("### 📊 Report Generation")

col1, col2 = st.columns([2, 1])

with col1:
    report_type = st.selectbox(
        "Select Report Type",
        [
            "Executive Summary",
            "Fraud Pattern Analysis",
            "Geographic Risk Assessment",
            "Demographic Insights",
            "Time Series Trends",
            "Organization Comparison",
            "Custom Report"
        ]
    )

with col2:
    time_period = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "Custom Range"]
    )

# Report Configuration
st.markdown("### ⚙️ Report Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    include_charts = st.checkbox("Include Visualizations", value=True)
    include_data = st.checkbox("Include Data Tables", value=True)

with col2:
    include_insights = st.checkbox("Include AI Insights", value=True)
    include_recommendations = st.checkbox("Include Recommendations", value=True)

with col3:
    export_format = st.selectbox(
        "Export Format",
        ["PDF", "Excel (XLSX)", "CSV", "JSON"]
    )

# Generate Report Button
if st.button("📄 Generate Report", type="primary", use_container_width=True):
    with st.spinner("Generating report..."):
        st.success("✅ Report generated successfully!")
        
        # Preview section
        st.markdown("### 📋 Report Preview")
        
        st.markdown(f"""
        <div style="background-color: #F9FAFB; padding: 2rem; border-radius: 10px; border: 1px solid #E5E7EB;">
            <h2 style="color: #1F2937;">{report_type}</h2>
            <p style="color: #6B7280;">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p style="color: #6B7280;">Period: {time_period}</p>
            <hr style="border-color: #E5E7EB;">
            
            <h3 style="color: #1F2937;">Executive Summary</h3>
            <p>This privacy-safe report aggregates insights from multiple participating organizations while maintaining individual data confidentiality.</p>
            
            <h4>Key Findings:</h4>
            <ul>
                <li>🔴 12 high-risk fraud patterns detected affecting ~4,500 anonymized profiles</li>
                <li>📊 Geographic concentration in ZIP code prefix 103 (Risk Score: 82)</li>
                <li>👥 Age group 25-34 shows highest fraud correlation (7.2%)</li>
                <li>💰 Estimated fraud prevention: $2.3M across all organizations</li>
            </ul>
            
            <h4>Privacy Compliance:</h4>
            <p style="color: #10B981;">✅ All data aggregated (min. 50 records)<br>
            ✅ No individual PII exposed<br>
            ✅ GDPR and CCPA compliant<br>
            ✅ Complete audit trail maintained</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Download buttons
        st.markdown("### 📥 Download Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if export_format == "PDF" or export_format == "All Formats":
                st.download_button(
                    "📄 Download PDF",
                    data="Sample PDF content",
                    file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col2:
            if export_format == "Excel (XLSX)" or export_format == "All Formats":
                # Create sample data
                sample_df = pd.DataFrame({
                    'Metric': ['Total Alerts', 'High Risk', 'Fraud Rate', 'Organizations'],
                    'Value': [85, 12, '7.2%', 4]
                })
                st.download_button(
                    "📊 Download Excel",
                    data=sample_df.to_csv(index=False),
                    file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        with col3:
            if export_format == "CSV" or export_format == "All Formats":
                sample_df = pd.DataFrame({
                    'Date': [datetime.now() - timedelta(days=i) for i in range(7)],
                    'Alerts': [12, 15, 11, 14, 16, 13, 18],
                    'Risk_Score': [72, 68, 75, 71, 69, 73, 70]
                })
                st.download_button(
                    "📁 Download CSV",
                    data=sample_df.to_csv(index=False),
                    file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col4:
            if export_format == "JSON" or export_format == "All Formats":
                st.download_button(
                    "🔤 Download JSON",
                    data='{"report": "sample"}',
                    file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )

st.markdown("---")

# Recent Reports Section
st.markdown("### 📚 Recent Reports")

recent_reports = [
    {"name": "Monthly Fraud Analysis - November 2025", "date": "Nov 30, 2025", "type": "PDF", "size": "2.3 MB"},
    {"name": "Geographic Risk Assessment - Q4 2025", "date": "Nov 28, 2025", "type": "Excel", "size": "1.8 MB"},
    {"name": "Executive Summary - October 2025", "date": "Nov 01, 2025", "type": "PDF", "size": "1.5 MB"},
    {"name": "Demographic Insights - Q3 2025", "date": "Oct 15, 2025", "type": "PDF", "size": "2.1 MB"},
]

for report in recent_reports:
    col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
    
    with col1:
        st.markdown(f"**{report['name']}**")
    with col2:
        st.text(report['date'])
    with col3:
        st.text(report['type'])
    with col4:
        st.text(report['size'])
    with col5:
        if st.button("📥", key=f"download_{report['name']}", help="Download"):
            st.info("Download would start here")

st.markdown("---")

# Scheduled Reports Section
st.markdown("### ⏰ Scheduled Reports")

st.info("""
**Current Schedule:**
- 📄 Executive Summary: Weekly (Every Monday at 9:00 AM)
- 📊 Fraud Pattern Analysis: Daily (Every day at 7:00 AM)
- 📈 Monthly Report: Monthly (1st of each month at 8:00 AM)
""")

if st.button("⚙️ Manage Schedule"):
    st.success("Schedule management interface would open here")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 1rem;">
    <small>🔒 All reports maintain privacy compliance | No individual PII included</small>
</div>
""", unsafe_allow_html=True)
