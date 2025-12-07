# 🧪 Testing Guide - SecureInsights Platform

## What This App Does

Your app is a **Privacy-Safe Analytics Platform** that allows banks, insurers, and retailers to collaborate on fraud detection **without sharing raw customer data**. Think of it as a "secure meeting room" where organizations can see patterns but not individual records.

---

## 🎯 Quick Start - 5 Minute Test

### 1. **Home Page** (Current Page)
**What you see:**
- Platform overview
- Core features explanation
- Use cases
- Organization list in sidebar

**What to test:**
- ✅ Check all text loads correctly
- ✅ Verify sidebar shows 3 organizations (Bank, Insurance, Retail)
- ✅ Resources links are visible
- ✅ Gradient hero section displays

**Expected Result:** Professional landing page with clear value proposition

---

### 2. **Cross Company Insights Page** 
**Click:** "Cross Company Insights" in sidebar

**What it does:** 
Natural language query interface where you ask questions like "Which age groups have highest fraud risk?" and get privacy-safe answers.

**Testing Steps:**

#### Test A: Demographic Analysis
1. Select any organization from dropdown
2. Choose query type: **"Demographic Analysis"**
3. Click **"Run Analysis"** button
4. **Expected Result:**
   - Bar chart showing risk scores by age group
   - Table with aggregated data (age groups, risk scores, fraud cases)
   - All groups have ≥50 records (privacy threshold)
   - Risk scores range from ~40-80

#### Test B: Geographic Analysis  
1. Choose query type: **"Geographic Analysis"**
2. Click **"Run Analysis"**
3. **Expected Result:**
   - Map or chart showing risk by ZIP code prefix
   - High-risk areas highlighted in red
   - Privacy-safe aggregation maintained

#### Test C: Fraud Pattern Detection
1. Choose query type: **"Fraud Pattern Detection"**
2. Click **"Run Analysis"**
3. **Expected Result:**
   - Line chart showing fraud trends over time
   - Statistics on fraud cases
   - Cross-organization patterns identified

**What to verify:**
- ✅ Queries execute without errors
- ✅ Charts render properly
- ✅ No individual customer data shown (only aggregates)
- ✅ Privacy badge shows "≥50 records" constraint
- ✅ Results match your Snowflake data

---

### 3. **Fraud Detection Page**
**Click:** "Fraud Detection" in sidebar

**What it does:**
Real-time monitoring dashboard showing detected fraud patterns across organizations.

**Testing Steps:**

1. Page loads with alert cards
2. **Expected Result:**
   - 5 fraud pattern cards displayed:
     - "Multiple Claims + Defaults" (Risk: 87)
     - "Rapid Account Openings" (Risk: 82)
     - "Geographic Anomalies" (Risk: 68)
     - "Return Fraud Pattern" (Risk: 65)
     - "Identity Indicators" (Risk: 78)

3. Filter by alert level (High/Medium/Low)
4. **Expected Result:** Cards filter dynamically

5. Scroll down to see:
   - **Fraud Trends Chart:** Line graph showing fraud over time
   - **Pattern Distribution:** Pie chart of fraud types
   - **Statistics:** Total alerts, high-risk patterns, organizations

**What to verify:**
- ✅ All 5 demo patterns display
- ✅ Risk scores are color-coded (red/yellow/green)
- ✅ Filters work correctly
- ✅ Charts render without errors
- ✅ Statistics update when filtering

---

### 4. **Reports Page**
**Click:** "Reports" in sidebar

**What it does:**
Generate and export reports in multiple formats.

**Testing Steps:**

1. Select report type: **"Fraud Risk Summary"**
2. Choose date range (last 30 days)
3. Select organizations (select all 3)
4. Click **"Generate Report"**
5. **Expected Result:**
   - Report preview shows with sample data
   - Download buttons appear (PDF, CSV, Excel, JSON)

6. Click **"Download CSV"**
7. **Expected Result:**
   - CSV file downloads with sample fraud data
   - File contains aggregated insights (not raw data)

**What to verify:**
- ✅ Report generation works
- ✅ Preview displays correctly
- ✅ All export formats available
- ✅ Downloads work (may be mock data)

---

## 🐛 Common Issues & Fixes

### Issue 1: "Connection Error" or "Database Not Found"
**Cause:** Snowflake connection failed  
**Fix:**
```bash
# Check .env file has correct credentials
cat .env

# Test connection manually
python -c "from app.utils.snowflake_connector import get_connection; conn = get_connection(); print('✅ Connected!' if conn else '❌ Failed')"
```

### Issue 2: "No Data Returned" on Queries
**Cause:** Clean Room views not created or no data  
**Check:**
```sql
-- In Snowflake, run:
SELECT COUNT(*) FROM CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK;
-- Should return > 0 rows
```

### Issue 3: Charts Not Rendering
**Cause:** Plotly/Altair installation issue  
**Fix:**
```bash
pip install plotly==5.18.0 altair==5.2.0 --force-reinstall
```

### Issue 4: "Session State Error"
**Fix:** Refresh the page (Ctrl+R or F5)

---

## 📊 What Each Page Should Show

### Home Page
- Hero banner with gradient
- 3 sections: Challenge, Solution, Features
- Sidebar with 3 organizations
- Tech stack list at bottom

### Cross Company Insights
- Query input/selection area
- Results in charts + tables
- Privacy indicators
- Query history (if implemented)
- Should take 2-5 seconds to load results

### Fraud Detection  
- 5 fraud pattern alert cards
- Risk level badges (87, 82, 78, 68, 65)
- 3 charts: Trends, Distribution, Stats
- Filter controls
- Should load instantly (demo data)

### Reports
- Form with dropdowns
- Date picker
- Generate button
- Preview area
- 4 download buttons (PDF, CSV, Excel, JSON)

---

## 🎬 Demo Flow for Judges/Presentation

**5-Minute Demo Script:**

1. **Start at Home (30 sec)**
   - "This is SecureInsights - a privacy-safe fraud detection platform"
   - "Banks, insurers, retailers collaborate WITHOUT sharing raw data"
   - Show organizations in sidebar

2. **Cross Company Insights (2 min)**
   - "Let's find high-risk age groups"
   - Run Demographic Analysis
   - Point out: "See? Only aggregated data, minimum 50 records"
   - Show chart: "Ages 25-34 have highest fraud risk at 68"
   - "This insight comes from 3 organizations combined"

3. **Fraud Detection (1.5 min)**
   - "Real-time pattern monitoring"
   - Show alert cards
   - "87 risk score - Multiple Claims + Defaults detected"
   - "3 organizations affected, 450 segments impacted"
   - Show trends chart

4. **Reports (1 min)**
   - "Generate exportable reports"
   - Generate report
   - "Download in any format for compliance"
   - "All data remains aggregated for privacy"

5. **Wrap up (30 sec)**
   - "Built on Snowflake Data Clean Rooms"
   - "30,000 records, real-time analytics"
   - "GDPR/CCPA compliant by design"

---

## ✅ Testing Checklist

Run through this before your demo/submission:

**Technical Tests:**
- [ ] App starts without errors: `streamlit run app/Home.py`
- [ ] All 4 pages load successfully
- [ ] No Python errors in terminal
- [ ] No JavaScript errors in browser console (F12)
- [ ] Snowflake connection works

**Functional Tests:**
- [ ] Can run at least one query successfully
- [ ] Charts render correctly
- [ ] Filters work on Fraud Detection page
- [ ] Can generate at least one report
- [ ] Privacy indicators show ≥50 records

**Visual Tests:**
- [ ] Logo/icons display correctly
- [ ] Colors match theme (blue/teal)
- [ ] Text is readable
- [ ] Mobile responsive (resize browser)
- [ ] No broken images

**Data Tests:**
- [ ] Results match what's in Snowflake
- [ ] Aggregation rules enforced (min 50 records)
- [ ] No individual customer IDs visible
- [ ] Fraud patterns are realistic

**Performance Tests:**
- [ ] Queries return in <10 seconds
- [ ] Page navigation is smooth
- [ ] No memory leaks (refresh works)
- [ ] Can handle multiple queries

---

## 🎥 Recording Your Demo Video

**Recommended Tools:**
- Loom (free): https://loom.com
- OBS Studio (free): https://obsproject.com
- Windows Game Bar: Win+G

**Video Structure (3-5 minutes):**
1. **Intro (20s):** "Hi, I'm [name], this is SecureInsights for Snowflake AI for Good hackathon"
2. **Problem (30s):** Show Home page, explain the challenge
3. **Demo (3min):** Walk through the 3 main pages with live clicks
4. **Impact (30s):** "This helps detect $X billion in fraud while protecting privacy"
5. **Tech (20s):** "Built with Snowflake Data Clean Rooms, Streamlit, Cortex AI"
6. **Outro (10s):** "Thank you! Link in description"

---

## 📈 Expected Data Ranges

When testing, you should see approximately:

**Risk Scores:**
- Low Risk: 30-50
- Medium Risk: 51-70  
- High Risk: 71-95

**Age Groups:**
- 18-24, 25-34, 35-44, 45-54, 55-64, 65+
- Each with ≥50 records

**Fraud Cases:**
- Total: ~2,400 cases (8% of 30,000)
- Bank defaults: ~800
- Insurance fraud: ~480
- Retail returns: ~600

**Organizations:**
- Metro Bank (🏦): 10,000 records
- SafeGuard Insurance (🛡️): 8,000 records
- RetailCorp (🛒): 12,000 records

---

## 🚀 Next Steps After Testing

1. **If Everything Works:**
   - Take screenshots of each page
   - Record demo video
   - Push to GitHub
   - Deploy to Streamlit Cloud
   - Submit to hackathon!

2. **If Issues Found:**
   - Check error messages in terminal
   - Review Snowflake connection
   - Verify SQL scripts ran successfully
   - Check this guide's troubleshooting section

3. **Improvements (Optional):**
   - Add more query examples
   - Enhance visualizations
   - Add user authentication
   - Implement real-time streaming

---

## 💡 Pro Tips

- **Practice your demo** 2-3 times before recording
- **Have backup screenshots** in case live demo fails
- **Know your numbers:** "30,000 records, 3 organizations, 8% fraud rate"
- **Explain privacy:** "Minimum 50 records, no individual data"
- **Emphasize impact:** "Prevent fraud while protecting privacy"
- **Show, don't tell:** Click buttons, show real results

---

## ❓ FAQ

**Q: What if Cortex AI doesn't work?**  
A: We built fallbacks - demo data will display instead

**Q: Can judges test this without Snowflake account?**  
A: Yes, if deployed to Streamlit Cloud with your credentials

**Q: How do I reset the demo data?**  
A: Re-run `python data_generators/generate_all_data.py`

**Q: What if a chart doesn't show?**  
A: Check browser console (F12) for errors, usually a data format issue

**Q: Is this production-ready?**  
A: It's a hackathon MVP - great for demo, needs hardening for production

---

## 📞 Need Help?

- Streamlit Docs: https://docs.streamlit.io
- Snowflake Docs: https://docs.snowflake.com
- Check terminal for error messages
- Look at browser console (F12 → Console tab)
- Test Snowflake connection independently

---

**Good luck with your hackathon! 🎉**

**Remember:** The judges care about:
1. **Problem solved** ✓ (Fraud detection with privacy)
2. **Use of Snowflake** ✓ (Data Clean Rooms, Cortex AI)
3. **Demo quality** (Practice makes perfect!)
4. **Real-world impact** ✓ (Billions saved, privacy protected)
